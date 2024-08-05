<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable no-unused-vars -->

<template>
  <div class="FileManagerPanel">
    <div class="panelHead">
            <i class="el-icon-s-shop"></i>
      知识库
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
    },
    fileData(val) {
      const _this = this;
      let tableData = []
      val.forEach((element,index)=> {
        let temp = {
          id:element['_id'],
          sort: index+1,
          name: element['fileName'],
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

    handleChoose(index, row) {
      let cId = row['id'];
      this.ModifyChooseTag(cId);
    },
    handleEdit(index, row) {
      this.$bus.$emit("changeFilePre", row['fileName']);
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
          console.log(response)
          _this.fileData = response.body;
          // }
        });
    },
  },
  created() {



    const _this = this;
    this.getTagData()
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
