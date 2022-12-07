FROM python:3.10-slim

# copy code
COPY . /ui

# install as a package
RUN pip install --upgrade pip && \
    pip install /ui/

WORKDIR /ui
EXPOSE 8501

# cmd for running the API
CMD ["python", "-m", "streamlit", "run", "ui/webapp.py"]
