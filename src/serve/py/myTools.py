from docx import Document

def read_word_file(file_path):
    # 读取Word文件内容
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def remove_newline_items(data):
    return [item for item in data if item.strip() != '']

def read_pdf_as_blob(file_path):
    with open(file_path, "rb") as file:
        pdf_blob = file.read()
    return pdf_blob