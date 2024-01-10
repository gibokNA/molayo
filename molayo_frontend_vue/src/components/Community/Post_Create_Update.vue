<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

// @ts-ignore
import BlotFormatter from 'quill-blot-formatter/dist/BlotFormatter'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
// @ts-ignore
import ImageUploader from 'quill-image-uploader';

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

const title = ref("")
const body = ref("")

function submit_button_clicked() {
    if (title.value.length == 0 || body.value.length == 0) {
        modal_title.value = "제목 or 내용 없음."
        modal_text.value = "제목과 내용을 채워주세요."   
        is_modal_show.value = true
        return 
    }

    let post_data = {
        title: title.value,
        body: body.value
    }

    axios.post('https://api.molayo.work/posts', post_data, auth_header.value.data).then((res: any) => {

        router.push({
            path: "/posts/" + String(res.data)
        })

    }).catch((error: any) => {
        let error_modal_title = "게시글 작성 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

if (route.path != '/posts/create') {
    let post_id = route.params.post_id

    axios.get('https://api.molayo.work/posts/' + String(post_id)).then((res: any) => {
        title.value = res.data.title
        body.value = res.data.body
    })
}

function edit_button_clicked() {
    if (title.value.length == 0 || body.value.length == 0) {
        modal_title.value = "제목 or 내용 없음."
        modal_text.value = "제목과 내용을 채워주세요."   
        is_modal_show.value = true
        return 
    }

    let post_id = route.params.post_id

    let put_data = {
        title: title.value,
        body: body.value
    }

    axios.put('https://api.molayo.work/posts/' + String(post_id), put_data, auth_header.value.data).then((res: any) => {
        router.push({
            path: "/posts/" + String(post_id)
        })
    }).catch((error: any) => {
        let error_modal_title = "게시글 수정 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

const modules = [
    {
        name: 'imageUploader',
        module: ImageUploader,
        options: {
            upload: (file: any) => {
            return new Promise((resolve, reject) => {
                const formData = new FormData();
                formData.append("file", file);

                axios.post('https://api.molayo.work/posts/upload-image', formData, auth_header.value.data)
                .then((res: any) => {
                resolve(res.data.url);
                })
                .catch((err: any) => {
                reject("Upload failed");
                })
            })
            }
        }
    },
    {
      name: 'blotFormatter',  
      module: BlotFormatter, 
      options: {}
    }
]


</script>

<template>
    <BContainer fluid="true">
        <BRow style="margin-bottom: 10px;">
            <BCol>
                <BCard>
                    <BRow style="margin-bottom: 10px;">
                        <BCol>
                            <BFormInput v-model="title" placeholder="제목"></BFormInput>
                        </BCol>
                    </BRow>

                    <BRow style="margin-bottom: 80px; min-height: 400px;">
                        <BCol>
                            <QuillEditor theme="snow" toolbar="full" :modules="modules" v-model:content="body" contentType="html"/>
                        </BCol>
                    </BRow>

                    <BRow align-h="end">
                        <BCol cols="auto">
                            <BButton squared style="margin-right: 10px;" @click="() => router.push('/')">취소</BButton>
                            <BButton v-if="route.path == '/posts/create'" squared variant="success" @click="submit_button_clicked">등록</BButton>
                            <BButton v-else squared variant="warning" @click="edit_button_clicked">수정</BButton>
                        </BCol>
                    </BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>