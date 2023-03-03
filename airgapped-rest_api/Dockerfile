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

# Use a base image providing the desired Haystack version (e.g. `cpu-v1.14.0`)
ARG HAYSTACK_BASE_IMAGE
FROM $HAYSTACK_BASE_IMAGE

# Haystack collects anonymous usage statistics for improvement purposes.
# The container won't have access to the internet, so we disable the telemetry service altogether.
ENV HAYSTACK_TELEMETRY_ENABLED=False

# `hf_model_names` should be a list of strings containing the model names as they appear in HuggingFace hub,
# for example: "['deepset/roberta-base-squad2']" or "['deepset/minilm-uncased-squad2', 'bert-base-uncased']"
ARG hf_model_names

# The following instruction will download the models listed in `hf_models_names`. If one or more models
# in the list are private, remove or comment the following line and see below what to do instead.
RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names)"

# If one or more models listed in `hf_model_names` is private, we need to provide a valid HuggingFace API token.
# Uncomment the following two lines and be sure to pass the `hf_token` argument to the `docker build` command:
#ARG hf_token=''
#RUN python3 -c "from haystack.utils.docker import cache_models;cache_models($hf_model_names, $hf_token)"

# The following lines will copy the models we downloaded previously into the Docker image. We need to specify
# both the local path containing the model (`local_model_path') and the path inside the Docker image where
# we want to copy it (`container_model_path`).
# NOTE: make sure to use the same value you passed to `container_model_path`
#       for the `model_path` field inside the pipeline definition file (in this case,  `retriever_reader.yml`)
ARG local_model_path
ARG container_model_path
COPY $local_model_path $container_model_path

# The following lines will copy the pipeline definition file into the Docker image.
# The logic is the same as for the models.
ARG local_pipeline_path
ARG container_pipeline_path
COPY $local_pipeline_path $container_pipeline_path

# Haystack will read this environment variable to load the appropriate pipeline when the container starts:
ENV PIPELINE_YAML_PATH=$container_pipeline_path

# The following line will start the Haystack API server when the container starts.
CMD ["gunicorn", "rest_api.application:app",  "-b", "0.0.0.0", "-k", "uvicorn.workers.UvicornWorker", "--workers", "1", "--timeout", "180"]
