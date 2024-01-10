/* eslint-disable prefer-const */
import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'
import passwordvalidator from 'password-validator'

export const use_global_store = defineStore('global_store', () => {
  
  const password_schema = new passwordvalidator()
  
  password_schema
  .is().min(8)
  .is().max(100)
  .has().digits()
  .has().not().spaces()

  const is_login = ref(false)
  const username = ref("")
  const auth_header = reactive({data: {} as any})

  if (localStorage.getItem('auth_header') != null && localStorage.getItem("username") != null && localStorage.getItem('last_login') != null) {
    let last_login = JSON.parse(localStorage.getItem('last_login')!)

    let now_time = Date.now()

    if (last_login > now_time - 60 * 60 * 24 * 1000) {
      is_login.value = true
      username.value = localStorage.getItem("username")!
      auth_header.data = JSON.parse(localStorage.getItem("auth_header")!)
    } else {
      localStorage.removeItem('username')
      localStorage.removeItem('auth_header')
      localStorage.removeItem('last_login')
    }
  }

  const modal_title = ref("")
  const modal_text = ref("")
  const is_modal_show = ref(false)

  function error_handler(title: string, text: string) {
    modal_title.value = title
    modal_text.value = text + "   |   재로그인이 필요할수도 있습니다."
    is_modal_show.value = true

    is_login.value = false
    username.value = ""
    auth_header.data = {}
    localStorage.removeItem('username')
    localStorage.removeItem('auth_header')
    localStorage.removeItem('last_login')
  }

  function convert_timestamp_to_datetime(timestamp: number) {
    let converted_time_1 = new Date(timestamp * 1000)
    let converted_time_2 = ""

    converted_time_2 = converted_time_1.getFullYear() + "."
    if (converted_time_1.getMonth() <= 8) {converted_time_2 += "0"}
    converted_time_2 += (converted_time_1.getMonth()+1) + "."
    if (converted_time_1.getDate() <= 9) {converted_time_2 += "0"}
    converted_time_2 += converted_time_1.getDate() + " "
    if (converted_time_1.getHours() <= 9) {converted_time_2 += "0"}
    converted_time_2 += converted_time_1.getHours() + ":"
    if (converted_time_1.getMinutes() <= 9) {converted_time_2 += "0"}
    converted_time_2 += converted_time_1.getMinutes() + ":"
    if (converted_time_1.getSeconds() <= 9) {converted_time_2 += "0"}
    converted_time_2 += converted_time_1.getSeconds()

    return converted_time_2
  }

  return { 
    password_schema,
    is_login,
    username,
    auth_header,
    modal_title,
    modal_text,
    is_modal_show,
    error_handler,
    convert_timestamp_to_datetime
   }
})
