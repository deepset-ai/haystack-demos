This folder contains an example of how to use [Docker Compose](https://docs.docker.com/compose/) to orchestrate
a simple web application serving two Haystack pipelines, one for indexing documents and a second to query them,
using [Qdrant](https://github.com/qdrant/qdrant) for storage and retrieval.

## Quickstart

To jump straight into running the demo, clone this repo and cd into the current folder:

```
$ git clone https://github.com/deepset-ai/haystack-demos.git
$ cd haystack-demos/qdrant_indexing
```

### Build and run the containers

Run this command to pull the Qdrant Docker image, build the one defined by this demo and run both of them:

```
$ docker-compose up -d
```

Eventually you should have two containers running, check it out by running:

```
$ docker-compose ps
```

To ensure the server is responding, visit [http://localhost:1416/docs](http://localhost:1416/docs#) in your browser:
you should see the OpenAPI documentation for the available endpoints. Two of these endpoints are for managing new
and existing pipelines:

- /deploy
- /undeploy/{pipeline_name}
- /draw/{pipeline_name}
- /status

The remaining ones expose two pipelines, named `qdrant_query` and `qdrant_indexing`: one is for indexing documents and
the other to query them:

- /qdrant_query
- /qdrant_indexing

You can look into the request and response schemas for each endpoint to see which parameters the pipelines expect,
along with which parameters they will return upon a successful run.

### Inspect the pipelines

To better understand what the two pipelines do, you can visualize their graph using the `/draw/` endpoint. For example,
to visualize `qdrant_indexing` you can point your browser to
[http://localhost:1416/draw/qdrant_indexing](http://localhost:1416/draw/qdrant_indexing).

### Index some text

This demo is trivial by design, as we want to focus on showing the building blocks of a Haystack
application. The only way to index data is by hitting the indexing endpoint passing some text,
let's see an example with `curl`:

```
curl -X "POST" "http://localhost:1416/qdrant_indexing" \
     -H 'Accept: application/json' \
     -H 'Content-Type: application/json' \
     -d $'{
  "converter": {
    "sources": [
      {
        "meta": {},
        "data": "RapidAPI for Mac is a full-featured HTTP client that lets you test and describe the APIs you build or consume. It has a beautiful native macOS interface to compose requests, inspect server responses, generate client code and export API definitions.",
        "mime_type": "text"
      }
    ],
    "meta": {}
  },
  "writer": {}
}'
```

Upon a successful request, you should get the following JSON response:

```
{
  "writer": {
    "documents_written": 1
  }
}
```

### Make a query

Similarly to indexing, we can query our data by making a POST request to the `/qdrant_query` endpoint:

```
curl -X "POST" "http://localhost:1416/qdrant_query" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
  "embedder": {
    "text": "What is RapidAPI?"
  },
  "retriever": {}
}'
```

The response should be something like:

```
{"retriever":{"documents":[{"id":"818170b2f8681bf03cc5b9534454366edcbd61325a4fb5e5154ec7b148322c16","content":"RapidAPI for Mac is a full-featured..."}]}}
```

## Where to go from here

This demo relies on Hayhooks, an application that serves Haystack pipelines as HTTP endpoints. Pipelines can be
added or removed while the server is running by using the `/deploy` and `/undeploy` endpoints respectively, but
Hayhooks can also load any Haystack pipeline it finds in yaml format under the directory you specify with
`--pipelines-dir` at startup.

In this demo we mount the folder `./pipelines` into the Docker container at the path `/pipelines`, and we tell Hayhooks
to look there for yaml files containing Haystack pipelines when it starts. You can add or change the pipelines in the
`./pipelines` local directory, restart Docker Compose and see your changes reflected in the server.

If you change the pipelines in a way that more dependencies are needed, say you want to use a different document store,
remember to also change the `Dockerfile` and `pip install` any additional requirement you might have. After changing
the `Dockerfile`, remember to rebuild the application container by running:

```
docker-compose build --no-cache
```

Happy Hacking!
