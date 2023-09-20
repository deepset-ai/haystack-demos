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

import logging
logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)

# 1) what are requirements for a custom component?
@component
class OutputParser():

    @component.output_types(valid=List[str], invalid=Optional[List[str]], error_message=Optional[str])
    def run(
        self,
        replies: List[str]):

        try:
            json.loads(replies[0])
            return {"valid": replies, "invalid": None, "error_message": None}
        except ValueError as e:
            return {"valid": None, "invalid": replies, "error_message": str(e)}


        
@component
class FinalResult():

    @component.output_types(replies=List[str])
    def run(
        self,
        replies: List[str]):
        
        return {"replies": replies}      

@component
class InputSwitch():

    @component.output_types(prompt=str)
    def run(self, prompt1: Optional[str]=None, prompt2: Optional[str]=None):
        if prompt1:
            return {"prompt": prompt1}

        if prompt2:
            return {"prompt": prompt2}



prompt_template = """
 {{query}}
"""

prompt_template_correction="""
{{query}}
We already got the following output: {{replies}}
However, this doesn't comply with the format requirements from above.
Error message: {{error_message}}
Please correct the output and try again.
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

# 1) how to make this one optional depending on output? additional classification node needed?
# 2) limit retries (?)


## Run the Pipeline
query  = ("Create a json file of the 3 biggest cities in the wolrld with the following fields: name, country, and population. None of the fields must be empty.")
result = pipeline.run({
    "prompt_builder":   {"query": query},
    "prompt_correction": {"query": query},
})

print(result)
