import asyncio
import python_weather
from typing import AsyncGenerator, Annotated, Optional, List

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage, ImageContent
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.generators.utils import print_streaming_chunk
from haystack.tools import tool

from hayhooks import BasePipelineWrapper, async_streaming_generator
from hayhooks.open_webui import OpenWebUIEvent, create_notification_event, create_status_event, create_details_tag

class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        # Initialize tool
        @tool
        def get_weather(location: Annotated[str, "The location to get the weather for"]) -> dict:
            """A function to get the weather for a given location"""
            async def _fetch_weather():
                async with python_weather.Client(unit=python_weather.METRIC) as client:
                    weather = await client.get(location)
                    return {
                        "description": weather.description,
                        "temperature": weather.temperature,
                        "humidity": weather.humidity,
                        "precipitation": weather.precipitation,
                        "wind_speed": weather.wind_speed,
                        "wind_direction": weather.wind_direction
                    }

            return asyncio.run(_fetch_weather())
        
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
            system_prompt="You're a helpful agent",
            tools=[get_weather]
        )
    
    # Deploy Tool Calling Agent 
    def run_api(self, query: str, image_path: Optional[str] = None) -> str:
        if image_path:
            image = ImageContent.from_file_path(image_path)
            content_parts = [query, image]
        else:
            content_parts = [query]
        result = self.agent.run([ChatMessage.from_user(content_parts=content_parts)], streaming_callback=print_streaming_chunk)
        return result["last_message"].text
    
    # Open WebUI hooks
    def on_tool_call_start(
        self, tool_name: str, arguments: dict, id: str
    ) -> List[OpenWebUIEvent]:
        return [
            create_status_event(description=f"Tool call started: {tool_name}"),
            create_notification_event(
                notification_type="info",
                content=f"Tool call started: {tool_name}",
            )
        ]
    
    def on_tool_call_end(
        self,
        tool_name: str,
        arguments: dict,
        result: str,
        error: bool,  # noqa: ARG002
    ) -> list[OpenWebUIEvent]:
        return [
            create_status_event(
                description=f"Tool call ended: {tool_name} with arguments: {arguments}",
                done=True,
            ),
            create_notification_event(
                notification_type="success",
                content=f"Tool call ended: {tool_name}",
            ),
            create_details_tag(
                tool_name=tool_name,
                summary=f"Tool call result for {tool_name}",
                content=(f"```\nArguments:\n{arguments}\n\nResponse:\n{result}\n```"),
            ),
        ]
    
    # handles OpenAI-compatible chat completion requests asynchronously for Open WebUI
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