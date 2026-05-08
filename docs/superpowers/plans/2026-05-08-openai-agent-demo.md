# OpenAI Agent Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在当前目录实现一个基于 OpenAI Python SDK 和 Responses API 的最小命令行 demo，展示 function calling 的完整闭环。

**Architecture:** 代码保持在项目根目录，只拆成入口文件和工具文件两个 Python 模块。验证分成两层：一层是无需 API Key 的本地 `--self-check`，另一层是用户填写 Key 后的真实请求路径。

**Tech Stack:** Python 3 `.venv`、OpenAI Python SDK、标准库 `argparse` `json` `unittest`

---

### Task 1: 依赖与测试骨架

**Files:**
- Create: `test_demo.py`
- Modify: `requirements.txt`

- [ ] **Step 1: 写出失败的测试**

```python
import unittest

from tools import call_tool, get_tool_definitions


class ToolContractTests(unittest.TestCase):
    def test_get_tool_definitions_exposes_three_tools(self) -> None:
        definitions = get_tool_definitions()
        names = [item["name"] for item in definitions]
        self.assertEqual(
            names,
            ["get_weather", "convert_temperature", "get_time_in_city"],
        )

    def test_call_tool_converts_temperature(self) -> None:
        result = call_tool(
            "convert_temperature",
            {"value": 25.0, "from_unit": "celsius", "to_unit": "fahrenheit"},
        )
        self.assertEqual(result["converted_value"], 77.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools'`

- [ ] **Step 3: 声明依赖**

```text
openai
```

- [ ] **Step 4: 再次确认测试仍然失败**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools'`

### Task 2: 实现工具模块

**Files:**
- Create: `tools.py`
- Test: `test_demo.py`

- [ ] **Step 1: 用已有测试作为目标实现最小工具模块**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: tools.py
Author:
Date: 2026-05-08
Version: 1.0.0
Description: 定义 OpenAI function calling demo 使用的本地工具与分发逻辑。
"""
```

- [ ] **Step 2: 实现 3 个工具和分发函数**

```python
def get_tool_definitions() -> list[dict[str, object]]:
    ...


def call_tool(name: str, arguments: dict[str, object]) -> dict[str, object]:
    ...
```

- [ ] **Step 3: 运行测试确认通过**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: PASS

### Task 3: 实现命令行入口

**Files:**
- Create: `main.py`
- Modify: `test_demo.py`

- [ ] **Step 1: 先补一个失败测试，约束本地自检入口**

```python
from main import run_self_check

def test_run_self_check_returns_summary(self) -> None:
    summary = run_self_check()
    self.assertEqual(summary["tool_count"], 3)
    self.assertEqual(summary["conversion_check"]["converted_value"], 77.0)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: 实现命令行解析、Responses API 调用循环和自检入口**

```python
def run_self_check() -> dict[str, object]:
    ...


def main() -> int:
    ...
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: PASS

### Task 4: 文档与项目说明

**Files:**
- Create: `README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: 写 README**

```markdown
# OpenAI Agent Demo
```

- [ ] **Step 2: 更新项目根 AGENTS 动态区**

```markdown
<!-- AI-DYNAMIC-SECTION:START -->
...
<!-- AI-DYNAMIC-SECTION:END -->
```

- [ ] **Step 3: 运行最终验证**

Run: `.venv/bin/python -m unittest test_demo.py -v`
Expected: PASS

Run: `.venv/bin/python main.py --self-check`
Expected: self-check summary printed with 3 tools

Run: `.venv/bin/python main.py --help`
Expected: usage text printed
