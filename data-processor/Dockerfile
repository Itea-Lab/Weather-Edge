# syntax=docker/dockerfile:1.7
FROM python:3.10-slim
LABEL author="PancakesLmao <phucthin29@gmail.com>"
LABEL description="Dockerfile for edge processor configuration"
LABEL version="1.1"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]