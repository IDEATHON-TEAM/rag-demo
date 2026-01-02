from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from dotenv import load_dotenv
from core.rag_builder import RagBuilder
from core.web3_service import get_web3_service
from core.storage import get_storage_service
from core.auth_middleware import require_nft_access, get_user_address_from_request
from core.query_package_service import get_query_package_service
from core.query_history_service import get_query_history_service
from core.ipfs_service import get_ipfs_service
from core.vector_hash_service import VectorHashService
import chromadb

# 加载环境变量
load_dotenv()

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

# 初始化服务
storage_service = get_storage_service()
query_history_service = get_query_history_service()
query_package_service = get_query_package_service()
ipfs_service = get_ipfs_service()
web3_service = None

# 初始化向量哈希服务（用于计算向量索引哈希）
# 注意：这里使用与RagBuilder相同的路径
import chromadb
chroma_client = chromadb.PersistentClient(path="/app/chroma_db")
vector_hash_service = VectorHashService(chroma_client)

# 尝试初始化Web3服务（如果配置了环境变量）
try:
    web3_service = get_web3_service()
    print("Web3 service initialized successfully")
except Exception as e:
    print(f"Warning: Web3 service not initialized: {e}")
    print("NFT features will be disabled. Please configure blockchain settings.")

@app.get("/")
def read_root():
    return {"message": "RAG Platform MVP Backend is running"}

# 1. 文件上传并创建 RAG（可选NFT铸造）
@app.post("/v1/rag/")
async def create_rag(
    file: UploadFile = File(...),
    price: int = Query(None, description="NFT price in smallest unit (wei). If provided, NFT will be minted."),
    mint_nft: bool = Query(False, description="Whether to mint NFT")
):
    try:
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 调用 RAG 构建器
        # 使用简单的 ID 生成策略
        rag_id = f"rag_{len(rag_engine_cache)+1}" 
        
        print(f"Building RAG for {file.filename}...")
        builder = RagBuilder()
        
        # 如果需要铸造NFT，上传到IPFS并计算向量哈希
        upload_to_ipfs = mint_nft and web3_service is not None
        
        query_engine, ipfs_cid, vector_hash = builder.build_from_file(file_path, upload_to_ipfs=upload_to_ipfs)
        
        rag_engine_cache[rag_id] = query_engine # 缓存
        print(f"RAG built successfully with ID: {rag_id}")
        
        # 准备NFT铸造数据（如果启用）
        mint_data = None
        if mint_nft and web3_service and ipfs_cid and vector_hash:
            try:
                if price is None:
                    price = 0  # 默认免费
                
                # 准备铸造数据（不实际铸造，由前端完成）
                mint_data = web3_service.prepare_mint_data(ipfs_cid, vector_hash, price)
                print(f"NFT mint data prepared for rag_id: {rag_id}")
            except Exception as e:
                print(f"Warning: Failed to prepare NFT mint data: {e}")
        
        response = {
            "rag_id": rag_id,
            "message": "RAG 创建成功"
        }
        
        if mint_data:
            response["mint_data"] = mint_data
            response["ipfs_cid"] = ipfs_cid
        
        return response
    except Exception as e:
        print(f"Error creating RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. 问答接口（带权限验证）
class QueryRequest(BaseModel):
    rag_id: str
    question: str
    user_address: str = None  # 可选，如果提供则进行权限验证

@app.post("/v1/chat/")
async def chat(request: QueryRequest):
    if request.rag_id not in rag_engine_cache:
        raise HTTPException(status_code=404, detail="RAG 不存在或已过期")
    
    # 如果提供了user_address且Web3服务可用，进行权限验证
    if request.user_address and web3_service:
        token_id = storage_service.get_token_id(request.rag_id)
        if token_id:
            has_access = web3_service.check_access(request.user_address, token_id)
            if not has_access:
                nft_info = web3_service.get_nft_info(token_id)
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Access denied",
                        "message": "You do not have access to this knowledge asset. Please purchase access first.",
                        "token_id": token_id,
                        "price": nft_info.get('price') if nft_info else None,
                        "purchase_required": True
                    }
                )
    
    try:
        query_engine = rag_engine_cache[request.rag_id]
        response = query_engine.query(request.question) # 执行查询
        
        # 提取答案和来源
        answer = str(response)
        sources = []
        
        # 尝试从响应中提取来源信息
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_info = {
                    "content": node.text if hasattr(node, 'text') else str(node),
                    "metadata": {}
                }
                if hasattr(node, 'node_metadata'):
                    source_info["metadata"] = node.node_metadata
                elif hasattr(node, 'metadata'):
                    source_info["metadata"] = node.metadata
                sources.append(source_info)
        
        # 计算向量索引哈希（用于NFT元数据）
        vector_hash = None
        try:
            collection_name = f"rag_{abs(hash(request.rag_id))}"
            vector_hash = vector_hash_service.calculate_vector_hash_hex32(collection_name)
        except Exception as e:
            print(f"Warning: Failed to calculate vector hash: {e}")
        
        # 保存查询历史
        query_id = query_history_service.save_query(
            question=request.question,
            answer=answer,
            sources=sources,
            rag_id=request.rag_id,
            user_address=request.user_address or "anonymous",
            vector_hash=vector_hash
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "rag_id": request.rag_id,
            "query_id": query_id
        }
    except HTTPException:
        raise
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

