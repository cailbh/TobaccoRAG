<!-- eslint-disable no-unused-vars -->
<template>
  <div v-show="AuxiliaryShow" class="AuxiliaryPanel" ref="AuxiliaryPanel">
    <div id="AuxiliaryHead" @mousedown="startDrag">
      <el-button class="tagBut" type="danger" size="mini" icon="el-icon-close" circle @click="close"></el-button>
    </div>
    <div id="AuxiliaryPanelDiv" class="dataBody" ref="AuxiliaryPanelDiv">
      <div class="pdfContainer" ref="bodypanel" style="overflow-y: auto;overflow-x: hidden;">
        <div style="position: relative;width: 100%;height: 100%;">
          <canvas ref="renderContext"></canvas>
        </div>
      </div>
    </div>
    <div class="resizer" v-for="direction in ['right', 'bottom', 'left', 'bottom-right', 'bottom-left']"
      :class="`resizer-${direction}`" @mousedown.stop="startResize(direction, $event)"></div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import axios from "axios";
const docx = require("docx-preview");
import * as PDFJS from "pdfjs-dist/legacy/build/pdf";  // 引入PDFJS 
import pdfjsWorker from "pdfjs-dist/legacy/build/pdf.worker.entry.js"; // 引入workerSrc的地址
PDFJS.GlobalWorkerOptions.workerSrc = pdfjsWorker; //设置PDFJS.GlobalWorkerOptions.workerSrc的地址
export default {
  props: [],
  components: {},
  data() {
    return {
      path: 'D:/Cailibuhong/XGD/fileData',
      fileName: '',
      pdfPagesNum: 0,
      currentpage: 2,
      pdfUrl: '',
      rate: 1,
      isDragging: false,
      isResizing: false,
      initialMouseX: 0,
      initialMouseY: 0,
      initialWidth: 0,
      initialHeight: 0,
      initialLeft: 0,
      initialTop: 0,
      direction: '',
      AuxiliaryShow: false,
    };
  },
  watch: {

  },
  methods: {
    close() {
      this.AuxiliaryShow = false;
    },
    goPreview(fileName,text) {
      console.log(fileName,text)
      axios({
        method: "post",
        responseType: "blob",
        url: "/api/filePre",
        params: {
          file: fileName,
          text: text,
        },
      }).then((res) => {
        let blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        if (window.createObjectURL != undefined) {
          // basic
          this.pdfUrl = window.createObjectURL(blob);
        } else if (window.URL != undefined) {
          // mozilla(firefox)
          this.pdfUrl = window.URL.createObjectURL(blob);
        } else if (window.webkitURL != undefined) {
          // webkit or chrome
          this.pdfUrl = window.webkitURL.createObjectURL(blob);
        }
        console.log(res,res.headers.pagenumber)
        this.getPdf(this.pdfUrl,parseInt(res.headers.pagenumber));
        // docx.renderAsync(data, this.$refs.fileTest); // 渲染到页面
      });
    },
    getPdf(url, pageNum) {

      PDFJS.getDocument(url).promise.then((pdfDoc) => {
        this.pdfPagesNum = pdfDoc.numPages * 10; // pdf的总页数
        //获取第pageNum页的数据
        this.readerpdfDoc = pdfDoc;
        this.showPdf(pdfDoc, pageNum)
      });
    },
    showPdf(pdfDoc, pageNum) {
      let that = this;
      console.log(pdfDoc, pageNum)
      pdfDoc.getPage(pageNum).then((page) => {
        console.log(page)
        // 设置canvas相关的属性
        const canvas = this.$refs.renderContext
        const ctx = canvas.getContext("2d");
        const dpr = window.devicePixelRatio || 1;
        const bsr =
          ctx.webkitBackingStorePixelRatio ||
          ctx.mozBackingStorePixelRatio ||
          ctx.msBackingStorePixelRatio ||
          ctx.oBackingStorePixelRatio ||
          ctx.backingStorePixelRatio ||
          1;
        const ratio = dpr / bsr;
        const viewport = page.getViewport({ scale: that.rate });
        canvas.width = viewport.width * ratio;
        canvas.height = viewport.height * ratio;
        console.log(viewport, canvas.width)
        canvas.style.width = viewport.width + "px";
        canvas.style.height = viewport.height + "px";
        //canvas.style.transform="translate(-20px,-30px)";
        // canvas.style["z-index"]="-1";
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        const context = {
          canvasContext: ctx,
          viewport: viewport,
        };
        // 数据渲染到canvas画布上
        page.render(context);
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
        console.log("left", deltaX)
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
    let path = this.path;
    this.$bus.$on('quote', (val) => {
      _this.fileName = val;
      _this.goPreview(val.fileName,val.sentence)
      _this.AuxiliaryShow = true;
    });
    // this.goPreview(path,fileName);
  },
} 
</script>

<style>
@import './index.css';
</style>
