from typing import List, Optional
from haystack.dataclasses import ByteStream
from fastapi import UploadFile
from hayhooks import BasePipelineWrapper, log
from haystack import Pipeline
from haystack.components.converters import TextFileToDocument
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore


class PipelineWrapper(BasePipelineWrapper):
    def setup(self) -> None:
        indexing = Pipeline()
        indexing.add_component("converter", TextFileToDocument())
        indexing.add_component("embedder", SentenceTransformersDocumentEmbedder())
        document_store = QdrantDocumentStore(host="qdrant")
        indexing.add_component("writer", DocumentWriter(document_store=document_store))
        indexing.connect("converter", "embedder")
        indexing.connect("embedder", "writer")

        self.pipeline = indexing

    def run_api(self, files: Optional[List[UploadFile]] = None) -> dict:
        if files:
            for file in files:
                text = file.file.read().decode("utf-8")
                log.debug(f"Indexing file: {file.filename}")

                self.pipeline.run(
                    {"converter": {"sources": [ByteStream(text.encode())]}}
                )
        else:
            log.debug("No files to index")

        return {"success": True}
