import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'
import VueAxios from 'vue-axios'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css';

const app = createApp(App)
app.component('QuillEditor', QuillEditor)

app.use(VueAxios, axios)
app.provide('axios', app.config.globalProperties.axios) // provide 'axios'

app.use(createPinia())
app.use(router)

app.mount('#app')
