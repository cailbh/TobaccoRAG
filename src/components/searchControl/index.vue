<!--  -->
<template>
    <div class="searchControl" style="width: 100%; position: relative;">
        <!-- 打开按钮 -->
        <el-button type="text" @click="dialog = true">设置文件检索策略</el-button>

        <el-button type="text" @click="clearHistory" style="position: absolute; right: 0%; top: 0%;">清空历史记录</el-button>
        <!-- 窗口主体 -->
        <el-dialog title="设置文件检索策略" :visible.sync="dialog" :append-to-body="true" :modal-append-to-body="false"
            @close="cancelChange" style="">

            <div style="display: flex; position: relative; width: 100%;height: 150px;justify-content: space-around;">
                <div style="width: 40%;height: 100%; position: relative;">
                    <div class="title" style="height: 16%;">
                        检索度量值
                    </div>

                    <el-radio-group v-model="controlList[0].checked">
                        <div class="title2">&nbsp;&nbsp;关键词</div>
                        <el-radio :label="controlList[0].content[0]">{{ controlList[0].content[0] }}</el-radio>
                        <div class="title2">&nbsp;&nbsp;相似度</div>
                        <el-radio :label="controlList[0].content[1]">{{ controlList[0].content[1] }}</el-radio>
                        <el-radio :label="controlList[0].content[2]">{{ controlList[0].content[2] }}</el-radio>
                    </el-radio-group>
                </div>
                <div style="width: 45%;height: 100%; position: relative;">
                    <div class="title" style="height: 16%;">优化方法</div>
                    <div style="width: 100%;height: 42%; position: relative;">
                        <div class="title2">&nbsp;&nbsp;排列优化</div>
                        <el-checkbox-group v-model="controlList[1].checked">
                            <el-checkbox :label="controlList[1].content[0]"></el-checkbox>
                            <el-checkbox :label="controlList[1].content[1]"></el-checkbox>
                        </el-checkbox-group>
                    </div>
                    <div style="width: 100%;height: 42%; position: relative;">
                        <div class="title2">&nbsp;&nbsp;问答优化</div>
                        <el-checkbox-group v-model="controlList[2].checked">
                            <el-checkbox :label="controlList[2].content[0]"></el-checkbox>
                            <el-checkbox :label="controlList[2].content[1]"></el-checkbox>
                        </el-checkbox-group>
                    </div>
                </div>
            </div>


            <div class="block">
                <span class="title">检索强度</span>
                <el-slider v-model="weight" show-input :min="1" :max="10" :step="1">
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
            controlList: [
                {
                    content: ["关键词匹配", "余弦相似度度量", "欧氏距离度量"],
                    checked: "余弦相似度度量",
                    preChecked: "余弦相似度度量",
                },
                {
                    content: ["混合检索", "是否重排"],
                    checked: ["混合检索", "是否重排"],
                    preChecked: ["混合检索", "是否重排"],
                },
                {
                    content: ["优化表述", "假设文档嵌入"],
                    checked: ["假设文档嵌入"],
                    preChecked: ["假设文档嵌入"],
                }
            ],
            weight: 10,
            preWeight: 10
        };
    },
    methods: {
        cancelChange() {
            // 关闭表单
            this.controlList.map(d => {
                d.checked = d.preChecked
            })
            this.weight = this.preWeight

            this.dialog = false;
        },
        outputChange() {
            this.controlList.map(d => {
                d.preChecked = d.checked
            })
            this.preWeight = this.weight

            //发送到父元素
            this.$emit("searchChange", this.controlList, this.weight)

            this.dialog = false;
        },
        clearHistory() {
            console.log("clear Hist")
            //发送到父元素
            this.$emit("clearHistory")
        }
    },
    watch: {
        controlList: {
            handler(newval, oldval) {
                this.weight = 10
            },
            deep: true,
            immediate: true
        }
    },
    mounted() {
        // 初始化
        this.outputChange()
    }
}
</script>

<style scoped>
@import './index.css';
</style>
