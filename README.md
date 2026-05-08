# OpenAI Agent Demo

这是一个最小可运行的 Python 命令行 demo，使用 OpenAI 官方 Python SDK 调用 `Responses API`，并演示本地 function calling 的完整闭环。

## 功能

- 使用 `OpenAI().responses.create(...)` 发起请求
- 提供 3 个本地 function calling 工具
- 展示“模型请求工具 -> 本地执行 -> 工具结果回传 -> 模型给出最终答复”的流程
- 提供无需 API Key 的 `--self-check` 本地自检

## 文件说明

- `main.py`：命令行入口与 Responses API 调用循环
- `tools.py`：本地工具函数、工具 schema、工具分发
- `test_demo.py`：最小行为测试
- `requirements.txt`：当前 `.venv` 的依赖声明

## 环境准备

当前项目使用本目录下的 `.venv`。

安装依赖：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## API Key

你需要先设置环境变量 `OPENAI_API_KEY`：

```bash
export OPENAI_API_KEY="在这里填你的 key"
```

## 先做本地自检

这个命令不会访问 OpenAI API：

```bash
.venv/bin/python main.py --self-check
```

## 运行 demo

默认模型是 `gpt-5.4-mini`，你也可以自己改成别的模型：

```bash
.venv/bin/python main.py --prompt "东京现在天气怎么样？顺便把 25 摄氏度换算成华氏度。"
```

指定模型：

```bash
.venv/bin/python main.py --model gpt-5.4-mini --prompt "现在川崎几点？再告诉我旧金山的天气。"
```

## 这个 demo 里的函数

- `get_weather(location)`：返回本地预设天气数据
- `convert_temperature(value, from_unit, to_unit)`：做摄氏度和华氏度换算
- `get_time_in_city(city)`：返回本地预设城市时区的当前时间

这些函数都是本地演示数据，不依赖第三方天气或时间服务。
