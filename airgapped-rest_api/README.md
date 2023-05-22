This folder contains a Dockerfile and a minimal pipeline setup to showcase an example of how to use Haystack in an airgapped environment.

### Important points to note:

1. While the container can run in an air-gapped environment, Internet access is required to build the container itself.
2. The number and size of the models used in the pipeline will increase the size of the resulting Docker image.
3. This is an overly simplistic Dockerfile provided for reference, some changes are expected to suit realistic use cases.

### Docker build process:

For the example here, you need [`docker compose`](https://docs.docker.com/compose/install/) installed on your system.

You’ll also need to clone the `haystack-demos` repository and run the following commands.

1. Read the `docker-compose.yml` , `Dockerfile` , and `retriever-reader.yml` files carefully.
2. Make any appropriate change: choose the desired pipeline and components, add or remove unnecessary commands from the `Dockerfile`.
3. `cd haystack-demos/airgapped-rest_api`
4. `docker compose build`

After building the Docker image, it should be possible to run the container without internet access.

### Docker run command:

`docker compose up`

### Sending requests to Docker:

To find Airgapped Docker’s IP address:

```bash
docker inspect <AIRGAPPED_DOCKER_ID> | grep IPAddress
```

You will need to replace the IP address in the commands below.

To index the test data through REST APIs:

```bash
find ./airgapped-test-data -name '*.txt' -exec curl --request POST --url http://<IPAddress>:8000/file-upload --header 'accept: application/json' --header 'content-type: multipart/form-data' --form files="@{}" --form meta=null \;
```

To verify if the data is written in the DocumentStore:

```bash
curl --request POST --url http://<IPAddress>:8000/documents/get_by_filters --header 'accept: application/json' --header 'content-type: application/json' --data '{"filters": {}}'
```

Sample Query through REST API:
```bash
curl --request POST --url http://<IPAddress>:8000/query --header 'accept: application/json' --header 'content-type: application/json' --data '{"query": "what is my name?"}' 
```