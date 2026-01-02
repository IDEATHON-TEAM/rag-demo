<template>
  <div class="wallet-connect">
    <el-button
      v-if="!isConnected"
      @click="handleConnect"
      :loading="connecting"
      type="primary"
    >
      <el-icon class="mr-1"><CreditCard /></el-icon>
      连接钱包
    </el-button>
    
    <el-dropdown v-else @command="handleCommand" trigger="click">
      <el-button class="bg-white border border-gray-200 text-gray-900 hover:bg-gray-50">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>{{ formattedAddress }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu class="bg-white border border-gray-200">
          <el-dropdown-item disabled class="text-gray-500">
            <div class="text-xs">{{ account }}</div>
          </el-dropdown-item>
          <el-dropdown-item disabled class="text-gray-500">
            <div class="text-xs">网络: {{ networkName }}</div>
          </el-dropdown-item>
          <el-dropdown-item divided command="disconnect" class="text-red-600 hover:text-red-700">
            断开连接
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, ArrowDown } from '@element-plus/icons-vue'
import walletService from '../services/walletService.js'
import { SEPOLIA_CONFIG } from '../config/networkConfig.js'

const isConnected = ref(false)
const connecting = ref(false)
const account = ref(null)
const chainId = ref(null)

const formattedAddress = computed(() => {
  return account.value ? walletService.formatAddress(account.value) : ''
})

const networkName = computed(() => {
  if (chainId.value === parseInt(SEPOLIA_CONFIG.chainId, 16)) {
    return 'Sepolia'
  }
  return `Chain ${chainId.value}`
})

const handleConnect = async () => {
  connecting.value = true
  try {
    if (!walletService.isMetaMaskInstalled()) {
      ElMessage.error('请先安装 MetaMask 钱包扩展')
      return
    }

    const result = await walletService.connectWallet()
    account.value = result.account
    chainId.value = result.chainId
    isConnected.value = true
    ElMessage.success('钱包连接成功')
  } catch (error) {
    console.error('连接失败:', error)
    ElMessage.error(error.message || '连接钱包失败')
  } finally {
    connecting.value = false
  }
}

const handleCommand = async (command) => {
  if (command === 'disconnect') {
    walletService.disconnectWallet()
    isConnected.value = false
    account.value = null
    chainId.value = null
    ElMessage.info('已断开连接')
  }
}

const updateConnectionStatus = () => {
  isConnected.value = walletService.isConnected()
  account.value = walletService.getAccount()
  walletService.getChainId().then((id) => {
    chainId.value = id
  })
}

// 监听账户变化
const handleAccountsChanged = (accounts) => {
  if (accounts.length === 0) {
    isConnected.value = false
    account.value = null
  } else {
    account.value = accounts[0]
  }
}

// 监听网络变化
const handleChainChanged = (newChainId) => {
  chainId.value = newChainId
  ElMessage.info('网络已切换')
}

onMounted(() => {
  updateConnectionStatus()
  walletService.on('accountsChanged', handleAccountsChanged)
  walletService.on('chainChanged', handleChainChanged)
})

onUnmounted(() => {
  walletService.off('accountsChanged', handleAccountsChanged)
  walletService.off('chainChanged', handleChainChanged)
})
</script>

<style scoped>
.wallet-connect {
  display: flex;
  align-items: center;
}

:deep(.el-dropdown-menu__item) {
  color: #030213;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f3f3f5;
}
</style>

