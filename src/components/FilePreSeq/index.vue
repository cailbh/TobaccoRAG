<!-- eslint-disable no-unused-vars -->
<template>
  <div class="FilePreSeqPanel" ref="FilePreSeqPanel">
    <div id="FilePreSeqHead">
      <div class="fileTxtHead">
        <input type="file" ref="fileUpload" @change="handleFileChange" style="display: none;" />
        <el-button class="buts" size="small" type="primary" @click="confirmClk">确认</el-button>
      </div>
    </div>
    <div id="FilePreSeqBody">
      <div class="filePre">
        <div class="pdfContainer" ref="bodypanel" style="overflow-y: auto;overflow-x: hidden;">
          <div style="position: relative;width: 100%;height: 100%;">
            <canvas ref="renderContext"></canvas>
          </div>
        </div>
      </div>
      <div class="paginationDiv">
        <el-row justify="center" style="transform: translate(0,0px);">
          <el-col :span="24">
            <el-pagination layout="prev, pager, next" small background :total="pdfPagesNum"
              @current-change="currentChange" />
          </el-col>
        </el-row>
      </div>
      <div class="fileTxt" ref="fileTest">
        <div class="fileTxtBody">
          <el-card v-for="item in textData" :key="item.index" class="box-card">
            <el-input type="textarea" autosize placeholder="" v-model="item.sentence">
            </el-input>
            <!-- <div :key="o" class="text item">
              {{ item.sentence }}
            </div> -->
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import axios from "axios";
import * as PDFJS from "pdfjs-dist/legacy/build/pdf";  // 引入PDFJS 
import pdfjsWorker from "pdfjs-dist/legacy/build/pdf.worker.entry.js"; // 引入workerSrc的地址
PDFJS.GlobalWorkerOptions.workerSrc = pdfjsWorker; //设置PDFJS.GlobalWorkerOptions.workerSrc的地址

export default {
  props: [],
  components: {},
  data() {
    return {
      pdfPagesNum: 0,
      currentpage: 2,
      pdfUrl: '',
      fileName:'',
      rate: 1,
    };
  },
  watch: {

  },
  methods: {
    close() {
      this.FilePreSeqShow = false;
    },
    currentChange(num) {
      this.showPdf(this.readerpdfDoc, num);
      this.currentpage = num;
      this.mode = 1;
    },
    confirmClk() {
      const _this = this;
      this.$http
        .post("/api/seqToVec", { textData: _this.textData,fileName:  _this.fileName}, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((res) => {
          console.log(res.body);
          _this.$message({
            message: '成功建立向量数据库',
            type: 'success'
          });
        });
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      console.log(file)
      let fileName = file.name;
      this.fileName = fileName
      const _this = this;
      if (file) {

        const formData = new FormData();
        formData.append('file', file);

        axios({
          method: "post",
          responseType: "blob",
          url: "/api/fileUpload",
          params: {
            file: fileName,
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
          this.getPdf(this.pdfUrl, 1);
          // docx.renderAsync(data, this.$refs.fileTest); // 渲染到页面
        });
        let chunkSize = 300;
        let overlap = 80;
        this.$http
          .post("/api/wordToSeq", { file: fileName, overlap: overlap, chunkSize: chunkSize }, {
            headers: {
              'Content-Type': 'application/json'
            }
          })
          .then((res) => {
            let seqData = res.body;
            _this.textData = seqData;
          });
      }
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
  },
  created() {
    const _this = this;
    this.$nextTick(() => {
    });
  },
  mounted() {
    const _this = this;
      _this.$refs.fileUpload.click();
  },
} 
</script>

<style>
@import './index.css';
</style>
