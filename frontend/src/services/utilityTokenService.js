import { ethers } from 'ethers'
import walletService from './walletService.js'
import { CONTRACT_ADDRESS, UTILITY_TOKEN_ABI } from '../config/contractConfig.js'
import { RPC_URL } from '../config/networkConfig.js'

class UtilityTokenService {
  constructor() {
    this.contract = null
    this.readOnlyContract = null
    this.tokenInfo = null
  }

  // 获取只读合约实例（不需要钱包连接）
  getReadOnlyContract() {
    if (!CONTRACT_ADDRESS) {
      throw new Error('合约地址未配置，请先部署合约并更新配置')
    }

    if (!this.readOnlyContract) {
      // 使用公共 RPC 端点创建只读 provider
      const provider = new ethers.JsonRpcProvider(RPC_URL)
      this.readOnlyContract = new ethers.Contract(CONTRACT_ADDRESS, UTILITY_TOKEN_ABI, provider)
    }

    return this.readOnlyContract
  }

  // 获取可写合约实例（需要钱包连接）
  async getContract() {
    if (!CONTRACT_ADDRESS) {
      throw new Error('合约地址未配置，请先部署合约并更新配置')
    }

    if (!walletService.isConnected()) {
      throw new Error('请先连接钱包')
    }

    if (!this.contract) {
      const signer = walletService.getSigner()
      this.contract = new ethers.Contract(CONTRACT_ADDRESS, UTILITY_TOKEN_ABI, signer)
    }

    return this.contract
  }

  // 获取代币信息（可以使用只读合约）
  async getTokenInfo() {
    if (this.tokenInfo) {
      return this.tokenInfo
    }

    try {
      // 使用只读合约，不需要连接钱包
      const contract = this.getReadOnlyContract()
      const [name, symbol, decimals, totalSupply] = await Promise.all([
        contract.name(),
        contract.symbol(),
        contract.decimals(),
        contract.totalSupply(),
      ])

      this.tokenInfo = {
        name,
        symbol,
        decimals: Number(decimals),
        totalSupply: ethers.formatUnits(totalSupply, Number(decimals)),
      }

      return this.tokenInfo
    } catch (error) {
      console.error('获取代币信息失败:', error)
      throw error
    }
  }

  // 查询余额（可以使用只读合约）
  async getBalance(address) {
    try {
      // 使用只读合约，不需要连接钱包
      const contract = this.getReadOnlyContract()
      const balance = await contract.balanceOf(address)
      const tokenInfo = await this.getTokenInfo()
      return ethers.formatUnits(balance, tokenInfo.decimals)
    } catch (error) {
      console.error('查询余额失败:', error)
      throw error
    }
  }

  // 查询总供应量（可以使用只读合约）
  async getTotalSupply() {
    try {
      // 使用只读合约，不需要连接钱包
      const contract = this.getReadOnlyContract()
      const totalSupply = await contract.totalSupply()
      const tokenInfo = await this.getTokenInfo()
      return ethers.formatUnits(totalSupply, tokenInfo.decimals)
    } catch (error) {
      console.error('查询总供应量失败:', error)
      throw error
    }
  }

  // 转账
  async transfer(to, amount) {
    try {
      const contract = await this.getContract()
      const tokenInfo = await this.getTokenInfo()
      const amountWei = ethers.parseUnits(amount.toString(), tokenInfo.decimals)

      // 检查余额
      const balance = await contract.balanceOf(walletService.getAccount())
      if (balance < amountWei) {
        throw new Error('余额不足')
      }

      // 发送交易
      const tx = await contract.transfer(to, amountWei)
      return tx
    } catch (error) {
      console.error('转账失败:', error)
      throw error
    }
  }

  // 授权
  async approve(spender, amount) {
    try {
      const contract = await this.getContract()
      const tokenInfo = await this.getTokenInfo()
      const amountWei = ethers.parseUnits(amount.toString(), tokenInfo.decimals)

      const tx = await contract.approve(spender, amountWei)
      return tx
    } catch (error) {
      console.error('授权失败:', error)
      throw error
    }
  }

  // 查询授权额度（可以使用只读合约）
  async allowance(owner, spender) {
    try {
      // 使用只读合约，不需要连接钱包
      const contract = this.getReadOnlyContract()
      const allowance = await contract.allowance(owner, spender)
      const tokenInfo = await this.getTokenInfo()
      return ethers.formatUnits(allowance, tokenInfo.decimals)
    } catch (error) {
      console.error('查询授权额度失败:', error)
      throw error
    }
  }

  // 从授权账户转账
  async transferFrom(from, to, amount) {
    try {
      const contract = await this.getContract()
      const tokenInfo = await this.getTokenInfo()
      const amountWei = ethers.parseUnits(amount.toString(), tokenInfo.decimals)

      // 检查授权额度
      const allowance = await contract.allowance(from, walletService.getAccount())
      if (allowance < amountWei) {
        throw new Error('授权额度不足')
      }

      const tx = await contract.transferFrom(from, to, amountWei)
      return tx
    } catch (error) {
      console.error('transferFrom 失败:', error)
      throw error
    }
  }

  // 铸造代币（仅owner）
  async mint(to, amount) {
    try {
      const contract = await this.getContract()
      const tokenInfo = await this.getTokenInfo()
      const amountWei = ethers.parseUnits(amount.toString(), tokenInfo.decimals)

      // 检查是否为owner
      const owner = await contract.owner()
      const currentAccount = walletService.getAccount()
      if (owner.toLowerCase() !== currentAccount.toLowerCase()) {
        throw new Error('只有合约所有者可以铸造代币')
      }

      const tx = await contract.mint(to, amountWei)
      return tx
    } catch (error) {
      console.error('铸造失败:', error)
      throw error
    }
  }

  // 销毁代币（仅owner）
  async burn(from, amount) {
    try {
      const contract = await this.getContract()
      const tokenInfo = await this.getTokenInfo()
      const amountWei = ethers.parseUnits(amount.toString(), tokenInfo.decimals)

      // 检查是否为owner
      const owner = await contract.owner()
      const currentAccount = walletService.getAccount()
      if (owner.toLowerCase() !== currentAccount.toLowerCase()) {
        throw new Error('只有合约所有者可以销毁代币')
      }

      const tx = await contract.burn(from, amountWei)
      return tx
    } catch (error) {
      console.error('销毁失败:', error)
      throw error
    }
  }

  // 检查是否为owner（可以使用只读合约）
  async isOwner(address) {
    try {
      // 使用只读合约，不需要连接钱包
      const contract = this.getReadOnlyContract()
      const owner = await contract.owner()
      return owner.toLowerCase() === address.toLowerCase()
    } catch (error) {
      console.error('检查owner失败:', error)
      return false
    }
  }

  // 等待交易确认
  async waitForTransaction(txHash) {
    try {
      const provider = walletService.getProvider()
      const receipt = await provider.waitForTransaction(txHash)
      return receipt
    } catch (error) {
      console.error('等待交易确认失败:', error)
      throw error
    }
  }

  // 格式化金额显示
  formatAmount(amount, decimals = 18) {
    try {
      return ethers.formatUnits(amount, decimals)
    } catch (error) {
      return amount.toString()
    }
  }

  // 解析金额为wei
  parseAmount(amount, decimals = 18) {
    try {
      return ethers.parseUnits(amount.toString(), decimals)
    } catch (error) {
      throw new Error('金额格式错误')
    }
  }
}

// 导出单例
export default new UtilityTokenService()

