<template>
  <div class="container">
    <img src="./assets/logo2.png" />
    <div class="buttons">
      <div class="files">
        <div class="first">
          <input type="file" id="file1" ref="file1" @change="onFileChange('file1')" />
          <label class="label1" for="file1">
            <font-awesome-icon class="upload-icon" icon="fa-solid fa-upload" />
            Upload File
          </label>
          <span class="file-info">
            <span class="file-name" id="file-name1"> No File Selected </span>
            <button class="remove-button" @click="removeFile('file1')" style="display: none;">X</button>
          </span>
        </div>
        <div class="first">
          <input type="file" id="file2" ref="file2" @change="onFileChange('file2')" />
          <label class="label1" for="file2">
            <font-awesome-icon class="upload-icon" icon="fa-solid fa-upload" />
            Upload File
          </label>
          <span class="file-info">
            <span class="file-name" id="file-name2"> No File Selected </span>
            <button class="remove-button" @click="removeFile('file2')" style="display: none;">X</button>
          </span>
        </div>
      </div>
      <button class="send" @click="sendFiles">Send Files</button>
    </div>
    
    <div class="switch-container" v-if="oldData">
      <span class="switch-label">Added</span>
      <div class="switch">
        <input type="checkbox" id="toggle" class="toggle-btn" v-model="showOld">
        <label class="toggle" for="toggle"></label>
      </div>
      <span class="switch-label">Removed</span>
    </div>

    <div class="tree" v-if="showOld && send">
      <CollapsibleTidyTree class="old" v-if="oldData" :data="oldData" />
    </div>
    <div class="tree" v-else-if="!showOld && send">
      <CollapsibleTidyTree class="new" v-if="newData" :data="newData" />
    </div>

    <div class="double-table">
      <div class="table" v-if="showOld && send">
          <div v-for="(entry, index) in Object.entries(oldFeatures).slice(0, 7)" :key="index">
          <h3 class="thead">{{ entry[0] }}</h3>
          <table class="table-values">
            <template v-if="entry[1].length">
              <tr v-for="(item, index) in entry[1]" :key="index">
                <td class="tvalue"  :style="{ color: isOld(entry[0], item) ? '#bd0606' : 'black' }">
                  <span class="index-dot">{{ index + 1 }}. </span>{{ item }}
                </td>
              </tr>
            </template>
            <template v-else>
              <tr>
                <td class="tvalue">
                  <font-awesome-icon class="minus-icon" icon="fa-solid fa-minus" />
                </td>
              </tr>
            </template>
          </table>
        </div>
      </div>

      <div class="table2" v-if="showOld && send">
          <div v-for="(entry, index) in Object.entries(oldFeatures).slice(7,)" :key="index">
          <h3 class="thead">{{ entry[0] }}</h3>
          <table class="table-values">
            <template v-if="entry[1].length">
              <tr v-for="(item, index) in entry[1]" :key="index">
                <td class="tvalue"  :style="{ color: isOld(entry[0], item) ? '#bd0606' : 'black' }">
                  <span class="index-dot">{{ index + 1 }}. </span>{{ item }}
                </td>
              </tr>
            </template>
            <template v-else>
              <tr>
                <td class="tvalue">
                  <font-awesome-icon class="minus-icon" icon="fa-solid fa-minus" />
                </td>
              </tr>
            </template>
          </table>
        </div>
      </div>
    </div>

    <div class="double-table">
      <div class="table" v-if="!showOld && send">
          <div v-for="(entry, index) in Object.entries(newFeatures).slice(0, 7)" :key="index">
          <h3 class="thead">{{ entry[0] }}</h3>
          <table class="table-values">
            <template v-if="entry[1].length">
              <tr v-for="(item, index) in entry[1]" :key="index">
                <td class="tvalue" :style="{ color: isNew(entry[0], item) ? '#00b830' : 'black' }">
                  <span class="index-dot">{{ index + 1 }}. </span>{{ item }}
                </td>
              </tr>
            </template>
            <template v-else>
              <tr>
                <td class="tvalue">
                  <font-awesome-icon class="minus-icon" icon="fa-solid fa-minus" />
                </td>
              </tr>
            </template>
          </table>
        </div>
      </div>

      <div class="table2" v-if="!showOld && send">
          <div v-for="(entry, index) in Object.entries(newFeatures).slice(7,)" :key="index">
          <h3 class="thead">{{ entry[0] }}</h3>
          <table class="table-values">
            <template v-if="entry[1].length">
              <tr v-for="(item, index) in entry[1]" :key="index">
                <td class="tvalue"  :style="{ color: isNew(entry[0], item) ? '#00b830' : 'black' }">
                  <span class="index-dot">{{ index + 1 }}. </span>{{ item }}
                </td>
              </tr>
            </template>
            <template v-else>
              <tr>
                <td class="tvalue">
                  <font-awesome-icon class="minus-icon" icon="fa-solid fa-minus" />
                </td>
              </tr>
            </template>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>
<script>
import CollapsibleTidyTree from './components/CollapsibleTidyTree.vue'
import axios from 'axios'

