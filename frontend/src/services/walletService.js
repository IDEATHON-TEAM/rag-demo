import { ethers } from 'ethers'
import { SEPOLIA_CONFIG, RPC_URL } from '../config/networkConfig.js'

class WalletService {
  constructor() {
    this.provider = null
    this.signer = null
    this.account = null
    this.chainId = null
    this.listeners = {
      accountsChanged: [],
      chainChanged: [],
    }
  }

  // 检查 MetaMask 是否安装
  isMetaMaskInstalled() {
    return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined'
  }

  // 连接钱包
  async connectWallet() {
    if (!this.isMetaMaskInstalled()) {
      throw new Error('请安装 MetaMask 钱包扩展')
    }

    try {
      // 请求账户访问
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      })

      if (accounts.length === 0) {
        throw new Error('未授权账户访问')
      }

      // 创建 provider 和 signer
      this.provider = new ethers.BrowserProvider(window.ethereum)
      this.signer = await this.provider.getSigner()
      this.account = accounts[0]
      this.chainId = await this.getChainId()

      // 检查网络
      await this.ensureSepoliaNetwork()

      // 设置事件监听
      this.setupEventListeners()

      return {
        account: this.account,
        chainId: this.chainId,
      }
    } catch (error) {
      console.error('连接钱包失败:', error)
      throw error
    }
  }

  // 断开连接
  disconnectWallet() {
    this.provider = null
    this.signer = null
    this.account = null
    this.chainId = null
    this.removeEventListeners()
  }

  // 获取当前账户
  getAccount() {
    return this.account
  }

  // 获取当前链ID
  async getChainId() {
    if (!this.provider) {
      return null
    }
    const network = await this.provider.getNetwork()
    return Number(network.chainId)
  }

  // 获取 provider
  getProvider() {
    return this.provider
  }

  // 获取 signer
  getSigner() {
    return this.signer
  }

  // 确保在 Sepolia 网络
  async ensureSepoliaNetwork() {
    const currentChainId = await this.getChainId()
    const sepoliaChainId = parseInt(SEPOLIA_CONFIG.chainId, 16)

    if (currentChainId !== sepoliaChainId) {
      await this.switchNetwork()
    }
  }

  // 切换到 Sepolia 网络
  async switchNetwork() {
    if (!this.isMetaMaskInstalled()) {
      throw new Error('请安装 MetaMask 钱包扩展')
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: SEPOLIA_CONFIG.chainId }],
      })
    } catch (switchError) {
      // 如果网络不存在，尝试添加
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [SEPOLIA_CONFIG],
          })
        } catch (addError) {
          throw new Error('添加网络失败: ' + addError.message)
        }
      } else {
        throw new Error('切换网络失败: ' + switchError.message)
      }
    }
  }

  // 设置事件监听
  setupEventListeners() {
    if (!this.isMetaMaskInstalled()) return

    // 账户变化监听
    window.ethereum.on('accountsChanged', (accounts) => {
      if (accounts.length === 0) {
        this.disconnectWallet()
      } else {
        this.account = accounts[0]
        // 重新创建 signer
        this.provider = new ethers.BrowserProvider(window.ethereum)
        this.provider.getSigner().then((signer) => {
          this.signer = signer
        })
      }
      this.notifyListeners('accountsChanged', accounts)
    })

    // 链变化监听
    window.ethereum.on('chainChanged', (chainId) => {
      this.chainId = parseInt(chainId, 16)
      // 重新创建 provider 和 signer
      this.provider = new ethers.BrowserProvider(window.ethereum)
      this.provider.getSigner().then((signer) => {
        this.signer = signer
      })
      this.notifyListeners('chainChanged', this.chainId)
    })
  }

  // 移除事件监听
  removeEventListeners() {
    if (!this.isMetaMaskInstalled()) return
    window.ethereum.removeAllListeners('accountsChanged')
    window.ethereum.removeAllListeners('chainChanged')
  }

  // 添加事件监听器
  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  // 移除事件监听器
  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter((cb) => cb !== callback)
    }
  }

  // 通知监听器
  notifyListeners(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach((callback) => callback(data))
    }
  }

  // 检查是否已连接
  isConnected() {
    return this.account !== null && this.signer !== null
  }

  // 格式化地址显示
  formatAddress(address) {
    if (!address) return ''
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }
}

// 导出单例
export default new WalletService()

