<!-- eslint-disable no-unused-vars -->
<template>
  <div v-show="AuxiliaryShow" class="AuxiliaryPanel" ref="AuxiliaryPanel">
    <div id="AuxiliaryHead" @mousedown="startDrag">
      <el-button class="tagBut" type="danger" size="mini" icon="el-icon-close" circle @click="close"></el-button>
    </div>
    <div id="AuxiliaryPanelDiv" class="dataBody" ref="AuxiliaryPanelDiv">
      asdasd
    </div>
    <div
      class="resizer"
      v-for="direction in ['right', 'bottom', 'left', 'bottom-right', 'bottom-left']"
      :class="`resizer-${direction}`"
      @mousedown.stop="startResize(direction, $event)"
    ></div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import axios from "axios";
const docx = require("docx-preview");
export default {
  props: [],
  components: {},
  data() {
    return {
      path:'D:/Cailibuhong/XGD/fileData',
      isDragging: false,
      isResizing: false,
      initialMouseX: 0,
      initialMouseY: 0,
      initialWidth: 0,
      initialHeight: 0,
      initialLeft: 0,
      initialTop: 0,
      direction: '',
      AuxiliaryShow:true,
    };
  },
  watch: {

  },
  methods: {
    close(){
      this.AuxiliaryShow = false;
    },
    goPreview(path, fileName) {
      axios({
        method: "get",
        responseType: "blob", // 因为是流文件，所以要指定blob类型
        url: "/api/file/getDoc", // 自己的服务器，提供的一个word下载文件接口
        params: {
          path: path,
          fileName: fileName
        },
      }).then(({ data }) => {
        console.log(data); // 后端返回的是流文件
        docx.renderAsync(data, this.$refs.AuxiliaryPanelDiv); // 渲染到页面
      });
    },
    startDrag(event) {
      this.isDragging = true;
      this.initialMouseX = event.screenX;
      this.initialMouseY = event.screenY;
      // const rect = this.$refs.AuxiliaryPanel.getBoundingClientRect();
      // this.initialLeft = rect.left;
      // this.initialTop = rect.top;
      const style = window.getComputedStyle(this.$refs.AuxiliaryPanel);
      const matrix = new WebKitCSSMatrix(style.transform);
      this.initialLeft = matrix.m41 || 0;
      this.initialTop = matrix.m42 || 0;
      document.addEventListener('mousemove', this.onMouseMove);
      document.addEventListener('mouseup', this.stopDrag);
    },
    onMouseMove(event) {
      if (this.isDragging) {
        const deltaX = event.screenX - this.initialMouseX;
        const deltaY = event.screenY - this.initialMouseY;
        this.$refs.AuxiliaryPanel.style.transform = `translate(${this.initialLeft + deltaX}px, ${this.initialTop + deltaY}px)`;
      } else if (this.isResizing) {
        this.resizeComponent(event);
      }
    },
    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.onMouseMove);
      document.removeEventListener('mouseup', this.stopDrag);
    },
    startResize(direction, event) {
      this.isResizing = true;
      this.direction = direction;
      this.initialMouseX = event.screenX;
      this.initialMouseY = event.screenY;
      // const rect = this.$refs.AuxiliaryPanel.getBoundingClientRect();
      // this.initialWidth = rect.width;
      // this.initialHeight = rect.height;
      const style = window.getComputedStyle(this.$refs.AuxiliaryPanel);
      const matrix = new WebKitCSSMatrix(style.transform);
      this.initialLeft = matrix.m41 || 0;
      this.initialTop = matrix.m42 || 0;
      
      this.initialWidth = parseFloat(style.width);
      this.initialHeight = parseFloat(style.height);
      // this.initialLeft = rect.left;
      // this.initialTop = rect.top;
      document.addEventListener('mousemove', this.onMouseMove);
      document.addEventListener('mouseup', this.stopResize);
    },
    resizeComponent(event) {
      const deltaX = event.screenX - this.initialMouseX;
      const deltaY = event.screenY - this.initialMouseY;
      const style = window.getComputedStyle(this.$refs.AuxiliaryPanel);
      const matrix = new WebKitCSSMatrix(style.transform);
      let oriLeft = matrix.m41 || 0;
      let oriTop = matrix.m42 || 0;
      // console.log(this.direction,this.direction.includes('top'),this.direction.includes('left'))
      if (this.direction.includes('right')) {
        console.log("right")
        this.$refs.AuxiliaryPanel.style.width = `${this.initialWidth + deltaX}px`;
      }
      if (this.direction.includes('bottom')) {
        console.log("bottom")
        this.$refs.AuxiliaryPanel.style.height = `${this.initialHeight + deltaY}px`;
      }
      if (this.direction.includes('left')) {
        console.log("left",deltaX)
        this.$refs.AuxiliaryPanel.style.width = `${this.initialWidth - deltaX}px`;
        // this.$refs.AuxiliaryPanel.style.left = `${this.initialLeft + deltaX}px`;
        this.$refs.AuxiliaryPanel.style.transform = `translate(${this.initialLeft + deltaX}px, ${oriTop}px)`;
      }
      if (this.direction.includes('top')) {
        console.log("top")
        this.$refs.AuxiliaryPanel.style.height = `${this.initialHeight - deltaY}px`;
        this.$refs.AuxiliaryPanel.style.transform = `translate(${oriLeft}px, ${this.initialTop + deltaY}px)`;
        // this.$refs.AuxiliaryPanel.style.top = `${this.initialTop + deltaY}px`;
      }
    },
    stopResize() {
      this.isResizing = false;
      document.removeEventListener('mousemove', this.onMouseMove);
      document.removeEventListener('mouseup', this.stopResize);
    },
  },
  created() {
    const _this = this;
    this.$nextTick(() => {
    });
  },
  mounted() {
    const _this = this;
    let path =this.path;
    let fileName = 'testFile1';
    this.goPreview(path,fileName);
  },
} 
</script>

<style>
@import './index.css';
</style>
