from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


def RCSplit(word,chunkSize,overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunkSize,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False,
        separators = ["\n\n", "\n", " " , ""]
    )
    seqs = text_splitter.create_documents([word])
    seqs_dict = [{'sentence': seq.page_content, 'index': i} for i,seq in enumerate(seqs)]
    return seqs_dict


def split_documentByOriChunk(text):
    # 正则表达式匹配章节和条款
    chapter_pattern = re.compile(r'(第[一二三四五六七八九十]+章)\s*(.*)')
    article_pattern = re.compile(r'(第[一二三四五六七八九十]+条)\s*(.*)')

    # 初始化结果
    result = []
    current_chapter = None
    chapter_description = ''
    current_articles = []

    # 按行处理文本
    lines = text.split('\n')
    for line in lines:
        chapter_match = chapter_pattern.match(line)
        article_match = article_pattern.match(line)

        if chapter_match:
            # 保存当前章节及其条款
            if current_chapter:
                result.append((current_chapter, chapter_description, current_articles))
            # 设置新的章节标题和描述
            current_chapter = chapter_match.group(1)
            chapter_description = chapter_match.group(2)
            current_articles = []
        elif article_match:
            # 添加条款到当前条款列表中
            current_articles.append(article_match.group(1) + ' ' + article_match.group(2))
        else:
            # 添加到当前章节的描述部分
            if current_articles:
                # 当行包含条款时，将描述合并到当前条款中
                current_articles[-1] += '\n' + line
            else:
                # 章节描述的内容
                chapter_description += '\n' + line

    # 保存最后一个章节及其条款
    if current_chapter:
        result.append((current_chapter, chapter_description, current_articles))
    
    res = []
    i=0
    for i,ch in enumerate(result):
        print(ch)
        for seq in ch[2]:
            res.append({'sentence':ch[0]+ch[1]+seq,"index":i})
            i+=1
    return res
