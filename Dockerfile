FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE related_messages.py ./
COPY data ./data
RUN python -m pip install --no-cache-dir .
CMD ["related-messages", "solve", "data/demo.json"]
