from typing import Dict, List, Optional
import json
from datetime import datetime

class QueryPackageService:
    """查询结果打包服务"""
    
    def package_query_result(
        self,
        question: str,
        answer: str,
        sources: List[Dict],  # 引用来源
        rag_id: str,
        user_address: str,
        vector_hash: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        打包查询结果为NFT内容
        
        Args:
            question: 用户的查询问题
            answer: RAG生成的答案
            sources: 引用来源列表，每个包含content和metadata
            rag_id: 知识库ID
            user_address: 用户钱包地址
            vector_hash: 向量索引哈希（可选）
            metadata: 额外的元数据（可选）
            
        Returns:
            包含所有查询结果信息的字典
        """
        package = {
            "version": "1.0",
            "question": question,
            "answer": answer,
            "sources": sources,  # 包含文档片段、页码、CID等
            "rag_id": rag_id,
            "created_at": datetime.now().isoformat(),
            "creator": user_address,
            "vector_hash": vector_hash,
            "metadata": metadata or {}
        }
        return package
    
    def package_to_json(self, package: Dict) -> str:
        """
        将打包结果转换为JSON字符串
        
        Args:
            package: 打包的查询结果字典
            
        Returns:
            JSON字符串
        """
        return json.dumps(package, ensure_ascii=False, indent=2)
    
    def package_to_bytes(self, package: Dict) -> bytes:
        """
        将打包结果转换为字节流（用于IPFS上传）
        
        Args:
            package: 打包的查询结果字典
            
        Returns:
            字节流
        """
        json_str = self.package_to_json(package)
        return json_str.encode('utf-8')

# 单例实例
_query_package_service = None

def get_query_package_service() -> QueryPackageService:
    """获取查询结果打包服务单例"""
    global _query_package_service
    if _query_package_service is None:
        _query_package_service = QueryPackageService()
    return _query_package_service

