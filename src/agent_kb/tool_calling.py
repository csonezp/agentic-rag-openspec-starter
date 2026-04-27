import json
from dataclasses import dataclass
from typing import Callable, Optional, Protocol


class ToolCallingClient(Protocol):
    def create_chat_completion(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> dict:
        """创建一次支持工具调用的聊天响应。"""


@dataclass(frozen=True)
class ToolRequest:
    call_id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class ToolDefinition:
    schema: dict
    handler: Callable[[], str]


def get_phase1_progress() -> str:
    return json.dumps(
        {
            "completed": [
                "Responses API 请求和响应结构",
                "基础聊天调用",
                "流式输出",
                "DeepSeek 官方 API 真实模型调用",
                "小 schema 结构化输出",
                "function/tool calling 与本地函数",
            ],
            "next": "记录延迟、token 使用量、模型名和错误",
        },
        ensure_ascii=False,
    )


def get_phase1_progress_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": "get_phase1_progress",
            "description": "获取当前 Agent 开发学习项目 Phase 1 的进度摘要。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }


def parse_tool_request(tool_call: dict) -> ToolRequest:
    function = tool_call.get("function", {})
    arguments_text = function.get("arguments") or "{}"
    try:
        arguments = json.loads(arguments_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"工具 arguments 不是合法 JSON：{exc.msg}") from exc

    if not isinstance(arguments, dict):
        raise ValueError("工具 arguments 必须是 JSON object")

    return ToolRequest(
        call_id=tool_call.get("id", ""),
        name=function.get("name", ""),
        arguments=arguments,
    )


class DryRunToolCallingClient:
    def create_chat_completion(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> dict:
        if len(messages) == 1:
            return {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "dry_run_call_1",
                        "type": "function",
                        "function": {
                            "name": "get_phase1_progress",
                            "arguments": "{}",
                        },
                    }
                ],
            }

        return {
            "role": "assistant",
            "content": "Phase 1 进度已通过本地函数读取：下一步是记录延迟、token 使用量、模型名和错误。",
        }


class ToolCallingRunner:
    def __init__(
        self,
        client: ToolCallingClient,
        tools: list[ToolDefinition],
    ) -> None:
        self._client = client
        self._tools = {
            tool.schema["function"]["name"]: tool for tool in tools
        }

    def run(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        tool_schemas = [tool.schema for tool in self._tools.values()]

        assistant_message = self._client.create_chat_completion(
            messages,
            tools=tool_schemas,
        )
        tool_calls = assistant_message.get("tool_calls", [])
        if not tool_calls:
            content = assistant_message.get("content")
            if content:
                return content
            raise RuntimeError("模型没有返回 tool_calls 或 content")

        messages.append(assistant_message)
        for tool_call in tool_calls:
            request = parse_tool_request(tool_call)
            if request.name not in self._tools:
                raise ValueError(f"未注册工具：{request.name}")
            if request.arguments:
                raise ValueError(f"工具 {request.name} 不接受参数")

            result = self._tools[request.name].handler()
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": request.call_id,
                    "content": result,
                }
            )

        final_message = self._client.create_chat_completion(messages)
        content = final_message.get("content")
        if not content:
            raise RuntimeError("模型最终回答为空")
        return content
