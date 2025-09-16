from typing import AsyncGenerator, Optional

from haystack.components.agents import Agent
from haystack.dataclasses import ChatMessage, ImageContent
from haystack.components.generators.chat import OpenAIChatGenerator
from hayhooks import BasePipelineWrapper, async_streaming_generator

class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        self.agent = Agent(
            chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
            system_prompt="You're a helpful agent",
        )
    
    # Deploy Basic Agent 
    def run_api(self, query: str, image_path: Optional[str] = None) -> str:
        if image_path:
            image = ImageContent.from_file_path(image_path)
            content_parts = [query, image]
        else:
            content_parts = [query]
        result = self.agent.run([ChatMessage.from_user(content_parts=content_parts)])
        return result["last_message"].text

    # handles OpenAI-compatible chat completion requests asynchronously for Open WebUI
    # async def run_chat_completion_async(
    #     self, model: str, messages: list[dict], body: dict
    # ) -> AsyncGenerator[str, None]:
    #     chat_messages = [
    #         ChatMessage.from_openai_dict_format(message) for message in messages
    #     ]

    #     return async_streaming_generator(
    #         pipeline=self.agent,
    #         pipeline_run_args={
    #             "messages": chat_messages,
    #         },
    #     )