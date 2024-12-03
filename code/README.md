# SEAPIG_TORNADO_MOCK

手动模拟数据查询接口

## 基础用法

- 通过在指定路径创建`JSON`实现接口自动生成

### 创建模拟 API

- 在`seapig-mock`创建`JSON`文件，即可自动生成可访问的`API`接口

#### 使用案例

1. 在`seapig-mock`中创建文件夹`demo`，并继续往下创建`test.json`文件，最终文件路径为`seapig-mock/demo/test.json`

2. 在`JSON`文件中写入数据

```json
{
  "code": 200,
  "msg": "测试数据",
  "data": []
}
```

3. 通过`Postman`等工具调用接口

只支持`POST`方法，调用接口`http://localhost:8080/demo/test`，即可正常运行

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
