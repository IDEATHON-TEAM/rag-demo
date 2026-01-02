// Sepolia 测试网配置
export const SEPOLIA_CONFIG = {
  chainId: '0xaa36a7', // 11155111 in hex
  chainName: 'Sepolia',
  nativeCurrency: {
    name: 'Ether',
    symbol: 'ETH',
    decimals: 18,
  },
  rpcUrls: [
    'https://sepolia.infura.io/v3/',
    'https://rpc.sepolia.org',
    'https://sepolia.gateway.tenderly.co',
  ],
  blockExplorerUrls: ['https://sepolia.etherscan.io'],
}

// RPC 端点（测试使用公共端点，生产环境使用自己的Infura/Alchemy密钥）
export const RPC_URL = 'https://rpc.sepolia.org'

// 区块浏览器URL
export const BLOCK_EXPLORER_URL = 'https://sepolia.etherscan.io'

