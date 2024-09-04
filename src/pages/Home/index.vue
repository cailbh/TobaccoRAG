<template>
  <div id="root">
    <el-dialog :title="isregist ? '注册' : '登录'" :visible.sync="isunlogin" width="30%" center label-position="left"
      :close-on-click-modal="false" :show-close="false">
      <el-form :model="ruleForm" :rules="loginrules" ref="ruleForm" label-width="100px" class="demo-ruleForm">
        <el-form-item label="用户名" prop="userName">
          <el-input v-model="ruleForm.userName"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="ruleForm.password" show-password></el-input>
        </el-form-item>
        <el-form-item v-if="isregist" label="确定密码" prop="repassword">
          <el-input v-model="ruleForm.repassword" show-password></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer" style="display: block;">
        <div v-if="isregist === false">
          <el-button type="text" @click="registChange()" v-text="'先注册'"
            style="width: 40%; text-align: right;"></el-button>
          <el-button type="text" @click="registChange()" v-text="'忘记密码'"
            style="width: 40%; text-align: left;"></el-button>
        </div>
        <div v-else>
          <el-button type="text" @click="registChange()" v-text="'去登录'" style="width: 100%;"></el-button>
        </div>
        <el-button type="primary" style="width: calc(100% - 40px);"
          @click="logincheck(ruleForm.userName, ruleForm.password)">确 定</el-button>
      </span>
    </el-dialog>

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
        <div class="navs">
          <!-- <el-menu class="el-menu-demo navs" mode="horizontal">
            <el-menu-item index="1">About</el-menu-item>
            <el-menu-item index="2">Contact</el-menu-item>
            <el-menu-item index="3">Help</el-menu-item>
          </el-menu> -->
          <span style="display: inline-block;margin-right: 20px;margin-top: 20px;">{{ ruleForm.userName }}</span>
          <el-button style="display: inline-block;margin-right: 20px;margin-top: 20px;" v-if="!isunlogin" size="small"
            type="primary" @click="exitLogin">退出登录</el-button>
        </div>


      </div>
      <div id="menuDiv">
        <el-menu :default-active="defaultActive" class="el-menu" @open="handleOpen" @close="handleClose"
          @select="select" background-color="rgb(244, 244, 247)" text-color="rgb(156, 158, 161)"
          active-text-color="rgb(64, 110, 245)">
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
        <component :is="currentView" :curFileName="curFileName" :userName="ruleForm.userName"></component>
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
import { json, tree } from 'd3';
const docx = require("docx-preview");

export default {
  components: { Head, FilePreSeq, ChatWindow, FileManager },
  /* eslint-disable no-unused-vars */
  data() {
    return {
      fileContent: '',
      curFileName: '',
      textData: [
        { index: 0, sentence: '' },
      ],
      defaultActive: "3",
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
      isunlogin: true,
      isregist: false,
      ruleForm: {
        userName: '',
        password: '',
        repassword: ''
      },
      loginrules: {
        userName: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 2, max: 5, message: '长度在 2 到 5 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 15, message: '长度在 6 到 15 个字符', trigger: 'blur' }
        ],
        repassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: this.checkPassword, trigger: 'blur' }
        ]
      }
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

      const loading = this.$loading({
        lock: true,
        text: '正在上传文件',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });

      // 保存文件
      let formData = new FormData();
      formData.append('file', file)
      this.$http
        .post("/api/filesave", formData, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then((response) => {
          console.log("OK")
        });

      this.$bus.$emit("curFileName", fileName);

      loading.close();
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
        _this.defaultActive = "2";
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
    },
    checkPassword(rule, value, callback) {
      if (value !== this.ruleForm.password) {
        callback(new Error('两次输入的密码不一致'));
      } else {
        callback();
      }
    },
    logincheck(name, password) {
      let _this = this
      if (this.isregist) {
        if (this.ruleForm.password == this.ruleForm.repassword) {
          this.$http
            .post("/api/registcheck", {
              name: name,
              password: password
            }, {
              headers: {
                'Content-Type': 'application/json'
              }
            })
            .then((response) => {
              console.log(response)
              let data = response.body;
              if (data.logindata != 0) {
                _this.isunlogin = false

                _this.$cookies.set("user", JSON.stringify(_this.ruleForm))
                _this.$notify({
                  title: data.data,
                  type: 'success',
                  message: `注册成功 欢迎您${name}`
                });
              }
              else {
                _this.$notify({
                  title: data.data,
                  type: 'error',
                  message: `用户名已被占用 请重新登录`
                });
              }
            });
        }
      }
      else {
        this.$http
          .post("/api/logincheck", {
            name: name,
            password: password
          }, {
            headers: {
              'Content-Type': 'application/json'
            }
          })
          .then((response) => {
            console.log(response)
            let data = response.body;
            if (data.logindata == 0) {
              _this.isunlogin = false

              _this.$cookies.set("user", JSON.stringify(_this.ruleForm))
              _this.$notify({
                title: data.data,
                type: 'success',
                message: `登录成功，欢迎您 ${name}`
              });
            }
            else {
              _this.$notify({
                title: data.data,
                type: 'error',
                message: `登录失败，请检查重试`
              });
            }
          });
      }
    },
    registChange() {
      this.isregist = !this.isregist
    },
    exitLogin() {
      this.isregist = false
      this.isunlogin = true

      this.ruleForm = {
        userName: '',
        password: '',
        repassword: ''
      }
    }
  },
  created: function () {
    var _this = this;
  },
  mounted() {
    const loading = this.$loading({
      lock: true,
      text: '正在加载',
      spinner: 'el-icon-loading',
      background: 'rgba(0, 0, 0, 0.7)'
    });

    const _this = this;
    this.$el.style.setProperty("--heightStyle", document.documentElement.clientHeight + "px");
    this.$bus.$on('changeFilePre', (val) => {
      _this.curFileName = val;
      _this.currentView = "FilePreSeq";
    });

    // 获取cookie查看是否已经登录
    if (this.$cookies.isKey("user")) {
      this.ruleForm = this.$cookies.get("user")
      _this.logincheck(_this.ruleForm.userName, _this.ruleForm.password)
    }

    this.$nextTick(() => {
      loading.close()
    })

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