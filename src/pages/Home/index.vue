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
          科研战略管理系统
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
      <div class="menuDiv">
        <el-menu default-active="3" class="el-menu" @open="handleOpen" @close="handleClose" @select="select">
          <el-submenu index="1">
            <template slot="title">
              <i class="el-icon-user"></i>
              <span slot="title">用户管理</span>
            </template>
            <!-- <el-menu-item index="1-1"></el-menu-item> -->
          </el-submenu>
          <el-menu-item index="2">
            <template slot="title">
              <i class="el-icon-upload"></i>
              <span slot="title" class="navTxt">数据底数</span>
            </template>
          </el-menu-item>
          <el-submenu index="3">
            <template slot="title">
              <i class="el-icon-data-analysis"></i>
              <span slot="title">可视分析</span>
            </template>
            <el-menu-item index="3-1">态势分析</el-menu-item>
          </el-submenu>
          <!-- <el-menu-item index="4">智能图谱</el-menu-item> -->
          <el-menu-item index="4">
            <template slot="title">
              <i class="el-icon-location"></i>
              <span slot="title" class="navTxt">智能图谱</span>
            </template>
          </el-menu-item>
        </el-menu>
      </div>
      <div id="contentBody">
        <component :is="currentView"></component>
      </div>
    </div>
  </div>
</template>

<script>
import Head from '@/components/Header/index.vue'
export default {
  components: { Head },
  /* eslint-disable no-unused-vars */
  data() {
    return {
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
    handleOpen(key, keyPath) {
      console.log(key)
      const _this = this;
      if (key == '2') {
        _this.currentView = "DataView";
      }
      if (key == '4') {
        _this.currentView = "Kg4Qa";
      }
    },
    select(key, keyPath) {
      console.log("key", key)
      const _this = this;
      _this.currentView = ""
      if (key == '3-1') {
        _this.currentView = "SituAnaly"
      }
      if (key == '2') {
        _this.currentView = "DataView";
      }
      if (key == '4') {
        _this.currentView = "Kg4Qa"
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
    this.$bus.$emit("colorMap", _this.mLigntcolor);
  },
  beforeDestroy() {
    clearTimeout(this.timer);
  }
};
</script>

<style>
@import './index.css';
</style>