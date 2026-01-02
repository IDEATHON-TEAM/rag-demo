import { ethers } from 'ethers'
import walletService from './walletService.js'
import { KNOWLEDGE_NFT_CONTRACT_ADDRESS, KNOWLEDGE_NFT_ABI } from '../config/knowledgeNFTConfig.js'

class KnowledgeNFTService {
  constructor() {
    this.contract = null
  }

  // 获取合约实例
  async getContract() {
    if (!KNOWLEDGE_NFT_CONTRACT_ADDRESS) {
      throw new Error('KnowledgeNFT合约地址未配置，请先部署合约并更新配置')
    }

    if (!walletService.isConnected()) {
      throw new Error('请先连接钱包')
    }

    if (!this.contract) {
      const signer = walletService.getSigner()
      this.contract = new ethers.Contract(KNOWLEDGE_NFT_CONTRACT_ADDRESS, KNOWLEDGE_NFT_ABI, signer)
    }

    return this.contract
  }

  // 铸造NFT
  async mintNFT(ipfsCID, vectorHashHex, price) {
    try {
      const contract = await this.getContract()
      
      // 将vectorHash转换为bytes32
      const vectorHashBytes32 = '0x' + vectorHashHex.slice(0, 64)
      
      // 调用合约铸造NFT
      const tx = await contract.mintKnowledgeNFT(ipfsCID, vectorHashBytes32, price)
      
      // 等待交易确认
      const receipt = await tx.wait()
      
      // 从事件中提取token_id
      let tokenId = null
      if (receipt.logs) {
        for (const log of receipt.logs) {
          try {
            const parsedLog = contract.interface.parseLog(log)
            if (parsedLog && parsedLog.name === 'KnowledgeNFTMinted') {
              tokenId = parsedLog.args.tokenId.toString()
              break
            }
          } catch (e) {
            // 继续尝试下一个日志
          }
        }
      }
      
      if (!tokenId) {
        // 如果无法从事件中提取，尝试从Transfer事件中提取
        // ERC721的Transfer事件格式: Transfer(address indexed from, address indexed to, uint256 indexed tokenId)
        for (const log of receipt.logs) {
          try {
            if (log.topics && log.topics.length >= 4) {
              // 检查from是否为0地址（表示铸造）
              const from = '0x' + log.topics[1].slice(26)
              if (from === '0x0000000000000000000000000000000000000000') {
                tokenId = BigInt(log.topics[3]).toString()
                break
              }
            }
          } catch (e) {
            // 继续尝试
          }
        }
      }
      
      return {
        txHash: receipt.hash,
        tokenId: tokenId,
        receipt: receipt
      }
    } catch (error) {
      console.error('铸造NFT失败:', error)
      throw error
    }
  }

  // 检查访问权限
  async checkAccess(userAddress, tokenId) {
    try {
      const contract = await this.getContract()
      const hasAccess = await contract.hasAccess(userAddress, tokenId)
      return hasAccess
    } catch (error) {
      console.error('检查权限失败:', error)
      return false
    }
  }

  // 购买访问权限
  async purchaseAccess(tokenId) {
    try {
      const contract = await this.getContract()
      const tx = await contract.purchaseAccess(tokenId)
      const receipt = await tx.wait()
      return {
        txHash: receipt.hash,
        receipt: receipt
      }
    } catch (error) {
      console.error('购买访问权限失败:', error)
      throw error
    }
  }

  // 获取NFT信息
  async getNFTInfo(tokenId) {
    try {
      const contract = await this.getContract()
      const asset = await contract.assets(tokenId)
      const owner = await contract.ownerOf(tokenId)
      
      return {
        ipfsCID: asset[0],
        vectorHash: asset[1],
        price: asset[2].toString(),
        isActive: asset[3],
        createdAt: asset[4].toString(),
        totalSales: asset[5].toString(),
        revenue: asset[6].toString(),
        owner: owner
      }
    } catch (error) {
      console.error('获取NFT信息失败:', error)
      throw error
    }
  }

  // 获取所有者
  async getOwner(tokenId) {
    try {
      const contract = await this.getContract()
      const owner = await contract.ownerOf(tokenId)
      return owner
    } catch (error) {
      console.error('获取所有者失败:', error)
      throw error
    }
  }
}

// 导出单例
export default new KnowledgeNFTService()

