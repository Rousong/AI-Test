#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: tools.py
Author:
Date: 2026-05-08
Version: 1.0.0
Description: 定义 OpenAI function calling demo 使用的本地工具与分发逻辑。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


# ------------------------------------------------------------
# 获取天气数据
# ------------------------------------------------------------
def get_weather(location: str) -> dict[str, object]:
    """
    返回示例天气数据

    Args:
        location: 用户请求的地点名称。

    Returns:
        包含地点、天气描述和温度信息的字典。
    """
    normalized_location = location.strip().lower()
    preset_weather = {
        "tokyo": {"condition": "sunny", "temperature_celsius": 24},
        "kawasaki": {"condition": "cloudy", "temperature_celsius": 22},
        "san francisco": {"condition": "foggy", "temperature_celsius": 16},
        "new york": {"condition": "rainy", "temperature_celsius": 19},
    }
    weather = preset_weather.get(
        normalized_location,
        {"condition": "clear", "temperature_celsius": 21},
    )
    return {
        "location": location,
        "condition": weather["condition"],
        "temperature_celsius": weather["temperature_celsius"],
        "source": "local-demo-data",
    }


# ------------------------------------------------------------
# 换算温度
# ------------------------------------------------------------
def convert_temperature(value: float, from_unit: str, to_unit: str) -> dict[str, object]:
    """
    在摄氏度和华氏度之间换算温度

    Args:
        value: 原始温度数值。
        from_unit: 原始单位，只允许 celsius 或 fahrenheit。
        to_unit: 目标单位，只允许 celsius 或 fahrenheit。

    Returns:
        包含原始数值、目标数值和单位信息的字典。
    """
    normalized_from_unit = from_unit.strip().lower()
    normalized_to_unit = to_unit.strip().lower()

    if normalized_from_unit == normalized_to_unit:
        converted_value = value
    elif normalized_from_unit == "celsius" and normalized_to_unit == "fahrenheit":
        converted_value = (value * 9 / 5) + 32
    elif normalized_from_unit == "fahrenheit" and normalized_to_unit == "celsius":
        converted_value = (value - 32) * 5 / 9
    else:
        raise ValueError("Unsupported temperature units.")

    return {
        "original_value": value,
        "from_unit": normalized_from_unit,
        "to_unit": normalized_to_unit,
        "converted_value": round(converted_value, 2),
    }


# ------------------------------------------------------------
# 获取城市时间
# ------------------------------------------------------------
def get_time_in_city(city: str) -> dict[str, object]:
    """
    返回示例城市的当前本地时间

    Args:
        city: 城市名称。

    Returns:
        包含城市、UTC 偏移和 ISO 时间字符串的字典。
    """
    normalized_city = city.strip().lower()
    utc_offsets = {
        "tokyo": 9,
        "kawasaki": 9,
        "san francisco": -7,
        "new york": -4,
        "london": 1,
    }
    offset_hours = utc_offsets.get(normalized_city, 0)
    current_time = datetime.now(timezone(timedelta(hours=offset_hours)))
    return {
        "city": city,
        "utc_offset_hours": offset_hours,
        "local_time_iso": current_time.isoformat(timespec="seconds"),
        "source": "local-demo-data",
    }


# ------------------------------------------------------------
# 获取工具定义
# ------------------------------------------------------------
def get_tool_definitions() -> list[dict[str, object]]:
    """
    返回传给 OpenAI Responses API 的 function tools 定义

    Args:

    Returns:
        一个包含三个函数 schema 的列表。
    """
    return [
        {
            "type": "function",
            "name": "get_weather",
            "description": "Get demo weather data for a city or place name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or place name, for example Tokyo.",
                    }
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "convert_temperature",
            "description": "Convert a temperature between celsius and fahrenheit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Temperature value to convert.",
                    },
                    "from_unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Source temperature unit.",
                    },
                    "to_unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Target temperature unit.",
                    },
                },
                "required": ["value", "from_unit", "to_unit"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "get_time_in_city",
            "description": "Get demo local time information for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, for example Kawasaki.",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    ]


# ------------------------------------------------------------
# 分发工具调用
# ------------------------------------------------------------
def call_tool(name: str, arguments: dict[str, object]) -> dict[str, object]:
    """
    按工具名分发本地函数调用

    Args:
        name: 工具名称。
        arguments: 从模型工具调用中解析出的参数字典。

    Returns:
        对应工具函数返回的结果字典。
    """
    if name == "get_weather":
        return get_weather(str(arguments["location"]))
    if name == "convert_temperature":
        return convert_temperature(
            float(arguments["value"]),
            str(arguments["from_unit"]),
            str(arguments["to_unit"]),
        )
    if name == "get_time_in_city":
        return get_time_in_city(str(arguments["city"]))
    raise ValueError(f"Unknown tool: {name}")
