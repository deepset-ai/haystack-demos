FROM deepset/hayhooks:v1.7.0

RUN pip install "qdrant-haystack>=10.4.0" sentence-transformers sentence-transformers-haystack

CMD ["hayhooks", "run", "--host", "0.0.0.0"]
