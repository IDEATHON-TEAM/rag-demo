<template>
  <div class="token-balance bg-white rounded-xl border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-xl text-gray-900 font-semibold">代币余额</h3>
      <el-button
        :icon="Refresh"
        circle
        @click="refreshBalance"
        :loading="loading"
        class="border-gray-200 text-gray-700 hover:bg-gray-50"
      />
    </div>
    
    <div v-if="tokenInfo" class="space-y-2">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold">{{ tokenInfo.symbol.charAt(0) }}</span>
        </div>
        <div>
          <div class="text-gray-900 font-semibold">{{ tokenInfo.name }}</div>
          <div class="text-gray-600 text-sm">{{ tokenInfo.symbol }}</div>
        </div>
      </div>
      
      <div class="border-t border-gray-200 pt-4">
        <div class="text-gray-600 text-sm mb-1">我的余额</div>
        <div class="text-3xl font-bold text-gray-900">
          {{ formattedBalance }}
        </div>
        <div class="text-gray-500 text-xs mt-1">{{ tokenInfo.symbol }}</div>
      </div>
      
      <div v-if="showTotalSupply" class="border-t border-gray-200 pt-4 mt-4">
        <div class="text-gray-600 text-sm mb-1">总供应量</div>
        <div class="text-xl text-gray-900">
          {{ formattedTotalSupply }} {{ tokenInfo.symbol }}
        </div>
      </div>
    </div>
    
    <div v-else-if="loading" class="text-center py-8">
      <el-icon class="is-loading text-gray-600 text-4xl"><Loading /></el-icon>
      <div class="text-gray-600 mt-2">加载中...</div>
    </div>
    
    <div v-else class="text-center py-8 text-gray-500">
      请先连接钱包
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading } from '@element-plus/icons-vue'
import walletService from '../services/walletService.js'
import tokenService from '../services/utilityTokenService.js'

const props = defineProps({
  showTotalSupply: {
    type: Boolean,
    default: false,
  },
})

const balance = ref('0')
const totalSupply = ref('0')
const tokenInfo = ref(null)
const loading = ref(false)

const formattedBalance = computed(() => {
  if (!balance.value || balance.value === '0') return '0.00'
  const num = parseFloat(balance.value)
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  })
})

const formattedTotalSupply = computed(() => {
  if (!totalSupply.value || totalSupply.value === '0') return '0'
  const num = parseFloat(totalSupply.value)
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
})

const loadTokenInfo = async () => {
  try {
    tokenInfo.value = await tokenService.getTokenInfo()
  } catch (error) {
    console.error('加载代币信息失败:', error)
  }
}

const loadBalance = async () => {
  if (!walletService.isConnected()) {
    balance.value = '0'
    return
  }

  loading.value = true
  try {
    const account = walletService.getAccount()
    balance.value = await tokenService.getBalance(account)
  } catch (error) {
    console.error('加载余额失败:', error)
    ElMessage.error('加载余额失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadTotalSupply = async () => {
  if (!props.showTotalSupply) return

  try {
    totalSupply.value = await tokenService.getTotalSupply()
  } catch (error) {
    console.error('加载总供应量失败:', error)
  }
}

const refreshBalance = async () => {
  await Promise.all([loadBalance(), loadTotalSupply()])
}

// 监听账户变化
watch(
  () => walletService.getAccount(),
  () => {
    loadBalance()
  }
)

onMounted(async () => {
  await loadTokenInfo()
  await loadBalance()
  if (props.showTotalSupply) {
    await loadTotalSupply()
  }

  // 监听账户变化事件
  walletService.on('accountsChanged', () => {
    loadBalance()
  })
})
</script>

<style scoped>
.token-balance {
  min-height: 200px;
}
</style>

