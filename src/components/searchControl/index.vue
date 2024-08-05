<!--  -->
<template>
    <div class="searchControl" style="width: 120px;">
        <el-button type="text" @click="dialog = true">设置文件检索策略</el-button>

        <el-dialog title="设置文件检索策略" :visible.sync="dialog" :append-to-body="true" :modal-append-to-body="false"
            @close="cancelChange">
            <el-radio-group v-model="checkedSearch">
                <el-radio v-for="(search, index) in searchList" :label="search">{{ search }}</el-radio>
            </el-radio-group>

            <div class="block">
                <span class="title">设置检索强度</span>
                <el-slider v-model="weight" show-input :min="1" :max="10" :step="1" v-if="checkedSearch == '关键词匹配'">
                </el-slider>
                <el-slider v-model="weight" show-input :min="1" :max="10" :step="0.1" v-else>
                </el-slider>
            </div>

            <span slot="footer" class="dialog-footer">
                <el-button @click="cancelChange">取 消</el-button>
                <el-button type="primary" @click="outputChange">确 定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
export default {
    data() {
        return {
            dialog: false,
            searchList: ["关键词匹配", "相似度度量", "欧氏距离度量", "大模型优化提问", "预回答检索"],
            checkedSearch: "相似度度量",
            preChecked: "相似度度量",
            weight: 3,
            preWeight: 3
        };
    },
    methods: {
        cancelChange() {
            // 关闭表单
            this.checkedSearch = this.preChecked;
            this.weight = this.preWeight

            this.dialog = false;
        },
        outputChange() {
            this.preChecked = this.checkedSearch;
            this.preWeight = this.weight

            //发送到父元素
            this.$emit("searchChange", this.checkedSearch, this.weight)

            this.dialog = false;
        },
    },
    watch: {
        checkedSearch: {
            handler(newval, oldval) {
                this.weight = 3
            },
            deep: true,
            immediate: true
        }
    }
}
</script>

<style scoped>
@import './index.css';
</style>
