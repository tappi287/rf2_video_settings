<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <p>
      For a guide and recipes on how to configure / customize this project,<br>
      check out the
      <a href="https://cli.vuejs.org" target="_blank" rel="noopener">vue-cli documentation</a>.
    </p>
    <b-button size="sm" variant="warning" @click="getTestMessagePython">
      <span class="mr-2">Test Button</span><b-icon icon="exclamation-triangle"></b-icon>
    </b-button>
    <p v-html="testMessage"></p>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data: function () {
    return {
      testMessage: ''
    }
  },
  methods: {
    getTestMessagePython: async function () {
      window.eel.message()((val) => {
        this.testMessage = val
      })
    }
  },
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