# 4. 准备NFT铸造数据
@app.get("/v1/nft/prepare_mint")
async def prepare_mint(rag_id: str = Query(..., description="RAG ID"), price: int = Query(0, description="NFT price in wei")):
    """
    为已存在的RAG准备NFT铸造数据
    返回铸造所需的所有信息，由前端完成实际铸造
    """
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    if rag_id not in rag_engine_cache:
        raise HTTPException(status_code=404, detail="RAG 不存在")
    
    try:
        # 需要重新计算IPFS CID和向量哈希
        # 这里简化处理，假设可以从rag_id获取文件路径
        # 实际应该存储文件路径或从ChromaDB获取collection信息
        
        # 临时方案：返回错误提示，建议在上传时同时准备
        raise HTTPException(
            status_code=400,
            detail="请在上传文档时同时启用NFT铸造（mint_nft=true）。如果已上传，需要重新上传并启用NFT铸造。"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. 获取NFT信息
@app.get("/v1/nft/{rag_id}")
async def get_nft_info(rag_id: str):
    """根据rag_id获取NFT信息"""
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    token_id = storage_service.get_token_id(rag_id)
    if not token_id:
        raise HTTPException(status_code=404, detail=f"No NFT found for rag_id: {rag_id}")
    
    nft_info = web3_service.get_nft_info(token_id)
    if not nft_info:
        raise HTTPException(status_code=404, detail=f"NFT {token_id} not found")
    
    owner = web3_service.get_owner(token_id)
    
    return {
        "rag_id": rag_id,
        "token_id": token_id,
        "owner": owner,
        **nft_info
    }

# 5. 购买访问权限（前端调用，实际支付在链上完成）
@app.post("/v1/nft/{token_id}/purchase")
async def purchase_access(token_id: int, user_address: str = Query(..., description="User wallet address")):
    """
    购买NFT访问权限
    注意：实际的支付交易需要在链上完成（前端调用合约）
    此接口用于验证购买状态
    """
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    # 检查用户是否已有权限
    has_access = web3_service.check_access(user_address, token_id)
    if has_access:
        return {
            "message": "User already has access",
            "token_id": token_id,
            "has_access": True
        }
    
    # 获取NFT信息
    nft_info = web3_service.get_nft_info(token_id)
    if not nft_info:
        raise HTTPException(status_code=404, detail=f"NFT {token_id} not found")
    
    return {
        "message": "Please complete the purchase transaction on-chain",
        "token_id": token_id,
        "price": nft_info.get('price'),
        "has_access": False,
        "contract_address": web3_service.contract_address,
        "purchase_function": "purchaseAccess(uint256 tokenId)"
    }

# 6. 将查询结果铸造为NFT
class MintQueryRequest(BaseModel):
    query_id: str
    price: int
    user_address: str

@app.post("/v1/nft/mint_query")
async def mint_query(request: MintQueryRequest):
    """
    将查询结果铸造为NFT
    
    Args:
        query_id: 查询记录ID
        price: NFT价格（wei）
        user_address: 用户钱包地址
    """
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    # 获取查询记录
    query_record = query_history_service.get_query(query_id=request.query_id)
    if not query_record:
        raise HTTPException(status_code=404, detail=f"Query {request.query_id} not found")
    
    # 验证用户权限
    if query_record["user_address"] != request.user_address:
        raise HTTPException(status_code=403, detail="You can only mint your own queries")
    
    # 检查是否已经铸造
    if query_record.get("minted_as_nft"):
        raise HTTPException(
            status_code=400,
            detail=f"Query already minted as NFT (token_id: {query_record.get('nft_token_id')})"
        )
    
    try:
        # 打包查询结果
        package = query_package_service.package_query_result(
            question=query_record["question"],
            answer=query_record["answer"],
            sources=query_record["sources"],
            rag_id=query_record["rag_id"],
            user_address=request.user_address,
            vector_hash=query_record.get("vector_hash"),
            metadata=query_record.get("metadata", {})
        )
        
        # 上传到IPFS
        ipfs_cid = ipfs_service.upload_query_package(package)
        
        # 计算向量索引哈希（如果还没有）
        vector_hash_hex = query_record.get("vector_hash")
        if not vector_hash_hex:
            try:
                collection_name = f"rag_{abs(hash(query_record['rag_id']))}"
                vector_hash_hex = vector_hash_service.calculate_vector_hash_hex32(collection_name)
            except Exception as e:
                print(f"Warning: Failed to calculate vector hash: {e}")
                vector_hash_hex = "0x" + "0" * 64  # 默认值
        
        # 准备铸造数据（实际铸造由前端完成）
        # 将vector_hash转换为bytes32格式
        vector_hash_bytes32 = bytes.fromhex(vector_hash_hex[:64])
        
        return {
            "query_id": request.query_id,
            "ipfs_cid": ipfs_cid,
            "vector_hash_hex": vector_hash_hex,
            "vector_hash_bytes32": vector_hash_bytes32.hex(),
            "price": request.price,
            "mint_data": {
                "ipfs_cid": ipfs_cid,
                "vector_hash_hex": vector_hash_hex,
                "price": request.price
            },
            "message": "Mint data prepared. Please call the contract mintKnowledgeNFT function from frontend."
        }
    except Exception as e:
        print(f"Error preparing mint data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 7. 获取查询历史
@app.get("/v1/query/history")
async def get_query_history(
    rag_id: str = Query(None, description="RAG ID (optional)"),
    user_address: str = Query(None, description="User address (optional)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    获取查询历史
    
    Args:
        rag_id: 可选，过滤特定知识库
        user_address: 可选，过滤特定用户
        page: 页码（从1开始）
        page_size: 每页大小
    """
    history = query_history_service.get_query_history(
        rag_id=rag_id,
        user_address=user_address,
        page=page,
        page_size=page_size
    )
    return history

# 8. NFT市场列表
@app.get("/v1/nft/marketplace")
async def get_nft_marketplace(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    category: str = Query(None, description="Category filter (optional)"),
    sort_by: str = Query("recent", description="Sort by: price, recent, sales")
):
    """
    获取NFT市场列表
    
    注意：这是一个简化实现，实际应该从链上或数据库获取NFT列表
    """
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    # 从存储服务获取所有映射的NFT
    mappings = storage_service.list_all_mappings()
    
    nfts = []
    for rag_id, token_id in mappings.items():
        try:
            nft_info = web3_service.get_nft_info(token_id)
            if nft_info and nft_info.get('isActive'):
                owner = web3_service.get_owner(token_id)
                nfts.append({
                    "token_id": token_id,
                    "rag_id": rag_id,
                    "owner": owner,
                    **nft_info
                })
        except Exception as e:
            print(f"Error getting NFT info for token {token_id}: {e}")
            continue
    
    # 排序
    if sort_by == "price":
        nfts.sort(key=lambda x: x.get('price', 0))
    elif sort_by == "sales":
        nfts.sort(key=lambda x: x.get('totalSales', 0), reverse=True)
    else:  # recent
        nfts.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
    
    # 分页
    total = len(nfts)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_nfts = nfts[start:end]
    
    return {
        "nfts": paginated_nfts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

# 9. 获取用户拥有的NFT
@app.get("/v1/nft/my_nfts")
async def get_my_nfts(
    user_address: str = Query(..., description="User wallet address"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size")
):
    """
    获取用户拥有的NFT
    
    注意：这是一个简化实现，实际应该从链上查询用户拥有的所有NFT
    """
    if not web3_service:
        raise HTTPException(status_code=503, detail="Web3 service not available")
    
    # 从存储服务获取所有映射的NFT
    mappings = storage_service.list_all_mappings()
    
    user_nfts = []
    for rag_id, token_id in mappings.items():
        try:
            owner = web3_service.get_owner(token_id)
            if owner.lower() == user_address.lower():
                nft_info = web3_service.get_nft_info(token_id)
                if nft_info:
                    user_nfts.append({
                        "token_id": token_id,
                        "rag_id": rag_id,
                        "owner": owner,
                        **nft_info
                    })
        except Exception as e:
            print(f"Error getting NFT info for token {token_id}: {e}")
            continue
    
    # 按创建时间倒序排序
    user_nfts.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
    
    # 分页
    total = len(user_nfts)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_nfts = user_nfts[start:end]
    
    return {
        "nfts": paginated_nfts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

