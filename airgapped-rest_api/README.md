This folder contains a Dockerfile and a minimal pipeline setup to showcase an example of how to use Haystack in an airgapped environment.

### Important points to note:

1. To build the container, you still need internet access.
2. The more and larger models you add to Docker, the larger its size will become.
3. This is just a sample Dockerfile provided for your reference. Feel free to modify it to suit your specific use case.

### Docker build process:

To build the Dockerfile, you need [`docker compose`](https://docs.docker.com/compose/install/) installed on your system or You can build the `Dockerfile` using the alternate process.

You’ll also need to clone the `haystack-demos` repository and run the following commands.

1. Read the `docker-compose.yml` , `Dockerfile` , and `retriever-reader.yml` files carefully and make appropriate changes.
2. `cd haystack-demos/airgapped-rest_api`
3. `docker compose build`

### Alternative build process:

Uncomment the last line in the Dockerfile and use the following commands. Pass the required arguments using `build-args`.

`docker build -t haystack_airgapped -f airgapped-rest_api/Dockerfile .`

After building the Docker image, it should be possible to run the docker without internet access.

### Docker run command:

`docker compose up`

If you have built the docker using the alternate process: `docker run -it --rm haystack_airgapped`

### Sending requests to Docker:

To find Airgapped Docker’s IP address:

```bash
docker inspect <AIRGAPPED_DOCKER_ID> | grep IPAddress
```

You will need to replace the IP address in the commands below.

To index the test data through REST APIs:

```bash
find ./airgapped-test-data -name '*.txt' -exec curl --request POST --url [http://<IPAddress>:8000/file-upload](http://172.17.0.2:8000/file-upload) --header 'accept: application/json' --header 'content-type: multipart/form-data' --form files="@{}" --form meta=null \;
```

To verify if the data is written in the DocumentStore:

```bash
curl --request POST --url [http://<IPAddress>](http://172.17.0.2:8000/file-upload)[:8000/documents/get_by_filters](http://172.17.0.3:8000/documents/get_by_filters) --header 'accept: application/json' --header 'content-type: application/json' --data '{"filters": {}}'
```

Sample Query through REST API:
```bash
curl --request POST --url [http://<IPAddress>:](http://172.17.0.2:8000/file-upload)[8000/query](http://172.17.0.3:8000/query) --header 'accept: application/json' --header 'content-type: application/json' --data '{"query": "what is my name?"}' 
```