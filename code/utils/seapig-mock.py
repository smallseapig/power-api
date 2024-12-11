from utils import common
import math


# MOCK 数据接口查询方法
def mock(file_path):
    # 读取 JSON 文件
    file_content = common.get_context_list(file_path)
    return file_content
  

# 本地数据库万能接口查询方法
def seapig_query(file_path, data):
    # 读取 JSON 文件
    file_content = common.get_context_list(file_path)
    # 将文件内容处理为列表
    if isinstance(file_content, list):
        data_list = file_content
    else:
        data_list = file_content.get("data", {}).get("records", [])

    # 过滤无效查询条件
    exclude_files = ["size", "current"]
    filter_condition = [(key, value)
                        for key, value in data.items() if key not in exclude_files]
    # 根据查询条件进行模糊查询
    filter_data_list = [item for item in data_list if all(
        str(value) in str(item.get(key, "")) for key, value in filter_condition)]

    # 构建返回数据
    size = int(data.get("size", 10))
    current = int(data.get("current", 1))
    records = filter_data_list[(current - 1) * size: current * size]
    total = len(filter_data_list)
    pages = math.ceil(total / size)

    return {
        "code": 0,
        "msg": None,
        "data": {
            "records": records,
            "total": total,
            "size": size,
            "current": current,
            "pages": pages,
            "tag": None
        }
    }
