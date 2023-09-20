import json
import os

from haystack.preview import Pipeline, Document
from haystack.preview.document_stores import MemoryDocumentStore
from haystack.preview.components.retrievers import MemoryBM25Retriever
from haystack.preview.components.generators.openai.gpt35 import GPT35Generator
from haystack.preview.components.builders.answer_builder import AnswerBuilder
from haystack.preview.components.builders.prompt_builder import PromptBuilder
import random
from haystack.preview import component
from typing import Optional, List

import pydantic
from pydantic import BaseModel, ValidationError

import logging

logging.basicConfig()


logging.getLogger().setLevel(logging.INFO)

class City(BaseModel):
    name: str
    country: str
    population: int

class CitiesData(BaseModel):
    cities: List[City]

schema = CitiesData.schema_json(indent=2)
print(schema)

print(str(CitiesData))

@component
class OutputParser():
    def __init__(self, pydantic_model:pydantic.BaseModel):
        self.pydantic_model = pydantic_model

    @component.output_types(valid=List[str], invalid=Optional[List[str]], error_message=Optional[str])
    def run(
            self,
            replies: List[str]):
        with open("/Users/bijaygurung/work/haystack-demos/auto_fixing_parser_v2/outputs.txt", "a+") as f:
            f.write(replies[0].replace("\n", "") + "\n")

        # create a corrupt json with 40% probability (for demo purposes)
        if random.randint(0, 100) < 40:
            replies[0] = "Corrupt Key" + replies[0]
        try:
            output_dict = json.loads(replies[0])
            self.pydantic_model.parse_obj(output_dict)
            logging.info(f"Valid LLM output: {replies[0]}")
            return {"valid": replies, "invalid": None, "error_message": None}
        except (ValueError, ValidationError) as e:
            logging.info(f"Invalid LLM output: {replies[0]}, error: {e}")
            return {"valid": None, "invalid": replies, "error_message": str(e)}

#TODO let's eventually get rid of this component
@component
class FinalResult():
    @component.output_types(replies=List[str])
    def run(
            self,
            replies: List[str]):
        return {"replies": replies}



prompt_template = """
 Create a JSON object with information extracted from the following passage: {{passage}}. 
 Follow this JSON schema, but only return the actual instances without the additional schema definition:"
 {{schema}}
 Make sure your response is a dict and not a list.
 {% if replies %}
    We already got the following output: {{replies}}
    However, this doesn't comply with the format requirements from above. 
    Correct the output and try again. Just return the corrected output wihtout any extra explanations.
  {% endif %}
"""

def create_pipeline(pydantic_models_str:Optional[str]=None, pydantic_main_model_str:Optional[str]=None):
    pipeline = Pipeline(max_loops_allowed=5)
    pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
    pipeline.add_component(instance=GPT35Generator(api_key=os.environ.get("OPENAI_API_KEY")), name="llm")

    # ugly and dangerous, but for demo purposes
    if pydantic_models_str and pydantic_main_model_str:
        d = dict(locals(), **globals())
        exec(pydantic_models_str, d,d)
        pipeline.add_component(instance=OutputParser(pydantic_model=eval(pydantic_main_model_str, d, d)), name="output_parser")
        schema = eval(pydantic_main_model_str, d, d).schema_json(indent=2)

    pipeline.add_component(instance=FinalResult(), name="final_result")

    pipeline.connect("prompt_builder", "llm")
    pipeline.connect("llm", "output_parser")
    pipeline.connect("output_parser.invalid", "prompt_builder.replies")
    pipeline.connect("output_parser.valid", "final_result.replies")
    return pipeline, schema

if __name__ == "__main__":
    pipeline, schema = create_pipeline(pydantic_models_str="""
class City(BaseModel):
    name: str
    country: str
    population: int

class CitiesData(BaseModel):
    cities: List[City]""", pydantic_main_model_str="CitiesData")

    passage = "Berlin is the capital of Germany. It has a population of 3,850,809"
    result = pipeline.run({
        "prompt_builder": {"passage": passage, "schema": schema}
    })
    print(result)
