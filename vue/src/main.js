import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import "fontsource-ubuntu/500.css"
import "fontsource-ubuntu/400.css"
import "fontsource-ubuntu/300.css"

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Axios from "axios"

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.config.productionTip = false
// Vue.config.devtools = true

export const settingsAreaId = 'settings-area'
export const userScreenShots =
    ['https://steamuserimages-a.akamaihd.net/ugc/778482308449119648/AF3A15572629B5E3D3E6CA8F61F1D22D00CC015F/',
     'https://steamuserimages-a.akamaihd.net/ugc/784111684599129210/9082347712B91CD634968AFFBBFD93F28FECD32D/',
     'https://i.imgur.com/vosgbaj.jpg',
     'https://steamuserimages-a.akamaihd.net/ugc/782979273624056824/156BBD766A6FA08774365288C6ACB85CB78DD34C/',
     'https://steamuserimages-a.akamaihd.net/ugc/81465294112521264/7DF6076CE337ECAD339F8A87641BD595B508862F/?imw=1920&&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false',
     'https://steamuserimages-a.akamaihd.net/ugc/1651096185421784231/0627A7B634416946B1E312B1F6137310F42E47E4/',
     'https://steamuserimages-a.akamaihd.net/ugc/773987969333324412/899168BBB83DE14E0C7442B7D32B2C5532ECA60A/',
     'https://forum.studio-397.com/index.php?attachments/grab_2782-jpg.24090/',
     'https://forum.studio-397.com/index.php?attachments/grab_360-jpg.27884/',
     'https://forum.studio-397.com/index.php?attachments/mc-laren-gtr-senna_06-jpg.27691/'
    ]

new Vue({
  render: h => h(App),
}).$mount('#app')

export async function getEelJsonObject (promise) {
  const value = await promise
  return JSON.parse(value)
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

export var isValid=(function(){
  let rg1=/^[^\\/:*?"<>|]+$/; // forbidden characters \ / : * ? " < > |
  let rg2=/^\./; // cannot start with dot (.)
  let rg3=/^(nul|prn|con|lpt[0-9]|com[0-9])(\.|$)/i; // forbidden file names
  return function isValid(fname){
    return rg1.test(fname)&&!rg2.test(fname)&&!rg3.test(fname);
  }
})();

// Generic axios GET request
export async function getRequest(url) {
  try {
    let requestUrl
    requestUrl = url
    const response = await Axios.get(requestUrl)
    return { result: true, data: response.data }
  } catch (error) {
    return { result: false, data: error.response.data }
  }
}
