FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 trader && mkdir -p /home/trader/.local/bin && chown -R trader:trader /app /home/trader
ENV PATH=/home/trader/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=trader:trader . .
USER trader
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import sys; sys.exit(0)" || exit 1
CMD ["python", "claude-opus-4-6.py"]
