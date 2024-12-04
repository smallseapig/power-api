# SEAPIG_TORNADO_MOCK

手动模拟数据查询接口

## 基础用法

- 通过在指定路径创建`JSON`实现接口自动生成

### 模拟 API

- 调用创建模拟`API`的接口，即可自动生成可访问的`API`接口

- 只支持`POST`方法，支持以下几种接口，后缀为`get-mock`, `create-mock`, `delete-mock`, `delete-mock-all`的方法

  - 查询所有可用的`MOCK-API`: `http://localhost:8080/get-mock`

  - 新增（覆盖）可用的`MOCK-API`: `http://localhost:8080/power/mock-api/create-mock`

    - 新增完成后，通过去掉后缀`create-mock`即可正常调用，如：`http://localhost:8080/power/mock-api`

  - 删除可用的`MOCK-API`: `http://localhost:8080/power/mock-api/delete-mock`

  - 查询所有可用的`MOCK-API`: `http://localhost:8080/delete-mock-all`

#### 使用案例

- 通过`Postman`等工具调用接口

1. 新增`MOCK-API`

只支持`POST`方法，调用接口`http://localhost:8080/power/mock-api/create-mock`，在`body`中写入以下数据

```json
{
  "code": 200,
  "msg": "测试数据",
  "data": []
}
```

2. 使用`MOCK-API`

只支持`POST`方法，调用接口`http://localhost:8080/power/mock-api`

## 高级用法

### 万能接口

- 直接调用`http://localhost:8080/`的任意接口，支持后缀为`get`, `create`, `page`, `update`, `delete`的所有方法

#### 使用案例

- 使用`GET`方法调用查询接口，`http://localhost:8080/power/get`

  - 支持`params`的`id`
  - 支持`body`的`id`
  - 支持`body`的`ids`，需要为数组

- 使用`POST`方法调用新增接口，`http://localhost:8080/power/create`

- 使用`POST`方法调用查询接口，`http://localhost:8080/power/page`

- 使用`PUT`方法调用查询接口，`http://localhost:8080/power/update`

- 使用`DELETE`方法调用查询接口，`http://localhost:8080/power/delete`

  - 支持`params`的`id`
  - 支持`body`的`id`
  - 支持`body`的`ids`，需要为数组
