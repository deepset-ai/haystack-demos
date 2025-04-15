from haystack import Pipeline
from hayhooks import BasePipelineWrapper, log
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        query = Pipeline()
        query.add_component("embedder", SentenceTransformersTextEmbedder())
        query.add_component(
            "retriever", QdrantEmbeddingRetriever(QdrantDocumentStore(host="qdrant"))
        )
        query.connect("embedder.embedding", "retriever.query_embedding")

        self.pipeline = query

    def run_api(self, query: str) -> dict:
        log.debug(f"Querying with: '{query}'")
        return self.pipeline.run({"embedder": {"text": query}})
