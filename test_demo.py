#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: test_demo.py
Author:
Date: 2026-05-08
Version: 1.0.0
Description: 为 OpenAI Agent demo 提供最小行为测试。
"""

from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from main import load_env_file, resolve_runtime_config, run_chat_session, run_self_check
from tools import call_tool, get_tool_definitions


class ToolContractTests(unittest.TestCase):
    # ------------------------------------------------------------
    # 校验工具定义
    # ------------------------------------------------------------
    def test_get_tool_definitions_exposes_three_tools(self) -> None:
        """
        校验工具定义列表中暴露了预期的三个工具

        Args:

        Returns:
            None
        """
        definitions = get_tool_definitions()
        names = [item["name"] for item in definitions]
        self.assertEqual(
            names,
            ["get_weather", "convert_temperature", "get_time_in_city"],
        )

    # ------------------------------------------------------------
    # 校验温度换算
    # ------------------------------------------------------------
    def test_call_tool_converts_temperature(self) -> None:
        """
        校验工具分发可以完成温度换算

        Args:

        Returns:
            None
        """
        result = call_tool(
            "convert_temperature",
            {"value": 25.0, "from_unit": "celsius", "to_unit": "fahrenheit"},
        )
        self.assertEqual(result["converted_value"], 77.0)

    # ------------------------------------------------------------
    # 校验本地自检
    # ------------------------------------------------------------
    def test_run_self_check_returns_summary(self) -> None:
        """
        校验本地自检返回预期摘要

        Args:

        Returns:
            None
        """
        summary = run_self_check()
        self.assertEqual(summary["tool_count"], 3)
        self.assertEqual(summary["conversion_check"]["converted_value"], 77.0)

    # ------------------------------------------------------------
    # 校验环境文件读取
    # ------------------------------------------------------------
    def test_load_env_file_reads_api_key(self) -> None:
        """
        校验可以从环境文件读取 API Key

        Args:

        Returns:
            None
        """
        with TemporaryDirectory() as temporary_directory:
            env_path = f"{temporary_directory}/.env"
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write("OPENAI_API_KEY=test-from-env-file\n")

            with patch.dict("os.environ", {}, clear=False):
                loaded_values = load_env_file(env_path)
                self.assertEqual(
                    loaded_values["OPENAI_API_KEY"],
                    "test-from-env-file",
                )

    # ------------------------------------------------------------
    # 校验 DeepSeek 运行时配置
    # ------------------------------------------------------------
    def test_resolve_runtime_config_uses_deepseek_settings(self) -> None:
        """
        校验运行时配置会正确读取 DeepSeek 的 base URL、模型和 API Key

        Args:

        Returns:
            None
        """
        with TemporaryDirectory() as temporary_directory:
            env_path = f"{temporary_directory}/.env"
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write("DEEPSEEK_API_KEY=deepseek-test-key\n")
                env_file.write("DEEPSEEK_BASE_URL=https://api.deepseek.com\n")
                env_file.write("DEEPSEEK_MODEL=deepseek-v4-flash\n")

            with patch.dict("os.environ", {}, clear=True):
                config = resolve_runtime_config(env_path, None, None)
                self.assertEqual(config["api_key"], "deepseek-test-key")
                self.assertEqual(config["base_url"], "https://api.deepseek.com")
                self.assertEqual(config["model"], "deepseek-v4-flash")

    # ------------------------------------------------------------
    # 校验终端对话循环
    # ------------------------------------------------------------
    def test_run_chat_session_handles_multiple_turns(self) -> None:
        """
        校验终端对话模式会保留多轮上下文并正确退出

        Args:

        Returns:
            None
        """
        prompts = iter(["你好", "再说一次", "quit"])
        outputs: list[str] = []
        calls: list[tuple[str, str, str | None]] = []

        def fake_input(prompt: str) -> str:
            """
            返回预设输入

            Args:
                prompt: 输入提示文本。

            Returns:
                下一条用户输入。
            """
            outputs.append(prompt)
            return next(prompts)

        def fake_output(message: str) -> None:
            """
            记录输出消息

            Args:
                message: 要输出的文本。

            Returns:
                None
            """
            outputs.append(message)

        def fake_turn_runner(
            prompt: str,
            model: str,
            previous_response_id: str | None,
        ) -> tuple[str, str]:
            """
            返回伪造的模型答复

            Args:
                prompt: 用户输入。
                model: 当前模型名称。
                previous_response_id: 上一轮响应 ID。

            Returns:
                伪造答复和新的响应 ID。
            """
            calls.append((prompt, model, previous_response_id))
            response_id = f"resp-{len(calls)}"
            return (f"reply:{prompt}", response_id)

        exit_code = run_chat_session(
            "demo-model",
            fake_turn_runner,
            input_func=fake_input,
            output_func=fake_output,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            calls,
            [
                ("你好", "demo-model", None),
                ("再说一次", "demo-model", "resp-1"),
            ],
        )
        self.assertIn("AI: reply:你好", outputs)
        self.assertIn("AI: reply:再说一次", outputs)
        self.assertIn("Bye.", outputs)


if __name__ == "__main__":
    unittest.main()
