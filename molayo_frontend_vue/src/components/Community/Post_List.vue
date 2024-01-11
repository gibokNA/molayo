<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { inject, ref, reactive } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'
import axios from 'axios';

const global_store = use_global_store()

const {
  is_login
} = storeToRefs(global_store)

const { convert_timestamp_to_datetime } = global_store

const route = useRoute()
const router = useRouter()

const post_list = reactive({data: [] as any})

request_post_list(1)


function create_post_button_clicked() {
    let path = ""

    if (is_login.value == false) {
        path = "/login"
    } else {
        path = "/posts/create"
    }

    router.push({
        path: path
    })
}

const post_list_page = ref(1)
const total_rows = ref(10)


function post_list_pagenation_clicked(event: any, page: number) {
    if (search_text.value == "") request_post_list(page)
    else search_button_clicked(page)

    total_rows.value = page + 10
}

function request_post_list(page: number) {
    let offset = String(50 * (page - 1))
    let limit = "50"

    axios.get('https://molayo.work/api/posts?offset=' + offset + '&limit=' + limit).then((res: any) => {
    post_list.data = res.data
})
}

const search_text = ref("")
const search_target = ref("all")

function search_button_clicked(page: number) {
    if (search_text.value.length == 0) return 

    let offset = String(50 * (page - 1))

    axios.get('https://molayo.work/api/posts/search?q=' + search_text.value +
     '&target=' + search_target.value + '&offset=' + offset + '&limit=50').then((res: any) => {
        post_list.data = res.data
     })
}

function keydown(event: any) {
    if (event.which === 13) {
        search_button_clicked(1)
    }
}

</script>

<template>
    <BContainer fluid="true">
        <BRow style="margin-bottom: 10px;">
            <BCol>
                <BCard>
                    <BRow style="text-align: center;">
                        <BCol cols="1">번호</BCol>
                        <BCol cols="5">제목</BCol>
                        <BCol>글쓴이</BCol>
                        <BCol>날짜</BCol>
                        <BCol cols="1">조회</BCol>
                        <BCol cols="1">추천</BCol>
                    </BRow>
                    <hr>

                    <BRow v-for="post in post_list.data" :key=post.id align-h="between" style="text-align: center; font-size: 15px;">
                        <BCol cols="1">{{ post.id }}</BCol>
                        <BCol cols="5" style="text-align: left; cursor: pointer;" @click="() => {router.push('/posts/' + String(post.id))}">
                            {{ post.title }} [{{ post.comment_count }}]
                        </BCol>
                        <BCol>{{ post.nickname }}</BCol>
                        <BCol>{{ convert_timestamp_to_datetime(post.created) }}</BCol>
                        <BCol cols="1">{{ post.view_count }}</BCol>
                        <BCol cols="1">{{ post.like_count }}</BCol>
                        <hr>
                    </BRow>
                    <hr>
                    <BRow align-h="between">
                        <BCol cols="auto"><BButton squared @click="request_post_list(post_list_page)">새로고침</BButton></BCol>
                        <BCol cols="auto">
                            <BPagination v-model="post_list_page" :total-rows="total_rows" perPage="1" @page-click="post_list_pagenation_clicked"></BPagination>
                        </BCol>
                        <BCol cols="auto"><BButton squared variant="success" @click="create_post_button_clicked">글쓰기</BButton></BCol>
                    </BRow>
                    
                    <hr>

                    <BRow align-h="center">
                        <BCol cols="auto">
                            <BDropdown variant="success" :text="search_target">
                                <BDropdownItem @click="() => {search_target='all'}">all</BDropdownItem>
                                <BDropdownItem @click="() => {search_target='nickname'}">nickname</BDropdownItem>
                                <BDropdownItem @click="() => {search_target='title'}">title</BDropdownItem>
                            </BDropdown> 
                        </BCol>
                        <BCol cols="auto">
                            <BFormInput v-model="search_text" placeholder="검색" @keydown="keydown"></BFormInput>
                        </BCol>
                        <BCol cols="auto">
                            <BButton squared variant="info" @click="search_button_clicked(1)">검색</BButton>
                        </BCol>
                    </BRow>
                </BCard>
            </BCol>
        </BRow>
    </BContainer>
</template>