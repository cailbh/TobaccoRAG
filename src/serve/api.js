/* eslint-disable no-unused-vars */
"use strict";
const models = require('./db');
const express = require('express');
const router = express.Router();

const child_process = require('child_process');
const iconv = require('iconv-lite');



// / 引入文件模块 
const fs = require("fs");
var encoding = 'cp936';
var binaryEncoding = 'binary';
// 获取具体文件
router.get('/api/file/getDoc', (req, res) => {
    let fileName = req.query.fileName;
    let path = req.query.path;
    // 假设我们的word文档文件就存放在这个doc目录里面
    // let docxUrl = `D:/Work/YanCao/jg/fileData/${fileName}.docx`
    let docxUrl = `${path}/${fileName}.docx`
  
    // 允许跨域
    res.header("Access-Control-Allow-Origin", "*");
  
    // 设置请求头
    res.writeHead(200, {
      // 指定文件类型为docx
      'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document;charset=utf-8',
    })
  
    //创建可读流
    let readStream = fs.createReadStream(docxUrl,{encoding: null})// 默认null})
    // 将读取的结果以管道pipe流的方式返回给前端
    readStream.pipe(res);
  
  })

router.get('/api/project/getData', async (req, res) => {

  try {
    const posts = await models.Project.find({});
    // console.log(posts);
    res.send(posts);
  } catch (err) {
    console.log(err);
  }
});

router.post('/api/wordCloud/JieBa', (req, res) => {
  let words = req.body.params.words;
  let indexStr = ` ${words}`;
  process.env.LANG = 'zh_CN.GBK';
  // models.Words.updateOne({ "id": "this" }, { $set: { words: words } }).then(result => {
    var workerProcess = child_process.exec(`conda activate LLM &&  python py/fc.py ${indexStr}`, { encoding: 'buffer' }, function (error, stdout, stderr) {
      if (error) {
        console.log(error.stack);
        console.log('Error code: ' + error.code);
        console.log('Signal received: ' + error.signal);
      } else {
        console.log(iconv.decode(stdout, 'cp936'));
        res.send(eval("(" + (iconv.decode(stdout, 'cp936')).replace(/\n/g, '') + ")"))   //这里要eval一下，然后在客户端才能eval将字符串转化为json数组
      }
    });
      workerProcess.on('exit', function (code) {
        console.log('子进程已退出，退出码 ' + code);
      });
  // }
  // ).catch(error => {
  //   console.error('更新时发生错误:', error);
  //   res.send(error)
  // });//

  // res.send('{"技术领域": ["人工智能", "数据安全", "能源管理"],"关键技术": ["异构资源调度", "GPU自动适配", "RDMA网络技术", "算力管理优化", "AI任务切分与调度"]}')
})
// router.get('/api/project/getData', (req, res) => {
//     // 通过模型去查找数据库
//     models.Project.find((err, data) => {
//         if (err) {
//             res.send(err);
//         } else {

//             res.send(data);
//         }
//     });
// });

module.exports = router;