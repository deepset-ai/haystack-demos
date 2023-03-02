# NOTE: This is a sample dockerfile for creating airgapped docker images for deploying
#       a Haystack pipeline. Follow the comments and make suitable changes for your use-case.
#
# Use-case showcased here:
#       Air-gapped Dockerfile for a Reader-Retriever pipeline.
#
# The reader is a custom trained locally available FARM Model.
# The retriever is a simple TF-IDF retriever.
#
# We also show how to cache HuggingFace models; both public and private. More details in the comments.
# CAUTION: Do not use `huggingface-cli login` inside the docker as it store the access token locally.
#          Here we prefer passing access token as an `ARG` because
#          we only need to use access token to cache required model.
#          Also, do not create an ENV variable containing access token,
#          as ENV variable remains active inside docker for its entire lifecycle.
#          To know further: https://huggingface.co/docs/hub/security-tokens#best-practices

# Choose appropriate Haystack base image (e.g. v1.14.0)
ARG HAYSTACK_BASE_IMAGE
FROM $HAYSTACK_BASE_IMAGE

# Haystack collects anonymous usage statistics for improvement purposes
# In this case your docker won't have access to the internet, so let's disable sending
# the usage statistics to Haystack.
ENV HAYSTACK_TELEMETRY_ENABLED=False

ARG hf_model_names
# `hf_model_names` should be a list of strings containing model names from HuggingFace hub
# e.g., "['hf/model1']"        or        "['hf/model1', 'hf/model2', 'hf/model3']"

#ARG hf_token=''

# To cache HuggingFace public models
RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names)"

# To cache HuggingFace private models
#RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names, $hf_token)"

# To copy model from local directory.
# NOTE: make sure to use `container_model_path` for your model_path in `retriever_reader.yml`
ARG local_model_path
ARG container_model_path
COPY $local_model_path $container_model_path

# To copy pipeline yml into the docker
ARG local_pipeline_path
ARG container_pipeline_path
COPY $local_pipeline_path $container_pipeline_path

# Exporting Pipeline path as an env variable
# Haystack reads this env variable to load the appropriate pipeline
ENV PIPELINE_YAML_PATH=$container_pipeline_path

# cmd for starting Haystack API server
#CMD ["gunicorn", "rest_api.application:app",  "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--timeout", "180"]
