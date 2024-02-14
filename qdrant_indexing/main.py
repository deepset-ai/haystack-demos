from haystack import Pipeline
from haystack.dataclasses import ByteStream
from haystack.components.converters import TextFileToDocument
from haystack.components.writers import DocumentWriter
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

if __name__ == "__main__":
    indexing = Pipeline()
    indexing.add_component("converter", TextFileToDocument())
    indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
    indexing.add_component("writer", DocumentWriter(QdrantDocumentStore()))
    indexing.connect("converter", "embedder")
    indexing.connect("embedder", "writer")
    data = {
        "converter": {
            "sources": [
                ByteStream(
                    "Alerts are an extension of Markdown used to emphasize critical information. On GitHub, they are displayed with distinctive colors and icons to indicate the importance of the content.".encode()
                )
            ],
        }
    }
    print(indexing.run(data))
    print(indexing.dumps())
    # prints {'writer': {'documents_written': 1}}

    query = Pipeline()
    query.add_component("embedder", SentenceTransformersTextEmbedder())
    query.add_component("retriever", QdrantEmbeddingRetriever(QdrantDocumentStore()))
    query.connect("embedder.embedding", "retriever.query_embedding")
    print(query.run({"embedder": {"text": "GitHub"}}))
