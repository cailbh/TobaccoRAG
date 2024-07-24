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
                        <div class="chatText">{{ message.text }}</div> 
                        <el-button v-for="(item, index) in message.quote" :key="index" type="text" @click="quoteClk(item)">{{ (index+1) }}</el-button>
                    </el-card>
                </div>
            </div>
        </div>
        <!-- 输入消息的表单 -->
        <div class="input-form">
            <el-input type="textarea" :autosize="{ minRows: 4, maxRows: 4 }" placeholder="请输入内容" v-model="inputText">
            </el-input>
            <el-button class="subBut" size="mini" @click="submit" icon="el-icon-upload2" type="primary"
                circle>
            </el-button>
        </div>
    </div>
</template>

<script>
import Auxiliary from '@/components/Auxiliary/index.vue';
export default { 
    components: {Auxiliary},
    data() {
        return {
            inputText: '',
            messages: [
                { id: 1, text: '你好,我有什么可以帮助你的吗？', isMe: false,quote:[]},
            ],
        };
    },
    methods: {
        quoteClk(val){
            this.$bus.$emit("quote",val);
        },
        submit() {
            const _this = this;
            if (this.inputText.trim()) {
                let questions = _this.inputText;
                this.messages.push({ id: Date.now(), text: this.inputText, isMe: true });
                this.inputText = ''; 
                this.$http
                    .post("/api/QA", { questions: questions,}, {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then((res) => {
                        console.log(res.body)
                        let data = res.body;
                        let ans = data['answers'];
                        let quote = data['quote'];
                        console.log("quote",quote);
                        this.messages.push({ id: Date.now(), text: ans, isMe: false, quote:quote });
                    });
            }
        },
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