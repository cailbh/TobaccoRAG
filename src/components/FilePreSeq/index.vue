<!-- eslint-disable no-unused-vars -->
<template>
  <div class="FilePreSeqPanel" ref="FilePreSeqPanel">
    <div id="FilePreSeqHead">
      <div class="fileTxtHead">
      </div>
    </div>
    <div v-if="contextMenu.visible" :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      class="context-menu">
      <ul>
        <li @click="addSelectText(contextMenu.index)">添加</li>
        <!-- <li @click="deleteText(contextMenu.index)">删除</li> -->
      </ul>
    </div>
    <div id="FilePreSeqBody">
      <div class="filePre">

        <el-card class="filePre-card filePreC filepretitle" style="position: absolute; z-index: 2;">
          <div slot="header" class="clearfix">
            <span class="h1Txt">文件预览</span>
            <span>&nbsp;</span>
            <span class="h2Txt">{{ curFileName }}</span>
          </div>
          <!-- <div class="pdfContainer" ref="bodypanel" style="overflow-y: auto;overflow-x: hidden;">
            <div class="canvasContainer"  ref="prePanel" style="position: relative;width: 100%;height: 100%;">
              <canvas ref="renderContext"></canvas>
            </div>
          </div>
          <div class="paginationDiv">
            <el-row justify="center" style="transform: translate(0,0px);">
              <el-col :span="24">
                <el-pagination layout="prev, pager, next" small background :total="pdfPagesNum"
                  @current-change="currentChange" />
              </el-col>
            </el-row>
          </div> -->
        </el-card>

        <div class="docWrap">
          <div ref="prePanel"></div>
        </div>
      </div>
      <div class="toolsDiv">
        <el-card class="filePre-card  tools-card">
          <div slot="header" class="clearfix">
            <i class="el-icon-s-operation"></i>
            <span class="h1Txt">参数配置</span>
            <el-tag class="infoTags" size="mini" type="info">{{ `总分段：${textData.length}` }}</el-tag>
            <el-tag class="infoTags" size="mini" type="info">{{ `总字数 ${textNum}` }}</el-tag>

            <el-button class="buts1" size="small" type="primary" @click="dgShowClk"
              icon="el-icon-s-claim">递归分割</el-button>

            <el-button class="buts1" size="small" type="primary" @click="gsShowClk"
              icon="el-icon-s-order">格式分割</el-button>
          </div>
          <div class="halfDiv" v-show="dgShow">
            <span class="h3Txt">理想分块长度: {{ chunkSize }}</span>
            <!-- <el-input-number class="inputNumbe" v-model="chunkSize" controls-position="right"></el-input-number> -->
            <!-- <div class="slider-value"></div> -->
            <el-slider class="custom-slider" v-model="chunkSize" :show-tooltip="false" :max="textNum">
            </el-slider>
          </div>

          <div class="halfDiv" v-show="dgShow">
            <span class="h3Txt">理想重叠长度: {{ overlap }}</span>
            <!-- <el-input-number class="inputNumbe" v-model="overlap" controls-position="right"></el-input-number> -->
            <!-- <div class="slider-value">/div> -->
            <el-slider class="custom-slider" v-model="overlap" :show-tooltip="false" :max="chunkSize">
            </el-slider>
          </div>
          <div class="halfDiv" v-show="dgShow">
            <span class="h3Txt">自定义分割符: {{ SplitSybs }}</span>
            <el-input v-model="SplitSybs" size="small" :placeholder="SplitSybs"></el-input>
            <!-- <el-input-number class="inputNumbe" v-model="overlap" controls-position="right"></el-input-number> -->
            <!-- <div class="slider-value">/div> -->
            <!-- <el-slider class="custom-slider" v-model="overlap" :show-tooltip="false" :max="chunkSize"> -->
            <!-- </el-slider> -->
          </div>
          <div class="halfDiv" v-show="gsShow">
            <span class="h3Txt">父块分割符: {{ SplitSybsChart }}</span>
            <el-input v-model="SplitSybs" size="small" style="width: 200px;" :placeholder="SplitSybsChart"></el-input>
            <!-- <el-input-number class="inputNumbe" v-model="overlap" controls-position="right"></el-input-number> -->
            <!-- <div class="slider-value">/div> -->
            <!-- <el-slider class="custom-slider" v-model="overlap" :show-tooltip="false" :max="chunkSize"> -->
            <!-- </el-slider> -->
          </div>
          <div class="halfDiv" v-show="gsShow">
            <span class="h3Txt">子块分割符: {{ SplitSybsArt }}</span>
            <el-input v-model="SplitSybs" size="small" style="width: 200px;;" :placeholder="SplitSybsArt"></el-input>
            <!-- <el-input-number class="inputNumbe" v-model="overlap" controls-position="right"></el-input-number> -->
            <!-- <div class="slider-value">/div> -->
            <!-- <el-slider class="custom-slider" v-model="overlap" :show-tooltip="false" :max="chunkSize"> -->
            <!-- </el-slider> -->
          </div>
          <!-- </div> -->
          <el-button class="buts" size="small" type="primary" @click="textChunkClk"
            icon="el-icon-s-opportunity">开始分割</el-button>

          <el-button class="buts" size="small" type="primary" @click="confirmClk" icon="el-icon-upload">确认导入</el-button>
          <!-- <el-button v-show="dgShow" class="buts" size="small" type="primary" @click="textChunkClk"
            icon="el-icon-s-opportunity">开始分割</el-button>

          <el-button v-show="dgShow" class="buts" size="small" type="primary" @click="confirmClk" icon="el-icon-upload">确认导入</el-button> -->

        </el-card>
      </div>
      <div class="fileTxt" ref="fileTest">
        <div class="fileTxtBody">
          <el-card v-for="item in textData" :key="item.index" class="box-card">
            <div slot="header" class="clearfix">
              <el-tag type="info">{{ `#chunk ${item.index + 1}` }}</el-tag>
              <el-button class="chunkButs" size="small" type="primary" plain
                @click="deleteText(item.index)">删除</el-button>

              <el-button class="chunkButs" size="small" type="primary" plain
                @click="editText(item.index)">编辑</el-button>
              <el-button class="chunkButs" size="small" type="primary" plain
                @click="chunkText(item.index)">分割</el-button>

              <el-button class="chunkButs" size="small" type="primary" plain @click="addText(item.index)">新增</el-button>
              <template v-if="mergeHoverIndex != item.index">
                <el-button class="chunkButs split-button" size="small" type="primary" plain
                  @mouseover.native="mergeButHover(item.index)"
                  @mouseleave.native="mergeButLeave(item.index)">合并</el-button>
              </template>
              <div class="chunkButsDiv" v-else @mouseleave="mergeButLeave(item.index)">
                <el-button class="chunkButs1" size="small" type="primary" plain @click="merageUpText(item.index)"
                  icon="el-icon-caret-top"></el-button>
                <el-button class="chunkButs1" size="small" type="primary" plain @click="merageDownText(item.index)"
                  icon="el-icon-caret-bottom"></el-button>
              </div>
            </div>
            <p class="formatted-text1" v-if="editingIndex != item.index"
              @contextmenu.prevent="showContextMenu($event, item.index)" @click="pClk()" @mouseup="handleSelection">
              {{ item.prevOverlap }}
            </p>
            <p class="formatted-text" v-if="editingIndex != item.index"
              @contextmenu.prevent="showContextMenu($event, item.index)" @click="pClk()" @mouseup="handleSelection">
              {{ item.nonOverlap }}
            </p>
            <p class="formatted-text1" v-if="editingIndex != item.index"
              @contextmenu.prevent="showContextMenu($event, item.index)" @click="pClk()" @mouseup="handleSelection">
              {{ item.nextOverlap }}
            </p>
            <el-input v-else ref="input" @blur="saveText" type="textarea" autosize placeholder=""
              v-model="item.sentence">
            </el-input>
          </el-card>
        </div>
        <!-- <treeMap :treeData="tree_data" ref="treecontainer"></treeMap> -->
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';
import axios from "axios";
import * as PDFJS from "pdfjs-dist/legacy/build/pdf";  // 引入PDFJS 
import pdfjsWorker from "pdfjs-dist/legacy/build/pdf.worker.entry.js"; // 引入workerSrc的地址
import treeMap from '../treeMap/index.vue'
PDFJS.GlobalWorkerOptions.workerSrc = pdfjsWorker; //设置PDFJS.GlobalWorkerOptions.workerSrc的地址
const docx = require("docx-preview");
export default {
  props: ["curFileName"],
  components: { treeMap },
  data() {
    return {
      dgShow: true,
      gsShow: false,
      pdfPagesNum: 0,
      currentpage: 2,
      textNum: 600,
      editingIndex: null,
      SplitSybs: "",
      SplitSybsChart: "章",
      SplitSybsArt: "条",
      SplitType: 0,
      pdfUrl: '',
      fileName: '',
      rate: 1,
      textData: [],
      tree_data: {},
      chunkSize: 300,
      overlap: 50,
      selectedText: '',
      contextMenu: {
        visible: false,
        x: 0,
        y: 0,
        index: null
      },
      mergeHoverIndex: null,
    };
  },
  watch: {
    curFileName(val) {
      console.log("curFileNamesss", val);
    }
  },
  methods: {
    dgShowClk() {
      this.dgShow = true;
      this.gsShow = false;
      this.SplitType = 0;
    },
    gsShowClk() {
      this.gsShow = true;
      this.dgShow = false;
      this.SplitType = 1;
    },
    mergeButHover(index) {
      this.mergeHoverIndex = index;
    },
    mergeButLeave() {
      this.mergeHoverIndex = null;
    },
    showContextMenu(event, index) {
      event.preventDefault(); // 防止默认的上下文菜单出现
      console.log(event)
      this.contextMenu = {
        visible: true,
        x: event.layerX + 10,
        y: event.layerY + 50,
        index: index
      };
    },
    editText(index) {
      this.editingIndex = index;
      this.contextMenu.visible = false;
      this.$nextTick(() => {
        this.$refs.input[0].focus();
      });
    },
    chunkText(index) {
      console.log("cccc", this.textData[index])
      const _this = this;
      this.$http
        .post("/api/chunkWordToSeq", { textData: _this.textData[index]['sentence'], overlap: _this.overlap, chunkSize: _this.chunkSize }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((res) => {
          let seqData = res.body

          _this.textData.splice(index, 1, ...seqData);
          _this.updataChunk(_this.textData);
          // _this.$message({
          //   message: '文本分割完成',
          //   type: 'success'
          // });
          _this.$notify({
            title: '文本分割完成',
            type: 'success',
            message: '文本分割完成,请确认后添加至知识库'
          });
        });
      // this.textData.splice(index, 0, { 'sentence': '' });
      // this.updataChunk(this.textData);
      this.contextMenu.visible = false;
    },
    updataChunk(data) {
      this.textData = this.processTexts(data);
      console.log("data", this.textData)
    },
    pClk() {
      this.contextMenu.visible = false;
    },
    deleteText(index) {
      this.textData.splice(index, 1);
      this.updataChunk(this.textData);
      this.contextMenu.visible = false;
    },
    addText(index) {
      this.textData.splice(index, 0, { 'sentence': '' });
      this.updataChunk(this.textData);
      this.contextMenu.visible = false;
    },
    merageUpText(index) {
      const _this = this;
      if (index != 0) {
        this.textData.splice(index - 1, 2, { 'sentence': _this.textData[index - 1]['sentence'] + _this.textData[index]['sentence'] });
        this.updataChunk(this.textData);
        this.contextMenu.visible = false;
        this.mergeHoverIndex = null;
        this.editingIndex = null;
      }
    },
    merageDownText(index) {
      const _this = this;
      if (index != this.textData.length - 1) {
        this.textData.splice(index, 2, { 'sentence': _this.textData[index]['sentence'] + _this.textData[index + 1]['sentence'] });
        this.updataChunk(this.textData);
        this.contextMenu.visible = false;
        this.mergeHoverIndex = null;
        this.editingIndex = null;
      }
    },
    splitText(longText, shortText) {
      // 找到短文本在长文本中的起始位置
      const startIndex = longText.indexOf(shortText);

      if (startIndex === -1) {
        throw new Error("");
      }

      // 计算短文本的结束位置
      const endIndex = startIndex + shortText.length;

      // 分割长文本为三部分
      const beforeText = longText.substring(0, startIndex);
      const middleText = shortText;
      const afterText = longText.substring(endIndex);

      return [
        beforeText,
        middleText,
        afterText
      ]
    },
    addSelectText(index) {
      const _this = this;
      let data = this.splitText(_this.textData[index]['sentence'], _this.selectedText);
      this.textData.splice(index, 1);
      if (data[2] != "")
        this.textData.splice(index, 0, { 'sentence': data[2] })
      if (data[1] != "")
        this.textData.splice(index, 0, { 'sentence': data[1] })
      if (data[0] != "")
        this.textData.splice(index, 0, { 'sentence': data[0] })
      this.updataChunk(this.textData);
      this.contextMenu.visible = false;
    },
    saveText() {
      this.editingIndex = null;
    },
    handleSelection() {
      const selectedText = window.getSelection().toString();
      if (selectedText) {
        this.selectedText = selectedText;
      } else {
        this.selectedText = "";
      }
    },
    findOverlap(text1, text2) {
      let overlap = '';
      for (let i = 0; i < text1.length; i++) {
        for (let j = text2.length; j > 0; j--) {
          if (text1.slice(-i) === text2.slice(0, j)) {
            overlap = text1.slice(-i);
            break;
          }
        }
        if (overlap) break;
      }
      return overlap;
    },
    processTexts(texts) {
      // tests是分割后的数组[{index: int,sentence: str}]
      if (texts.length === 0) return [];

      const result = [];
      let textNum = 0;
      for (let i = 0; i < texts.length; i++) {
        const prevText = i > 0 ? texts[i - 1]['sentence'] : '';
        const currentText = texts[i]['sentence'];
        const nextText = i < texts.length - 1 ? texts[i + 1]['sentence'] : '';

        // 与上一条文本块的重叠部分
        const prevOverlap = this.findOverlap(prevText, currentText);
        // 与下一条文本块的重叠部分
        const nextOverlap = this.findOverlap(currentText, nextText);

        // 没有重叠的部分
        const nonOverlap = currentText.slice(prevOverlap.length, currentText.length - nextOverlap.length);

        textNum += nonOverlap.length;
        result.push({
          index: parseInt(i),
          sentence: currentText,
          prevOverlap: prevOverlap,
          nonOverlap: nonOverlap,
          nextOverlap: nextOverlap,
        });
      }
      this.textNum = textNum;
      return result;
    },
    close() {
      this.FilePreSeqShow = false;
    },
    currentChange(num) {
      this.showPdf(this.readerpdfDoc, num);
      this.currentpage = num;
      this.mode = 1;
    },
    textChunkClk() {
      const _this = this;
      let chunkSize = this.chunkSize;
      let overlap = this.overlap;
      let fileName = this.curFileName;
      let SplitType = this.SplitType;
      this.$http
        .post("/api/wordToSeq", { file: fileName, overlap: overlap, chunkSize: chunkSize, SplitType: SplitType }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((res) => {
          console.log(res)
          let seqData = res.body.sentences
          _this.updataChunk(seqData);

          // this.$refs.treecontainer.treeDataUpdate(_this.tree_data, res.body.treeData)
          _this.tree_data = res.body.treeData
          // _this.$message({
          //   message: '文本分割完成',
          //   type: 'success'
          // });
          _this.$notify({
            title: '文本分割完成',
            type: 'success',
            message: '文本分割完成,请确认后添加至知识库'
          });
        });
    },
    confirmClk() {
      const _this = this;
      this.$http
        .post("/api/seqToVec", { textData: _this.textData, fileName: _this.curFileName }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((res) => {
          // _this.$message({
          //   message: '成功建立向量数据库',
          //   type: 'success'
          // });

          _this.$notify({
            title: '保存成功',
            type: 'success',
            message: '当前数据已添加至知识库'
          });
        });
    },
    fileChange(fileName) {
      const _this = this;
      axios({
        method: "post",
        responseType: "blob",
        url: "/api/fileUpload",
        params: {
          file: fileName,
        },
      }).then((res) => {
        console.log(res)
        let blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        const option = {
          className: "docx", // 默认和文档样式类的类名/前缀
          inWrapper: true, // 启用围绕文档内容渲染包装器
          ignoreWidth: false, // 禁止页面渲染宽度
          ignoreHeight: false, // 禁止页面渲染高度
          ignoreFonts: false, // 禁止字体渲染
          breakPages: true, // 在分页符上启用分页
          ignoreLastRenderedPageBreak: true, //禁用lastRenderedPageBreak元素的分页
          experimental: false, //启用实验性功能（制表符停止计算）
          trimXmlDeclaration: true, //如果为真，xml声明将在解析之前从xml文档中删除
          debug: false, // 启用额外的日志记录
        };
        if (this.$refs.prePanel) {
          docx.renderAsync(blob, this.$refs.prePanel, null, option); // 渲染到页面
        }
        // if (window.createObjectURL != undefined) {
        //   // basic
        //   this.pdfUrl = window.createObjectURL(blob);
        // } else if (window.URL != undefined) {
        //   // mozilla(firefox)
        //   this.pdfUrl = window.URL.createObjectURL(blob);
        // } else if (window.webkitURL != undefined) {
        //   // webkit or chrome
        //   this.pdfUrl = window.webkitURL.createObjectURL(blob);
        // }
        // this.getPdf(this.pdfUrl, 1);
        // docx.renderAsync(data, this.$refs.fileTest); // 渲染到页面
      });
      this.getSeqData(fileName);
    },
    getSeqData(fileName) {
      const _this = this;
      this.$http
        .post("/api/getFileTextSeq", { fileName: fileName }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((response) => {
          console.log("getFileTextSeq", response.body);
          _this.updataChunk(response.body);
          // }
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
      pdfDoc.getPage(pageNum).then((page) => {
        // 设置canvas相关的属性
        const canvas = this.$refs.renderContext
        console.log('canvas', canvas);
        if (canvas) {
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
        }
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
    if (this.curFileName != '') {
      _this.fileChange(_this.curFileName + '.pdf')
    }
    this.$bus.$on('curFileName', (val) => {
      _this.curFileName = val;
      _this.fileChange(_this.curFileName);
    });
  },
} 
</script>

<style>
@import './index.css';
</style>
