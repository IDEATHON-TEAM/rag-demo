// KnowledgeNFT 合约配置
// 部署后需要更新 CONTRACT_ADDRESS

export const KNOWLEDGE_NFT_CONTRACT_ADDRESS = '' // TODO: 部署后更新此地址

// KnowledgeNFT ABI (从合约编译后获取)
export const KNOWLEDGE_NFT_ABI = [
  // NFT铸造函数
  {
    inputs: [
      { internalType: 'string', name: 'ipfsCID', type: 'string' },
      { internalType: 'bytes32', name: 'vectorHash', type: 'bytes32' },
      { internalType: 'uint256', name: 'price', type: 'uint256' },
    ],
    name: 'mintKnowledgeNFT',
    outputs: [{ internalType: 'uint256', name: 'tokenId', type: 'uint256' }],
    stateMutability: 'nonpayable',
    type: 'function',
  },
  // 权限检查
  {
    inputs: [
      { internalType: 'address', name: 'user', type: 'address' },
      { internalType: 'uint256', name: 'tokenId', type: 'uint256' },
    ],
    name: 'hasAccess',
    outputs: [{ internalType: 'bool', name: '', type: 'bool' }],
    stateMutability: 'view',
    type: 'function',
  },
  // 购买访问权限
  {
    inputs: [{ internalType: 'uint256', name: 'tokenId', type: 'uint256' }],
    name: 'purchaseAccess',
    outputs: [],
    stateMutability: 'nonpayable',
    type: 'function',
  },
  // 获取NFT信息
  {
    inputs: [{ internalType: 'uint256', name: '', type: 'uint256' }],
    name: 'assets',
    outputs: [
      { internalType: 'string', name: 'ipfsCID', type: 'string' },
      { internalType: 'bytes32', name: 'vectorHash', type: 'bytes32' },
      { internalType: 'uint256', name: 'price', type: 'uint256' },
      { internalType: 'bool', name: 'isActive', type: 'bool' },
      { internalType: 'uint64', name: 'createdAt', type: 'uint64' },
      { internalType: 'uint256', name: 'totalSales', type: 'uint256' },
      { internalType: 'uint256', name: 'revenue', type: 'uint256' },
    ],
    stateMutability: 'view',
    type: 'function',
  },
  // 获取所有者
  {
    inputs: [{ internalType: 'uint256', name: 'tokenId', type: 'uint256' }],
    name: 'ownerOf',
    outputs: [{ internalType: 'address', name: '', type: 'address' }],
    stateMutability: 'view',
    type: 'function',
  },
  // 事件
  {
    anonymous: false,
    inputs: [
      { indexed: true, internalType: 'uint256', name: 'tokenId', type: 'uint256' },
      { indexed: true, internalType: 'address', name: 'owner', type: 'address' },
      { indexed: false, internalType: 'string', name: 'ipfsCID', type: 'string' },
      { indexed: false, internalType: 'bytes32', name: 'vectorHash', type: 'bytes32' },
      { indexed: false, internalType: 'uint256', name: 'price', type: 'uint256' },
    ],
    name: 'KnowledgeNFTMinted',
    type: 'event',
  },
]

