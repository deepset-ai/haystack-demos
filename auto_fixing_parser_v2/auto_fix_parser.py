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
 {{query}}
 ##
 Passage:
 {{passage}}
 ##
 Schema:
 {{schema}}
 {% if replies %}
    We already got the following output: {{replies}}
    However, this doesn't comply with the format requirements from above. 
    Correct the output and try again. Just return the corrected output wihtout any extra explanations.
  {% endif %}
"""

def create_pipeline():
    pipeline = Pipeline(max_loops_allowed=5)
    pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
    pipeline.add_component(instance=GPT35Generator(api_key=os.environ.get("OPENAI_API_KEY")), name="llm")

    pipeline.add_component(instance=OutputParser(pydantic_model=CitiesData), name="output_parser")
    pipeline.add_component(instance=FinalResult(), name="final_result")

    pipeline.connect("prompt_builder", "llm")
    pipeline.connect("llm", "output_parser")
    pipeline.connect("output_parser.invalid", "prompt_builder.replies")
    pipeline.connect("output_parser.valid", "final_result.replies")
    return pipeline

if __name__ == "__main__":
    pipeline = create_pipeline()

    query = (
        "Create a json file with the following fields extracted from the supplied passage: name, country, and population. None of the fields must be empty."
    )

    passage = "Berlin is the capital of Germany. It has a population of 3,850,809"
    result = pipeline.run({
        "prompt_builder": {"query": query, "schema": schema}
    })
    print(result)
