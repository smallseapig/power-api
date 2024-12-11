import tornado.web
import socket
import traceback
import json
import logging
import os
import datetime
import traceback
import decimal
import uuid
from enum import Enum


from utils import common
import importlib
seapig_mock = importlib.import_module("utils.seapig-mock")


class StatusCode(Enum):
    OK = 0
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


logging.basicConfig(level=logging.DEBUG)


class BaseHandler(tornado.web.RequestHandler):
    # 前端跨域
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Methods",
                        "GET, POST, PUT, DELETE, OPTIONS")

    def options(self, *args):
        # 处理预检请求
        self.set_status(204)
        self.finish()


class JsonEncoder(json.JSONEncoder):
    # Json 格式化
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, uuid.UUID):
            return o.hex
        elif isinstance(o, Enum):
            return o.value
        super(JsonEncoder, self).default(o)


def get_server_ip():
    # 获取本机主机名
    hostname = socket.gethostname()
    # 获取本机IP地址
    ip_address = socket.gethostbyname(hostname)
    return ip_address


class MockHandler(BaseHandler):

    def initialize(self, mock_dir, db_dir):
        self.mock_dir = mock_dir
        self.db_dir = db_dir

    def get(self, path):
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            params = {key: self.get_query_argument(
                key) for key in self.request.query_arguments}

            # 构建完整文件路径
            full_path = f"{self.mock_dir}/{path}.json"

            # 检查文件是否存在
            if os.path.exists(full_path):
                # 存在则直接走获取文件数据的逻辑

                # 判断数据格式是否为定制化数据，定制化数据则走分页逻辑
                exist_content = seapig_mock.mock(full_path)
                if isinstance(exist_content, dict) and isinstance(exist_content.get("data", {}), dict) and isinstance(exist_content.get("data", {}).get("records"), list):
                    self.write(json.dumps(seapig_mock.seapig_query(
                        full_path, {**data, **params}), cls=JsonEncoder))
                else:
                    # 不为定制格式数据则直接返回
                    self.write(json.dumps(exist_content, cls=JsonEncoder))
            else:
                # 不存在则走模拟数据库的逻辑
                get_id = self.get_argument('id', '')

                valid_operation = ["get"]
                dir_path = os.path.dirname(path)
                base_path = os.path.basename(path)
                operation = base_path
                # 只匹配 get 后缀的接口
                if operation in valid_operation:
                    db_path = f"{self.db_dir}/{dir_path}/data.db"

                    # 根据不同的操作，触发不同的方法
                    if operation == "get":
                        self.trigger_get(db_path, {**data, "get_id": get_id})
                    else:
                        pass
                else:
                    self.write(json.dumps(
                        {"code": StatusCode.NOT_FOUND, "msg": "API 不存在", "data": {}}, cls=JsonEncoder))

        except Exception as e:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": str(e), "data": {}}, cls=JsonEncoder))
            traceback.print_exc()

    def post(self, path):
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            params = {key: self.get_query_argument(
                key) for key in self.request.query_arguments}

            # 构建完整文件路径
            full_path = f"{self.mock_dir}/{path}.json"

            # 检查文件是否存在
            if os.path.exists(full_path):
                # 存在则直接走获取文件数据的逻辑

                # 判断数据格式是否为定制化数据，定制化数据则走分页逻辑
                exist_content = seapig_mock.mock(full_path)
                if isinstance(exist_content, dict) and isinstance(exist_content.get("data", {}), dict) and isinstance(exist_content.get("data", {}).get("records"), list):
                    self.write(json.dumps(seapig_mock.seapig_query(
                        full_path, {**data, **params}), cls=JsonEncoder))
                else:
                    # 不为定制格式数据则直接返回
                    self.write(json.dumps(exist_content, cls=JsonEncoder))
            else:
                # 不存在则走模拟数据库，“增删改查”的逻辑
                valid_operation = ["create", "page"]
                mock_operation = ["get-mock", "create-mock", "append-mock",
                                  "delete-mock", "delete-mock-all"]
                dir_path = os.path.dirname(path)
                base_path = os.path.basename(path)
                operation = base_path

                # 如果是 MOCK 操作则放行到 MOCK 逻辑中
                if operation in mock_operation:
                    # MOCK 文件路径
                    mock_path = f"{self.mock_dir}/{dir_path}.json"

                    if operation == "get-mock":
                        self.get_mock()
                    elif operation == "create-mock":
                        self.create_mock(mock_path, data)
                    elif operation == "append-mock":
                        self.append_mock(mock_path, data)
                    elif operation == "delete-mock":
                        self.delete_mock(mock_path)
                    elif operation == "delete-mock-all":
                        self.delete_mock_all()
                    else:
                        pass

                # 判断为有效操作才允许进入“增删改查”逻辑
                elif operation in valid_operation:
                    # 模拟数据库文件路径
                    db_path = f"{self.db_dir}/{dir_path}/data.db"

                    # 根据不同的操作，触发不同的方法
                    if operation == "create":
                        self.trigger_create(db_path, data)
                    elif operation == "page":
                        self.trigger_page(db_path, data)
                    else:
                        pass
                else:
                    self.write(json.dumps(
                        {"code": StatusCode.NOT_FOUND, "msg": "API 不存在，请先创建对应文件", "data": {}}, cls=JsonEncoder))

        except Exception as e:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": str(e), "data": {}}, cls=JsonEncoder))
            traceback.print_exc()

    def put(self, path):
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            create_time = common.get_current_time()
            remote_ip = self.request.remote_ip

            valid_operation = ["update"]
            dir_path = os.path.dirname(path)
            base_path = os.path.basename(path)
            operation = base_path
            # 只匹配 update 后缀的接口
            if operation in valid_operation:
                db_path = f"{self.db_dir}/{dir_path}/data.db"

                # 根据不同的操作，触发不同的方法
                if operation == "update":
                    self.trigger_update(
                        db_path, {**data, "ip_addr": remote_ip, "create_time": create_time})
                else:
                    pass
            else:
                self.write(json.dumps(
                    {"code": StatusCode.NOT_FOUND, "msg": "API 不存在", "data": {}}, cls=JsonEncoder))

        except Exception as e:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": str(e), "data": {}}, cls=JsonEncoder))
            traceback.print_exc()

    def delete(self, path):
        try:
            data = json.loads(self.request.body) if self.request.body else {}
            delete_id = self.get_argument('id', '')

            valid_operation = ["delete"]
            dir_path = os.path.dirname(path)
            base_path = os.path.basename(path)
            operation = base_path
            # 只匹配 delete 后缀的接口
            if operation in valid_operation:
                db_path = f"{self.db_dir}/{dir_path}/data.db"

                # 根据不同的操作，触发不同的方法
                if operation == "delete":
                    self.trigger_delete(
                        db_path, {**data, "delete_id": delete_id})
                else:
                    pass
            else:
                self.write(json.dumps(
                    {"code": StatusCode.NOT_FOUND, "msg": "API 不存在", "data": {}}, cls=JsonEncoder))

        except Exception as e:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": str(e), "data": {}}, cls=JsonEncoder))
            traceback.print_exc()

    def get_mock(self):
        # 获取已有的所有 MOCK API（文件路径）
        mock_api_list = common.get_mock_api_list(self.mock_dir)
        self.write(json.dumps(
            {"code": StatusCode.OK, "msg": "当前有效的 API 清单", "data": mock_api_list}, cls=JsonEncoder))

    def create_mock(self, mock_path, data):
        # 创建或者覆盖 MOCK API（文件路径）

        # 首先，如果文件夹不存在，则创建文件夹
        os.makedirs(os.path.dirname(mock_path), exist_ok=True)
        json_data = json.dumps(data, cls=JsonEncoder)

        # 将数据写入指定文件路径
        common.write_file(mock_path, json_data)
        self.write(json.dumps(
            {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

    def append_mock(self, mock_path, data):
        # 这是一个专门定制的接口，追加数据到 MOCK API（文件路径）

        # 首先，判断文件存不存在
        if os.path.exists(mock_path):
            # 第二，判断数据结构是否符合定制化要求
            # 如果已有的数据结构符合要求的，则追加数据
            exist_content = seapig_mock.mock(mock_path)
            if isinstance(exist_content, dict) and isinstance(exist_content.get("data", {}), dict) and isinstance(exist_content.get("data", {}).get("records"), list):
                # 已有的数据结构符合要求后，需要判断新增的数据格式，根据不同的数据类型进行追加
                # 情况一：数据为列表
                if isinstance(data, list):
                    exist_content["data"]["records"] = data + \
                        exist_content["data"]["records"]
                    json_data = json.dumps(exist_content, cls=JsonEncoder)
                    # 重写文件内容
                    common.write_file(mock_path, json_data)
                    self.write(json.dumps(
                        {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

                # 情况二：指定数据格式为列表
                elif isinstance(data.get("data", {}), dict) and isinstance(data.get("data", {}).get("records"), list):
                    exist_content["data"]["records"] = data.get("data", {}).get(
                        "records") + exist_content["data"]["records"]
                    json_data = json.dumps(exist_content, cls=JsonEncoder)
                    # 重写文件内容
                    common.write_file(mock_path, json_data)
                    self.write(json.dumps(
                        {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

                # 情况三：常规数据，任意格式都可，直接塞到 records 中去
                else:
                    exist_content["data"]["records"] = [
                        data] + exist_content["data"]["records"]
                    json_data = json.dumps(exist_content, cls=JsonEncoder)
                    # 重写文件内容
                    common.write_file(mock_path, json_data)
                    self.write(json.dumps(
                        {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

            else:
                self.write(json.dumps(
                    {"code": StatusCode.BAD_REQUEST, "msg": "只支持定制数据结构追加数据", "data": {}}, cls=JsonEncoder))
        else:
            # 文件夹不存在，则创建文件夹
            os.makedirs(os.path.dirname(mock_path), exist_ok=True)

            # 将数据写入指定文件路径
            json_data = json.dumps(data, cls=JsonEncoder)
            common.write_file(mock_path, json_data)
            self.write(json.dumps(
                {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

    def delete_mock(self, mock_path):
        # 删除一个 MOCK API（文件路径）

        file_list = common.get_file_path_list(self.mock_dir)
        if mock_path in file_list:
            # 删除文件
            os.remove(mock_path)
            self.write(json.dumps(
                {"code": StatusCode.OK, "msg": "删除成功", "data": {}}, cls=JsonEncoder))

        else:
            self.write(json.dumps(
                {"code": StatusCode.NO_CONTENT, "msg": "不存在待删除的 API，无需删除", "data": {}}, cls=JsonEncoder))

    def delete_mock_all(self):
        # 删除所有 MOCK API（文件路径），包括整个文件夹
        common.clear_folder(self.mock_dir)
        self.write(json.dumps(
            {"code": StatusCode.OK, "msg": "删除成功", "data": {}}, cls=JsonEncoder))

    def trigger_get(self, db_path, data):
        # 触发获取方法

        # 判断数据是否有各项 ID，如果没有，则不允许获取

        if data.get("id") or data.get("ids", []) or data.get("get_id"):

            # 检查模拟数据库文件是否存在
            if os.path.exists(db_path):
                # 存在则直接使用，将所有的 ID 都集中到一起获取

                # 如果存在 ids，需要保证格式为列表
                if isinstance(data.get("ids", []), list):
                    get_list = []

                    # 将所有的 ID 都集中到一起获取
                    if data.get("ids", []):
                        get_list.extend(data.get("ids", []))
                    if data.get("id"):
                        get_list.append(data.get("id"))
                    if data.get("get_id"):
                        get_list.append(data.get("get_id"))

                    # 获取是否有符合要求的数据
                    data_list = common.get_context_list(db_path)
                    match_get_list = [
                        i for i in data_list if i.get("id") in get_list]

                    if match_get_list:
                        if len(match_get_list) == 1:
                            # 只有一个值返回对象
                            self.write(json.dumps(
                                {"code": StatusCode.OK, "msg": None, "data": match_get_list[0]}, cls=JsonEncoder))
                        else:
                            # 有多个值时返回一个列表
                            self.write(json.dumps(
                                {"code": StatusCode.OK, "msg": None, "data": match_get_list}, cls=JsonEncoder))

                    else:
                        self.write(json.dumps(
                            {"code": StatusCode.NO_CONTENT, "msg": "指定 id 的数据不存在", "data": {}}, cls=JsonEncoder))

                else:
                    self.write(json.dumps(
                        {"code": StatusCode.BAD_REQUEST, "msg": "ids 必须为数组", "data": {}}, cls=JsonEncoder))
            else:
                # 文件不存在，意味着数据为空，提示数据 ID 不存在
                self.write(json.dumps(
                    {"code": StatusCode.NO_CONTENT, "msg": "指定 id 的数据不存在", "data": {}}, cls=JsonEncoder))
        else:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": "请指定获取的数据 id", "data": {}}, cls=JsonEncoder))

    def trigger_create(self, db_path, data):
        # 触发新增方法

        create_time = common.get_current_time()
        remote_ip = self.request.remote_ip

        # 检查模拟数据库文件是否存在
        if os.path.exists(db_path):
            # 存在则直接使用，在原有的列表中推入新的数据
            data_list = common.get_context_list(db_path)

            # 处理数据时，分三种情况
            # 情况一：数据为列表
            if isinstance(data, list):
                # 插入批量新值，并在每项值中插入 ID、IP 和时间
                aggregation = [{**i, "id": uuid.uuid1(), "ip_addr": remote_ip,
                                "create_time": create_time} for i in data] + data_list
                json_data = json.dumps(aggregation, cls=JsonEncoder)
                # 重写文件内容
                common.write_file(db_path, json_data)
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

            # 情况二：指定数据格式为列表
            elif isinstance(data.get("data", {}), dict) and isinstance(data.get("data", {}).get("records"), list):
                # 插入批量新值，并在每项值中插入 ID、IP 和时间
                aggregation = [{**i, "id": uuid.uuid1(), "ip_addr": remote_ip, "create_time": create_time}
                               for i in data.get("data", {}).get("records")] + data_list
                json_data = json.dumps(aggregation, cls=JsonEncoder)
                # 重写文件内容
                common.write_file(db_path, json_data)
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

            # 情况三：常规数据，任意格式都可，直接保存
            else:
                random_id = uuid.uuid1()
                # 插入新值
                data_list.insert(
                    0, {**data, "id": random_id, "ip_addr": remote_ip, "create_time": create_time})
                json_data = json.dumps(data_list, cls=JsonEncoder)
                # 重写文件内容
                common.write_file(db_path, json_data)
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": random_id}, cls=JsonEncoder))

        else:
            # 不存在，则先创建目录，再写入文件
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # 处理数据时，分三种情况
            # 情况一：数据为列表
            if isinstance(data, list):
                # 在每项值中插入 ID、IP 和时间
                aggregation = [{**i, "id": uuid.uuid1(), "ip_addr": remote_ip, "create_time": create_time}
                               for i in data]
                json_data = json.dumps(aggregation, cls=JsonEncoder)
                common.write_file(db_path, json_data)
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

            # 情况二：指定数据格式为列表
            elif isinstance(data.get("data", {}), dict) and isinstance(data.get("data", {}).get("records"), list):
                # 在每项值中插入 ID、IP 和时间
                aggregation = [{**i, "id": uuid.uuid1(), "ip_addr": remote_ip, "create_time": create_time}
                               for i in data.get("data", {}).get("records")]
                json_data = json.dumps(aggregation, cls=JsonEncoder)
                common.write_file(db_path, json_data)
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": {}}, cls=JsonEncoder))

            # 情况三：常规数据，任意格式都可，直接保存
            else:
                random_id = uuid.uuid1()
                json_data = json.dumps(
                    {**data, "id": random_id, "ip_addr": remote_ip, "create_time": create_time}, cls=JsonEncoder)
                common.write_file(db_path, f"[{json_data}]")
                self.write(json.dumps(
                    {"code": StatusCode.OK, "msg": None, "data": random_id}, cls=JsonEncoder))

    def trigger_page(self, db_path, data):
        # 触发查询方法

        # 检查模拟数据库文件是否存在
        if os.path.exists(db_path):
            # 存在则直接使用，调用数据分页查询方法
            self.write(json.dumps(seapig_mock.seapig_query(
                db_path, data), cls=JsonEncoder))
        else:
            # 不存在，则返回一份空数据
            self.write(json.dumps({
                "code": StatusCode.OK,
                "msg": None,
                "data": {
                    "current": 1,
                    "pages": 0,
                    "records": [],
                    "size": 10,
                    "tag": None,
                    "total": 0,
                }}, cls=JsonEncoder))

    def trigger_update(self, db_path, data):
        # 触发更新方法

        # 判断数据是否有 ID，如果没有 ID，则不允许更新
        if data.get("id"):

            # 检查模拟数据库文件是否存在
            if os.path.exists(db_path):
                # 存在则直接使用，判断对应 ID 的数据是否有效
                data_list = common.get_context_list(db_path)

                for ind, item in enumerate(data_list):
                    if item.get("id", 0) == data.get("id", 1):
                        # 更新指定数据
                        data_list[ind] = data
                        json_data = json.dumps(data_list, cls=JsonEncoder)
                        # 重写文件内容
                        common.write_file(db_path, json_data)
                        self.write(json.dumps(
                            {"code": StatusCode.OK, "msg": "更新成功", "data": {}}, cls=JsonEncoder))
                        # 找到匹配项后退出循环
                        break
                else:
                    self.write(json.dumps(
                        {"code": StatusCode.NO_CONTENT, "msg": f"不存在 id 为 {data.get('id')} 的数据", "data": {}}, cls=JsonEncoder))

            else:
                # 文件不存在，意味着数据为空，提示数据 ID 不存在
                self.write(json.dumps(
                    {"code": StatusCode.NO_CONTENT, "msg": f"不存在 id 为 {data.get('id')} 的数据", "data": {}}, cls=JsonEncoder))
        else:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": "请指定更新的数据 id", "data": {}}, cls=JsonEncoder))

    def trigger_delete(self, db_path, data):
        # 触发删除方法

        # 判断数据是否有各项 ID，如果没有，则不允许删除
        if data.get("id") or data.get("ids", []) or data.get("delete_id"):

            # 检查模拟数据库文件是否存在
            if os.path.exists(db_path):
                # 存在则直接使用，将所有的 ID 都集中到一起删除

                # 如果存在 ids，需要保证格式为列表
                if isinstance(data.get("ids", []), list):
                    delete_list = []

                    # 将所有的 ID 都集中到一起删除
                    if data.get("ids", []):
                        delete_list.extend(data.get("ids", []))
                    if data.get("id"):
                        delete_list.append(data.get("id"))
                    if data.get("delete_id"):
                        delete_list.append(data.get("delete_id"))

                    # 获取是否有符合要求的数据
                    data_list = common.get_context_list(db_path)
                    match_delete_list = [
                        i for i in data_list if i.get("id") in delete_list]

                    if match_delete_list:
                        # 重新保存不在删除列表中的数据
                        save_list = [i for i in data_list if i.get(
                            "id") not in delete_list]
                        json_data = json.dumps(save_list, cls=JsonEncoder)

                        # 重写文件内容
                        common.write_file(db_path, json_data)
                        self.write(json.dumps(
                            {"code": StatusCode.OK, "msg": "删除成功", "data": {}}, cls=JsonEncoder))

                    else:
                        self.write(json.dumps(
                            {"code": StatusCode.NO_CONTENT, "msg": "指定 id 的数据不存在", "data": {}}, cls=JsonEncoder))

                else:
                    self.write(json.dumps(
                        {"code": StatusCode.BAD_REQUEST, "msg": "ids 必须为数组", "data": {}}, cls=JsonEncoder))
            else:
                # 文件不存在，意味着数据为空，提示数据 ID 不存在
                self.write(json.dumps(
                    {"code": StatusCode.NO_CONTENT, "msg": "指定 id 的数据不存在", "data": {}}, cls=JsonEncoder))
        else:
            self.write(json.dumps(
                {"code": StatusCode.BAD_REQUEST, "msg": "请指定删除的数据 id", "data": {}}, cls=JsonEncoder))


def run():
    app = tornado.web.Application(
        [(r"/(.*)", MockHandler,
          {"mock_dir": "seapig-mock", "db_dir": "seapig-database"})],
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    port = 34001
    http_server.listen(port)
    print(f"running on http://{get_server_ip()}:{port}")

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run()
