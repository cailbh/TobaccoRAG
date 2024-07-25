from langchain_text_splitters import RecursiveCharacterTextSplitter

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