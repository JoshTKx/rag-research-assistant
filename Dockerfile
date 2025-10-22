FROM python:3.11-slim 


RUN apt-get update && apt-get install -y\
    gcc\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY day3_api.py .
COPY day3_rag_query.py .
COPY day2_document_processing.py .
COPY migrate_to_persistent.py .

RUN mkdir -p /app/chroma_db

EXPOSE 8000

ENV PYTHONUNBUFFERED=1


HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "day3_api:app", "--host", "0.0.0.0", "--port", "8000"]