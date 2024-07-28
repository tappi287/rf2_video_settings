import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue'
import Vue from 'vue'
import App from './App.vue'
import "@fontsource/ubuntu/500.css"
import "@fontsource/ubuntu/400.css"
import "@fontsource/ubuntu/300.css"
import "@fontsource/inter/100.css"
import "@fontsource/inter/200.css"
import "@fontsource/inter/300.css"
import "source-sans/source-sans-3.css"

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.config.productionTip = false
// Vue.config.devtools = true

export const userScreenShotsUrl = 'https://raw.githubusercontent.com/tappi287/rf2_screenshots/master/data.json'

const eventHub = new Vue()
Vue.prototype.$eventHub = eventHub

new Vue({
    render: h => h(App),
}).$mount('#app')

export async function getEelJsonObject(promise) {
    const value = await promise
    return JSON.parse(value)
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

export function getMaxWidth(elements) {
    let maxWidth = 0
    for (let i in elements) {
        if (elements[i].clientWidth !== undefined) {
            maxWidth = Math.max(maxWidth, parseInt(elements[i].clientWidth))
        }
    }
    return maxWidth
}

export function clearWidthStyle(elements) {
    for (let i in elements) {
        if (elements[i].style !== undefined) {
            elements[i].style.width = null
        }
    }
}

export function chooseIndex(choices) {
    return Math.floor(Math.random() * choices.length);
}

export var isValid = (function () {
    let rg1 = /^[^\\/:*?"<>|]+$/; // forbidden characters \ / : * ? " < > |
    let rg2 = /^\./; // cannot start with dot (.)
    let rg3 = /^(nul|prn|con|lpt[0-9]|com[0-9])(\.|$)/i; // forbidden file names
    return function isValid(fname) {
        return rg1.test(fname) && !rg2.test(fname) && !rg3.test(fname);
    }
})();

window.eel.expose(updateProgress, 'server_progress')

function updateProgress(newProgress, newMaxProgress) {
    const progressEvent = new CustomEvent('update-progress',
        {detail: {progress: newProgress, maxProgress: newMaxProgress}})
    window.dispatchEvent(progressEvent)
}

window.eel.expose(addServerListChunk, 'add_server_list_chunk')

function addServerListChunk(newServerListChunk) {
    const serverListEvent = new CustomEvent('add-server-list-chunk', {detail: newServerListChunk})
    window.dispatchEvent(serverListEvent)
}

export const controllerInputTypes = {768: 'Key', 1536: 'Axis', 1538: 'Dpad', 1539: 'Button'}

// Get the Name of a Controller input Type
export function getControllerDeviceTypeName(setting) {
    if (setting === undefined) {
        return 'Unknown'
    }
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
        if (key !== undefined && key !== '' && key !== null) {
            return key.toUpperCase()
        }
    }
    // Axis
    if (type === 1536 && axis !== undefined) {
        let a = String(axis)
        return (value > 0) ? a + ' +' : a + ' -'
    }
    // Button
    if ([768, 1539].indexOf(type) !== -1) {
        if (value !== undefined && value !== '' && value !== null) {
            return value
        }
        if (button !== undefined) {
            return button
        }
    }
    // Dpad
    if (Number(type) === 1538) {
        let result = String(hat) + ' '
        switch (value[0]) {
            case -1:
                result += 'Left';
                break
            case 1:
                result += 'Right';
                break
        }
        switch (value[1]) {
            case -1:
                result += 'Down';
                break
            case 1:
                result += 'Up';
                break
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

    let nameMaxWidth = getMaxWidth(nameElem);
    let settMaxWidth = getMaxWidth(settElem)

    let e = document.getElementById(nameId)
    if (e !== null) {
        e.style.width = String(nameMaxWidth) + 'px'
    }
    let s = document.getElementById(elemId)
    if (s !== null) {
        s.style.width = String(settMaxWidth) + 'px'
    }
}

export function minutesToDaytime(num) {
    const hours = ('0' + String(Math.floor(num / 60))).slice(-2)
    const minutes = ('0' + String(num % 60)).slice(-2)
    return String(hours + ":" + minutes)
}