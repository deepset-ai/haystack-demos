import os
import json

import streamlit as st

from auto_fix_parser import create_pipeline

from config import INTERMEDIATE_OUTPUT_FILE


st.set_page_config(page_title="Mine City", layout="wide", initial_sidebar_state="expanded")

DEFAULT_DATA_MODEL = """
class City(BaseModel):
    name: str
    country: str
    population: int

class CitiesData(BaseModel):
    cities: List[City]
"""

DEFAULT_MAIN_DATA_MODEL = "CitiesData"

@st.cache_resource
def load_search_pipelines():
    return create_pipeline(pydantic_models_str=DEFAULT_DATA_MODEL, pydantic_main_model_str=DEFAULT_MAIN_DATA_MODEL)

pipeline, schema = load_search_pipelines()
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = pipeline
    st.session_state.schema = schema

if 'data_model' not in st.session_state:
    st.session_state.data_model = DEFAULT_DATA_MODEL

if 'main_data_model' not in st.session_state:
    st.session_state.main_data_model = DEFAULT_MAIN_DATA_MODEL

if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None
    st.session_state.intermediates = None

def extraction_handler():
    passage = st.session_state.input_passage

    if os.path.exists(INTERMEDIATE_OUTPUT_FILE):
        os.remove(INTERMEDIATE_OUTPUT_FILE)

    # Run Pipeline
    result = st.session_state.pipeline.run({
        "prompt_builder": {"passage": passage,
                           "schema": st.session_state.schema}
    })
    city = result['final_result']['replies'][0]

    st.session_state.extraction_result = city
    intermediates = []
    with open(INTERMEDIATE_OUTPUT_FILE) as f:
        intermediates = [l for l in f.readlines()]
    st.session_state.intermediates = intermediates



def update_pipeline():
    pipeline, schema = create_pipeline(pydantic_models_str=st.session_state.data_model,
                                       pydantic_main_model_str=st.session_state.main_data_model)
    st.session_state.pipeline = pipeline
    st.session_state.schema = schema


with st.sidebar:
    st.markdown("## Data Model")
    with st.form("data_model_form"):
        st.text_area(label="Data Model", placeholder=st.session_state.data_model, key="data_model")
        st.text_input(label="Main Data Model", placeholder=st.session_state.main_data_model, key="main_data_model")
        # st.button(label="Update Data Model", key="update_model", on_click=update_pipeline)
        st.form_submit_button(label="Update Data Model", on_click=update_pipeline)

st.markdown("# Extract City Data")
st.image("assets/pipeline.png")
st.text("Input a passage")
st.text_area(label="Passage:", placeholder="<passage-to-extract-from>", key="input_passage")

search_disabled = True
if "input_passage" in st.session_state and st.session_state.input_passage != "":
    search_disabled = False

st.button(label="Extract", key="extraction", disabled=search_disabled, on_click=extraction_handler)

if st.session_state.extraction_result is not None:
    # st.write(st.session_state.extraction_result)
    st.json(st.session_state.extraction_result)
    for i, intermediate in enumerate(st.session_state.intermediates):
        st.markdown(f"### Output {i}")
        st.write(intermediate)