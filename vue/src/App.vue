<template>
  <div id="app">
    <Main></Main>
  </div>
</template>

<script>
import "fontsource-ubuntu"
import Main from "./components/Main.vue";
import { createPopperLite as createPopper, preventOverflow, flip } from "@popperjs/core";

export default {
  name: 'App',
  data: function () {
    return {}
  },
  components: {
    Main
  }
}

function neverCalled () {
  createPopper()
  preventOverflow()
  flip()
}
let pass = true
if (!pass) { neverCalled() }
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
.btn-rf-yellow, .btn-rf-yellow:hover, .rf-yellow { color: #161616; background-color: #FF9900;}
.b-popover-rf-yellow .popover-header  {color: #161616; background-color: #fac87c;}
.btn-rf-orange-light, .btn-rf-orange-light:hover, .rf-orange-light { color: #efefef; background-color: #FF3000;}
.b-popover-rf-orange-light .popover-header  {color: #efefef; background-color: #fc9982;}
.btn-rf-orange, .btn-rf-orange:hover, .rf-orange { color: #ffffff; background-color: #E06119;}
.b-popover-rf-orange .popover-header  {color: #efefef; background-color: #E06119;}
.btn-rf-blue, .btn-rf-blue:hover, .rf-blue { color: #efefef; background-color: #3E6BAD;}
.b-popover-rf-blue .popover-header  {color: #161616; background-color: #728bb0;}
</style>
