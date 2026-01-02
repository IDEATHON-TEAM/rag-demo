from functools import wraps
from fastapi import HTTPException, Request
from typing import Optional
from .web3_service import get_web3_service
from .storage import get_storage_service

def require_nft_access(func):
    """
    权限验证装饰器
    检查用户是否有访问NFT的权限
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 从kwargs中获取请求对象
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")
        
        # 获取用户钱包地址（从请求头或请求体）
        user_address = None
        
        # 尝试从请求头获取
        user_address = request.headers.get('X-User-Address')
        
        # 如果请求头没有，尝试从请求体获取（如果是POST请求）
        if not user_address and hasattr(request, 'json'):
            try:
                body = await request.json()
                user_address = body.get('user_address')
            except:
                pass
        
        if not user_address:
            raise HTTPException(
                status_code=401,
                detail="User wallet address required. Please provide X-User-Address header or user_address in request body."
            )
        
        # 获取rag_id
        rag_id = kwargs.get('rag_id') or (request.path_params.get('rag_id') if hasattr(request, 'path_params') else None)
        
        if not rag_id:
            # 尝试从请求体获取
            if hasattr(request, 'json'):
                try:
                    body = await request.json()
                    rag_id = body.get('rag_id')
                except:
                    pass
        
        if not rag_id:
            raise HTTPException(status_code=400, detail="rag_id is required")
        
        # 获取token_id
        storage = get_storage_service()
        token_id = storage.get_token_id(rag_id)
        
        if not token_id:
            raise HTTPException(
                status_code=404,
                detail=f"No NFT found for rag_id: {rag_id}"
            )
        
        # 检查权限
        web3_service = get_web3_service()
        has_access = web3_service.check_access(user_address, token_id)
        
        if not has_access:
            # 获取NFT信息
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
        
        # 有权限，继续执行
        return await func(*args, **kwargs)
    
    return wrapper

def get_user_address_from_request(request: Request) -> Optional[str]:
    """
    从请求中提取用户钱包地址
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        用户钱包地址或None
    """
    # 尝试从请求头获取
    user_address = request.headers.get('X-User-Address')
    
    if user_address:
        return user_address
    
    # 尝试从查询参数获取
    user_address = request.query_params.get('user_address')
    
    return user_address

