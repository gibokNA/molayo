<script setup lang="ts">

import passwordvalidator from 'password-validator'
import { useRouter, useRoute } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

const axios: any = inject('axios')  // inject axios

const router = useRouter()
const route = useRoute()

const register_username = ref("")
const register_password = ref("")
const register_password_2 = ref("")
const register_nickname = ref("")

const global_store = use_global_store()

const {
  modal_title,
  modal_text,
  is_modal_show
} = storeToRefs(global_store)

const { password_schema } = global_store

const nickname_schema = new passwordvalidator()

nickname_schema
.is().min(1)
.is().max(50)
.has().not().spaces()

function register_button_clicked(){

    if (password_schema.validate(register_username.value) == false) {
        modal_title.value = "아이디 제한조건"
        modal_text.value = "아이디는 8자 이상 100자 이하, 숫자, 문자 포함, 공백없음 입니다."
        is_modal_show.value = true
        return
    } else if (password_schema.validate(register_password.value) == false) {
        modal_title.value = "비밀번호 제한조건"
        modal_text.value = "비밀번호는 8자 이상 100자 이하, 숫자, 문자 포함, 공백없음 입니다."
        is_modal_show.value = true
        return
    } else if (register_password.value != register_password_2.value) {
        modal_title.value = "비밀번호 다름"
        modal_text.value = "비밀번호 1 과 비밀번호 2 가 일치하지 않습니다."
        is_modal_show.value = true
        return
    } else if (nickname_schema.validate(register_nickname.value) == false) {
        modal_title.value = "닉네임 제한조건"
        modal_text.value = "닉네임은 1자 이상 50자 이하, 공백없음 입니다."
        is_modal_show.value = true
        return
    }

    let formData = new FormData()
    formData.append("username", register_username.value)
    formData.append("password", register_password.value)
    formData.append("password2", register_password_2.value)
    formData.append("nickname", register_nickname.value)

    axios.post('https://molayo.work/api/users', formData).then((res: any) => {
        if (res.data == true) {
            modal_title.value = "회원가입 성공"
            modal_text.value = "2초뒤 로그인 페이지로 이동합니다."
            is_modal_show.value = true

            setTimeout(() => {
                is_modal_show.value = false

                router.push({path:'/login'})
            }, 2000);
        }
    }).catch((error: any) => {
        modal_title.value = "회원가입 실패"
        modal_text.value = String(error.response.data.detail)
        is_modal_show.value = true
    })
}

function keydown(event: any) {
    if (event.which === 13) {
        register_button_clicked()
    }
}

</script>

<template>
    <BContainer fluid="true" style="margin-bottom: 10px;">
        <BRow align-h="center">
            <BCol cols="auto">
                <BCard>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BButton style="width: 300px;" variant="success" @click="() => {router.push({path:'/login'})}">로그인</BButton>
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="register_username" placeholder="아이디"></BFormInput >
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="register_nickname" placeholder="닉네임"></BFormInput >
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="register_password" placeholder="비밀번호" type="password"></BFormInput >
                    </BCol></BRow>
                    <BRow style="margin-bottom: 10px;"><BCol>
                        <BFormInput v-model="register_password_2" placeholder="비밀번호 다시한번" type="password" @keydown="keydown"></BFormInput >
                    </BCol></BRow>
                    <BRow><BCol>
                        <BButton style="width: 300px;" variant="primary" @click="register_button_clicked">회원가입</BButton>
                    </BCol></BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>