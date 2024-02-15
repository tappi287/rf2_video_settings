<template>
  <b-card class="text-left">
    <template #header v-if="!noHeader">
      <h6>
        <b-icon class="mr-1" icon="hdd-stack-fill" shift-v="-0.7"></b-icon>
        <span>{{ computedTitle }}</span>
      </h6>
    </template>

    <div class="pt-0 pl-0 card-body text-left" v-if="showOptions">
      <span class="mr-2">Options</span>
      <b-form-checkbox v-model="optionEditable" name="Editable" switch inline>
        Editable
      </b-form-checkbox>
      <b-form-checkbox v-model="optionSelectOnly" name="Select Only" switch inline>
        Select only
      </b-form-checkbox>
      <b-form-checkbox v-model="optionShowLoad" name="Show Load" switch inline>
        Show Load
      </b-form-checkbox>
      <b-form-checkbox v-model="optionShowSubFolderNumber" name="Show Sub Folder Num" switch inline>
        Show Sub Folder Num
      </b-form-checkbox>
    </div>

    <b-dropdown :text="currentDropdownText" block class="p-0 card-body" menu-class="w-100 pl-0" toggle-class="text-left">
      <template #button-content>
        <b-icon class="mr-1" icon="hdd-fill" shift-v="-0.5"></b-icon>
        <span>{{ currentDropdownText }}</span>
      </template>
      <b-dropdown-item v-for="(rootNode, index) in rootFolders" :key="index" class="pl-1"
                       link-class="pl-2"
                       @click="selectFolderDropdown(index)">
        <b-icon class="mr-1" icon="hdd-fill" shift-v="-0.5"></b-icon>
        <span class="">{{ rootNode.name }}</span>
      </b-dropdown-item>
    </b-dropdown>

    <b-overlay v-if="showFileSystemNode" :show="isBusy" blur="1px" variant="transparent">
      <FileSystemNode v-for="(rootChildNode, index) in currentFileSystemNode.children" :key="index"
                      :editable="optionEditable"
                      :expand_key="expand_key"
                      :loadedId="loadedId"
                      :nodeProp="rootChildNode"
                      :show-sub-folder-number="optionShowSubFolderNumber"
                      :show-load-buttons="optionShowLoad"
                      :show-select-only="optionSelectOnly"
                      parent-expanded
                      v-on:create-clicked="createClicked"
                      v-on:remove-clicked="removeClicked"
                      v-on:load-clicked="loadClicked"
                      v-on:single-load-clicked="singleLoadClicked"
                      v-on:folder-clicked="folderClicked"
                      v-on:label-clicked="labelClicked"
                      v-on:set-busy="setBusy">
      </FileSystemNode>
    </b-overlay>
  </b-card>
</template>

<script>
import {getEelJsonObject} from "@/main";
import FileSystemNode from "@/components/files/FileSystemNode.vue";

export default {
  name: "LocalFileExplorer",
  components: {FileSystemNode},
  data: function () {
    return {
      rootFolders: [],
      currentFolderIndex: -1,
      showFileSystemNode: false,
      folders: [],
      defaultTitle: 'Local File System',
      optionEditable: false,
      optionSelectOnly: false,
      optionShowLoad: false,
      optionShowSubFolderNumber: false,
      isBusy: false
    }
  },

  props: {
    editable: Boolean, showSelectOnly: Boolean, showLoadButtons: Boolean, showSubFolderNumber: Boolean,
    loadedId: String, expand_key: String,
    showOptions: Boolean,
    noHeader: Boolean,
    title: String
  },
  methods: {
    async getRootFolders() {
      let r
      try {
        r = await getEelJsonObject(window.eel.list_root_directories()())
      } catch (error) {
        this.$eventHub.$emit('create-toast', error.errorText, 'danger', 'Get system root directories failed!')
        console.error(error)
      }

      if (r?.result) {
        this.rootFolders = r.data
      } else if (r?.msg) {
        this.$eventHub.$emit('create-toast', r.msg, 'danger', 'Get Windows root folders', true)
      } else {
        this.$eventHub.$emit('create-toast', 'Connection failed. Please check the logs.',
            'danger', 'Get Windows root folders', true)
      }
    },
    selectFolderDropdown: function (index) {
      this.showFileSystemNode = false
      this.currentFolderIndex = index

      this.$nextTick(() => {
        this.showFileSystemNode = true
      })
    },
    setBusy: function (busy) {
      this.isBusy = busy
    },
    createClicked: function (createObj) {
      console.log('NodeId: ' + createObj.nodeId + ' Label:' + createObj.label)
      this.$emit('create-clicked', createObj)
    },
    removeClicked: function (node) {
      this.$emit('remove-clicked', node)
      console.log("remove clicked " + node.path)
    },
    loadClicked: function (node) {
      this.$emit('load-clicked', node);
      console.log("load clicked " + node.path)
    },
    singleLoadClicked: function (node) {
      this.$emit('single-load-clicked', node);
      console.log("single load clicked " + node.path)
    },
    folderClicked: function (node) {
      this.$emit('folder-clicked', node)
    },
    labelClicked: function (node) {
      this.$emit('label-clicked', node);
      console.log("label clicked " + node.path)
    },
  },
  computed: {
    currentFileSystemNode: function () {
      if (this.rootFolders.length === 0) {
        return {}
      }
      return this.rootFolders[this.currentFolderIndex]
    },
    currentDropdownText: function () {
      if (this.currentFolderIndex === -1) {
        return 'Select System Drive'
      }
      return this.currentFileSystemNode.name
    },
    computedTitle: function () {
      return this.title || this.defaultTitle
    }
  },
  created() {
    this.optionShowLoad = this.showLoadButtons
    this.optionSelectOnly = this.showSelectOnly
    this.optionEditable = this.editable
    this.optionShowSubFolderNumber = this.showSubFolderNumber

    this.getRootFolders()
  }
}
</script>

<style scoped>

</style>