import * as d3 from 'd3'

function arraysContainSameElements(array1, array2) {
  // 将数组转换为集合
  const set1 = new Set(array1);
  const set2 = new Set(array2);

  // 如果集合大小不同，直接返回 false
  if (set1.size !== set2.size) {
      return false;
  }

  // 比较每个元素
  for (let item of set1) {
      if (!set2.has(item)) {
          return false;
      }
  }

  // 如果所有元素都相同，则返回 true
  return true;
}

function arraysEqual(array1, array2) {
  // 如果数组长度不同，则直接返回 false
  if (array1.length !== array2.length) {
      return false;
  }

  // 比较每个元素
  for (let i = 0; i < array1.length; i++) {
      if (array1[i] !== array2[i]) {
          return false;
      }
  }

  // 如果所有元素都相同，则返回 true
  return true;
}

function calcTriangle(x, y, r) {
  let areas = [[x - r * (Math.sqrt(3)) / 2, y + r / 2], [x + r * (Math.sqrt(3)) / 2, y + r / 2], [x, y - r]];
  return areas;
}

function calcRect(x, y, r) {
  let areas = [[x - r / 2, y - r / 2], [x + r / 2, y - r / 2], [x + r / 2, y + r / 2], [x - r / 2, y + r / 2]];
  return areas;
}

function drawTxt(svg, tx, ty, txts, fill, size, idName, anchor = '') {
  let txt = svg.append("text")
    .attr("y", ty)
    .attr("x", tx)
    .attr("id", idName)
    .attr("fill", fill)
    .attr("font-size", size)
    .style("text-anchor", anchor)
    .text(txts)

  let textArea = document.getElementById(idName).getBBox();
  return [txt, textArea];
  // .style("text-anchor", anchor)//"middle")
  // .attr("transform", `rotate(${roat} ${tx} ${ty})`);
}

function  drawTxts(svg, x, y, width, txts, fill, fontsize = 12, idN,className) {
  let tx = x;
  let ty = y;
  let preWidth = 0;
  let preIdN = 0;
  let pretext = '';
  txts = txts.split(" ");
  let g = svg.append("g")
      .attr("id", `${idN}`)
  for (let t = 0; t < txts.length; t++) {
    pretext +=" "+ txts[t];
    let txt = g.append("text")
      .attr("y", ty)
      .attr("x", tx)
      .attr('class', className)
      .attr("id", `${idN}_${t}`)
      .attr("fill", fill)
      .attr("font-size", fontsize)
      .style("text-anchor", "middle")
      .text(pretext)
    let textWidth = document.getElementById(`${idN}_${t}`).getBBox().width;
    if((textWidth>width)||(t==txts.length -1)){
      pretext = '';
      tx = x;
      ty += 25;
    }
    else{
      txt.remove()
    }
    preWidth += textWidth;
  }
}

