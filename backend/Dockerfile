FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 初始化种子数据并启动服务
CMD ["sh", "-c", "python data/seed.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
