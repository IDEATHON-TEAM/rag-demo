import os
import ipfshttpclient
from typing import Optional

class IPFSService:
    def __init__(self):
        self.api_url = os.getenv("IPFS_API_URL", "http://localhost:5001")
        self.client = None
        self._connect()
    
    def _connect(self):
        """连接到IPFS节点"""
        try:
            self.client = ipfshttpclient.connect(self.api_url)
            print(f"Connected to IPFS at {self.api_url}")
        except Exception as e:
            print(f"Warning: Failed to connect to IPFS at {self.api_url}: {e}")
            print("IPFS uploads will be disabled. Please ensure IPFS node is running.")
            self.client = None
    
    def upload_to_ipfs(self, file_path: str) -> Optional[str]:
        """
        上传文件到IPFS
        
        Args:
            file_path: 本地文件路径
            
        Returns:
            IPFS CID (Content Identifier) 或 None
        """
        if not self.client:
            raise Exception("IPFS client not connected. Please check IPFS_API_URL configuration.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # 上传文件到IPFS
            result = self.client.add(file_path)
            
            # result可能是单个文件或列表
            if isinstance(result, list):
                cid = result[0]['Hash']
            else:
                cid = result['Hash']
            
            print(f"File uploaded to IPFS: {cid}")
            return cid
        except Exception as e:
            print(f"Error uploading to IPFS: {e}")
            raise Exception(f"IPFS upload failed: {str(e)}")
    
    def get_from_ipfs(self, cid: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        从IPFS获取文件
        
        Args:
            cid: IPFS CID
            output_path: 可选，保存文件的路径
            
        Returns:
            文件内容（bytes）或 None
        """
        if not self.client:
            raise Exception("IPFS client not connected.")
        
        try:
            content = self.client.cat(cid)
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(content)
            
            return content
        except Exception as e:
            print(f"Error retrieving from IPFS: {e}")
            return None
    
    def pin(self, cid: str) -> bool:
        """
        固定IPFS内容（防止被垃圾回收）
        
        Args:
            cid: IPFS CID
            
        Returns:
            是否成功
        """
        if not self.client:
            return False
        
        try:
            self.client.pin.add(cid)
            return True
        except Exception as e:
            print(f"Error pinning CID {cid}: {e}")
            return False
    
    def upload_query_package(self, package_dict: dict) -> Optional[str]:
        """
        上传查询结果包到IPFS
        
        Args:
            package_dict: 查询结果包字典（包含问题、回答、引用等）
            
        Returns:
            IPFS CID (Content Identifier) 或 None
        """
        if not self.client:
            raise Exception("IPFS client not connected. Please check IPFS_API_URL configuration.")
        
        try:
            import json
            import tempfile
            import os
            
            # 将字典转换为JSON字符串
            json_str = json.dumps(package_dict, ensure_ascii=False, indent=2)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(json_str)
                tmp_path = tmp_file.name
            
            try:
                # 上传文件到IPFS
                result = self.client.add(tmp_path)
                
                # result可能是单个文件或列表
                if isinstance(result, list):
                    cid = result[0]['Hash']
                else:
                    cid = result['Hash']
                
                print(f"Query package uploaded to IPFS: {cid}")
                return cid
            finally:
                # 清理临时文件
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            print(f"Error uploading query package to IPFS: {e}")
            raise Exception(f"IPFS upload failed: {str(e)}")

# 单例实例
_ipfs_service = None

def get_ipfs_service() -> IPFSService:
    """获取IPFS服务单例"""
    global _ipfs_service
    if _ipfs_service is None:
        _ipfs_service = IPFSService()
    return _ipfs_service

