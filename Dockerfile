FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir requests anthropic httpx
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "claude-opus-4-6.py"]
