from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from core.rag_builder import RagBuilder

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# 简单的内存缓存，实际生产应使用 Redis
# 键为 rag_id，值为 query_engine 实例
rag_engine_cache = {} 

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "RAG Platform MVP Backend is running"}

# 1. 文件上传并创建 RAG
@app.post("/v1/rag/")
async def create_rag(file: UploadFile = File(...)):
    try:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 调用 RAG 构建器
        # 使用简单的 ID 生成策略
        rag_id = f"rag_{len(rag_engine_cache)+1}" 
        
        print(f"Building RAG for {file.filename}...")
        builder = RagBuilder()
        query_engine = builder.build_from_file(file_path) # 构建 RAG
        
        rag_engine_cache[rag_id] = query_engine # 缓存
        print(f"RAG built successfully with ID: {rag_id}")
        
        return {"rag_id": rag_id, "message": "RAG 创建成功"}
    except Exception as e:
        print(f"Error creating RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. 问答接口
class QueryRequest(BaseModel):
    rag_id: str
    question: str

@app.post("/v1/chat/")
async def chat(request: QueryRequest):
    if request.rag_id not in rag_engine_cache:
        raise HTTPException(status_code=404, detail="RAG 不存在或已过期")
    
    try:
        query_engine = rag_engine_cache[request.rag_id]
        response = query_engine.query(request.question) # 执行查询
        return {"answer": str(response)}
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. 获取定价预览（模拟）
@app.get("/v1/pricing_preview/")
async def get_pricing_preview(rag_id: str):
    # 这里可以模拟根据文件大小/页数计算价格
    return {"price_options": [
        {"type": "按次付费", "price": "0.1 元/次"},
        {"type": "包周套餐", "price": "10 元/周"},
        {"type": "企业买断", "price": "999 元/永久"},
    ]}

