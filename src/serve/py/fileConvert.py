# 导入操作系统接口，用于文件和目录操作
import os

# 导入base64库，用于处理二进制数据的编码和解码
import base64

# 导入win32com.client，用于与Windows COM对象交互，如Word、Excel等
import win32com.client as win32

# 导入pythoncom，用于COM对象的初始化和清理
import pythoncom

# 导入fitz库，用于处理PDF文件
import fitz

# 从easyofd.ofd模块导入OFD类，用于处理OFD文件
from easyofd.ofd import OFD

# 导入pdf2docx库的parse模块，用于解析PDF文件
from pdf2docx import Converter


# # 指定PDF和输出Word文件路径
# pdf_document = r"C:\Users\28162\Desktop\RAG技术.pdf"
# output_word = "output.docx"


# 文件类型转化
def convert_word_to_pdf(input_path, output_path):
    """
    docx2pdf转化
    from cai
    """
    pythoncom.CoInitialize()
    # 创建Word应用程序实例
    pdf_file = os.path.join(
        output_path, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )
    try:
        # print("wps called")
        word_app = win32.gencache.EnsureDispatch("Kwps.Application")
        print("wps openning")
    except:
        # print("word")
        word_app = win32.gencache.EnsureDispatch("Word.Application")
        print("word openning")

    # 设置应用程序可见性为False（不显示Word界面）
    word_app.Visible = False
    try:
        # 打开Word文档
        doc = word_app.Documents.Open(input_path)
        print(pdf_file)
        # 保存为PDF
        doc.SaveAs(pdf_file, FileFormat=17)
        doc.Close()
        return True
    except Exception as e:
        print("转换失败：" + str(e))
        return False
    finally:
        # 关闭Word应用程序
        word_app.Quit()


def convert_ofd_to_pdf(ofd_file, output_dir):
    pdf_file = os.path.join(
        output_dir, os.path.splitext(os.path.basename(ofd_file))[0] + ".pdf"
    )
    doc = fitz.open(ofd_file)
    pdf_bytes = doc.convert_to_pdf()
    with open(pdf_file, "wb") as f:
        f.write(pdf_bytes)
    return pdf_file


def doc2docx(file_path, output_dir=None):
    """
    使用WPS将指定的doc文件转化为docx格式
    file_path: 文件路径，字符串类型
    output_dir: 输出目录，如果为None，则在原文件路径下保存
    """
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        print(f"文件不存在：{file_path}")
        return

    # 如果未指定输出目录，则在原文件路径下保存
    if output_dir is None:
        output_dir = os.path.dirname(file_path)

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件名和输出文件名
    file_name = os.path.basename(file_path)
    output_file_name = os.path.splitext(file_name)[0] + ".docx"
    output_file_path = os.path.join(output_dir, output_file_name)

    # 初始化COM库
    pythoncom.CoInitialize()
    # 调用WPS进行转换
    try:
        word = win32.Dispatch("kwps.Application")
        doc = word.Documents.Open(file_path)
        doc.SaveAs(output_file_path, 12)  # 12是docx格式的WPS常量
        doc.Close()
        word.Quit()
        print(f"{file_path}已经被成功转换为{output_file_path}")
    except Exception as e:
        print(f"转换失败：{e}")
    finally:
        # 清理COM库
        pythoncom.CoUninitialize()


def ofd2pdf(file_path, output_dir=None):
    """
    ofd转化为pdf
    """
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        print(f"文件不存在：{file_path}")
        return

    # 如果未指定输出目录，则在原文件路径下保存
    if output_dir is None:
        output_dir = os.path.dirname(file_path)

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件名和输出文件名
    file_name = os.path.basename(file_path)
    output_file_name = os.path.splitext(file_name)[0] + ".pdf"
    output_file_path = os.path.join(output_dir, output_file_name)

    try:
        with open(file_path, "rb") as f:
            ofdb64 = str(base64.b64encode(f.read()), "utf-8")
            ofd = OFD()  # 初始化OFD 工具类
            ofd.read(ofdb64, save_xml=False, xml_name="testxml")  # 读取ofdb64
            pdf_bytes = ofd.to_pdf()  # 转pdf
        ofd.del_data()

        with open(output_file_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"转换成功：{file_path} 已经被转换为 {output_file_path}")
    except Exception as e:
        print(f"转换失败：{e}")


def pdf2docx(file_path, output_dir=None):
    """
    使用pdf2docx库将指定的PDF文件转化为DOCX格式
    file_path: 文件路径，字符串类型
    output_dir: 输出目录，如果为None，则在原文件路径下保存
    """
    # 检查文件是否存在
    if not os.path.isfile(file_path):
        print(f"文件不存在：{file_path}")
        return

    # 如果未指定输出目录，则在原文件路径下保存
    if output_dir is None:
        output_dir = os.path.dirname(file_path)

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件名和输出文件名
    file_name = os.path.basename(file_path)
    output_file_name = os.path.splitext(file_name)[0] + ".docx"
    output_file_path = os.path.join(output_dir, output_file_name)

    # 创建转换器对象
    cv = Converter(file_path)

    # 进行转换
    try:
        cv.convert(output_file_path, start=0, end=None)
        cv.close()
        print(f"{file_path}已经被成功转换为{output_file_path}")
    except Exception as e:
        print(f"转换失败：{e}")


# 使用示例
# ofd2pdf("path/to/your/ofd_file.ofd", "path/to/output_directory")

# 使用示例
if __name__ == "__main__":
    input_file = r"D:/data/浙烟专[2023]23号 浙江省烟草专卖局关于印发浙江省涉烟违法行为举报奖励办法的通知.ofd"
    pdf_input = r"D:/data/浙烟专[2023]23号 浙江省烟草专卖局关于印发浙江省涉烟违法行为举报奖励办法的通知.pdf"
    ofd2pdf(input_file)
    pdf2docx(pdf_input)
