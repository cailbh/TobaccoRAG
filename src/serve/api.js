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
const filePath = 'D:/Cailibuhong/Tobacco/py/data/杭烟营销中心各类标准文件/'
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
  let readStream = fs.createReadStream(docxUrl, { encoding: null })// 默认null})
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

router.post('/api/fileUpload', (req, res) => {
  const fileName = req.query.file;
  const fileNameOri = fileName.split(".")[0];
  let path = `${filePath}${fileName}`;
  let outpath = `${filePath}/pdf`;
  const pdfPath = `${outpath}/${fileNameOri}.pdf`;

  const command = `start soffice --headless --invisible --convert-to pdf:writer_pdf_Export ${path} --outdir ${outpath}`;

  child_process.exec(command, { encoding: 'buffer' }, (error, stdout, stderr) => {
    if (error) {
      console.log(error.stack);
      console.log('Error code: ' + error.code);
      console.log('Signal received: ' + error.signal);
      res.status(500).send('File conversion failed.');
    } else {
      // 确保文件已创建
      fs.access(pdfPath, fs.constants.F_OK, (err) => {
        if (err) {
          console.log('Converted file does not exist:', pdfPath);
          res.status(500).send('File conversion failed.');
        } else {
          // 允许跨域
          res.header("Access-Control-Allow-Origin", "*");

          // 设置请求头
          res.writeHead(200, {
            'Content-Type': 'application/pdf;charset=utf-8',
          });

          // 创建可读流
          let readStream = fs.createReadStream(pdfPath);
          // 将读取的结果以管道pipe流的方式返回给前端
          readStream.pipe(res);
        }
      });
    }
  });
});
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