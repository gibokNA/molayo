from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile
from routes.users import get_user
from models.users import User

import io
import tensorflow as tf
import numpy as np
import PIL.Image as Image


deeplearning_router = APIRouter()

interpreter = tf.lite.Interpreter(model_path="/app/src/1.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

IMAGE_SHAPE = (224, 224)

labels_path = tf.keras.utils.get_file('ImageNetLabels.txt','https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt')
imagenet_labels = np.array(open(labels_path).read().splitlines())


@deeplearning_router.post('/deeplearning')
async def deeplearning(
        file: UploadFile
    ):

    local_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="허가되지 않은 이미지 포맷"
    )

    if not file.filename.split('.')[-1].lower() in ['jpg', 'jpeg', 'gif', 'png', 'webp', 'bmp']:
        raise local_exception
    
    if not 'image' in file.content_type:
        raise local_exception
    
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="사이즈가 너무 큼. 최대 10mb 까지만 허용."
        )
    
    content = await file.read()

    img = Image.open(io.BytesIO(content)).resize(IMAGE_SHAPE)
    img = np.array(img)/255.0
    img = img.astype(np.float32)

    with tf.device('CPU'):
        interpreter.set_tensor(input_details[0]['index'], img[np.newaxis, ...])
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

    predicted_class = np.argmax(output_data[0], axis=-1)

    return imagenet_labels[predicted_class]




