// Schema、Model、Entity或者Documents的关系:Schema生成Model，Model创造Entity，Model和Entity都可对数据库操作造成影响，但Model比Entity更具操作性。
const mongoose = require('mongoose');
// 连接数据库 
mongoose.set('strictQuery', true);
mongoose.connect('mongodb://127.0.0.1:27017/FMS');

// 为这次连接绑定事件
const db = mongoose.connection;
db.once('error', () => console.log('Mongo connection error'));
db.once('open', () => console.log('Mongo connection successed'));
/************** 定义模式Schema **************/
const projectSchema = mongoose.Schema({
    name: { type: String, required: true },
    unit: { type: String, required: true },
    unit2: { type: String, required: true },
    unit3: { type: String, required: true },
    unit4: { type: String, required: true },
    describe: { type: String, required: true },
    year: { type: String, required: true },
    yearDue: { type: String, required: true },
    funds: { type: String, required: true },
    level: { type: String, required: true },
    cat1: { type: String, required: true },
    cat2: { type: String, required: true },
    method: { type: String, required: true },
    tech: { type: String, required: true },
    space: { type: String, required: true },
    space2: { type: String, required: true },
    version: { type: String, required: true },
    resPerson: { type: String, required: true },
    person: { type: String, required: true },
    city: { type: String, required: true },
    field: { type: String, required: true },
    techLevel1: { type: String, required: true },
    techLevel2: { type: String, required: true },
    part: { type: String, required: true },
    aspect: { type: String, required: true },
    achForm: { type: String, required: true },
    result: { type: String, required: true }
});
const wordsSchema = mongoose.Schema({
    id: { type: String, required: true },
    words: { type: String, required: true }
});

/************** 定义模型Model **************/
const Models = {
    Project: mongoose.model('Project', projectSchema,'project'),
    Words: mongoose.model('Words', wordsSchema,'words'),
    // File: mongoose.model('files', filesSchema,'testFiles'),
}

module.exports = Models;
