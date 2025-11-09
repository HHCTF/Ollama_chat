FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tcl-dev \
        tk-dev \
        libx11-dev \
        libxext-dev \
        libxss1 \
        libnss3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ollama

COPY ollama_chat.py .

CMD ["bash", "-c", "exec python ollama_chat.py"]
