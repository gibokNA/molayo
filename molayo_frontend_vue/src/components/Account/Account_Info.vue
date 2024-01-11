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

const { error_handler, convert_timestamp_to_datetime } = global_store

const id = ref(0)
const nickname = ref("")
const post_count = ref(0)
const comment_count = ref(0)

axios.get('https://molayo.work/api/users/me', auth_header.value.data).then((res: any) => {
    id.value = res.data.id
    nickname.value = res.data.nickname
    post_count.value = res.data.post_count
    comment_count.value = res.data.comment_count
})

const is_change_nickname_button_clicked = ref(false)
const new_nickname = ref("")

function change_nickname_button_clicked() {
    if (new_nickname.value.length == 0) return

    axios.put('https://molayo.work/api/users/nickname', new_nickname.value, auth_header.value.data).then((res: any) => {
        nickname.value = new_nickname.value
        new_nickname.value = ""
        is_change_nickname_button_clicked.value = false
    }).catch((error: any) => {
        let error_modal_title = "닉네임 변경 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

const is_change_password_button_clicked = ref(false)

const change_password_confirm_old_password = ref("")
const change_password_confirm_new_password = ref("")

function change_password_button_clicked() {
    if (change_password_confirm_old_password.value.length == 0 || 
        change_password_confirm_new_password.value.length == 0) return 

    let formData = new FormData()
    formData.append("old_password", change_password_confirm_old_password.value)
    formData.append("new_password", change_password_confirm_new_password.value)

    axios.put('https://molayo.work/api/users/password', formData, auth_header.value.data).then((res: any) => {
        modal_title.value = "비밀번호 변경 성공"
        modal_text.value = "비밀번호 변경에 성공했습니다."
        is_modal_show.value = true

        change_password_confirm_old_password.value = ""
        change_password_confirm_new_password.value = ""
        is_change_password_button_clicked.value = false
    }).catch((error: any) => {
        let error_modal_title = "비밀번호 변경 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

const users_posts = reactive({data: [] as any})

request_users_post_list(1)

const users_post_list_page = ref(1)


function users_post_list_pagenation_clicked(event: any, page: number) {
    request_users_post_list(page)
}

function request_users_post_list(page: number) {
    let offset = String(50 * (page - 1))
    let limit = "50"

    axios.get('https://molayo.work/api/users/posts', auth_header.value.data).then((res: any) => {
        users_posts.data = res.data
    })
}

const users_comments = reactive({data: [] as any})

request_users_comment_list(1)

function request_users_comment_list(page: number) {
    let offset = String(50 * (page - 1))
    let limit = "50"

    axios.get('https://molayo.work/api/users/comments', auth_header.value.data).then((res: any) => {        
        users_comments.data = res.data
    })
}

const users_comment_list_page = ref(1)

function users_comment_list_pagenation_clicked(event: any, page: number) {
    request_users_comment_list(page)
}

const is_delete_user_button_clicked = ref(false)
const delete_user_username = ref("")
const delete_user_password = ref("")

function delete_user_button_clicked() {
    if (delete_user_username.value.length == 0 || delete_user_password.value.length == 0) return

    let formData = new FormData()
    formData.append("username", delete_user_username.value)
    formData.append("password", delete_user_password.value)

    axios.put('https://molayo.work/api/users', formData, auth_header.value.data).then((res: any) => {
        modal_title.value = "계정 삭제 완료"
        modal_text.value = "2초뒤 메인페이지로 이동합니다."
        is_modal_show.value = true

        is_login.value = false
        username.value = ""
        auth_header.value.data = {}
        localStorage.removeItem('username')
        localStorage.removeItem('auth_header')
        localStorage.removeItem('last_login')

        setTimeout(() => {
            router.push('/')
        }, 2000);
    }).catch((error: any) => {
        let error_modal_title = "계정 삭제 실패"
        let error_modal_text = String(error.response.data.detail)

        error_handler(error_modal_title, error_modal_text)
    })
}

</script>

<template>
    <BContainer fluid="true">
        <BRow align-h="center" style="margin-bottom: 10px;">
            <BCol>
                <BCard>
                    <BRow>
                        <BCol>아이디 : {{ username }}</BCol>
                    </BRow>
                    
                    <BRow>
                        <BCol>닉네임 : {{ nickname }}</BCol>
                    </BRow>

                    <BRow>
                        <BCol>게시글 : {{ post_count }} 개</BCol>
                    </BRow>

                    <BRow>
                        <BCol>댓글 : {{ comment_count }} 개</BCol>
                    </BRow>

                    <hr>

                    <BRow style="margin-bottom: 10px;" v-if="is_change_nickname_button_clicked==false">
                        <BCol>
                            <BButton squared variant="primary" style="width: 300px;" @click="is_change_nickname_button_clicked=true">닉네임변경</BButton>
                        </BCol>
                    </BRow>

                    <BRow style="margin-bottom: 10px;" v-if="is_change_nickname_button_clicked==true">
                        <BCol>
                            <BFormInput v-model="new_nickname" placeholder="새로운 닉네임"></BFormInput>
                        </BCol>
                    </BRow>

                    <BRow style="margin-bottom: 10px;" v-if="is_change_nickname_button_clicked==true">
                        <BCol>
                            <BButton squared style="margin-right: 10px;" @click="is_change_nickname_button_clicked=false">취소</BButton>
                            <BButton squared variant="primary" @click="change_nickname_button_clicked">변경</BButton>
                        </BCol>
                    </BRow>

                    <BRow v-if="is_change_password_button_clicked==false">
                        <BCol>
                            <BButton squared variant="warning" style="width: 300px;" @click="is_change_password_button_clicked=true">비밀번호변경</BButton>
                        </BCol>
                    </BRow>

                    <BRow v-if="is_change_password_button_clicked==true">
                        <BCol>
                            <BRow style="margin-bottom: 5px;">
                                <BCol>
                                    <BFormInput v-model="change_password_confirm_old_password" placeholder="이전 비밀번호" type="password"></BFormInput>
                                </BCol>
                            </BRow>

                            <BRow style="margin-bottom: 5px;">
                                <BCol>
                                    <BFormInput v-model="change_password_confirm_new_password" placeholder="새로운 비밀번호" type="password"></BFormInput>
                                </BCol>
                            </BRow>

                            <BRow>
                                <BCol>
                                    <BButton squared style="margin-right: 10px;" @click="is_change_password_button_clicked=false">취소</BButton>
                                    <BButton squared variant="warning" @click="change_password_button_clicked">변경</BButton>
                                </BCol>
                            </BRow>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow>
                        <BCol style="font-weight: bold;">
                            게시글 {{ post_count }} 개
                        </BCol>
                    </BRow>
                    
                    <BRow style="text-align: center; font-weight: bold; min-width: 900px;">
                        <BCol cols="1">번호</BCol>
                        <BCol cols="5">제목</BCol>
                        <BCol>글쓴이</BCol>
                        <BCol>날짜</BCol>
                        <BCol cols="1">조회</BCol>
                        <BCol cols="1">추천</BCol>
                    </BRow>

                    <BRow v-for="post in users_posts.data" :key="post.id" style="min-width: 900px; font-size: 14px; text-align: center;">
                        <BCol cols="1">{{ post.id }}</BCol>
                        <BCol cols="5" style="text-align: start; cursor: pointer;" @click="router.push('/posts/' + String(post.id))">{{ post.title }} [{{post.comment_count}}]</BCol>
                        <BCol>{{ post.nickname }}</BCol>
                        <BCol>{{ convert_timestamp_to_datetime(post.created) }}</BCol>
                        <BCol cols="1">{{ post.view_count }}</BCol>
                        <BCol cols="1">{{ post.like_count }}</BCol>
                    </BRow>

                    <hr>

                    <BRow align-h="center">
                        <BCol cols="auto">
                            <BPagination v-model="users_post_list_page" :total-rows="post_count" perPage="50" @page-click="users_post_list_pagenation_clicked"></BPagination>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow>
                        <BCol style="font-weight: bold;">
                            댓글 {{ comment_count }} 개
                        </BCol>
                    </BRow>

                    <BRow style="text-align: center; font-weight: bold; font-size: 14px;">
                        <BCol cols="1">댓글ID</BCol>
                        <BCol cols="1">글ID</BCol>
                        <BCol>댓글</BCol>
                        <BCol cols="2">작성자</BCol>
                        <BCol cols="2">날짜</BCol>
                    </BRow>

                    <BRow v-for="comment in users_comments.data" :key="comment.id" style="min-width: 900px; font-size: 14px; text-align: center;">
                        <BCol cols="1">{{ comment.id }}</BCol>
                        <BCol cols="1">{{ comment.post_id }}</BCol>
                        <BCol style="text-align: start; cursor: pointer;" @click="router.push('/posts/' + String(comment.post_id))">{{ comment.text }}</BCol>
                        <BCol cols="2">{{ comment.nickname }}</BCol>
                        <BCol cols="2">{{ convert_timestamp_to_datetime(comment.created) }}</BCol>
                    </BRow>

                    <hr>

                    <BRow align-h="center">
                        <BCol cols="auto">
                            <BPagination v-model="users_comment_list_page" :total-rows="comment_count" perPage="50" @page-click="users_comment_list_pagenation_clicked"></BPagination>
                        </BCol>
                    </BRow>

                    <hr>

                    <BRow v-if="is_delete_user_button_clicked==false">
                        <BCol>
                            <BButton squared variant="danger" style="width: 300px;" @click="is_delete_user_button_clicked=true">계정삭제</BButton>
                        </BCol>
                    </BRow>

                    <BRow v-if="is_delete_user_button_clicked==true">
                        <BCol>
                            <BRow style="margin-bottom: 10px;">
                                <BCol>
                                    <BFormInput v-model="delete_user_username" placeholder="아이디 확인"></BFormInput>
                                </BCol>
                            </BRow>

                            <BRow style="margin-bottom: 10px;">
                                <BCol>
                                    <BFormInput v-model="delete_user_password" placeholder="비밀번호 확인" type="password"></BFormInput>
                                </BCol>
                            </BRow>

                            <BRow style="margin-bottom: 10px;">
                                <BCol>
                                    <BButton squared style="margin-right: 10px;" @click="is_delete_user_button_clicked=false">취소</BButton>
                                    <BButton squared variant="danger" @click="delete_user_button_clicked">삭제</BButton>
                                </BCol>
                            </BRow>
                        </BCol>
                    </BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>