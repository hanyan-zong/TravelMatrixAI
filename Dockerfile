FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends fonts-noto-cjk libjpeg62-turbo-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY content_pipeline/ content_pipeline/
COPY api.py .
COPY ["BWS碎片化整理 - 2026年05月25日 chatGPT清洗过的.xlsx", "./"]

RUN mkdir -p output

EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
