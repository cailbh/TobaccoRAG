<template>
    <div class="chat-window">
        <!-- 显示聊天消息的容器 -->
        <div>
            <Auxiliary></Auxiliary>
        </div>
        <div class="message-container" id="chat-message-container">
            <div v-for="(message, Mindex) in messages" :key="message.id" class="message">
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
                        <!-- <div class="chatText" v-html="message.text"> -->
                        <div class="chatText" v-if="message.isStream">
                            <div v-html="rawToMarked(message.rawText)"></div>
                        </div>
                        <div class="chatText" v-else>
                            <div v-for="(sentence, index) in message.textWithQuote " @mouseover="quoteOver($event)"
                                @mouseout="quoteOut($event)" @click="quoteClk((message.quote[sentence.quote]))"
                                v-html="rawToMarked(sentence.text + ((sentence.quote == -1) ? '' : quoteHTML(index + 1, sentence.quote + 1)))"
                                class="chatTextLine">
                            </div>
                        </div>
                        <!-- <el-button v-for="( item, index ) in  message.quote " :key="index" type="text"
                            @click="quoteClk(item)">
                            {{ (index + 1) }}
                        </el-button> -->
                        <el-dropdown trigger="click" :hide-on-click="false" v-if="message.quote.length != 0">
                            <el-button type="primary" class="quoteBTN">
                                本次共检索到了{{ message.quote.length }}个文本块
                            </el-button>
                            <el-dropdown-menu slot="dropdown">
                                <el-dropdown-item v-for="(item, index) in message.quote" class="quote_item">
                                    <p @click="quoteClk(item)">
                                        {{ index + 1 }}. 《{{ item.fileName }}》 {{ item.sentence }}
                                    </p>
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </el-dropdown>
                        <div style="display: flex; justify-content: right;">
                            <i style="cursor: pointer;" class="el-icon-warning" :title="'回答的不好'" v-if="message.isbad"
                                :key="message.isbad" @click="notBadAns(Mindex)"></i>
                            <i style="cursor: pointer;" class="el-icon-warning-outline" :title="'回答的不好'"
                                v-else-if="!message.isbad" @click="badAns(Mindex)" :key="message.isbad"></i>
                            <i style="cursor: pointer; margin-left: 10px;" class="el-icon-s-order" :title="'复制回答内容'"
                                v-copy="message.rawText"></i>

                        </div>
                    </el-card>
                </div>
            </div>
        </div>
        <!--输入消息的表单 -->
        <div class=" input-form">
            <searchControl @searchChange="searchChange" @clearHistory="clearHistory">
            </searchControl>

            <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 4 }" placeholder="请输入内容" v-model="inputText"
                @keyup.enter.native="streamQA">
            </el-input>
            <el-button class="subBut" size="mini" @click="streamQA" icon="el-icon-upload2" type="primary" circle>
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
                {
                    id: 1,
                    text: '你好,我有什么可以帮助你的吗？', //marked语法编译过的text
                    isMe: false,
                    quote: [],
                    rawText: "你好,我有什么可以帮助你的吗？",
                    textWithQuote: [
                        {
                            text: "你好,我有什么可以帮助你的吗？",
                            quote: -1 //-1为无索引，其余对对应下标
                        }
                    ],
                    isbad: false
                },
            ],
            searchWay: 1,
            reAsk: false,
            preAns: true,
            isRRF: true,
            isReOrder: true,
            searchWeight: 10,
            ws: "",
            loading: null
        };
    },
    watch: {
        messages(val) {
            // console.log("new message hist", val)
            this.saveHistory()
        },
    },
    created() {
        const _this = this;
        this.username = this.userName
        console.log(this.username)
        this.getHistory()
        this.$nextTick(() => {
            setTimeout(() => {
                _this.scrollToBottom();
                _this.useWebSocket()
            }, 1000);
        });
    },
    methods: {
        quoteClk(val) {
            console.log("quoteClk")
            this.$bus.$emit("quote", val);
        },
        getHistory() {
            const _this = this;
            console.log(_this)
            this.$http
                .post("/api/getHistory", { username: _this.username }, {})
                .then((response) => {
                    console.log("getHistory", response)
                    _this.messages = response.body
                    // }
                    setTimeout(() => {
                        _this.scrollToBottom();
                    }, 1000);
                });
        },
        saveHistory() {
            const _this = this;
            this.$http
                .post("/api/saveHistory", { history: _this.messages, username: _this.username }, {
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
        clearHistory() {
            let _this = this
            this.messages = [
                {
                    id: 1,
                    text: '你好,我有什么可以帮助你的吗？', //marked语法编译过的text
                    isMe: false,
                    quote: [],
                    rawText: "你好,我有什么可以帮助你的吗？",
                    textWithQuote: [
                        {
                            text: "你好,我有什么可以帮助你的吗？",
                            quote: -1 //-1为无索引，其余对对应下标
                        }
                    ],
                    isbad: false
                },
            ]
            this.$nextTick(() => {
                _this.$notify({
                    title: '清空成功',
                    type: 'success',
                    message: '历史记录已清除'
                });
                this.saveHistory()
            })
        },
        submit() {
            const _this = this;
            if (this.inputText.trim()) {
                let questions = _this.inputText;
                // 将我的消息加入hist
                this.messages.push({
                    id: Date.now(),
                    text: this.inputText,
                    isMe: true
                });

                _this.loading = this.$loading({
                    lock: true,
                    text: '大模型正在回答您的问题',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });

                this.inputText = '';
                setTimeout(() => {
                    _this.scrollToBottom();
                }, 1000);
                console.log("reAsk", this.reAsk, "preAns", this.preAns)
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
                        let textWithQuote = data['textWithQuote'];
                        let isbad = false
                        console.log("quote", quote);
                        let markedText = marked(ans)
                        // console.log(markedText)
                        this.messages.push({
                            id: Date.now(),
                            text: markedText,
                            isMe: false,
                            quote: quote,
                            rawText: ans,
                            textWithQuote: textWithQuote,
                            isbad: isbad
                        });

                        _this.loading.close();
                        _this.loading = null

                        setTimeout(() => {
                            _this.scrollToBottom();
                        }, 1000);
                    });
            }
        },
        streamQA() {
            const _this = this;
            if (this.inputText.trim()) {
                let questions = _this.inputText;
                // 将我的消息加入hist
                this.messages.push({
                    id: Date.now(),
                    text: this.inputText,
                    isMe: true
                });

                _this.loading = this.$loading({
                    lock: true,
                    text: '大模型正在回答您的问题',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });

                this.inputText = '';
                setTimeout(() => {
                    _this.scrollToBottom();
                }, 1000);
                let input_data = {
                    questions: questions,
                    reAsk: this.reAsk,
                    preAns: this.preAns,
                    isRRF: this.isRRF,
                    isReOrder: this.isReOrder,
                    searchWay: this.searchWay,
                    searchWeight: this.searchWeight
                }
                this.messages.push({
                    id: Date.now(),
                    text: "",
                    isMe: false,
                    quote: [],
                    rawText: "",
                    textWithQuote: [],
                    isbad: false,
                    isStream: true
                });

                _this.wsSend(JSON.stringify(input_data))

                setTimeout(() => {
                    _this.scrollToBottom();
                }, 1000);
            }

        },
        useWebSocket: function () {
            let _this = this
            _this.ws = new WebSocket('/wss/QA')

            const init = () => {
                bindEvent();
            }

            function bindEvent() {
                _this.ws.addEventListener('open', handleOpen, false);
                _this.ws.addEventListener('error', handleError, false);
                _this.ws.addEventListener('message', handleMessage, false);
                _this.ws.addEventListener('close', handleClose, false);
            }

            function handleOpen(e) {
                console.log("WebSocket open", e);
            }

            function handleClose(e) {
                console.log("WebSocket close", e);
                if (_this.loading) {
                    _this.loading.close();
                    _this.loading = null
                }
            }

            function handleError(e) {
                console.log("WebSocket error", e);
                if (_this.loading) {
                    _this.loading.close();
                    _this.loading = null
                }
            }

            function handleMessage(e) {
                console.log("WebSocket message", e);
                let res = JSON.parse(e.data)
                // console.log(res)
                if (res.isOK != true) {
                    // _this.stream += e.data; // 将接收到的数据赋值给 stream 变量
                    _this.messages.at(-1).rawText += res.message
                    // console.log(e.data)
                    setTimeout(() => {
                        _this.scrollToBottom();
                    }, 1000);
                }
                else {
                    // console.log("ok")
                    _this.messages.pop()

                    let ans = res['answers'];
                    let quote = res['quote'];
                    let textWithQuote = res['textWithQuote'];
                    let isbad = false
                    // console.log("quote", quote);
                    let markedText = marked(ans)
                    // console.log(markedText)
                    _this.messages.push({
                        id: Date.now(),
                        text: markedText,
                        isMe: false,
                        quote: quote,
                        rawText: ans,
                        textWithQuote: textWithQuote,
                        isbad: isbad,
                        isStream: false
                    });
                    if (_this.loading) {
                        _this.loading.close();
                        _this.loading = null
                    }
                    setTimeout(() => {
                        _this.scrollToBottom();
                    }, 1000);
                    // console.log(markedText)
                    // _this.stream += '<br>';
                }
            }

            init();
        },
        wsSend(input) {
            let _this = this
            _this.ws.send(input)
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
                if (val[2].checked[0] == "假设文档嵌入") {
                    this.reAsk = false
                    this.preAns = true
                }
                else {
                    this.reAsk = true
                    this.preAns = false
                }
            }

            this.searchWeight = weight

            console.log(this.isRRF, this.isReOrder)
            // console.log(this.reAsk, this.preAns)
            // console.log(this.searchWay, this.searchWeight)
        },
        scrollToBottom() {
            // 将聊天框拉到最底下
            // 获取设置了滚动属性的div标签
            const chat_message_container = document.getElementById('chat-message-container');
            // 设置滚动的顶点坐标为滚动的总高度
            if (chat_message_container) {
                chat_message_container.scrollTop = chat_message_container.scrollHeight;
                console.log(chat_message_container.scrollTop, chat_message_container.scrollHeight)
            }
        },
        rawToMarked(raw) {
            return marked(raw)
        },
        quoteHTML(index, quote) {
            return `<span class='quoteNum'> ${quote} </span>`
        },
        quoteOver(event) {
            let nowElem = event.currentTarget.firstElementChild
            nowElem.setAttribute("id", "underline")
        },
        quoteOut(event) {
            let nowElem = event.currentTarget.firstElementChild
            nowElem.setAttribute("id", "")
        },
        copyFunc(val) {
            console.log(val)
            this.$notify({
                title: "复制",
                type: 'success',
                message: `复制成功`
            });
        },
        badAns(Mindex) {
            // let _this = this
            this.messages[Mindex].isbad = true
            console.log(this.messages[Mindex])
            this.$nextTick(() => {
                this.$notify({
                    title: "回答",
                    type: 'success',
                    message: `反馈成功`
                });
                this.saveHistory()
            })
        },
        notBadAns(Mindex) {
            // let _this = this
            this.messages[Mindex].isbad = false
            console.log(this.messages[Mindex])
            this.$nextTick(() => {
                console.log("ok")
                this.saveHistory()
            })
        }
    },
    props: ['userName']
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
    overflow-y: scroll;
    height: calc(100% - 110px);
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
<style>
.quoteBTN {
    background-color: #f3f5fc;
    color: #000;
    border: 0;
}

