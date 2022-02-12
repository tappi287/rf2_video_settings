<template>
  <div>
    <input v-if="edit"
           v-focus=""
           :value="valueLocal"
           type="text"
           @blur.native="valueLocal = $event.target.value; edit = false; $emit('input', valueLocal);"
           @keyup.enter.native="valueLocal = $event.target.value; edit = false; $emit('input', valueLocal);"
    />
    <p v-else @click="edit = true;">
      {{ valueLocal }}
    </p>
  </div>
</template>

<script>
export default {
  props: ['value'],
  data() {
    return {
      edit: false,
      valueLocal: this.value
    }
  },
  watch: {
    value: function () {
      this.valueLocal = this.value;
    }
  },
  directives: {
    focus: {
      inserted(el) {
        el.focus()
      }
    }
  }

}
</script>