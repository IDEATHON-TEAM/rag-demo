import hashlib
import json
import chromadb
from typing import Optional

class VectorHashService:
    def __init__(self, chroma_client: chromadb.Client):
        """
        初始化向量哈希服务
        
        Args:
            chroma_client: ChromaDB客户端实例
        """
        self.chroma_client = chroma_client
    
    def calculate_vector_hash(self, collection_name: str) -> Optional[str]:
        """
        计算ChromaDB集合的向量索引哈希
        
        Args:
            collection_name: ChromaDB集合名称
            
        Returns:
            SHA256哈希值（hex字符串）或 None
        """
        try:
            # 获取集合
            collection = self.chroma_client.get_collection(collection_name)
            
            # 获取所有数据
            results = collection.get()
            
            if not results or not results.get('ids'):
                return None
            
            # 准备哈希的数据结构
            hash_data = {
                'ids': results.get('ids', []),
                'embeddings': results.get('embeddings', []),
                'metadatas': results.get('metadatas', []),
                'documents': results.get('documents', [])
            }
            
            # 将数据序列化为JSON字符串（排序以确保一致性）
            json_str = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
            
            # 计算SHA256哈希
            hash_obj = hashlib.sha256(json_str.encode('utf-8'))
            vector_hash = hash_obj.hexdigest()
            
            # 转换为bytes32格式（前32字节）
            # Solidity的bytes32需要32字节，所以取前32字节
            bytes32_hash = bytes.fromhex(vector_hash[:64])
            
            return vector_hash  # 返回完整哈希用于调试，实际合约中会截取前32字节
        except Exception as e:
            print(f"Error calculating vector hash: {e}")
            return None
    
    def calculate_vector_hash_bytes32(self, collection_name: str) -> Optional[bytes]:
        """
        计算向量哈希并返回bytes32格式（用于Solidity合约）
        
        Args:
            collection_name: ChromaDB集合名称
            
        Returns:
            bytes32格式的哈希值（32字节）
        """
        hash_hex = self.calculate_vector_hash(collection_name)
        if not hash_hex:
            return None
        
        # 取前64个字符（32字节）
        return bytes.fromhex(hash_hex[:64])
    
    def calculate_vector_hash_hex32(self, collection_name: str) -> Optional[str]:
        """
        计算向量哈希并返回32字节的hex字符串（用于web3调用）
        
        Args:
            collection_name: ChromaDB集合名称
            
        Returns:
            64字符的hex字符串（32字节）
        """
        hash_hex = self.calculate_vector_hash(collection_name)
        if not hash_hex:
            return None
        
        return hash_hex[:64]  # 返回前64个字符（32字节）

