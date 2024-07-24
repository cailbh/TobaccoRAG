<template>
  <div id="root">
    <!-- <div class="head"> -->
    <!-- <Head></Head> -->
    <!-- </div> -->
    <div class="rootBody">
      <div id="menu">
        <div class="logo">
        </div>
        <div id="headTxt">
          智能问答系统
        </div>
        <!-- MOOC2Graph -->
        <div class="navs">
          <el-menu class="el-menu-demo navs" mode="horizontal">
            <el-menu-item index="1">About</el-menu-item>
            <el-menu-item index="2">Contact</el-menu-item>
            <el-menu-item index="3">Help</el-menu-item>
          </el-menu>
        </div>
        <!-- <b-nav class="navs" tabs fill>
        <b-nav-item>About |</b-nav-item>
        <b-nav-item>Contact |</b-nav-item>
        <b-nav-item>?Help</b-nav-item>
        <b-nav-item disabled>Disabled</b-nav-item>
      </b-nav> -->
      </div>
      <div id="menuDiv">
        <el-menu :default-active="defaultActive" class="el-menu" @open="handleOpen" @close="handleClose" @select="select"
          background-color="#545c64" text-color="#fff" active-text-color="#ffd04b">
          <el-menu-item index="1">
            <template slot="title">
              <i class="el-icon-upload"></i>
              <span slot="title" class="navTxt">文件上传</span>

              <input type="file" ref="fileUpload" @change="handleFileChange" style="display: none;" />
            </template>
          </el-menu-item>
          <el-menu-item index="2">
            <template slot="title">
              <i class="el-icon-setting"></i>
              <span slot="title" class="navTxt">文件管理</span>
            </template>
          </el-menu-item>
          <el-menu-item index="3">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span slot="title" class="navTxt">智能问答</span>
            </template>
          </el-menu-item>
        </el-menu>
      </div>
      <div id="contentBody">
        <component :is="currentView" :curFileName="curFileName"></component>
      </div>
    </div>
  </div>
</template>

<script>
import Head from '@/components/Header/index.vue';
import FilePreSeq from '@/components/FilePreSeq/index.vue';
import ChatWindow from '@/components/ChatWindow/index.vue';
import FileManager from '@/components/FileManager/index.vue';
import mammoth from "mammoth";
import axios from 'axios';
const docx = require("docx-preview");

export default {
  components: { Head, FilePreSeq, ChatWindow, FileManager },
  /* eslint-disable no-unused-vars */
  data() {
    return {
      fileContent: '',
      curFileName:'',
      textData: [
        { index: 0, sentence: '' },
      ],
      defaultActive:"3",
      mLigntcolor: [
        "#ff9c9c",
        "#cc88b0",
        "#ffa8ff",
        "#e3b097",
        "#f4c3d0",
        "#f4f4d0",
        "#ffd8b1",
        "#9ecac2",
        "#a8ccff",
        "#97e3ba",
        "#6f8be0",
        "rgb(0,122,244)",
        "#b6a2f7",
        "rgb(168,168,255)",
        "rgb(200,200,200)",
      ],
      currentView: "",
    };
  },
  watch: {
    pageState(val) {
      if (val == 0) {

      }
    },
    mLigntcolor(val) {
      this.$bus.$emit("colorMap", val);
    }
  },
  methods: {
    getData() {
      const _this = this;

    },
    getColor(index) {
      // 根据 index 返回颜色
      const colors = this.mLigntcolor;
      return colors[index % colors.length];
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      let fileName = file.name;
      this.$bus.$emit("curFileName", fileName);
    },
    handleOpen(key, keyPath) {
      const _this = this;
      if (key == '1') {
      }
      if (key == '4') {
        _this.currentView = "Kg4Qa";
      }
    },
    select(key, keyPath) {
      const _this = this;
      _this.currentView = ""
      if (key == '1') {
        _this.currentView = "FilePreSeq";
        _this.defaultActive="2";
        _this.$refs.fileUpload.click();
      }
      if (key == '2') {
        _this.currentView = "FileManager";
      }
      if (key == '3') {
        _this.currentView = "ChatWindow";
      }
    },
    handleClose(key, keyPath) {
    }
  },
  created: function () {
    var _this = this;
  },
  mounted() {
    const _this = this;
    this.$el.style.setProperty("--heightStyle", document.documentElement.clientHeight + "px");
    this.$bus.$on('changeFilePre', (val) => {
        _this.curFileName = val;
        _this.currentView = "FilePreSeq";
    });
  },
  beforeDestroy() {
    clearTimeout(this.timer);
  }
};
</script>

<style>
@import './index.css';
</style>
<style scoped>
.fileview {
  width: 30%;
  height: calc(100% - 4px);
  border: 1px solid #ddd;
  float: left;
  margin-top: 2px;
}

.pdfContainer {
  width: 100%;
  height: calc(100% - 30px);
}

canvas {
  left: 0px;
}

svg {
  transform: translateY(30px) !important;
}
</style>