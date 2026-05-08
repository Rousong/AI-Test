# OpenAI Agent Demo

这是一个最小可运行的 Python 命令行 demo，使用 OpenAI 官方 Python SDK 连接 OpenAI-compatible 接口，并演示本地 function calling 的完整闭环。当前默认配置已经对齐到 DeepSeek。

## 功能

- 使用 OpenAI Python SDK 的 `chat.completions` 兼容接口发起请求
- 提供 3 个本地 function calling 工具
- 展示“模型请求工具 -> 本地执行 -> 工具结果回传 -> 模型给出最终答复”的流程
- 提供无需 API Key 的 `--self-check` 本地自检
- 支持在终端里进行多轮对话
- 支持从当前目录 `.env` 读取 `OPENAI_API_KEY` 或 `DEEPSEEK_API_KEY`

## 文件说明

- `main.py`：命令行入口、DeepSeek 兼容配置解析和对话循环
- `tools.py`：本地工具函数、工具 schema、工具分发
- `test_demo.py`：最小行为测试
- `requirements.txt`：当前 `.venv` 的依赖声明
- `.env.example`：环境文件模板

## 环境准备

当前项目使用本目录下的 `.venv`。

安装依赖：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## API Key

你可以用下面两种方式之一提供 API Key。

方式一：直接设置 shell 环境变量

```bash
export DEEPSEEK_API_KEY="在这里填你的 key"
```

方式二：使用当前目录的 `.env`

```bash
cp .env.example .env
```

然后编辑 `.env`：

```bash
DEEPSEEK_API_KEY="在这里填你的 key"
DEEPSEEK_BASE_URL="https://api.deepseek.com"
DEEPSEEK_MODEL="deepseek-v4-flash"
```

## 先做本地自检

这个命令不会访问远程 API：

```bash
.venv/bin/python main.py --self-check
```

## 运行 demo

默认会优先读取 `.env` 里的 `DEEPSEEK_MODEL`，否则回退到 `deepseek-v4-flash`：

```bash
.venv/bin/python main.py --prompt "东京现在天气怎么样？顺便把 25 摄氏度换算成华氏度。"
```

指定模型：

```bash
.venv/bin/python main.py --model deepseek-v4-flash --prompt "现在川崎几点？再告诉我旧金山的天气。"
```

## 终端多轮对话

直接运行下面的命令就会进入终端对话模式：

```bash
.venv/bin/python main.py
```

退出方式：

- 输入 `exit`
- 输入 `quit`
- 或直接发送 `Ctrl-D`

如果环境文件不叫 `.env`，可以显式指定：

```bash
.venv/bin/python main.py --env-file .env.local
```

如果你想临时改接口地址，也可以显式指定：

```bash
.venv/bin/python main.py --base-url https://api.deepseek.com
```

## 这个 demo 里的函数

- `get_weather(location)`：返回本地预设天气数据
- `convert_temperature(value, from_unit, to_unit)`：做摄氏度和华氏度换算
- `get_time_in_city(city)`：返回本地预设城市时区的当前时间

这些函数都是本地演示数据，不依赖第三方天气或时间服务。
