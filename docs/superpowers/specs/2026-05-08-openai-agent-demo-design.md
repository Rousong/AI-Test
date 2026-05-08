# OpenAI Agent Demo 设计文档

## 目标

在当前目录创建一个最小可运行的 Python demo，使用 OpenAI 官方 Python SDK 调用 `Responses API`，并演示本地 function calling 的完整闭环。用户后续只需要自行填写 `OPENAI_API_KEY` 即可运行。

## 范围

本次只实现命令行 demo，不实现 Web 页面、不接数据库、不引入多 Agent 编排框架，也不添加超出演示所需的长期工程化设施。

## 方案选择

采用官方 `openai` Python SDK，而不是手写 HTTP 请求。

原因如下：
- 代码更接近 OpenAI 官方示例，便于后续继续扩展。
- function calling 的请求和回传结构更清晰，样板代码更少。
- 依赖增加很少，符合“最小实现”的目标。

## 目录与文件

本次实现预计只新增或修改以下根目录文件：

- `main.py`：命令行入口，负责读取环境变量、发起请求、处理工具调用循环，并输出最终结果。
- `tools.py`：定义本地工具函数、工具 schema，以及按名称分发函数调用的逻辑。
- `README.md`：说明环境准备、API Key 配置、运行命令和示例问题。
- `requirements.txt`：声明运行 demo 所需依赖。
- `AGENTS.md`：补充当前项目的简介和目录结构树。

## 功能设计

### 1. 命令行入口

`main.py` 提供一个简单的命令行界面：

- 接收用户问题，例如“帮我查一下今天适合做什么，然后换算 25 摄氏度到华氏度”。
- 从环境变量读取 `OPENAI_API_KEY`。
- 调用 `OpenAI().responses.create(...)` 发起请求。
- 将 `tools.py` 中定义的工具 schema 传给模型。

### 2. Function Calling 回路

请求发出后，程序按以下流程运行：

1. 把用户输入发送给模型。
2. 如果模型返回 `function_call`，解析函数名和参数。
3. 在本地执行对应 Python 函数。
4. 将本地执行结果以 `function_call_output` 形式发回模型。
5. 继续循环，直到模型返回最终文本答复。

这个流程会做成显式循环，确保示例代码能清楚展示每一步，而不是隐藏在抽象层里。

### 3. 本地工具示例

计划提供 3 个简单但足够展示能力的函数：

- `get_weather(location: str) -> dict`
  - 返回模拟天气数据，不依赖外部天气服务。
- `convert_temperature(value: float, from_unit: str, to_unit: str) -> dict`
  - 展示结构化参数和数值处理。
- `get_time_in_city(city: str) -> dict`
  - 展示另一个读取型函数，返回预设时区信息。

这些函数都只做本地演示，避免把 demo 复杂度带到第三方系统接入上。

### 4. 无 Key 下的本地校验

为了在未填写真实 API Key 时也能验证代码结构，本次会加入一个本地自检入口，例如 `--self-check`：

- 校验工具 schema 是否完整。
- 校验工具分发是否正常。
- 运行几个本地函数调用样例。

这样可以在当前环境中完成基础验证，而不阻塞在真实 API 调用上。

## 错误处理

只保留与演示直接相关的最小错误处理：

- 缺少 `OPENAI_API_KEY` 时，给出明确提示。
- 模型返回未知工具名时，抛出清晰错误。
- 工具参数 JSON 解析失败时，抛出清晰错误。

不加入与本需求无关的重试、日志系统、配置层、插件化机制。

## 验证标准

完成后至少满足以下可验证结果：

1. `python main.py --self-check` 能在本地成功运行。
2. `python main.py --help` 能显示基本用法。
3. 在用户填写 `OPENAI_API_KEY` 后，`python main.py --prompt "..."` 可以走完整的 function calling 流程。

## 参考依据

本设计基于 OpenAI 官方当前文档中的 `Responses API` 与 function calling 说明：

- `https://platform.openai.com/docs/guides/function-calling?api-mode=responses&lang=python`
- `https://platform.openai.com/docs/api-reference/responses`
