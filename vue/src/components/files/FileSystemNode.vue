<script>
import {getEelJsonObject} from "@/main";

export default {
  name: "FileSystemNode",
  data: function () {
    return {
      dataNode: {},
      showCreate: false,
      showDelete: false,
      createLabel: '',
      expandedState: false
    }
  },
  props: {
    nodeProp: Object, editable: Boolean,
    showSelectOnly: Boolean, showLoadButtons: Boolean, showSubFolderNumber: Boolean,
    loadedId: String, expand_key: String, parentExpanded: Boolean
  },
  methods: {
    async getSubFolders(node) {
      this.$emit('set-busy', true)
      let r
      try {
        r = await getEelJsonObject(window.eel.list_directory(node.path)())
      } catch (error) {
        this.$eventHub.$emit('create-toast', error.errorText, 'danger', 'Get system directory failed!')
        console.error(error)
      }

      if (r?.result) {
        this.dataNode = r.data
      } else if (r?.msg) {
        // Hide ui error message for now
        // this.$eventHub.$emit('create-toast', r.msg, 'danger', 'Error reading path', true, 10000, true)
        console.log(r.msg)
      } else {
        this.$eventHub.$emit('create-toast', 'Connection failed. Please check the logs.',
            'danger', 'Error reading path', true, 10000, true)
      }
      this.$emit('set-busy', false)
    },
    createConfirmed: function () {
      if (this.dataNode.id !== undefined) {
        this.$emit('create-clicked', {nodeId: this.dataNode.id, label: this.createLabel})
        this.showCreate = false
      }
    },
    _nodeEvent: function (eventName) {
      if (this.dataNode !== undefined) {
        this.$emit(eventName, this.dataNode)
      }
    },
    removeConfirmed: function () {
      this._nodeEvent('remove-clicked')
    },
    loadClicked: function () {
      this._nodeEvent('load-clicked')
    },
    singleLoadClicked: function () {
      this._nodeEvent('single-load-clicked')
    },
    _toggleExpanded: function () {
      // Expand on folder click if no node expand key provided
      if ((this.expand_key === undefined || this.expand_key === '') && this.dataNode.is_dir) {
        this.expandedState = !this.expandedState
      }
    },
    folderClicked: function () {
      this._nodeEvent('folder-clicked')
      this._toggleExpanded()
    },
    labelClicked: function () {
      this._nodeEvent('label-clicked')
    },
    // -- Forward events from child nodes --
    createSubClicked: function (createObj) {
      this.$emit('create-clicked', createObj)
    },
    removeSubClicked: function (node) {
      this.$emit('remove-clicked', node)
    },
    loadSubClicked: function (node) {
      this.$emit('load-clicked', node)
    },
    singleLoadSubClicked: function (node) {
      this.$emit('single-load-clicked', node)
    },
    folderSubClicked: function (node) {
      this.$emit('folder-clicked', node)
    },
    labelSubClicked: function (node) {
      this.$emit('label-clicked', node)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
  },
  computed: {
    documentsNum: function () {
      if (this.dataNode?.documents?.length) {
        return this.dataNode?.documents?.length
      }
      return 0
    },
    subFolderNum: function () {
      if (this.dataNode?.children?.length) {
        let num = 0
        for (let idx in this.dataNode.children) {
          if (this.dataNode.children[idx].is_dir) {
            num += 1
          }
        }
        return num
      }
      return 0
    },
    editableFolders: function () {
      return this.editable
    },
    nodeIcon: function () {
      if (this.dataNode?.is_dir) {
        return 'folder'
      }
      return 'file-earmark-fill'
    },
    expanded: {
      get: function () {
        if (this.expand_key !== undefined && this.expand_key !== '') {
          return this.dataNode[this.expand_key]
        } else {
          return this.expandedState
        }
      },
      set: async function (value) {
        this.expandedState = value
      }
    },
  },
  created() {
    this.dataNode = this.nodeProp
    if ((this.expanded || this.parentExpanded) && this.dataNode?.is_dir) {
      this.getSubFolders(this.dataNode)
    }
  }
}
</script>

<template>
  <b-list-group class="mt-0 mb-0">
    <b-list-group-item :variant="loadedId === dataNode?.id ? 'secondary' : ''" class="pt-0 pb-0 pl-0 mb-0">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <!-- Node Button -->
          <b-button :data-badge="showSubFolderNumber ? subFolderNum : false"
                    :variant="dataNode?.children?.length ? 'primary' : 'outline-primary'" class="mr-2 button-badge-note"
                    size="sm"
                    @click="folderClicked">
            <b-icon :icon="expanded ? 'folder2-open' : nodeIcon"></b-icon>
          </b-button>

          <!-- Label -->
          <b-link href="#" @click="labelClicked">{{ dataNode?.name }}</b-link>
        </div>

        <!-- Buttons -->
        <div>
          <b-badge v-if="documentsNum !== 0" pill class="mr-2"> {{ documentsNum }}</b-badge>

          <b-button-group v-if="!showSelectOnly" size="sm">
            <b-button v-if="showLoadButtons"
                      v-b-popover.hover.left="'Load all documents from this folder and all sub folders'"
                      variant="primary"
                      @click="loadClicked">
              <b-icon aria-hidden="true" icon="card-list"></b-icon>
            </b-button>
            <b-button v-if="dataNode?.documents?.length && showLoadButtons"
                      v-b-popover.hover.topleft="'Load ' + documentsNum + ' documents from this folder'"
                      @click="singleLoadClicked">
              {{ documentsNum }}
              <b-icon aria-hidden="true" icon="card-text"></b-icon>
            </b-button>
            <template v-if="editableFolders">
              <!-- Create Folder button -->
              <b-button :id="'create-' + dataNode?.id" v-b-popover.hover.topleft="'Create a sub-folder'"
                        variant="success" @click="showCreate = true">
                <b-icon aria-hidden="true" icon="folder-plus"></b-icon>
              </b-button>

              <!-- Remove Folder button -->
              <b-button :id="'delete-' + dataNode?.id"
                        v-b-popover.hover.topleft="'Remove this folder, documents inside this folder will be moved to the root folder'"
                        variant="danger" @click="showDelete = true">
                <b-icon aria-hidden="true" icon="folder-minus"></b-icon>
              </b-button>

              <!-- Popover Create -->
              <b-popover :show.sync="showCreate" :target="'create-' + dataNode?.id">
                <template v-slot:title>Create a new nested folder</template>
                <b-form-input v-model="createLabel" placeholder="New Folder Name"></b-form-input>
                <div class="mt-1 text-right">
                  <b-button size="sm" variant="success" @click="createConfirmed">Create</b-button>
                  <b-button aria-label="Close" size="sm" @click="showCreate = false">Close</b-button>
                </div>
              </b-popover>

              <!-- Popover Delete -->
              <b-popover :show.sync="showDelete" :target="'delete-' + dataNode?.id">
                <template v-slot:title>Delete the folder {{ dataNode?.name }} and all sub folders?</template>
                <div class="mt-1 text-right">
                  <b-button size="sm" variant="danger" @click="removeConfirmed">Delete</b-button>
                  <b-button aria-label="Close" size="sm" @click="showDelete = false">Close</b-button>
                </div>
              </b-popover>
            </template>
          </b-button-group>
        </div>
      </div>

      <!-- Child displayNodes -->
      <b-list-group v-if="expanded" class="mt-0 mb-0">
        <FileSystemNode v-for="child in dataNode?.children" v-bind:key="child.name"
                        class="pl-3"
                        :editable="editableFolders"
                        :expand_key="expand_key"
                        :loadedId="loadedId"
                        :nodeProp="child"
                        :parentExpanded="expanded"
                        :show-load-buttons="showLoadButtons"
                        :show-select-only="showSelectOnly"
                        :show-sub-folder-number="showSubFolderNumber"
                        v-on:create-clicked="createSubClicked"
                        v-on:remove-clicked="removeSubClicked"
                        v-on:load-clicked="loadSubClicked"
                        v-on:single-load-clicked="singleLoadSubClicked"
                        v-on:folder-clicked="folderSubClicked"
                        v-on:label-clicked="labelSubClicked"
                        v-on:set-busy="setBusy">
        </FileSystemNode>
      </b-list-group>
    </b-list-group-item>
  </b-list-group>
</template>

<style scoped>
.button-badge-note {
  position: relative;
}

.button-badge-note[data-badge]:after {
  content: attr(data-badge);
  position: absolute;
  transform: translate(-25%, -55%);
  font-family: inherit;
  font-weight: bold;
  font-size: .85em;
  background: #b2b2b2;
  color: #494949;
  width: 70%;
  height: 1.5em;
  text-align: center;
  line-height: 1rem;
  border-radius: 15%;
}
</style>