export default {
  components: {
    CollapsibleTidyTree
  },
  data() {
    return {
      showOld: false,
      send: false,
      oldData: null,
      newData: null,
      addedFeatures: null,
      removedFeatures: null,
      oldFeatures: null,
      newFeatures: null,
      file1: null,
      file2: null,
    }
  },
  methods: {
    onFileChange(refName) {
      this[refName] = this.$refs[refName].files[0]
      const input = document.getElementById(refName);
      const fileName = input.files[0].name;
      const fileNameElement = document.getElementById(`file-name${refName.slice(-1)}`);
      fileNameElement.textContent = fileName;
      const removeButton = input.parentNode.querySelector('.remove-button');
      removeButton.style.display = "inline-block";
    },
    removeFile(refName) {
      const input = document.getElementById(refName);
      const fileNameElement = document.getElementById(`file-name${refName.slice(-1)}`);
      fileNameElement.textContent = "No File Selected";
      input.value = "";
      const removeButton = input.parentNode.querySelector('.remove-button');
      removeButton.style.display = "none";
    },
    sendFiles() {
      const formData = new FormData()
      formData.append('file1', new Blob([this.file1], {type: 'text/xml'}), 'file1.xml');
      formData.append('file2', new Blob([this.file2], {type: 'text/xml'}), 'file2.xml');
      axios.post('http://localhost:5000/api/upload_files', formData)
        .then(response => {
          this.newData=response.data.new
          this.oldData=response.data.old
          this.addedFeatures=response.data.added
          this.removedFeatures=response.data.removed
          this.oldFeatures=response.data.old_features_by_key
          this.newFeatures=response.data.new_features_by_key
        })
        .catch(error => {
          console.log(error)
        })
        this.send = true;
    },
    isNew(key, value) {
      return this.addedFeatures[key] && this.addedFeatures[key].includes(value);
    },
    isOld(key, value) {
      return this.removedFeatures[key] && this.removedFeatures[key].includes(value);
    }
  },
}
</script>
<style scoped>
.container {
  height: 2000px;
  font-family: 'Raleway', arial, serif;
}

img {
  width: 200px;
  margin-left: 20px;
  margin-top: -30px;
}

.buttons {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 200px;
  margin-top: 200px;
}
.file-info{
  display: flex;
  justify-content: space-between;
  color: white;
}
.remove-button {
  background: transparent;
  font-size: 20px;
  font-weight: 600;
  border: 1px solid white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  margin-top:10px;
  color: white;
  cursor: pointer;
}

.files {
  margin-bottom: 100px;
  display: flex;
  width: 1000px;
  justify-content: space-around;
}

.first {
  display: flex;
  flex-direction: column;
}

.file-name {
  margin-top: 10px;
  font-size: 25px;
  font-weight: 600;
}

.send {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background-color: #3e8e41;
  color: white;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.2);
}

.send:hover {
  background-color: #99C24D;
}

.send {
  font-size: 18px;
  font-weight: bold;
  text-transform: uppercase;
  padding: 15px 40px;
  letter-spacing: 1.5px;
  user-select: none;
  cursor: pointer;
  box-shadow: 5px 15px 25px rgba(0, 0, 0, 0.35);
  border-radius: 3px;
}

.send:active {
  transform: scale(0.9);
}

input[type="file"] {
  /* padding: 10px 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
  font-size: 16px;
  box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.2); */
  display: none;
}

/* input[type="file"]:hover {
  background-color: #e8e8e8;
} */

.label1{
  display: inline-block;
  text-transform: uppercase;
  color: #fff;
  background: #db5445;
  text-align: center;
  padding: 15px 40px;
  font-weight: bold;
  font-size: 18px;
  letter-spacing: 1.5px;
  user-select: none;
  cursor: pointer;
  box-shadow: 5px 15px 25px rgba(0, 0, 0, 0.35);
  border-radius: 3px;
  min-width: 320px;
}

.label1:hover {
  background: #fa7c6e;
}
.label1 .upload-icon{
  font-size: 20px;
  margin-right: 10px;
}

.label1:active {
  transform: scale(0.9);
}

.tree{
  background-color: rgba(255,255,255,0.2); /* set the background color with an RGBA value */
  /* box-shadow: 1px 1px 5px 5px #888888; */
  height: 1000px;
  max-width: 2000px;
  margin-left: 275px;
}

.double-table {
  display: flex;
}

.table {
  background-color: rgba(255,255,255,0.2); /* set the background color with an RGBA value */
  min-width: 864px;
  max-width: 864px;
  margin-left: 275px;
  padding-top: 50px;
  padding-right: 135px;
  border-right: 2px solid #ccc;
  border-top: 2px solid #ccc;
  padding-bottom: 100px;
  margin-bottom: 100px;
}

.table2 {
  background-color: rgba(255,255,255,0.2); /* set the background color with an RGBA value */
  min-width: 864px;
  max-width: 864px;
  padding-top: 50px;
  padding-right: 135px;
  border-top: 2px solid #ccc;
  padding-bottom: 100px;
  margin-bottom: 100px;
}

.table-values {
  margin-top: -20px;
  margin-left: 140px;
}

.thead {
  margin-left: 100px;
  font-size: 22px;
  font-weight: 800;
  text-decoration: underline;
}

.tvalue {
  padding-top: 20px;
  font-size: 22px;
  font-weight: 800;
}
.switch-container {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  margin: 20px auto;
  margin-left: 275px;
  max-width: 300px;
  position: absolute;
}
.switch-label {
  margin: 0 10px;
  font-size: 20px;
  font-weight: bold;
}
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-btn {
  display: none;
}

.toggle {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #00b830;
  border-radius: 34px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle:after {
  position: absolute;
  content: "";
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ffffff;
  border: 2px solid black;
  top: 3px;
  left: 3px;
  transition: transform 0.2s;
}

input:checked + .toggle {
  background-color: #bd0606;
}

input:checked + .toggle:after {
  transform: translateX(26px);
}

.index-dot {
  margin-right: 5px;
  font-size: 22px;
}

.minus-icon {
  font-size: 40px;
  color: #222222;
}

</style>