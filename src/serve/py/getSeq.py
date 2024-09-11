from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

# 问答
import llmQA as llmqa
import chunk2tree as c2t
import multthreads as mthreads

import json

threads_num = 4
# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    threads_num = data["seq_threads_num"]


# 递归分割
def RCSplit(word, chunkSize, overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunkSize,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", " ", ""],
    )
    seqs = text_splitter.create_documents([word])
    # seqs_dict = [
    #     {"sentence": seq.page_content, "index": i} for i, seq in enumerate(seqs)
    # ]

    res = []
    i = 0
    seqList = []
    # i为索引 从0开始; seq为内容
    for i in range(len(seqs)):
        res.append(
            {
                "sentence": seqs[i].page_content,
                "index": i,
                # "tags": TagGet(ch[0] + ch[1] + seq),
                # "tree": c2t.getmind(ch[0] + ch[1] + seq),
            }
        )
        seqList.append(seqs[i].page_content)
        i += 1

    treeList = mthreads.multThreads(c2t.getmind, seqList, threads_num)
    tagsList = mthreads.multThreads(TagGet, seqList, threads_num)
    for i in range(len(res)):
        res[i]["tags"] = tagsList[i]
        res[i]["tree"] = treeList[i]

    return res


# 格式分割
def split_documentByOriChunk(filename, text):
    # 正则表达式匹配章节和条款
    chapter_pattern = re.compile(r"(第[零一二三四五六七八九十百千万]+章)\s*(.*)")
    article_pattern = re.compile(r"(第[零一二三四五六七八九十百千万]+条)\s*(.*)")

    # 初始化结果
    result = []
    current_chapter = None
    chapter_description = ""
    current_articles = []

    # 按行处理文本
    lines = text.split("\n")
    for line in lines:
        chapter_match = chapter_pattern.match(line)
        article_match = article_pattern.match(line)

        # 如果有新的章节来了
        if chapter_match:
            # 保存当前章节及其条款
            if current_chapter:
                result.append((current_chapter, chapter_description, current_articles))

            # 设置新的章节标题和描述
            current_chapter = chapter_match.group(1)
            chapter_description = chapter_match.group(2)
            current_articles = []

        # 有新的条款出现
        elif article_match:
            # 添加条款到当前条款列表中
            current_articles.append(
                article_match.group(1) + " " + article_match.group(2)
            )

        # 当前章节或条款还没结束
        else:
            # 添加到当前章节的描述部分
            if current_articles:
                # 当行包含条款时，将描述合并到当前条款中
                current_articles[-1] += "\n" + line
            else:
                # 章节描述的内容
                chapter_description += "\n" + line

    # 保存最后一个章节及其条款
    if current_chapter:
        result.append((current_chapter, chapter_description, current_articles))

    res = []
    i = 0
    seqList = []
    # i为索引 从0开始; ch为内容
    for i, ch in enumerate(result):
        # print("ch", ch)
        for seq in ch[2]:
            seqList.append(ch[0] + ch[1] + seq)
            res.append(
                {
                    "sentence": ch[0] + ch[1] + seq,
                    "index": i,
                    # "tags": TagGet(ch[0] + ch[1] + seq),
                    # "tree": c2t.getmind(ch[0] + ch[1] + seq),
                }
            )
            i += 1

    treeList = mthreads.multThreads(c2t.getmind, seqList, threads_num)
    tagsList = mthreads.multThreads(TagGet, seqList, threads_num)
    for i in range(len(res)):
        res[i]["tags"] = tagsList[i]
        res[i]["tree"] = treeList[i]

    return res


def TagGet(text):
    ans = ""
    input = (
        """
    你是一个文段标签总结人员，你需要提取下面的资料中的重要关键词并输出，对于一些不重要的动词或名词不用提取，
    输出例 开除党籍,处罚,党中央
    如果内容混乱或无法总结出，则输出None
    下面是你的资料，请按照指定格式输出：
    """
        + text
    )

    try:
        ans = llmqa.chatmodel(input)
        # ans = llmqa.zhipuChat(input)
    # except:
    # print("llm err")
    # ans = llmqa.zhipuChat(input)
    except:
        ans = "None"
    return ans.split(",") if ans != "None" else []


if __name__ == "__main__":
    res = TagGet(
        """
第二章设立第十二条 党组的设立，应当由党中央或者本级地方党委审批。有关管委会的工作部门设立党组，由本级党委授权管委会党工委审批。党组不得审批设立党组。
分党组的设立，由党组报本级党委组织部门审批。
新成立的有关单位符合设立党组条件的，党中央或者本级地方党委可以根据需要作出设立党组的决定，也可以由需要设立党组的单位或者其上级主管部门党组织提出设立申请，由党中央或者本级地方党委审批。
变更、撤销党组的，由批准其设立的党组织作出决定。
"""
    )
