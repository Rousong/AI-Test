#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: test_demo.py
Author:
Date: 2026-05-08
Version: 1.0.0
Description: 为 OpenAI Agent demo 提供最小行为测试。
"""

import unittest

from main import run_self_check
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


if __name__ == "__main__":
    unittest.main()
