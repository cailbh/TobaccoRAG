<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable no-unused-vars -->

<template>
  <div class="FileManagerPanel">
    <div class="panelHead">FileManager
      <el-button class="returnHomeBut" v-show="preShow" size="mini" @click="returnHome()">返回</el-button>
      <el-button class="returnHomeBut" v-show="preShow" size="mini" @click="preClick()">打标</el-button>
    </div>
    <div id="FileManagerPanelDiv" class="panelBody" ref="FileManagerPanelDiv">
      <el-table v-show="tableShow" :data="tableData" style="width: 100%" :row-class-name="tableRowClassName">
        <el-table-column label="序号" width="70">
          <template slot-scope="scope">
            <i class="el-icon-document"></i>
            <span style="margin-left: 10px">{{ scope.row.sort }}</span>
          </template>
        </el-table-column>
        <el-table-column label="文档标题">
          <template slot-scope="scope">
            <!-- <el-popover trigger="hover" placement="top"> -->
            <!-- <p>姓名: {{ scope.row.name }}</p>
              <p>住址: {{ scope.row.address }}</p> -->
            <div slot="reference" class="name-wrapper">
              <span style="margin-left: 10px">{{ scope.row.name }}</span>
            </div>
            <!-- </el-popover> -->
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">查看</el-button>
            <el-button size="mini" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-show="preShow" class="preDiv">
          <div class="tagWrap">
            <!-- <div > -->
              <!-- <TagControl state="file" :curTag="currentTagData"></TagControl> -->
              <!-- </div> -->
          </div>
          <div class="docWrap">
            <div ref="file"></div>
          </div>
      </div>
      <div class="chartTooltip">
        <p>
          <br /><strong class="name"></strong>
        </p>
      </div>

    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import { onMounted, ref } from 'vue';
// import domtoimage from 'dom-to-image';
import tools from "@/utils/tools.js";

// import TagControl from'@/components/TagControl/index.vue'
import { color } from 'd3';
import { _ } from 'core-js';
// let docx = require("docx-preview");
const docx = require("docx-preview");
import axios from "axios";
export default {
  props: [],
  components:{},
  data() {
    return {
      colorMap: {},
      tableShow:true,
      preShow:false,
      chooseTagsId:'',
      fileData: [],
      tableData: [],
      currentTagData:'',
      currentFile:''
    };
  },
  watch: {
    type(val) {
    },
    currentTagData(val){
      console.log(val);
    },
    fileData(val) {
      const _this = this;
      let tableData = []
      val.forEach((element,index)=> {
        let temp = {
          id:element['_id'],
          sort: index+1,
          name: element['title'],
          fileName: element['fileName'],
        }
        tableData.push(temp)
      });
      this.tableData = tableData;
    }
  },
  methods: {
    click_Ent(time) {
      this.$emit("timeDur", time);
    },
    preClick(){
      this.autoMarking(this.currentFile['id'])
    },
    goPreview(fileName) {
      axios({
        method: "get",
        responseType: "blob", // 因为是流文件，所以要指定blob类型
        url: "/api/file/getDoc", // 自己的服务器，提供的一个word下载文件接口
        params:{
             fileName:fileName
         },
      }).then(({ data }) => {
        console.log(data); // 后端返回的是流文件
        docx.renderAsync(data, this.$refs.file); // 渲染到页面
      });
    },
    returnHome(){
      this.tableShow = true;
      this.preShow = false;
    },
    autoMarking(cId){
      const _this = this;
      this.$http
        .post("/api/tag/AutoMarking", {
          params: {
            cId: cId
          }
        }, {})
        .then((response) => {
          _this.$message({
            message: '设置成功',
            type: 'success',
            duration: 1000
          });
          console.log("atm",response)
          let LLMTag = JSON.parse(response.bodyText);
          if(typeof(LLMTag) === 'object'){
            _this.$bus.$emit("LLMPreTags", LLMTag);
          }
        });
    },
    handleChoose(index, row) {
      let cId = row['id'];
      this.ModifyChooseTag(cId);
    },
    handleEdit(index, row) {
      this.tableShow = false;
      this.preShow = true;
      this.currentFile =this.fileData.find((d)=>{return d['_id'] == row['id']});
      console.log(row,this.fileData)
      this.goPreview(row.fileName)
      console.log(1,this.currentFile)
      this.$bus.$emit("currentFile", this.currentFile);
      
      this.$bus.$emit("tagEdit","true");
    },
    handleDelete(index, row) {
      console.log(index, row);
    },
    tableRowClassName({ row, rowIndex }) {
      if (row.isChoose) {
        return 'choose-row';
      }
      return '';
    },
    getTagData: function () {
      const _this = this;
      this.$http
        .get("/api/getFileList", { params: {} }, {})
        .then((response) => {
          _this.fileData = response.body;
          // }
        });
    },
  },
  created() {



    const _this = this;
    // this.getTagData()
    this.$nextTick(() => {
    });
  },
  mounted() {
    const _this = this
    this.$bus.$on('currentTagData', (val) => {
      _this.currentTagData  = val;
    });
  },
  // beforeDestroy() {
  //   clearInterval(this.moveTimer);
  // },
} 
</script>

<style>
@import './index.css';
</style>
