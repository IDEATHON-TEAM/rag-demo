import os
from web3 import Web3
from typing import Optional, Dict

class Web3Service:
    def __init__(self):
        self.rpc_url = os.getenv("RPC_URL", "https://rpc.sepolia.org")
        self.chain_id = int(os.getenv("CHAIN_ID", "11155111"))
        self.contract_address = os.getenv("KNOWLEDGE_NFT_CONTRACT_ADDRESS", "")
        
        if not self.contract_address:
            raise ValueError("KNOWLEDGE_NFT_CONTRACT_ADDRESS not set in environment variables")
        
        # 初始化Web3（只读模式，不需要私钥）
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise Exception(f"Failed to connect to blockchain at {self.rpc_url}")
        
        print(f"Web3 connected (read-only mode). Contract: {self.contract_address}")
        
        # KnowledgeNFT合约ABI（简化版，包含必要函数）
        self.contract_abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "ipfsCID", "type": "string"},
                    {"internalType": "bytes32", "name": "vectorHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "price", "type": "uint256"}
                ],
                "name": "mintKnowledgeNFT",
                "outputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"},
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"}
                ],
                "name": "hasAccess",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                "name": "purchaseAccess",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "name": "assets",
                "outputs": [
                    {"internalType": "string", "name": "ipfsCID", "type": "string"},
                    {"internalType": "bytes32", "name": "vectorHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "bool", "name": "isActive", "type": "bool"},
                    {"internalType": "uint64", "name": "createdAt", "type": "uint64"},
                    {"internalType": "uint256", "name": "totalSales", "type": "uint256"},
                    {"internalType": "uint256", "name": "revenue", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
                    {"indexed": False, "internalType": "string", "name": "ipfsCID", "type": "string"},
                    {"indexed": False, "internalType": "bytes32", "name": "vectorHash", "type": "bytes32"},
                    {"indexed": False, "internalType": "uint256", "name": "price", "type": "uint256"}
                ],
                "name": "KnowledgeNFTMinted",
                "type": "event"
            }
        ]
        
        # 创建合约实例
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )
    
    def get_contract(self):
        """获取合约实例"""
        return self.contract
    
    def check_access(self, user_address: str, token_id: int) -> bool:
        """
        检查用户是否有访问权限
        
        Args:
            user_address: 用户钱包地址
            token_id: NFT token ID
            
        Returns:
            是否有权限
        """
        try:
            user_address = Web3.to_checksum_address(user_address)
            has_access = self.contract.functions.hasAccess(user_address, token_id).call()
            return has_access
        except Exception as e:
            print(f"Error checking access: {e}")
            return False
    
    def get_nft_info(self, token_id: int) -> Optional[Dict]:
        """
        获取NFT信息
        
        Args:
            token_id: NFT token ID
            
        Returns:
            NFT信息字典或None
        """
        try:
            asset = self.contract.functions.assets(token_id).call()
            return {
                'ipfsCID': asset[0],
                'vectorHash': asset[1].hex(),
                'price': asset[2],
                'isActive': asset[3],
                'createdAt': asset[4],
                'totalSales': asset[5],
                'revenue': asset[6]
            }
        except Exception as e:
            print(f"Error getting NFT info: {e}")
            return None
    
    def get_owner(self, token_id: int) -> Optional[str]:
        """
        获取NFT所有者地址
        
        Args:
            token_id: NFT token ID
            
        Returns:
            所有者地址或None
        """
        try:
            owner = self.contract.functions.ownerOf(token_id).call()
            return owner
        except Exception as e:
            print(f"Error getting owner: {e}")
            return None
    
    def prepare_mint_data(self, ipfs_cid: str, vector_hash_hex: str, price: int) -> Dict:
        """
        准备NFT铸造数据（用于前端调用合约）
        
        Args:
            ipfs_cid: IPFS CID
            vector_hash_hex: 向量哈希（hex字符串）
            price: NFT价格（wei）
            
        Returns:
            包含铸造数据的字典
        """
        return {
            "ipfs_cid": ipfs_cid,
            "vector_hash_hex": vector_hash_hex,
            "price": price
        }

# 单例实例
_web3_service = None

def get_web3_service() -> Web3Service:
    """获取Web3服务单例"""
    global _web3_service
    if _web3_service is None:
        _web3_service = Web3Service()
    return _web3_service

