FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（如果需要处理图片或复杂PDF，可能需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要的目录
RUN mkdir -p uploads chroma_db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

