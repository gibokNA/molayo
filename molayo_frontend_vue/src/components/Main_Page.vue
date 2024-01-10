<script setup lang="ts">
import Post_List from '@/components/Community/Post_List.vue'
import Deep_Learning from './Deep_Learning.vue';

</script>

<template>
    <BContainer>
        <BRow>
            <BCol style="padding: 0px;">
                <Deep_Learning></Deep_Learning>
            </BCol>
        </BRow>

        <BRow>
            <BCol style="padding: 0px;">
                <Post_List></Post_List>
            </BCol>
        </BRow>
    </BContainer>
</template>