<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

const global_store = use_global_store()

const {
  is_login,
  username,
  auth_header
} = storeToRefs(global_store)

const route = useRoute()
const router = useRouter()

function nav_button_clicked(target: string){
  let current_path = route.path
  let path = ""

  if (target == "main") {
    path = "/"
  } else if (target == "deep_learning") {
    path = "/deeplearning"
  } else if (target == "post_list") {
    path = "/posts"
  } else if (target == "login") {

    if (is_login.value == false) {
      path = "/login"
    } else {
      is_login.value = false
      username.value = ""
      auth_header.value.data = {}
      localStorage.removeItem('username')
      localStorage.removeItem('auth_header')
      localStorage.removeItem('last_login')

      return
    }
  }
  else if (target == "account") {
    path = "/account"
  }

  if ( current_path == path ) {
      router.go(0)
    }
    else {
      router.push({
        path: path
      })
    }
}

</script>

<template>
  <BNavbar toggleable="lg" v-b-color-mode="'dark'" variant="dark" sticky="top">
    <BNavbarBrand @click="nav_button_clicked('main')" style="cursor: pointer;">몰라요</BNavbarBrand>

    <BNavbarToggle target="nav-collapse"></BNavbarToggle>

    <BCollapse id="nav-collapse" is-nav>
      <BNavbarNav>
        <BNavItem><BLink href="https://molayo.work/api/docs" target="_blank"><IBiLightning-Fill style="color: red" /> API</BLink></BNavItem>
        <BNavItem @click="nav_button_clicked('deep_learning')"><IBiPostage-Fill style="color: red" /> 딥러닝</BNavItem>
        <BNavItem @click="nav_button_clicked('post_list')"><IBiCard-List style="color: white;"/> 게시판</BNavItem>
      </BNavbarNav>

      <!-- Right aligned nav items -->
      <BNavbarNav class="ms-auto mb-2 mb-lg-0">
        <BNavForm>
          <BButton style="margin-right: -5px;" variant="info" @click="nav_button_clicked('login')" squared><IBiKey-Fill /> {{ is_login?"로그아웃":"로그인" }}</BButton>
          <BButton squared variant="info" style="margin-left: 15px;" @click="nav_button_clicked('account')" v-if="is_login==true">
            <IBiEmoji-Sunglasses/> 계정정보
          </BButton>
        </BNavForm>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>
</template>