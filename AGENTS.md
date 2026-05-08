# AGENTS.md

**始终使用当前目录的 `.venv`，并保持依赖声明同步。**

- 处理 Python 项目时，一定要使用当前目录下的 `.venv` 虚拟环境。
- 如果当前目录还没有 `.venv`，先创建虚拟环境并激活，再进行安装依赖、运行脚本、执行测试等操作。
- 安装任何依赖后，一定要同步更新 `requirements.txt`。
- 如果调整了依赖版本或删除了依赖，也要同步维护 `requirements.txt`，确保环境声明与实际安装状态一致。

## Python 编码与文档规范

这是一套偏严格的项目规范，适用于长期维护或需要多人 / 多 Agent 协作的 Python 自动化项目。一次性小脚本、测试辅助代码或探索性脚本，可以在不影响可读性和可维护性的前提下适当简化样板。

- 新增或修改 Python 模块时，文件头必须使用以下格式。`File:` 不要写死具体文件名，应替换为当前模块文件名：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: 当前模块文件名.py
Author:
Date:
Version: 1.0.0
Description:
"""
```

- 新增方法时，必须在方法定义外部紧邻上方添加如下格式的方法标识注释。这里不要写死固定人名，应替换为当前方法名或处理主题：

```python
# ------------------------------------------------------------
# 在这里填写方法名或处理主题
# ------------------------------------------------------------
```

- 每个函数或方法内部都必须编写 docstring，并至少包含方法简介、`Args:` 和 `Returns:`，推荐使用以下格式：

```python
"""
方法的简介

Args:

Returns:
"""
```

- 所有函数和方法都必须显式声明参数类型和返回值类型。
- 如果参数较多、返回值结构较复杂，必须在 docstring 中补充说明各参数含义、约束条件、默认值以及返回结果的结构。

## AI 动态维护区

<!-- AI-DYNAMIC-SECTION:START -->
## 项目概述

该项目是一个最小化的终端 Agent 命令行示例，核心功能包括：

- 使用 OpenAI 官方 Python SDK 调用 OpenAI-compatible 的 `chat.completions` 接口
- 提供 3 个本地 function calling 示例工具
- 演示工具调用回路与最终文本答复输出
- 提供无需真实 API Key 的本地自检和最小测试
- 支持终端中的多轮对话模式
- 支持从当前目录环境文件读取 DeepSeek 兼容配置

## 目录结构

```text
AI-Test/ # 项目根目录，存放 demo 代码、说明文档和虚拟环境配置。
├── .git/ # Git 仓库元数据目录。
├── .env.example # 提供 DeepSeek 兼容接口的环境文件模板。
├── .gitignore # 忽略虚拟环境、缓存、环境文件和 macOS 生成文件。
├── .venv/ # 当前项目专用的 Python 虚拟环境。
├── AGENTS.md # 项目级规则、代码概述和目录结构说明。
├── README.md # 说明 demo 的用途、运行方式和 API Key 配置方式。
├── docs/ # 存放设计文档、实施计划及其目录级说明。
├── main.py # 命令行入口，负责 DeepSeek 兼容配置解析、聊天循环和 function calling 回路。
├── requirements.txt # 与当前 `.venv` 安装状态同步的依赖声明。
├── test_demo.py # 验证工具定义、自检逻辑和基础行为的最小测试。
└── tools.py # 定义本地工具函数、工具 schema 和工具分发逻辑。
```
<!-- AI-DYNAMIC-SECTION:END -->
