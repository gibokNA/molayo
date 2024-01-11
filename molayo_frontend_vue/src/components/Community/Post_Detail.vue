<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'
import Post_List from './Post_List.vue'

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

const { error_handler, convert_timestamp_to_datetime } = global_store

const id = ref(route.params.post_id)
const post_username = ref("")
const nickname = ref("")
const title = ref("")
const created = ref("")
const edited = ref("")
const displayed_time = ref("")
const view_count = ref(0)
const like_count = ref(0)
const comment_count = ref(0)
const body = ref("")

const comments = reactive({data: [] as any})
const comments_page = ref(1)

axios.get('https://molayo.work/api/posts/' + String(id.value)).then((res: any) => {
    id.value = res.data.id
    post_username.value = res.data.username
    nickname.value = res.data.nickname
    title.value = res.data.title
    created.value = res.data.created
    edited.value = res.data.edited
    displayed_time.value = convert_timestamp_to_datetime((res.data.edited!=null?res.data.edited:res.data.created))
    view_count.value = res.data.view_count
    like_count.value = res.data.like_count
    comment_count.value = res.data.comment_count
    body.value = res.data.body

    comments.data = res.data.comments.reverse()

    setTimeout(() => {
        comments_page.value = Math.ceil(comment_count.value / 50)
    }, 500);
})


const is_delete_button_clicked = ref(false)

function delete_button_clicked() {

    axios.delete('https://molayo.work/api/posts/' + String(id.value), auth_header.value.data).then((res: any) => {
        modal_title.value = "삭제성공"
        modal_text.value = "삭제완료. 2초뒤 메인페이지로 이동합니다."
        is_modal_show.value = true

        setTimeout(() => {
            is_modal_show.value = false

            router.push('/')
        }, 2000);
    }).catch((error: any) => {
        let error_modal_title = "게시글 삭제 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}


const comment_input_text = ref("")

function submit_comment_button_clicked() {
    if (comment_input_text.value.length == 0) return

    let post_data = {
        "text": comment_input_text.value
    }

    axios.post('https://molayo.work/api/posts/' + String(id.value) + '/comments', post_data, auth_header.value.data).then((res: any) => {
        comment_input_text.value = ""

        axios.get('https://molayo.work/api/posts/' + String(id.value) + '/comments?offset=0&limit=50').then((res: any) => {
            comments.data = res.data.comments.reverse()
            comment_count.value = res.data.comment_count

            setTimeout(() => {
                comments_page.value = Math.ceil(comment_count.value / 50)
            }, 500);
        })

    }).catch((error: any) => {
        let error_modal_title = "댓글 작성 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}



function comment_pagenation_clicked(event: any, page: number) {
    request_comment_list(page)
}

function request_comment_list(page: number) {
    let offset = String((Math.ceil(comment_count.value / 50) - page) * 50)

    axios.get('https://molayo.work/api/posts/' + String(id.value) + '/comments?offset=' + offset + '&limit=50').then((res: any) => {
        comments.data = res.data.comments.reverse()
        comment_count.value = res.data.comment_count
    })
}


function keydown(event: any) {
    if (event.which === 13) {
        submit_comment_button_clicked()
    }
}

function comment_delete_button_clicked(comment_id: number) {
    axios.delete('https://molayo.work/api/posts/' + String(id.value) + '/' + String(comment_id), auth_header.value.data).then((res: any) => {
        request_comment_list(comments_page.value)
    }).catch((error: any) => {
        let error_modal_title = "댓글 삭제 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

</script>

<template>
    <BContainer fluid="true">
        <BRow style="margin-bottom: 10px;">
            <BCol>
                <BCard>
                    <BRow align-h="start">
                        <BCol cols="auto">
                            {{ title }}
                        </BCol>
                    </BRow>

                    <BRow align-h="between">
                        <BCol cols="auto">
                            <BRow>
                                <BCol cols="auto">{{ nickname }}  |  {{ (edited!=null?'수정됨 : ':'') + displayed_time }}</BCol>
                            </BRow>
                        </BCol>

                        <BCol cols="auto">
                            <BRow>
                                <BCol cols="auto">조회 {{ view_count }}  |  추천 {{ like_count }}  |  댓글  {{ comment_count }}</BCol>
                            </BRow>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow style="margin-bottom: 70px; min-height: 400px;">
                        <BCol>
                            <QuillEditor theme="bubble" :toolbar="[]" v-model:content="body" contentType="html" :readOnly="true"/>
                        </BCol>
                    </BRow>

                    <hr v-if="username==post_username">

                    <BRow v-if="username==post_username" align-h="end">
                        <BCol cols="auto" style="margin-right: -10px;" v-if="is_delete_button_clicked==false">
                            <BButton squared variant="warning" @click="() => router.push('/posts/' + String(id) + '/edit')">수정</BButton>
                        </BCol>
                        <BCol cols="auto" v-if="is_delete_button_clicked==false">
                            <BButton squared variant="danger" @click="is_delete_button_clicked=true">삭제</BButton>
                        </BCol>

                        <BCol cols="auto" style="margin-right: -10px;" v-if="is_delete_button_clicked==true">
                            <BButton squared @click="is_delete_button_clicked=false">취소</BButton>
                        </BCol>
                        <BCol cols="auto" v-if="is_delete_button_clicked==true">
                            <BButton squared variant="danger" @click="delete_button_clicked">삭제확인</BButton>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow align-h="between" v-if="comment_count >= 30">
                        <BCol cols="auto">
                            댓글 전체 {{comment_count}} 개
                        </BCol>
                        <BCol cols="auto">
                            <BPagination v-model="comments_page" :total-rows="comment_count" perPage="50" @page-click="comment_pagenation_clicked"></BPagination>
                        </BCol>
                        <BCol cols="auto">
                            <BButton squared @click="request_comment_list(comments_page)">새로고침</BButton>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow v-for="comment in comments.data" :key="comment.id" align-h="between">
                        <BCol cols="auto">{{comment.nickname}}</BCol>
                        <BCol style="text-align: start;">{{comment.text}}</BCol>
                        <BCol cols="auto">
                            {{convert_timestamp_to_datetime(comment.created)}} 
                            <IBiFile-Excel-Fill v-if="username==comment.username" @click="comment_delete_button_clicked(comment.id)" style="cursor: pointer;" />
                        </BCol>
                        <hr>
                    </BRow>
                    <BRow align-h="between">
                        <BCol cols="auto">
                            댓글 전체 {{comment_count}} 개
                        </BCol>
                        <BCol cols="auto">
                            <BPagination v-model="comments_page" :total-rows="comment_count" perPage="50" @page-click="comment_pagenation_clicked"></BPagination>
                        </BCol>
                        <BCol cols="auto">
                            <BButton squared @click="request_comment_list(comments_page)">새로고침</BButton>
                        </BCol>
                    </BRow>

                    <hr>


                    <BRow style="margin-bottom: 10px;">
                        <BCol>
                            <BFormTextarea style="min-height: 100px;" v-model="comment_input_text" placeholder="댓글" @keydown="keydown"></BFormTextarea>
                        </BCol>
                    </BRow>
                    <BRow align-h="end">
                        <BCol cols="auto">
                            <BButton squared variant="primary" @click="submit_comment_button_clicked">등록</BButton>
                        </BCol>
                    </BRow>
                </BCard>
            </BCol>
        </BRow>

        <hr>

        <Post_List style="padding-left: 0px; padding-right: 0px;"></Post_List>
    </BContainer>
</template>