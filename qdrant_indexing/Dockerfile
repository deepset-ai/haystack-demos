FROM deepset/haystack:base-v2.1.1

EXPOSE 1416

RUN pip install qdrant-haystack hayhooks sentence-transformers

CMD ["hayhooks", "run", "--pipelines-dir", "/pipelines", "--host", "0.0.0.0"]
