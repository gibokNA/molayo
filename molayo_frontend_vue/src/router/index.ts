import { createRouter, createWebHistory } from 'vue-router'
import Main_Page from '../components/Main_Page.vue'
import Post_Create_Update from '@/components/Community/Post_Create_Update.vue'
import Post_Detail from '@/components/Community/Post_Detail.vue'
import Post_List from '@/components/Community/Post_List.vue'
import Login from '@/components/Account/Login.vue'
import Register from '@/components/Account/Register.vue'
import Account_Info from '@/components/Account/Account_Info.vue'
import Deep_Learning from '@/components/Deep_Learning.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Main_Page
    },
    {
      path: '/deeplearning',
      component: Deep_Learning
    },
    {
      path: '/login',
      component: Login
    },
    {
      path: '/register',
      component: Register
    },
    {
      path: '/account',
      component: Account_Info
    },
    {
      path: '/posts',
      component: Post_List
    },
    {
      path: '/posts/create',
      component: Post_Create_Update
    },
    {
      path: '/posts/:post_id',
      name: 'post_detail',
      component: Post_Detail
    },
    {
      path: '/posts/:post_id/edit',
      name: 'edit_post',
      component: Post_Create_Update
    }
  ],
  scrollBehavior(to: any, from: any, savedPosition: any) {
    if (to.hash) {
      return {selector: to.hash}
    }
    else if (savedPosition) {
      return savedPosition
    }
    else {
      return { x: 0, y: 0 }
    }
  }
})

export default router
