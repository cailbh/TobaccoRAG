<template>
    <div class="chat-window">
        <!-- 显示聊天消息的容器 -->
        <div>
            <Auxiliary></Auxiliary>
        </div>
        <div class="message-container">
            <div v-for="message in messages" :key="message.id" class="message">
                <div v-if="message.isMe" class="isMe">
                    <div class="chatHead">
                        <div class="userIcon"></div>
                        <div class="textName">You</div>
                    </div>
                    <el-card class="box-card">
                        <!-- <div slot="header" class="clearfix">
                            <span class="isMeText"><el-avatar> user </el-avatar></span>
                            <span v-else><el-avatar icon="el-icon-user-solid"></el-avatar>GPT</span>
                            <el-button style="float: right; padding: 3px 0" type="text">123</el-button>
                        </div> -->
                        <div class="chatText">{{ message.text }}</div>
                    </el-card>
                </div>
                <div v-else class="notMe">
                    <div class="chatHead">
                        <div class="chatIcon"></div>
                        <div class="textName">烟草智能AI</div>
                    </div>
                    <el-card class="box-card">
                        <!-- <div slot="header" class="clearfix">
                            <span class="isMe"><el-avatar> user </el-avatar></span>
                            <span><el-avatar icon="el-icon-user-solid"></el-avatar>GPT</span>
                            <el-button style="float: right; padding: 3px 0" type="text"></el-button>
                        </div> -->
                        <div class="chatText" v-html="message.text"></div>
                        <el-button v-for="(item, index) in message.quote" :key="index" type="text"
                            @click="quoteClk(item)">{{ (index + 1) }}</el-button>
                    </el-card>
                </div>
            </div>
        </div>
        <!-- 输入消息的表单 -->
        <div class="input-form">
            <searchControl @searchChange="searchChange"></searchControl>

            <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 4 }" placeholder="请输入内容" v-model="inputText">
            </el-input>
            <el-button class="subBut" size="mini" @click="submit" icon="el-icon-upload2" type="primary" circle>
            </el-button>
        </div>
    </div>
</template>

<script>
import Auxiliary from '@/components/Auxiliary/index.vue';
import searchControl from '@/components/searchControl/index.vue';
import { tree } from 'd3';
// markdown库处理回复的聊天
import { marked } from 'marked';
import { f } from 'pdfjs-dist/legacy/build/pdf.worker';

