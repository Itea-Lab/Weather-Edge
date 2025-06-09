FROM python:3.10-slim
LABEL author="PancakesLmao <phucthin29@gmail.com>"
LABEL description="Dockerfile for edge device configuration"
LABEL version="1.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]