function drawLine(svg, path, stroke, width, stroke_dasharray = "0", idName, className) {
  let line = svg.append('path')
    .attr('d', path.toString())
    .attr('stroke', stroke)
    .attr('class', className)
    .attr('id', idName)
    .attr("stroke-dasharray", stroke_dasharray)
    .attr('stroke-width', width)
    .attr('fill', 'none')
  return line;
}
function drawCircle(svg, x, y, r, fill, opacity, stroke, width, className = 'circle', idName) {
  let circle = svg.append("circle")
    .attr("id", idName)
    .attr("class", className)
    .attr("opacity", opacity)
    .attr("cx", x)
    .attr("cy", y)
    .attr("r", r)
    .attr('stroke', stroke)
    .attr('stroke-width', width)
    .attr("fill", fill)
  return circle;
}
function hasDuplicates(arr1, arr2) {
  for (let i = 0; i < arr1.length; i++) {
    for (let j = 0; j < arr2.length; j++) {
      if (arr1[i] === arr2[j]) {
        return true;
      }
    }
  }
  return false;
}
function drawImage(svg, w, h,x,y, url, idName,className) {
  d3.select(`#${idName}`).remove();
  let img = svg.append("image")
  .attr("class", className)
  .attr("id", idName)
  .attr("width", w)
  .attr("height", h)
  
  .attr("x", x-w/2)
  .attr("y", y-h/2)
  // .attr("transform", "translate(" + x + "," + y + ")")
  .attr("xlink:href", url);
  return img;
}
function drawPolygon(svg, points, idName, strokeWidth, stroke, fill,className) {
  d3.select(`#${idName}`).remove();
  let polygon = svg.append("polygon")
    .attr("points", points)
    .attr("id", idName)
    .attr("class", className)
    .attr("stroke-linejoin", "round")
    .attr("stroke-width", strokeWidth)
    .attr("fill", fill)
    .attr("stroke", stroke)
  return polygon;
}
function transitionSvg(time,temp, x, y, w, h, fill, stroke, opacity, type) {
  if (type == 'rect') {
    temp.transition()  // 开始执行动画
      .duration(time)     // 设置动画持续时间
      .attr("x", x)
      .attr("y", y)
      .attr("width", w)
      .attr("height", h)
      .attr("fill", fill)
      .attr("opacity", opacity)
      .attr("stroke", stroke)
  }
}
function drawRect(svg, x, y, w, h, rx, fill, strokeWidth, stroke, opacity, idName, className, strokeDasharray = '0') {
  d3.select(`#${idName}`).remove();
  let rect = svg.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("id", idName)
    .attr("class", className)
    .attr("opacity", opacity)
    .attr("fill", fill)
    .attr("rx", rx)
    .attr("stroke", stroke)
    .attr("stroke-width", strokeWidth)
    .attr("stroke-opacity", 1)
    .attr("stroke-dasharray", strokeDasharray)
  return rect;
}
function drawArc(svg, x, y, arcPath, stroke, fill, className, idName, stroke_dasharray = "0", width = 3) {
  d3.select(`#${idName}`).remove();
  let arc = svg.append("path")
    .attr("d", arcPath)
    .attr("class", className)
    .attr("id", idName)
    .attr("transform", "translate(" + x + "," + y + ")")
    .attr("stroke", stroke)
    .attr('stroke-width', width)
    .attr("stroke-dasharray", stroke_dasharray)
    .attr("stroke-linejoin", "round")
    .attr("fill", fill);
  return arc;
}

function sleep(delay){
  return new Promise(res=>setTimeout(res,delay));
};

function time2seconds(time) {
  let lst = time.split(":");
  let h = lst[0];
  let m = lst[1];
  let s = lst[2];
  return parseInt(h) * 3600 + parseInt(m) * 60 + parseInt(s);
}
function getVideoCanvas(idName) {
  var player = document.getElementById(idName);   //获取video的Dom节点
  player.setAttribute("crossOrigin", "anonymous");  //添加srossOrigin属性，解决跨域问题
  var canvas = document.createElement("canvas");
  canvas.width = player.clientWidth;
  canvas.height = player.clientHeight;
  // canvas = canvas.getContext("2d")
  canvas.getContext("2d").drawImage(player, 0, 0, canvas.width, canvas.height);//截
  return canvas;
}

function time2seconds2(time) {
  let lst = time.split(".");
  let m = lst[0];
  let s = lst[1];
  return parseInt(m) * 60 + parseInt(s);
}
function seconds2time(seconds,t=0) {
  let m = Math.floor(seconds / 60);
  let s = seconds % 60;
  let h = Math.floor(m / 60);
  if (m < 10) m = '0' + m;
  if (h < 10) h = '0' + h;
  if (s < 10) s = '0' + s;
  if(t==1){
    return m + ":" + s;
  }
  return h + ":" + m + ":" + s;
}

