# NOTE: This is a sample dockerfile for creating airgapped docker images
#       for deploying haystack pipelines in 3 different ways.
#       - Follow the comments and make suitable changes for your use-case.
#       Use-cases:
#       1. Air-gapped Reader pipeline with publically available HuggingFace (HF) Model
#       2. Air-gapped Reader pipeline with locally available FARM/HF Model
#       3. Air-gapped Reader pipeline with private HF Model

# Choose haystack version (i.e. v1.12.2) and Get pre-built haystack docker
ARG haystack_version=v1.12.2
ARG BASE_IMAGE=deepset/haystack:base-gpu-local

FROM $BASE_IMAGE

# Use-case 1:Air-gapped Reader pipeline with publically available HuggingFace (HF) Model

# model_name_or_path must be a model name from HuggingFace hub or a path to a local model
# i.e., "['hf/model1']"        or        "['hf/model1', 'hf/model2', 'hf/model3']"

ARG hf_model_names="['deepset/minilm-uncased-squad2']"

# Cache NLTK data and chosen HuggingFace models
RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names)"


# Use-case 3:Air-gapped Reader pipeline with private HF Model

# model_name_or_path must be a model name from HuggingFace hub or a path to a local model
# i.e., "['hf/model1']"        or        "['hf/model1', 'hf/model2', 'hf/model3']"

#ARG hf_model_names="['private_model']"
#ARG hf_token=''

# CAUTION: Do not use `huggingface-cli login` inside the docker as it store the access token locally
#          Here we prefer passing access token as an arg because,
#          we only need to use access token to cache required model.
#          Also, Do not create an ENV variable containing access token,
#          as ENV variable remains active inside docker for its entire lifecycle.
#          To know futher: https://huggingface.co/docs/hub/security-tokens#best-practices

# Cache NLTK data and chosen HuggingFace models
#RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names, $hf_token)"


#ARG local_pipeline_path=basic_reader.yml
ARG docker_pipeline_path=/opt/haystack_pipelines/basic_reader.yml
COPY basic_reader.yml /opt/haystack_pipelines/basic_reader.yml
ENV PIPELINE_YAML_PATH=$docker_pipeline_path


# cmd for deploying pipeline through API (note: "--preload" is not working with cuda)
CMD ["gunicorn", "rest_api.application:app",  "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--timeout", "180"]
