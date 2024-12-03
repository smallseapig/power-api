import json
import time


# 读取文件内容
def get_context_list(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data


# 写入文件内容
def write_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


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

