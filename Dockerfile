FROM python:3.11-slim

# Устанавливаем системные зависимости для cryptography и cffi
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

EXPOSE 5000



CMD ["flask", "run", "--host=0.0.0.0"]