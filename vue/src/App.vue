<template>
  <div id="app">
    <Main></Main>
    <div class="mt-3 main-footer small font-weight-lighter">
      <span>Published under MIT license &#169; 2020 Stefan Tapper </span>
      <a href="https://www.github.com/tappi287/" target="_blank">Source @ Github</a>
    </div>
  </div>
</template>

<script>
import "fontsource-ubuntu"
import Main from "./components/Main.vue";
import {createPopperLite as createPopper, flip, preventOverflow} from "@popperjs/core";

export default {
  name: 'App',
  data: function () {
    return {}
  },
  components: {
    Main
  }
}

function neverCalled() {
  createPopper()
  preventOverflow()
  flip()
}

let pass = true
if (!pass) {
  neverCalled()
}
</script>

<style>
#app {
  /*font-family: Avenir, Helvetica, Arial, sans-serif;*/
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #efefef;
}

body {
  background: none !important;
}

html {
  background-image: linear-gradient(60deg, #172122 0%, #0c1013 100%);
}

.main-footer {
  margin-bottom: 3rem;
}

.info-field {
  background-image: linear-gradient(to left, #ddd9de 0%, #c6c7cd 100%), radial-gradient(88% 271%, rgba(255, 255, 255, 0.25) 0%, rgba(254, 254, 254, 0.25) 1%, rgba(0, 0, 0, 0.25) 100%), radial-gradient(50% 100%, rgba(255, 255, 255, 0.30) 0%, rgba(0, 0, 0, 0.30) 100%);
  background-blend-mode: normal, lighten, soft-light;
}

.setting-field {
  box-shadow: 0 6px 15px rgba(36, 37, 38, 0.3);
}

.logo-style {
  box-shadow: 0 6px 15px rgba(36, 37, 38, 0.9);
  border-radius: 0.25rem;
  background-image: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
  padding: 2px 3px 2px 4px;
}

.title {
  text-shadow: 0px 3px 7px rgba(36, 37, 38, 0.9);
  font-family: "Ubuntu", sans-serif;
}

.btn-rf-yellow, .btn-rf-yellow:hover, .rf-yellow {
  color: #161616;
  background-color: #FF9900;
}

.b-popover-rf-yellow .popover-header {
  color: #161616;
  background-color: #fac87c;
}

.btn-rf-orange-light, .btn-rf-orange-light:hover, .rf-orange-light {
  color: #efefef;
  background-color: #FF3000;
}

.b-popover-rf-orange-light .popover-header, .badge-rf-orange-light {
  color: #efefef;
  background-color: #fc9982;
}

.btn-rf-orange, .btn-rf-orange:hover, .rf-orange {
  color: #ffffff;
  border: none;
  font-weight: lighter;
  background: #fa5a57; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #cf4947, #ab6942); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #cf4947, #ab6942); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.b-popover-rf-orange .popover-header, .badge-rf-orange {
  color: #efefef;
  background-color: #E06119;
}

.btn-rf-blue, .btn-rf-blue:hover, .rf-blue {
  color: #efefef;
  border: none;
  background: #9D50BB; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #463ea6, #745ac4); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #463ea6, #745ac4); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.b-popover-rf-blue .popover-header {
  color: #161616;
  background-color: #728bb0;
}

.btn-rf-red, .btn-rf-red:hover, .rf-red {
  color: #efefef;
  border: none;
  background: #fa523c; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #fa523c, #fa7c56); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #fa523c, #fa7c56); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.bg-dark {
  background-color: #172122;
}
</style>