.quoteBTN:hover {
    background-color: #eef0f6;
    color: #000;
}

.quoteBTN:focus {
    background-color: #eef0f6;
    color: #000;
}

.quote_item p {
    text-overflow: ellipsis;
    overflow: hidden;
    word-break: break-all;
    white-space: nowrap;
    width: 20vw;
    margin: 0;
}

.quoteNum {
    /* position: absolute; */
    /* right: 0; */
    position: relative;
    background-color: #e5e7ed;
    width: 14px;
    height: 14px;
    text-align: center;
    line-height: 14px;

    display: inline-block;

    font-size: 10px;
    color: #5e6772;
    /* margin: auto; */
    margin-left: 0;

    cursor: pointer;
    text-decoration: none;
}

.quoteNum:hover {
    background-color: #2E67FA;
    color: #fff;
}

.chatText * {
    max-width: 100%;
}

.chatText li {
    /* display: inline-block; */
    /* flex-wrap: wrap; */
    text-wrap: wrap;
    /* white-space: nowrap; */
    /* display: list-item; */
    /* list-style: circle; */
}

.chatText ul {
    margin: 0;
}

.chatTextLine {
    position: relative;
    display: flex;
    flex-wrap: wrap;
    line-height: 34px;
}

#underline {
    text-decoration: underline dotted;
}
</style>