from typing import AsyncGenerator
from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage
from hayhooks import BasePipelineWrapper, async_streaming_generator
from haystack_integrations.tools.mcp import MCPToolset, StreamableHttpServerInfo
from haystack_integrations.components.generators.google_genai import (
    GoogleGenAIChatGenerator,
)
from hayhooks.open_webui import (
    OpenWebUIEvent,
    create_notification_event,
    create_status_event,
    create_details_tag,
)


system_message = """
You are an intelligent assistant equipped with tools for navigating the web.

You can use tools when appropriate, but not every task requires them — you also have strong reasoning and 
language capabilities.
If a request seems challenging, don't default to refusal due to perceived tool limitations. Instead, think creatively 
and attempt a solution using the skills you do have.
You are more capable than you might assume. Trust your abilities.
"""


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        server_info = StreamableHttpServerInfo(url="http://playwright-mcp:8931/mcp")

        chat_generator = GoogleGenAIChatGenerator(
            model="gemini-2.5-flash",
        )

        toolset = MCPToolset(
            server_info=server_info,
            tool_names=[
                "browser_navigate",
                "browser_snapshot",
                "browser_click",
                "browser_type",
                "browser_navigate_back",
                "browser_wait_for",
            ],
        )

        self.agent = Agent(
            chat_generator=chat_generator,
            tools=toolset,
            system_prompt=system_message,
            exit_conditions=["text"],
        )

    def on_tool_call_start(
        self, tool_name: str, arguments: str, id: str
    ) -> list[OpenWebUIEvent]:
        return [
            create_status_event(description=f"Tool call started: {tool_name}"),
            create_notification_event(
                notification_type="info",
                content=f"Tool call started: {tool_name}",
            ),
        ]

    def on_tool_call_end(
        self,
        tool_name: str,
        arguments: dict,
        result: str,
        error: bool,
    ) -> list[OpenWebUIEvent]:
        return [
            create_status_event(
                description=f"Tool call ended: {tool_name}",
                done=True,
            ),
            create_notification_event(
                notification_type="success",
                content=f"Tool call ended: {tool_name}",
            ),
            create_details_tag(
                tool_name=tool_name,
                summary=f"Tool call result for {tool_name}",
                content=f"```\nArguments:\n{arguments}\n\nResponse:\n{result}\n```",
            ),
        ]

    async def run_chat_completion_async(
        self, model: str, messages: list[dict], body: dict
    ) -> AsyncGenerator[str, None]:
        chat_messages = [
            ChatMessage.from_openai_dict_format(message) for message in messages
        ]

        return async_streaming_generator(
            on_tool_call_start=self.on_tool_call_start,
            on_tool_call_end=self.on_tool_call_end,
            pipeline=self.agent,
            pipeline_run_args={
                "messages": chat_messages,
            },
        )
