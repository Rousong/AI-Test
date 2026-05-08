#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: main.py
Author:
Date: 2026-05-08
Version: 1.0.0
Description: 提供 OpenAI Responses API function calling demo 的命令行入口。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from tools import call_tool, get_time_in_city, get_tool_definitions, get_weather


# ------------------------------------------------------------
# 构建命令行参数
# ------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器

    Args:

    Returns:
        配置好的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        description="Run a minimal OpenAI Responses API function calling demo.",
    )
    parser.add_argument(
        "--prompt",
        help="User prompt to send to the OpenAI API.",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.4-mini",
        help="OpenAI model name. Default: gpt-5.4-mini",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Run local checks without calling the OpenAI API.",
    )
    return parser


# ------------------------------------------------------------
# 提取函数调用
# ------------------------------------------------------------
def extract_function_calls(response: object) -> list[dict[str, str]]:
    """
    从 Responses API 返回对象中提取 function call 列表

    Args:
        response: OpenAI SDK 返回的响应对象。

    Returns:
        包含函数名、参数字符串和 call_id 的列表。
    """
    function_calls: list[dict[str, str]] = []
    for item in getattr(response, "output", []):
        if getattr(item, "type", "") != "function_call":
            continue
        function_calls.append(
            {
                "call_id": str(getattr(item, "call_id", "")),
                "name": str(getattr(item, "name", "")),
                "arguments": str(getattr(item, "arguments", "{}")),
            }
        )
    return function_calls


# ------------------------------------------------------------
# 提取最终文本
# ------------------------------------------------------------
def extract_output_text(response: object) -> str:
    """
    从 Responses API 返回对象中提取最终文本

    Args:
        response: OpenAI SDK 返回的响应对象。

    Returns:
        模型输出的文本内容。
    """
    output_text = getattr(response, "output_text", "")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    for item in getattr(response, "output", []):
        if getattr(item, "type", "") != "message":
            continue
        content_items = getattr(item, "content", [])
        for content in content_items:
            text_value = getattr(content, "text", "")
            if isinstance(text_value, str) and text_value.strip():
                return text_value.strip()

    return ""


# ------------------------------------------------------------
# 运行本地自检
# ------------------------------------------------------------
def run_self_check() -> dict[str, object]:
    """
    运行无需 API Key 的本地自检

    Args:

    Returns:
        包含工具数量与示例结果的摘要字典。
    """
    definitions = get_tool_definitions()
    weather_check = get_weather("Tokyo")
    conversion_check = call_tool(
        "convert_temperature",
        {"value": 25.0, "from_unit": "celsius", "to_unit": "fahrenheit"},
    )
    time_check = get_time_in_city("Kawasaki")
    return {
        "tool_count": len(definitions),
        "tool_names": [item["name"] for item in definitions],
        "weather_check": weather_check,
        "conversion_check": conversion_check,
        "time_check": time_check,
    }


# ------------------------------------------------------------
# 校验 API Key
# ------------------------------------------------------------
def require_api_key() -> str:
    """
    读取并校验 OPENAI_API_KEY

    Args:

    Returns:
        环境变量中的 API Key 字符串。
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Set it first, or run with --self-check.",
        )
    return api_key


# ------------------------------------------------------------
# 执行 OpenAI Agent 请求
# ------------------------------------------------------------
def run_agent_prompt(prompt: str, model: str) -> str:
    """
    使用 Responses API 运行带 function calling 的请求

    Args:
        prompt: 用户问题。
        model: 要调用的模型名称。

    Returns:
        模型最终返回的文本答复。
    """
    require_api_key()

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "The openai package is not installed. Install requirements first.",
        ) from error

    client = OpenAI()
    tools = get_tool_definitions()
    input_messages: list[dict[str, object]] = [
        {
            "role": "system",
            "content": (
                "You are a demo agent. Use the provided tools when they help. "
                "If a tool result already answers the user, summarize it clearly."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    for _ in range(5):
        response = client.responses.create(
            model=model,
            input=input_messages,
            tools=tools,
        )
        function_calls = extract_function_calls(response)
        if not function_calls:
            final_text = extract_output_text(response)
            if final_text:
                return final_text
            raise RuntimeError("The model returned no text output.")

        for function_call in function_calls:
            arguments = json.loads(function_call["arguments"])
            result = call_tool(function_call["name"], arguments)
            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call["call_id"],
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

    raise RuntimeError("Function calling exceeded the demo loop limit.")


# ------------------------------------------------------------
# 主程序入口
# ------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """
    执行命令行入口逻辑

    Args:
        argv: 可选的参数列表；为空时读取系统命令行参数。

    Returns:
        进程退出码，0 表示成功，1 表示失败。
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_check:
        print(json.dumps(run_self_check(), ensure_ascii=False, indent=2))
        return 0

    if not args.prompt:
        parser.error("either --prompt or --self-check is required")

    try:
        result = run_agent_prompt(args.prompt, args.model)
    except Exception as error:  # noqa: BLE001
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
