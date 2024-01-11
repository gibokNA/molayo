<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

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

const { password_schema } = global_store

const router = useRouter()
const route = useRoute()

const login_username = ref("")
const login_password = ref("")

function login_button_clicked() {
    if (password_schema.validate(login_username.value) == false || password_schema.validate(login_password.value) == false) {
        modal_title.value = "아이디, 비밀번호 제한조건"
        modal_text.value = "8자 이상 100자 이하, 숫자포함, 공백없음 입니다."
        is_modal_show.value = true
        return
    }

    let formData = new FormData()
    formData.append("username", login_username.value)
    formData.append("password", login_password.value)

    axios.post('https://molayo.work/api/users/token', formData).then((res: any) => {

        is_login.value = true
        username.value = login_username.value
        auth_header.value.data = {
            headers: {Authorization: res.data.token_type + ' ' + res.data.access_token}
        }

        localStorage.setItem('auth_header', JSON.stringify(auth_header.value.data))
        localStorage.setItem('username', username.value)
        localStorage.setItem('last_login', JSON.stringify(Date.now()))

        router.push({path:'/'})

    }).catch((error: any) => {
        modal_title.value = "로그인 실패"
        modal_text.value = String(error.response.data.detail)
        is_modal_show.value = true
    })
}

function keydown(event: any) {
    if (event.which === 13) {
        login_button_clicked()
    }
}

</script>

<template>
    <BContainer fluid="true" style="margin-bottom: 10px;">
        <BRow align-h="center">
            <BCol cols="auto">
                <BCard>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BButton style="width: 300px;" variant="success" @click="() => {router.push({path:'/register'})}">회원가입</BButton>
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="login_username" placeholder="아이디"></BFormInput >
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="login_password" placeholder="비밀번호" type="password" @keydown="keydown"></BFormInput >
                    </BCol></BRow>
                    <BRow><BCol>
                        <BButton style="width: 300px;" variant="primary" @click="login_button_clicked">로그인</BButton>
                    </BCol></BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>