# Bakery Bot — деплой на Timeweb Cloud
FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Порт API для health check
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
