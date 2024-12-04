import json
import time
import os
import shutil


# 读取文件内容
def get_context_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


# 写入文件内容
def write_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


# 获取所有文件路径
def get_file_path_list(dir_path):
    path_list = []  # 存储所有文件路径的列表
    for root, directories, files in os.walk(dir_path):
        for file_name in files:
            # 拼接完整的文件路径，并添加到列表中
            file_path = os.path.join(root, file_name)
            normal_path = file_path.replace("\\", "/")
            path_list.append(normal_path)

    return path_list


# 获取所有 MOCK API 路径
def get_mock_api_list(dir_path):
    mock_api_list = []  # 存储所有文件路径的列表
    for root, directories, files in os.walk(dir_path):
        for file_name in files:
            # 拼接完整的文件路径，并添加到列表中
            file_path = os.path.join(root, file_name)
            # 转换成 API 路径
            file_path_part = file_path.partition(os.sep)
            normal_path = file_path_part[-1].replace("\\", "/")
            mock_api_path, _ = os.path.splitext(normal_path)
            mock_api_list.append(f"/{mock_api_path}")

    return mock_api_list


# 清空文件夹
def clear_folder(dir_path):
    # 遍历文件夹中的所有文件和子文件夹
    for root, directories, files in os.walk(dir_path, topdown=False):
        for file_name in files:
            # 删除文件
            os.remove(os.path.join(root, file_name))
        for dir_name in directories:
            # 删除子文件夹
            shutil.rmtree(os.path.join(root, dir_name))


# 获取服务器当前时间
def get_current_time(val=''):
    if val == 'year':
        return time.strftime('%Y', time.localtime(time.time()))
    elif val == 'month':
        return time.strftime('%m', time.localtime(time.time()))
    elif val == 'date':
        return time.strftime('%d', time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
