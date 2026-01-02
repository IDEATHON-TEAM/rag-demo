"""
存储服务：管理rag_id与token_id的映射关系
使用内存字典存储，生产环境应使用数据库
"""
from typing import Optional, Dict

class StorageService:
    def __init__(self):
        # rag_id -> token_id 映射
        self.rag_to_token: Dict[str, int] = {}
        
        # token_id -> rag_id 映射
        self.token_to_rag: Dict[int, str] = {}
        
        # NFT元数据缓存
        self.nft_cache: Dict[int, Dict] = {}
    
    def link_rag_to_token(self, rag_id: str, token_id: int, nft_info: Optional[Dict] = None):
        """
        关联rag_id和token_id
        
        Args:
            rag_id: RAG ID
            token_id: NFT token ID
            nft_info: 可选的NFT元数据
        """
        self.rag_to_token[rag_id] = token_id
        self.token_to_rag[token_id] = rag_id
        
        if nft_info:
            self.nft_cache[token_id] = nft_info
    
    def get_token_id(self, rag_id: str) -> Optional[int]:
        """
        根据rag_id获取token_id
        
        Args:
            rag_id: RAG ID
            
        Returns:
            token_id或None
        """
        return self.rag_to_token.get(rag_id)
    
    def get_rag_id(self, token_id: int) -> Optional[str]:
        """
        根据token_id获取rag_id
        
        Args:
            token_id: NFT token ID
            
        Returns:
            rag_id或None
        """
        return self.token_to_rag.get(token_id)
    
    def get_nft_info(self, token_id: int) -> Optional[Dict]:
        """
        获取NFT信息（从缓存）
        
        Args:
            token_id: NFT token ID
            
        Returns:
            NFT信息或None
        """
        return self.nft_cache.get(token_id)
    
    def update_nft_info(self, token_id: int, nft_info: Dict):
        """
        更新NFT信息缓存
        
        Args:
            token_id: NFT token ID
            nft_info: NFT信息
        """
        self.nft_cache[token_id] = nft_info
    
    def remove_mapping(self, rag_id: str):
        """
        删除映射关系
        
        Args:
            rag_id: RAG ID
        """
        token_id = self.rag_to_token.get(rag_id)
        if token_id:
            del self.rag_to_token[rag_id]
            if token_id in self.token_to_rag:
                del self.token_to_rag[token_id]
            if token_id in self.nft_cache:
                del self.nft_cache[token_id]
    
    def list_all_mappings(self) -> Dict[str, int]:
        """
        列出所有映射关系
        
        Returns:
            rag_id到token_id的映射字典
        """
        return self.rag_to_token.copy()

# 单例实例
_storage_service = None

def get_storage_service() -> StorageService:
    """获取存储服务单例"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

