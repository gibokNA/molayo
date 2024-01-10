<script setup lang="ts">
import { RouterView } from 'vue-router'
import Header from './components/Header.vue'
import { ref } from 'vue'
import { use_global_store } from '@/stores/global_store'
import { storeToRefs } from 'pinia'

const global_store = use_global_store()

const {
  modal_title,
  modal_text,
  is_modal_show
} = storeToRefs(global_store)

</script>

<template>
  <BContainer style="padding: 0px; box-shadow: 2px 2px 10px 2px #A6A6A6; max-width: 1000px; margin-bottom: 15px;">
    <Header></Header>
    <BRow align-h="center">
      <BCol>
        <BRow><BCol><RouterView :key="$route.fullPath" style="margin-top: 10px;"></RouterView></BCol></BRow>
      </BCol>
    </BRow>

    <BModal v-model="is_modal_show" :title="modal_title"> {{ modal_text }} </BModal>
  </BContainer>
</template>

