import pandas as pd

file_path = r"..\files\问制度 问题和回答填写表.xlsx"

# 读取excel，存储问题，回答以及来源


def get_sheet_names(file_path):
    """
    获取xlsx文件中所有sheet名称

    :param file_path: xlsx文件路径
    :return: sheet名称列表
    """
    df = pd.read_excel(file_path, sheet_name=None)
    return list(df.keys())


def read_sheet_by_attrs(file_path, sheet_name, attrs):
    """
    根据属性读取sheet中的数据

    :param file_path: xlsx文件路径
    :param sheet_name: sheet名称
    :param attrs: 属性列表
    :return: 数据列表
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    data = []
    for i in range(len(df)):
        info = dict()
        for attr in attrs:
            # attr = df.iloc[i][attr]
            attr_info = df.iloc[i][attr]
            # print(attr_info, type(attr_info))
            # print(pd.isna(attr_info))
            # if not attr_info or attr_info == "nan"
            if pd.isna(attr_info):
                return data

            info[attr] = attr_info
        data.append(info)

    return data


if __name__ == "__main__":
    print(get_sheet_names(file_path))
    df = pd.read_excel(file_path, sheet_name="韩聪")
    first_row = df.iloc[0]["问题"]
    read_sheet_by_attrs(file_path, "韩聪", ["问题", "回答"])
    print(first_row)
    print(len(df))
