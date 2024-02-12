<script>
export default {
  name: "DirectoryTree",
  data () {
    return {
      folders: []
    }
  },
  methods: {
    async getFolders () {
      if (this.folders.length === 0) {
        // pass
      }
    }
  }
}
</script>

<template>
  <div>
    <DirectoryTree />
  </div>
</template>

<style scoped>

</style>