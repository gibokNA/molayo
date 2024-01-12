<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

const router = useRouter()
const route = useRoute()

const axios: any = inject('axios')  // inject axios

const global_store = use_global_store()

const {
    is_login,
    username,
    auth_header,
    modal_title,
    modal_text,
    is_modal_show
} = storeToRefs(global_store)

const { error_handler } = global_store

const file = ref<null | File>(null)
const image_url = ref("")

function submit_button_clicked() {
    if (file.value == null) return

    if (file.value.size >= 10 * 1024 * 1024) {
        modal_title.value = "이미지가 너무 큼"
        modal_text.value = "최대 10MB 까지만 됩니다."
        is_modal_show.value = true
        return
    }

    image_url.value = URL.createObjectURL(file.value)

    is_now_processing.value = true

    let formData = new FormData();
    formData.append("file", file.value);

    axios.post('https://molayo.work/api/deeplearning', formData, auth_header.value.data).then((res: any) => {
        deeplearning_predict.value = res.data

        is_now_processing.value = false
    }).catch((error: any) => {
        let error_modal_title = "딥러닝 처리 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)

        is_now_processing.value = false
    })
}

const deeplearning_predict = ref("")
const is_now_processing = ref(false)

</script>

<template>
    <BContainer fluid="true">
        <BRow style="margin-bottom: 10px;">
            <BCol>
                <BCard>
                    <BRow>
                        <BCol>
                            <span style="font-weight: bold; font-size: 20px;">딥러닝 - 이미지 올리면 무슨사진인지 맞춰드림. 몇초 걸립니다.</span>
                        </BCol>
                    </BRow>

                    <BRow>
                        <BCol>
                            <span style="font-weight: lighter;">model => mobilenet-v3/large-100-224-classification</span>
                        </BCol>
                    </BRow>

                    <BRow>
                        <BCol>
                            <span style="font-weight: lighter;">labels => ImageNetLabels [1000개의 카테고리]</span>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow>
                        <BCol style="margin-right: -10px;">
                            <BFormFile v-model="file" accept="image/*" size="lg" :change="() => {console.log(1)}"/>
                        </BCol>

                        <BCol cols="auto">
                            <BButton size="lg" squared variant="dark" @click="submit_button_clicked" :disabled="is_now_processing?true:false">보내기</BButton>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow style="text-align: center; margin-bottom: 10px;">
                        <BCol>
                            <BSpinner variant="primary" v-if="is_now_processing==true" />
                            <span v-else style="font-weight: bold; font-size: 25px;">{{ deeplearning_predict }}</span>
                        </BCol>
                    </BRow>

                    <BRow>
                        <BCol>
                            <BImg center fluid :src="image_url"></BImg>
                        </BCol>
                    </BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>