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
from pydantic import BaseModel

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

@component
class OutputParser():

    @component.output_types(valid=List[str], invalid=Optional[List[str]], error_message=Optional[str])
    def run(
            self,
            replies: List[str]):
        # create a corrupt json with 50% probability (for demo purposes)
        if random.randint(0, 100) < 50:
            replies[0] = "Corrupt Key" + replies[0]
        try:
            output_dict = json.loads(replies[0])
            CitiesData.parse_obj(output_dict)

            logging.info(f"Valid LLM output: {replies}")
            return {"valid": replies, "invalid": None, "error_message": None}
        except (ValueError, pydantic.error_wrappers.ValidationError) as e:
            logging.info(f"Invalid LLM output: {replies}")
            return {"valid": None, "invalid": replies, "error_message": str(e)}

#TODO let's eventually get rid of this component
@component
class FinalResult():

    @component.output_types(replies=List[str])
    def run(
            self,
            replies: List[str]):
        return {"replies": replies}

#TODO let's eventually get rid of this component
@component
class InputSwitch():

    @component.output_types(prompt=str)
    def run(self, prompt1: Optional[str] = None, prompt2: Optional[str] = None):
        if prompt1:
            return {"prompt": prompt1}

        if prompt2:
            return {"prompt": prompt2}


prompt_template = """
 {{query}}
 Schema:
 {{schema}}
"""

prompt_template_correction = """
{{query}}
Schema:
{{schema}}
We already got the following output: {{replies}}
However, this doesn't comply with the JSON format requirements from above.
Error message: {{error_message}}
Correct the output and try again. Just return the JSON without any extra explanations.
"""

pipeline = Pipeline(max_loops_allowed=5)
pipeline.add_component(instance=PromptBuilder(template=prompt_template), name="prompt_builder")
pipeline.add_component(instance=GPT35Generator(api_key=os.environ.get("OPENAI_API_KEY")), name="llm")

pipeline.add_component(instance=OutputParser(), name="output_parser")
pipeline.add_component(instance=PromptBuilder(template=prompt_template_correction), name="prompt_correction")
pipeline.add_component(instance=InputSwitch(), name="input_switch")
pipeline.add_component(instance=FinalResult(), name="final_result")

pipeline.connect("prompt_builder", "input_switch.prompt1")
pipeline.connect("input_switch", "llm.prompt")

pipeline.connect("llm", "output_parser")
pipeline.connect("output_parser.invalid", "prompt_correction.replies")
pipeline.connect("output_parser.error_message", "prompt_correction.error_message")
pipeline.connect("output_parser.valid", "final_result.replies")
pipeline.connect("prompt_correction", "input_switch.prompt2")


## Run the Pipeline
query = (
    "Create a json file of the 3 biggest cities in the world with the following fields: name, country, and population. None of the fields must be empty.")
result = pipeline.run({
    "prompt_builder": {"query": query, "schema": schema},
    "prompt_correction": {"query": query, "schema": schema},
})

print(result)
