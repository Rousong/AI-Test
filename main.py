#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: main.py
Author:Zongkun Yu
Date: 2026-05-08
Version: 1.0.0
Description: 提供兼容 DeepSeek OpenAI 风格接口的命令行 Agent 入口。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Callable

from tools import call_tool, get_time_in_city, get_tool_definitions, get_weather

SYSTEM_INSTRUCTIONS = (
    "You are a demo agent. Use the provided tools when they help. "
    "If a tool result already answers the user, summarize it clearly."
)
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"


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
        description="Run a minimal terminal agent with an OpenAI-compatible API.",
    )
    parser.add_argument(
        "--prompt",
        help="User prompt to send to the OpenAI API.",
    )
    parser.add_argument(
        "--model",
        help="Model name. Falls back to env vars or deepseek-v4-flash.",
    )
    parser.add_argument(
        "--base-url",
        help="API base URL. Falls back to env vars or https://api.deepseek.com.",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Run local checks without calling the OpenAI API.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Environment file path. Default: .env",
    )
    return parser


# ------------------------------------------------------------
# 读取环境文件
# ------------------------------------------------------------
def load_env_file(env_path: str) -> dict[str, str]:
    """
    从环境文件中读取键值并写入进程环境变量

    Args:
        env_path: 环境文件路径。

    Returns:
        从文件中解析出的键值字典。
    """
    if not os.path.exists(env_path):
        return {}

    loaded_values: dict[str, str] = {}
    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            normalized_key = key.strip()
            normalized_value = value.strip().strip("'\"")
            loaded_values[normalized_key] = normalized_value
            if normalized_key not in os.environ:
                os.environ[normalized_key] = normalized_value
    return loaded_values


# ------------------------------------------------------------
# 解析运行时配置
# ------------------------------------------------------------
def resolve_runtime_config(
    env_path: str,
    model_override: str | None,
    base_url_override: str | None,
) -> dict[str, str]:
    """
    解析运行时所需的 API key、base URL 和模型配置

    Args:
        env_path: 环境文件路径。
        model_override: 命令行传入的模型覆盖值。
        base_url_override: 命令行传入的 base URL 覆盖值。

    Returns:
        包含 api_key、base_url 和 model 的配置字典。
    """
    load_env_file(env_path)

    api_key = (
        os.getenv("OPENAI_API_KEY", "").strip()
        or os.getenv("DEEPSEEK_API_KEY", "").strip()
    )
    if not api_key:
        raise RuntimeError(
            "Missing API key. Set OPENAI_API_KEY or DEEPSEEK_API_KEY in the shell or env file.",
        )

    base_url = (
        (base_url_override or "").strip()
        or os.getenv("OPENAI_BASE_URL", "").strip()
        or os.getenv("DEEPSEEK_BASE_URL", "").strip()
        or DEFAULT_BASE_URL
    )
    model = (
        (model_override or "").strip()
        or os.getenv("OPENAI_MODEL", "").strip()
        or os.getenv("DEEPSEEK_MODEL", "").strip()
        or DEFAULT_MODEL
    )
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


# ------------------------------------------------------------
# 构建 Chat Completions 工具定义
# ------------------------------------------------------------
def build_chat_tools() -> list[dict[str, object]]:
    """
    将本地工具定义转换为 Chat Completions 兼容格式

    Args:

    Returns:
        可传给 Chat Completions 的 tools 列表。
    """
    chat_tools: list[dict[str, object]] = []
    for definition in get_tool_definitions():
        chat_tools.append(
            {
                "type": "function",
                "function": {
                    "name": definition["name"],
                    "description": definition["description"],
                    "parameters": definition["parameters"],
                },
            }
        )
    return chat_tools


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
def require_api_key(env_path: str = ".env") -> str:
    """
    读取并校验 API key

    Args:

    Returns:
        环境变量中的 API Key 字符串。
    """
    return resolve_runtime_config(env_path, None, None)["api_key"]


# ------------------------------------------------------------
# 创建 OpenAI 客户端
# ------------------------------------------------------------
def create_openai_client(config: dict[str, str]) -> object:
    """
    创建 OpenAI 客户端

    Args:
        config: 已解析的运行时配置。

    Returns:
        已初始化的 OpenAI 客户端实例。
    """
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "The openai package is not installed. Install requirements first.",
        ) from error

    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


# ------------------------------------------------------------
# 提取聊天消息文本
# ------------------------------------------------------------
def extract_chat_message_text(message: object) -> str:
    """
    从 Chat Completions 的消息对象中提取文本

    Args:
        message: Chat Completions 返回的消息对象。

    Returns:
        提取到的文本内容。
    """
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
            else:
                text_parts.append(str(getattr(item, "text", "")))
        return "".join(text_parts).strip()
    return ""


