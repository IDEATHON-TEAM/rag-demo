"""
查询历史服务：存储和管理查询历史记录
使用内存字典存储，生产环境应使用数据库
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class QueryHistoryService:
    def __init__(self):
        # 查询记录存储：query_id -> query_record
        self.query_records: Dict[str, Dict] = {}
        
        # rag_id -> [query_id列表] 索引
        self.rag_queries: Dict[str, List[str]] = {}
        
        # user_address -> [query_id列表] 索引
        self.user_queries: Dict[str, List[str]] = {}
    
    def save_query(
        self,
        question: str,
        answer: str,
        sources: List[Dict],
        rag_id: str,
        user_address: str,
        vector_hash: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        保存查询记录
        
        Args:
            question: 查询问题
            answer: 回答
            sources: 引用来源
            rag_id: 知识库ID
            user_address: 用户钱包地址
            vector_hash: 向量索引哈希
            metadata: 额外元数据
            
        Returns:
            query_id: 查询记录ID
        """
        query_id = f"query_{uuid.uuid4().hex[:16]}"
        
        query_record = {
            "query_id": query_id,
            "question": question,
            "answer": answer,
            "sources": sources,
            "rag_id": rag_id,
            "user_address": user_address,
            "vector_hash": vector_hash,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "minted_as_nft": False,
            "nft_token_id": None
        }
        
        # 保存记录
        self.query_records[query_id] = query_record
        
        # 更新索引
        if rag_id not in self.rag_queries:
            self.rag_queries[rag_id] = []
        self.rag_queries[rag_id].append(query_id)
        
        if user_address not in self.user_queries:
            self.user_queries[user_address] = []
        self.user_queries[user_address].append(query_id)
        
        return query_id
    
    def get_query(self, query_id: str) -> Optional[Dict]:
        """
        获取查询记录
        
        Args:
            query_id: 查询记录ID
            
        Returns:
            查询记录字典或None
        """
        return self.query_records.get(query_id)
    
    def mark_as_minted(self, query_id: str, token_id: int):
        """
        标记查询记录已铸造为NFT
        
        Args:
            query_id: 查询记录ID
            token_id: NFT token ID
        """
        if query_id in self.query_records:
            self.query_records[query_id]["minted_as_nft"] = True
            self.query_records[query_id]["nft_token_id"] = token_id
    
    def get_query_history(
        self,
        rag_id: Optional[str] = None,
        user_address: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        获取查询历史
        
        Args:
            rag_id: 可选，过滤特定知识库
            user_address: 可选，过滤特定用户
            page: 页码（从1开始）
            page_size: 每页大小
            
        Returns:
            包含查询列表和分页信息的字典
        """
        # 确定要查询的query_id列表
        query_ids = None
        
        if rag_id and user_address:
            # 两个条件都指定，取交集
            rag_query_ids = set(self.rag_queries.get(rag_id, []))
            user_query_ids = set(self.user_queries.get(user_address, []))
            query_ids = list(rag_query_ids & user_query_ids)
        elif rag_id:
            query_ids = self.rag_queries.get(rag_id, [])
        elif user_address:
            query_ids = self.user_queries.get(user_address, [])
        else:
            # 都没有指定，返回所有
            query_ids = list(self.query_records.keys())
        
        # 按时间倒序排序（最新的在前）
        query_ids.sort(key=lambda qid: self.query_records[qid]["created_at"], reverse=True)
        
        # 分页
        total = len(query_ids)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_ids = query_ids[start:end]
        
        # 获取查询记录
        queries = [self.query_records[qid] for qid in paginated_ids]
        
        return {
            "queries": queries,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_user_queries(self, user_address: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        获取用户的查询历史（便捷方法）
        
        Args:
            user_address: 用户钱包地址
            page: 页码
            page_size: 每页大小
            
        Returns:
            查询历史字典
        """
        return self.get_query_history(user_address=user_address, page=page, page_size=page_size)
    
    def get_rag_queries(self, rag_id: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        获取知识库的查询历史（便捷方法）
        
        Args:
            rag_id: 知识库ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            查询历史字典
        """
        return self.get_query_history(rag_id=rag_id, page=page, page_size=page_size)

# 单例实例
_query_history_service = None

def get_query_history_service() -> QueryHistoryService:
    """获取查询历史服务单例"""
    global _query_history_service
    if _query_history_service is None:
        _query_history_service = QueryHistoryService()
    return _query_history_service

