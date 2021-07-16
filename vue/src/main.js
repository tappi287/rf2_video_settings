import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue'
import "@fontsource/ubuntu/500.css"
import "@fontsource/ubuntu/400.css"
import "@fontsource/ubuntu/300.css"
import "@fontsource/inter/100.css"
import "@fontsource/inter/200.css"
import "@fontsource/inter/300.css"

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Axios from "axios"

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.config.productionTip = false
// Vue.config.devtools = true

export const settingsAreaId = 'settings-area'
export const userScreenShots =
    [
 ['https://forum.studio-397.com/index.php?attachments/porsche_911_gt3_r_2018_01-jpg.27876/', 'philmcqueen',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-320'],
 ['https://forum.studio-397.com/index.php?attachments/grab_360-jpg.27884/', 'juanchioooo',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-320'],
 ['https://forum.studio-397.com/index.php?attachments/20200113191349_1-jpg.28772/', 'datasting',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-324'],
 ['https://forum.studio-397.com/index.php?attachments/365960_20200322152429_1-png.30174/', 'Frank Murphy',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-331'],
 ['https://i.imgur.com/3RdME7Q.jpg', 'jayarrbee36',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-334'],
 ['https://forum.studio-397.com/index.php?attachments/20200521225453_1-jpg.31126/', 'Pocisk',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-334'],
 ['https://i.ibb.co/Jjtws8M/r-Factor2-2020-05-30-20-32-16.jpg', 'GeraArg',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-335'],
 ['https://forum.studio-397.com/index.php?attachments/grab_002-jpg.32749/', 'memoNo1',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-341'],
 ['https://forum.studio-397.com/index.php?attachments/ec551ad7-aedd-487c-8d8b-494a01f445a3-jpeg.34232/', 'M-Bimmer',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-348'],
 ['https://forum.studio-397.com/index.php?attachments/20201108231324_1-jpg.34446/', 'svictor',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-349'],
 ['https://forum.studio-397.com/index.php?attachments/365960_20201110141049_1-png.34504/', 'marciovs28',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-349'],
 ['https://i.imgur.com/CwYk11v.jpg', 'mantasisg',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-352'],
 ['https://forum.studio-397.com/index.php?attachments/20201221185422_1-jpg.35356/', 'svictor',
  'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-354#post-1050632'],
['https://forum.studio-397.com/index.php?attachments/2021-02-02-20-40-png.36838/', 'MiguelVallejo',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-359#post-1059084'],
['https://cdn.discordapp.com/attachments/541020496087482424/792889002901504080/20201227113904_1.jpg', 'boxwex',
 'https://discord.com/channels/253557076645773312/541020496087482424/792889005245988945'],
['https://cdn.discordapp.com/attachments/541020496087482424/792889678721843250/20201224110117_1.jpg', 'boxwex',
 'https://discord.com/channels/253557076645773312/541020496087482424/792889680517267457'],
['https://forum.studio-397.com/index.php?attachments/4-rf2-cockpit-rain-mist-copy-jpg.18789/', 'M D Gourley',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-256#post-967468'],
['https://forum.studio-397.com/index.php?attachments/2020-08-31-18-24_01-png.33144/', 'MiguelVallejo',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-344#post-1037906'],
['https://i.imgur.com/hQV5bIx.jpg', 'TheNexpresso',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-258#post-968996'],
['https://forum.studio-397.com/index.php?attachments/jsp3-jpg.19130/', 'sg333',
 'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-258#post-969316'],
['https://forum.studio-397.com/index.php?attachments/2021-02-18-17-18_01-png.37087/', 'MiguelVallejo',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-360#post-1060896'],
['https://forum.studio-397.com/index.php?attachments/2021-01-29-19-44-png.36723/', 'MiguelVallejo',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-359#post-1058550'],
['https://forum.studio-397.com/index.php?attachments/2021-02-07-17-56-png.36950/', 'MiguelVallejo',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-359#post-1059819'],
['https://i.imgur.com/1JMXxzi.jpg', 'jayarrbee36',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-362#post-1064530'],
['https://i.imgur.com/SbWk9px.jpg', 'jayarrbee36',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-367#post-1070446'],
['https://forum.studio-397.com/index.php?attachments/20210612210607_1-jpg.39120/', 'jayarrbee36',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-367#post-1071125'],
['https://i.imgur.com/PRD6FLd.jpg', 'jayarrbee36',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-367#post-1071137'],
['https://i.imgur.com/TQlkDNd.jpg', 'jayarrbee36',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-367#post-1071137'],
['https://forum.studio-397.com/index.php?attachments/2021-06-29-13-10-png.39390/', 'MiguelVallejo',
'https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/page-368#post-1072242']
]

Vue.prototype.$eventHub = new Vue(); // Global event bus

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

export function getMaxWidth (elements) {
  let maxWidth = 0
  for (let i in elements) {
    if (elements[i].clientWidth !== undefined) {
      maxWidth = Math.max(maxWidth, parseInt(elements[i].clientWidth))
    }
  }
  return maxWidth
}

export function clearWidthStyle (elements) {
  for (let i in elements) {
      if (elements[i].style !== undefined) { elements[i].style.width = null }
  }
}

export function chooseIndex(choices) {
  return Math.floor(Math.random() * choices.length);
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

window.eel.expose(updateProgress, 'server_progress')
function updateProgress (newProgress, newMaxProgress) {
  const progressEvent = new CustomEvent('update-progress',
      {detail: {progress: newProgress, maxProgress: newMaxProgress}})
  window.dispatchEvent(progressEvent)
}

window.eel.expose(addServerListChunk, 'add_server_list_chunk')
function addServerListChunk (newServerListChunk) {
  const serverListEvent = new CustomEvent('add-server-list-chunk', {detail: newServerListChunk})
  window.dispatchEvent(serverListEvent)
}

export const controllerInputTypes = {768: 'Key', 1536: 'Axis', 1538: 'Dpad', 1539: 'Button' }

// Get the Name of a Controller input Type
export function getControllerDeviceTypeName(setting) {
  if (setting === undefined) { return 'Unknown' }
  return controllerInputTypes[Number(setting.type)]
}

// Get the Name of a rFactor Controller.json input Type
export function getRfactorControllerDeviceTypeName(setting) {
    const inputType = setting.value[0]
    if (inputType > 0) {
        // Controller devices to be defined ...
        return 'Con'
    }
    if (inputType === 0) {
        // Keyboard keys have type value 0
        return 'Key'
    }
    return 'Unknown'
}

// Get the Name of a Controller Button/Axis
export function getControllerValueName({button, key, hat, type, value, axis}) {
  // Key
  if (type === 768) {
      if (key !== undefined && key !== '' && key !== null) { return key.toUpperCase() }
  }
  // Axis
  if (type === 1536 && axis !== undefined) {
      let a = String(axis)
      return (value > 0) ? a + ' +' : a + ' -'
  }
  // Button
  if ([768, 1539].indexOf(type) !== -1) {
      if (value !== undefined && value !== '' && value !== null) { return value }
      if (button !== undefined) { return button }
  }
  // Dpad
  if (Number(type) === 1538) {
    let result = String(hat) + ' '
    switch (value[0]) {
      case -1: result += 'Left'; break
      case 1: result += 'Right'; break
    }
    switch (value[1]) {
      case -1: result += 'Down'; break
      case 1:result += 'Up'; break
    }
    return result
  }
  return 'Not Set'
}

export function clearElementsWidthStyle(groupId) {
  const nameElem = document.querySelectorAll('#' + groupId + ' .fixed-width-name')
  const settElem = document.querySelectorAll('#' + groupId + ' .fixed-width-setting')
  clearWidthStyle(nameElem)
  clearWidthStyle(settElem)
}

export function setFixedWidth(groupId, nameId, elemId) {
  // Iterate all elements of this setting group_id and set width to widest element found
  const nameElem = document.querySelectorAll('#' + groupId + ' .fixed-width-name')
  const settElem = document.querySelectorAll('#' + groupId + ' .fixed-width-setting')

  let nameMaxWidth = getMaxWidth(nameElem); let settMaxWidth = getMaxWidth(settElem)

  let e = document.getElementById(nameId)
  if (e !== null) { e.style.width = String(nameMaxWidth) + 'px' }
  let s = document.getElementById(elemId)
  if (s !== null) { s.style.width = String(settMaxWidth) + 'px' }
}

export function minutesToDaytime(num) {
  const hours = ('0' + String(Math.floor(num / 60))).slice(-2)
  const minutes = ('0' + String(num % 60)).slice(-2)
  return String(hours + ":" + minutes)
}