# ------------------------------------------------------------
# 执行带工具调用的聊天请求
# ------------------------------------------------------------
def run_chat_completion_cycle(
    client: object,
    model: str,
    messages: list[dict[str, object]],
) -> str:
    """
    执行一轮带工具调用的 Chat Completions 对话

    Args:
        client: 已初始化的 OpenAI 兼容客户端。
        model: 要调用的模型名称。
        messages: 当前会话的消息历史，会在原地追加 assistant 和 tool 消息。

    Returns:
        当前轮最终生成的文本答复。
    """
    tools = build_chat_tools()

    for _ in range(5):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        assistant_message = response.choices[0].message
        tool_calls = getattr(assistant_message, "tool_calls", None) or []

        if not tool_calls:
            final_text = extract_chat_message_text(assistant_message)
            if final_text:
                messages.append({"role": "assistant", "content": final_text})
                return final_text
            raise RuntimeError("The model returned no text output.")

        messages.append(assistant_message.model_dump(exclude_none=True))

        for tool_call in tool_calls:
            arguments = json.loads(tool_call.function.arguments or "{}")
            result = call_tool(tool_call.function.name, arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    raise RuntimeError("Function calling exceeded the demo loop limit.")


# ------------------------------------------------------------
# 执行单次请求
# ------------------------------------------------------------
def run_agent_prompt(
    prompt: str,
    model: str | None,
    env_path: str = ".env",
    base_url: str | None = None,
) -> str:
    """
    执行单次用户请求并返回最终文本

    Args:
        prompt: 用户问题。
        model: 要调用的模型名称。
        env_path: 环境文件路径。

    Returns:
        模型最终返回的文本答复。
    """
    config = resolve_runtime_config(env_path, model, base_url)
    client = create_openai_client(config)
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": prompt},
    ]
    return run_chat_completion_cycle(client, config["model"], messages)


# ------------------------------------------------------------
# 构建终端对话执行器
# ------------------------------------------------------------
def build_chat_turn_runner(
    model: str | None,
    env_path: str = ".env",
    base_url: str | None = None,
) -> Callable[[str, str, str | None], tuple[str, str]]:
    """
    构建带历史上下文的终端对话执行器

    Args:
        model: 模型覆盖值。
        env_path: 环境文件路径。
        base_url: base URL 覆盖值。

    Returns:
        可供终端对话循环调用的单轮执行函数。
    """
    config = resolve_runtime_config(env_path, model, base_url)
    client = create_openai_client(config)
    message_history: list[dict[str, object]] = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
    ]
    turn_index = 0

    # ------------------------------------------------------------
    # 执行单轮终端对话
    # ------------------------------------------------------------
    def run_turn(
        prompt: str,
        _: str,
        __: str | None,
    ) -> tuple[str, str]:
        """
        执行一轮终端对话并保留消息历史

        Args:
            prompt: 用户输入。
            _: 与 run_chat_session 接口对齐的模型占位参数。
            __: 与 run_chat_session 接口对齐的上下文占位参数。

        Returns:
            当前轮的模型答复和一个伪造的轮次 ID。
        """
        nonlocal turn_index
        message_history.append({"role": "user", "content": prompt})
        reply = run_chat_completion_cycle(client, config["model"], message_history)
        turn_index += 1
        return reply, f"turn-{turn_index}"

    return run_turn


# ------------------------------------------------------------
# 运行终端对话循环
# ------------------------------------------------------------
def run_chat_session(
    model: str,
    turn_runner: Callable[[str, str, str | None], tuple[str, str]],
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> int:
    """
    运行终端中的多轮对话会话

    Args:
        model: 要调用的模型名称。
        turn_runner: 执行单轮对话的函数。
        input_func: 输入函数，默认使用内置 input。
        output_func: 输出函数，默认使用内置 print。

    Returns:
        进程退出码，0 表示正常退出。
    """
    previous_response_id: str | None = None
    output_func("Interactive chat started. Type 'exit' or 'quit' to leave.")

    while True:
        try:
            prompt = input_func("You: ").strip()
        except EOFError:
            output_func("Bye.")
            return 0

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            output_func("Bye.")
            return 0

        try:
            reply, previous_response_id = turn_runner(
                prompt,
                model,
                previous_response_id,
            )
        except Exception as error:  # noqa: BLE001
            output_func(f"Error: {error}")
            continue

        output_func(f"AI: {reply}")


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
        try:
            require_api_key(args.env_file)
        except Exception as error:  # noqa: BLE001
            print(f"Error: {error}", file=sys.stderr)
            return 1
        config = resolve_runtime_config(
            args.env_file,
            args.model,
            args.base_url,
        )
        return run_chat_session(
            config["model"],
            build_chat_turn_runner(
                args.model,
                args.env_file,
                args.base_url,
            ),
        )

    try:
        result = run_agent_prompt(
            args.prompt,
            args.model,
            args.env_file,
            args.base_url,
        )
    except Exception as error:  # noqa: BLE001
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