function deepClone(obj) {
  var objClone = JSON.parse(JSON.stringify(obj));
  return objClone;
}
function getRgbValue(str) {
  let reg = /^(rgb|RGB)/;
  if (!reg.test(str)) { return; }
  var arr = str.slice(4, str.length - 1).split(",")
  return arr;
}
function rgb2rgba(str){//加深
  let reg = /^(rgb|RGB)/;
  if (!reg.test(str)) { return; };
  let a = 0.8;//加深或加亮
  let BGcolur = 1;  
  var arr = str.slice(4, str.length - 1).split(",")
  var r = BGcolur * (1 - a) + arr[0] * a;  
  var g = BGcolur * (1 - a) + arr[1] * a;  
  var b = BGcolur * (1 - a) + arr[2] * a;  
  return `rgb(${r},${g},${b})`;
}

function getUniqueValues(arr, key) {
  const uniqueValuesSet = new Set();
  arr.forEach(obj => {
    if (obj.hasOwnProperty(key)) {
      uniqueValuesSet.add(obj[key]);
    }
  });
  return Array.from(uniqueValuesSet).sort((a, b) => {
    // 如果值是数字字符串，将它们转换为数字进行比较
    if (!isNaN(a) && !isNaN(b)) {
      return Number(a) - Number(b);
    }
    // 否则按字典顺序排序
    return b.localeCompare(a);
  });
}

export default {
  getUniqueValues:(arr, key)=>{
    return getUniqueValues(arr, key);
  },
  deepClone: (obj) => { return deepClone(obj); },
  arraysEqual:(array1, array2)=>{
    return arraysEqual(array1, array2);
  },
  arraysContainSameElements:(array1, array2) =>{
    return arraysContainSameElements(array1, array2);
  },
  time2seconds: (time) => {
    return time2seconds(time);
  },
  time2seconds2: (time) => {
    return time2seconds2(time);
  },
  seconds2time: (seconds,t) => {
    return seconds2time(seconds,t);
  },
  calcTriangle: (x, y, r) => {
    return calcTriangle(x, y, r);
  },
  getRgbValue: (str) => {
    return getRgbValue(str);
  },
  drawRect: (svg, x, y, w, h, rx, fill, strokeWidth, stroke, opacity, idName, className, strokeDasharray) => {
    return drawRect(svg, x, y, w, h, rx, fill, strokeWidth, stroke, opacity, idName, className, strokeDasharray)
  },
  getVideoCanvas: (idName) => {
    return getVideoCanvas(idName);
  },
  drawTxt: (svg, tx, ty, txts, fill, size, idName,anchor) => {
    return drawTxt(svg, tx, ty, txts, fill, size, idName,anchor);
  },
  drawTxts: (svg, x, y, width, txts, fill, fontsize, idN,className='texts')=>{
    return  drawTxts(svg, x, y, width, txts, fill, fontsize, idN,className);
  },
  drawCircle: (svg, x, y, r, fill, opacity, stroke, width, className, idName) => {
    return drawCircle(svg, x, y, r, fill, opacity, stroke, width, className, idName);
  },
  drawPolygon: (svg, points, idName, strokeWidth, stroke, fill,className="polygon") => {
    return drawPolygon(svg, points, idName, strokeWidth, stroke, fill,className);
  },
  drawArc: (svg, x, y, arcPath, stroke, fill, className, idName, stroke_dasharray, width) => {
    return drawArc(svg, x, y, arcPath, stroke, fill, className, idName, stroke_dasharray, width);
  },
  drawLine: (svg, path, stroke, width, stroke_dasharray, idName, className) => {
    return drawLine(svg, path, stroke, width, stroke_dasharray, idName, className);
  },
  calcRect: (x, y, r) => {
    return calcRect(x, y, r);
  },
  hasDuplicates: (arr1, arr2) => {
    return hasDuplicates(arr1, arr2);
  },
  rgb2rgba:(rgb)=>{
    return rgb2rgba(rgb);
  },
  drawImage:(svg, w, h,x,y, url, idName,className)=>{
    return drawImage(svg, w, h,x,y, url, idName,className);
  },
  sleep:(d)=>{
    return sleep(d);
  },
  transitionSvg:(time,temp, x, y, w, h, fill, stroke, opacity, type)=>{
    return transitionSvg(time,temp, x, y, w, h, fill, stroke, opacity, type);
  }
}