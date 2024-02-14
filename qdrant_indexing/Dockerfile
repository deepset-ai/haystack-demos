FROM deepset/haystack:base-v2.0.0-beta.7

EXPOSE 1416

RUN pip install qdrant-haystack hayhooks sentence-transformers

CMD ["hayhooks", "run", "--pipelines-dir", "/pipelines", "--host", "0.0.0.0"]
