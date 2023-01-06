#!/bin/bash
set -e
set -o pipefail

# Build can be customized using env vars:
#
# - DATA_IMAGE_NAME is the name of the Docker image containing the indexed data, it defaults
#   to deepset/elasticsearch-countries-and-capitals
# - DATA_IMAGE_PLATFORM is the target platform, defaults to current platform if not set. It must
#   be a valid string that can be passed to --platform, for example linux/amd64 or linux/arm64
# - DATA_IMAGE_PUSH if set, image will be pushed to Docker Hub
#

# STEP 0: initialize config variables
: "${DATA_IMAGE_NAME:=deepset/elasticsearch-countries-and-capitals}"
: "${HAYSTACK_IMAGE_NAME:=deepset/haystack:cpu-main}"
: "${DATASET_DIR:=dataset}"
: "${NETWORK:=explore_the_world}"

if [ -z "$DATA_IMAGE_PLATFORM" ]
then
    image_name=$DATA_IMAGE_NAME
    build_cmd="docker build -t $DATA_IMAGE_NAME -f Dockerfile.elasticsearch ."
else
    # If you're building multi-platform images locally, setup docker driver before running this script,
    # something like:
    # docker buildx create --use --name multi-builder --platform linux/amd64,linux/arm64

    # replace any / char with _ in DATA_IMAGE_PLATFORM to use it as Docker tag
    image_name=$DATA_IMAGE_NAME:${DATA_IMAGE_PLATFORM//\//_}
    build_cmd="docker buildx build -o type=docker -t $image_name --platform $DATA_IMAGE_PLATFORM -f Dockerfile.elasticsearch ."
fi

# STEP 1: build the empty Elasticsearch container for the target platform
echo "Building Elasticsearch container: ${build_cmd}"
$build_cmd

# STEP 2: create a Docker network to let Haystack talk to Elasticsearch. This is what
# docker-compose does under the hood, but we do it manually in this script. The command
# won't do anything if the network already exists (see the "|| true").
echo "Creating dedicated network..."
docker network create ${NETWORK} || true

# STEP 3: run the Elasticsearch container and wait until it can actually accept connections.
echo "Running Elasticsearch..."
docker rm -f elasticsearch
es_id=`docker run -d --name elasticsearch -p 9200:9200 --network ${NETWORK} $image_name`
until [ `docker inspect -f {{.State.Health.Status}} $es_id` = "healthy" ]; do
    echo "Waiting for Elasticsearch to be ready..."
    sleep 5;
done;

# STEP 4: run Haystack behind the rest_api from the official Docker image and wait for it to be ready
echo "Running Haystack..."
# We can use the name of the elasticsearch container as the hostname because on the same Docker network
export DOCUMENTSTORE_PARAMS_HOST=elasticsearch
# Select one of the default pipelines
export PIPELINE_YAML_PATH=/opt/venv/lib/python3.10/site-packages/rest_api/pipeline/pipelines_dpr.haystack-pipeline.yml
# Increase the timeout to account for the first request that needs more time to setup the models
export GUNICORN_CMD_ARGS="--timeout=300"
hs_id=`docker run -d -p 8000:8000 --network ${NETWORK} -e "DOCUMENTSTORE_PARAMS_HOST=${DOCUMENTSTORE_PARAMS_HOST}" -e "PIPELINE_YAML_PATH=${PIPELINE_YAML_PATH}" ${HAYSTACK_IMAGE_NAME}`
until [ "`curl -s --fail --max-time 1 http://localhost:8000/health || exit 0`" != "" ]; do
    echo "Waiting for Haystack to be ready..."
    sleep 5;
    docker logs --since=2s $hs_id
done;

# STEP 5: upload all the .txt files in the ./dataset folder
echo "Uploading dataset..."
for filename in ${DATASET_DIR}/*.txt; do
    [ -e "$filename" ] || continue
    echo "Uploading $filename..."
    curl -s -X POST -H 'Accept: application/json' -F files="@$PWD/$filename" http://127.0.0.1:8000/file-upload > /dev/null
done

# STEP 6: stop the containers, we're done
echo "Stopping containers..."
docker stop $es_id
docker stop $hs_id

# STEP 7: make the changes to the Elasticsearch image persistent so we don't need to re-index the dataset
# again
echo "Saving changes to a new Docker image..."
docker commit $es_id $image_name
docker image ls --digests

# STEP 8: push the image to Docker Hub, authentication is needed
if [ ! -z "$DATA_IMAGE_PUSH" ]
then
    echo "Pushing $image_name to Docker Hub..."
    docker push $image_name
fi

echo "Done"
