const xlsx = require('xlsx');
const fs = require('fs');
const neo4j = require('neo4j-driver');
const cal_layout=require("./layout")
// 读取 Excel 文件
const filePath = 'D:\\zy\\kg.xlsx'; // 替换为你的 Excel 文件路径
const workbook = xlsx.readFile(filePath);
const sheetName = workbook.SheetNames[0];
const sheet = workbook.Sheets[sheetName];

// 解析 Excel 数据
const rows = xlsx.utils.sheet_to_json(sheet, { header: 1 });

const cloumnum=26;//表头列数
let namefx={
    0:"项目名称",
    1:"申报单位",
    2:"申报单位",
    3:"申报单位",
    4:"申报单位",
    5:"用途及总要求",
    6:"计划年度",
    7:"研究周期",
    8:"总概算",
    9:"重要程度",
    10:"一级类别",
    11:"二级类别",
    12:"项目方法",
    13:"项目关键技术",
    14:"空间",
    15:"对象",
    16:"版本号",
    17:"主持人及联系方式",
    18:"团队主要骨干",
    19:"建设地点",
    20:"领域",
    21:"一级技术",
    22:"二级技术",
    23:"两个部分",
    24:"十个方面",
    25:"成果形式",
    26:"执行结果"
}

let heads=["name","unit","unit","unit","unit","describe","year","yearDue","funds","level","cat1","cat2","method","tech",
    "space","space2","version","resPerson","person","city","field","techLevel1","techLevel2","part","aspect","achForm","result"
]
let head2name={};

for(let i=0;i<heads.length;i++){
    head2name[heads[i]]=namefx[i];
}
let showrelation=[0,1,2,3,4,6,9,10,11,14,15,20,21,22,24,25];
let showlist={};
for(let i=0;i<=cloumnum;i++){
    let r=namefx[i];
    showlist[r]=showrelation.indexOf(i)>=0?true:false;
}
// 创建 Neo4j 驱动实例
const driver = neo4j.driver(
    'neo4j://localhost:7687',  // 替换为你的 Neo4j 数据库 URI
    neo4j.auth.basic('neo4j', 'hdvisIEU')  // 替换为你的 Neo4j 数据库用户名和密码
);

// 创建会话
const session = driver.session();

async function createNodesAndRelationships() {
    try {
        for (let i = 1; i < rows.length; i++) { // 跳过标题行
            for(let j=1;j<rows[i].length;j++){
                if(rows[i][j]!="[]"){
                    if(j==12||j==13||j==18)
                    {
                        let temp=rows[i][j].split(" ");
                        for(let k=0;k<temp.length;k++)
                        {
                            const query = `
                                MERGE (a:${heads[0]} {name: '${rows[i][0]}'})
                                MERGE (b:${heads[j]} {name: '${temp[k]}'})
                                MERGE (a)-[:${namefx[j]}]->(b)
                            `;
                            await session.run(query);
                        }
                    }
                    else{
                        const query = `
                            MERGE (a:${heads[0]} {name: '${rows[i][0]}'})
                            MERGE (b:${heads[j]} {name: '${rows[i][j]}'})
                            MERGE (a)-[:${namefx[j]}]->(b)
                        `;
                        await session.run(query);
                    }
                }

                
            }
        }
        console.log('节点和关系创建成功');
    } catch (error) {
        console.error('创建节点和关系失败:', error);
    } finally {
        await session.close();
        await driver.close();
    }
}

async function clearDatabase() {
    try {
        // 删除所有节点和关系的 Cypher 查询
        const query = `
            MATCH (n)
            DETACH DELETE n
        `;

        // 执行查询
        await session.run(query);

        console.log('数据库已清空');
    } catch (error) {
        console.error('清空数据库失败:', error);
    } finally {
        await session.close();
        await driver.close();
    }
}

async function fetchAllData() {
    try {
        // 查询所有节点和关系的 Cypher 查询
        const query = `
            MATCH (n)-[r]->(m)
            RETURN n, r, m
        `;

        // 执行查询
        const result = await session.run(query);

        // 处理查询结果
        const records = result.records;
        const data = [];

        records.forEach(record => {
            const node1 = record.get('n');
            const relation = record.get('r');
            const node2 = record.get('m');

            data.push({
                node1: {
                    labels: node1.labels,
                    properties: node1.properties
                },
                relation: {
                    type: relation.type,
                    properties: relation.properties
                },
                node2: {
                    labels: node2.labels,
                    properties: node2.properties
                }
            });
        });
        //let loadresult=JSON.stringify(data, null, 2);
        let nodelist=[],nodedict={};
        let linklist=[],linkdict={};
        let s=-1,t=-1;
        for(let i=0;i<data.length;i++){
            
            let node1=data[i].node1;
            let flag=nodelist.indexOf(node1.properties["name"]);
            if(flag<0){
                s=nodelist.length;
                nodelist.push(node1.properties["name"]);
                nodedict[s]={name:node1.properties["name"],type:node1.labels[0]};
            }
            else{
                s=flag;
            }
            let node2=data[i].node2;
            let flag2=nodelist.indexOf(node2.properties["name"]);
            if(flag2<0){
                t=nodelist.length;
                nodelist.push(node2.properties["name"]);
                nodedict[t]={name:node2.properties["name"],type:node2.labels[0]};
            }
            else{
                t=flag2;
            }
            let r=data[i].relation["type"];
            if(showlist[r])
                linklist.push([s,t]);
            
            //let r=data[i].relation;
        }
        console.log(data[1])
        let dict={};
        dict["showlist"]=showrelation;
        dict["namefx"]=namefx;
        dict["nodedict"]=nodedict;
        dict["heads"]=heads;
        dict["head2name"]=head2name;
        fs.writeFileSync('graph.json', JSON.stringify(dict, null, 2));
        //cal_layout(linklist);
        // console.log(linklist); 
        // console.log(nodelist);
        // console.log(data[0],data[1],data[2],data[3])
    } catch (error) {
        console.error('读取数据失败:', error);
    } finally {
        await session.close();
        await driver.close();
    }
}
async function fetchGraphData() {
    try {
        // 查询所有节点和关系
        const result = await session.run(
          'MATCH (n)-[r]->(m) RETURN n, r, m'
        );
    
        const triples = [];
    
        // 处理查询结果
        result.records.forEach(record => {
          const sourceNode = record.get('n');
          const targetNode = record.get('m');
          const relationship = record.get('r');
    
          triples.push({
            source: {
              name: sourceNode.properties.name || "",
              type: sourceNode.labels[0] || "" // 获取第一个标签作为类型
            },
            relationship: {
              type: relationship.type
            },
            target: {
              name: targetNode.properties.name || "",
              type: targetNode.labels[0] || "" // 获取第一个标签作为类型
            }
          });
        });
    
        // 将三元组数据保存到本地 JSON 文件
        fs.writeFileSync('graphData.json', JSON.stringify(triples, null, 2));
    
        console.log('Graph data has been written to graphData.json');
      } catch (error) {
      console.error('Error fetching data from Neo4j:', error);
    } finally {
      await session.close();
      await driver.close();
    }
  }

// 运行创建节点和关系的函数
//clearDatabase();
//createNodesAndRelationships();
fetchAllData()
//fetchGraphData()