export default {
    components: { Auxiliary, searchControl },
    data() {
        return {
            inputText: '',
            messages: [
                { id: 1, text: '你好,我有什么可以帮助你的吗？', isMe: false, quote: [] },
            ],
            searchWay: 1,
            reAsk: false,
            preAns: false,
            isRRF: false,
            isReOrder: false,
            searchWeight: 3
        };
    }, 
     watch: {
        messages(val) {
            this.saveHistory()
        },
    },
    created() {
        const _this = this;
        this.getHistory()
        this.$nextTick(() => {
        });
    },
    methods: {
        quoteClk(val) {
            this.$bus.$emit("quote", val);
        },
        getHistory(){
            const _this = this;
            this.$http
                .get("/api/getHistory", { params: {} }, {})
                .then((response) => {
                    console.log("getHistory",response)
                    _this.messages = response.body
                    // }
                });
        },
        saveHistory(){
            const _this = this;
            this.$http
                .post("/api/saveHistory", { history: _this.messages,}, {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then((res) => {
                    // _this.$message({
                    //   message: '成功建立向量数据库',
                    //   type: 'success'
                    // });

                    // _this.$notify({
                    //     title: '保存成功',
                    //     type: 'success',
                    //     message: '当前数据已添加至知识库'
                    // });
                });
        },
        submit() {
            const _this = this;
            if (this.inputText.trim()) {
                let questions = _this.inputText;
                this.messages.push({ id: Date.now(), text: this.inputText, isMe: true });
                this.inputText = '';
                this.$http
                    .post("/api/QA", {
                        questions: questions,
                        reAsk: this.reAsk,
                        preAns: this.preAns,
                        isRRF: this.isRRF,
                        isReOrder: this.isReOrder,
                        searchWay: this.searchWay,
                        searchWeight: this.searchWeight
                    }, {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then((res) => {
                        console.log(res)
                        let data = res.body;
                        let ans = data['answers'];
                        let quote = data['quote'];
                        console.log("quote", quote);
                        let markedText = marked(ans)
                        // console.log(markedText)
                        this.messages.push({ id: Date.now(), text: markedText, isMe: false, quote: quote });
                    });
            }
        },
        searchChange(val, weight) {
            // console.log(val)

            let wayList = ["关键词匹配", "余弦相似度度量", "欧氏距离度量"]
            this.searchWay = wayList.findIndex(i => i == val[0].checked)

            if (val[1].checked.length == 0) {
                this.isReOrder = false
                this.isRRF = false
            }
            else if (val[1].checked.length == 2) {
                this.isRRF = true
                this.isReOrder = true
            }
            else {
                if (val[1].checked[0] == "混合检索") {
                    this.isRRF = true
                    this.isReOrder = false
                }
                else {
                    this.isReOrder = true
                    this.isRRF = false
                }
            }


            if (val[2].checked.length == 0) {
                this.reAsk = false
                this.preAns = false
            }
            else if (val[2].checked.length == 2) {
                this.reAsk = true
                this.preAns = true
            }
            else {
                if (val[2].checked[0] == "优化提问") {
                    this.reAsk = true
                    this.preAns = false
                }
                else {
                    this.reAsk = false
                    this.preAns = true
                }
            }

            this.searchWeight = weight

            console.log(this.isRRF, this.isReOrder)
            // console.log(this.reAsk, this.preAns)
            // console.log(this.searchWay, this.searchWeight)
        }
    },
};
</script>

<style scoped>
.subBut {
    position: absolute;
    right: 20px;
    bottom: 0px;
}

.isMe {
    width: 50%;
    float: right;
    margin: 15px 200px;
}

.chatText {
    width: 100%;
    word-wrap: break-word;
    white-space: pre-wrap; /* 保留空格和换行符 */
    font-family: inherit; /* 保持字体一致 */
    font-size: inherit; /* 保持字体大小一致 */
    line-height: inherit; /* 保持行高一致 */
}

.isMeText {
    float: right;
}

.notMe .textName {
    float: left;
    line-height: 300%;
    margin-left: 10px;
    color: rgb(69, 71, 70);
}

.isMe .textName {
    float: right;
    line-height: 300%;
    margin-right: 10px;
    color: rgb(69, 71, 70);
}

.notMe .chatHead {
    float: left;
    line-height: 100%;
}

.isMe .chatHead {
    float: right;
}

.userIcon {
    float: right;
    width: 50px;
    height: 50px;
    background-image: url("~@/assets/imgs/userIcon.png");
    background-size: cover;
}

.chatIcon {
    float: left;
    width: 50px;
    height: 50px;
    background-image: url("~@/assets/imgs/gptIcon.png");
    background-size: cover;
}

.notMe {
    width: 60%;
    float: left;
    margin: 15px 200px;
}

.isMe .notMe .el-card {
    /* background: aqua; */
}

.chat-window {
    /* max-width: 400px;
    margin: 0 auto;
    overflow: hidden;
    overflow-y: auto; */
    height: 100%;
    /* scrollbar-width: none; */
}

.message-container {
    margin-bottom: 10px;
    max-width: 100%;
    margin: 0 auto;
    overflow: hidden;
    overflow-y: auto;
    height: calc(100% - 80px);
    scrollbar-width: none;
    background-image: url('~@/assets/imgs/chatBack.png');
    background-size: cover;
}

.message {
    padding: 5px;
    margin-bottom: 5px;
}

.notMe .el-card {
    background-color: rgba(255, 255, 255, 1);
    border: 0px;
    border-top-right-radius: 30px;
    border-bottom-left-radius: 30px;
    border-bottom-right-radius: 30px;
    margin-left: 120px;
    width: 80%;
    float: left;
    /* box-shadow: 0 12px 0px 0 rgba(0,0,0,.1); */
}

.isMe .el-card {
    background-color: rgba(10, 105, 173, 1);
    border: 0px;
    border-top-left-radius: 30px;
    border-bottom-left-radius: 30px;
    border-bottom-right-radius: 30px;

    margin-right: 120px;
    width: 80%;

    color: aliceblue;
    float: right;
    /* box-shadow: 0 24px 10px 0 rgba(0,0,0,.1); */
}

/* .clearfix{
    background-color: rgba(100, 1, 1,1) !important;
    border: 0px;
    box-shadow: 0 0px 0px 0 rgba(0,0,0,.1);
} */

.message-text {
    padding: 10px;
    border-radius: 5px;
}

.input-form {
    position: absolute;
    bottom: 10px;
    height: 80px;
    /* margin: 0px 40px; */
    width: calc(100% - 0px);
}

.mine {
    background-color: lightblue;
}
</style>