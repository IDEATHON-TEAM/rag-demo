<template>
  <div class="token-approve bg-white rounded-xl border border-gray-200 p-6">
    <h3 class="text-xl text-gray-900 font-semibold mb-6">授权</h3>
    
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="token-form">
      <el-form-item label="被授权地址" prop="spender">
        <el-input
          v-model="form.spender"
          placeholder="0x..."
          :disabled="approving"
          class="custom-input"
        />
      </el-form-item>
      
      <el-form-item label="授权金额" prop="amount">
        <el-input
          v-model="form.amount"
          placeholder="0.0"
          :disabled="approving"
          class="custom-input"
        >
          <template #append>
            <span class="text-gray-600">{{ tokenSymbol }}</span>
          </template>
        </el-input>
        <div class="text-gray-500 text-xs mt-1">
          可用余额: {{ formattedBalance }} {{ tokenSymbol }}
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          @click="handleApprove"
          :loading="approving"
          :disabled="!isConnected"
          class="w-full"
        >
          确认授权
        </el-button>
      </el-form-item>
    </el-form>
    
    <div v-if="currentAllowance !== null" class="mt-4 p-4 bg-gray-50 rounded-lg">
      <div class="text-gray-600 text-sm mb-1">当前授权额度</div>
      <div class="text-gray-900 text-lg">
        {{ formattedAllowance }} {{ tokenSymbol }}
      </div>
    </div>
    
    <div v-if="txHash" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
      <div class="text-green-700 text-sm mb-2">交易已提交</div>
      <a
        :href="`${blockExplorerUrl}/tx/${txHash}`"
        target="_blank"
        class="text-green-600 hover:text-green-700 text-xs break-all"
      >
        {{ txHash }}
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import walletService from '../services/walletService.js'
import tokenService from '../services/utilityTokenService.js'
import { BLOCK_EXPLORER_URL } from '../config/networkConfig.js'

const formRef = ref(null)
const approving = ref(false)
const txHash = ref('')
const balance = ref('0')
const currentAllowance = ref(null)
const tokenSymbol = ref('UTIL')
const blockExplorerUrl = BLOCK_EXPLORER_URL

const form = reactive({
  spender: '',
  amount: '',
})

const isConnected = computed(() => walletService.isConnected())

const formattedBalance = computed(() => {
  if (!balance.value || balance.value === '0') return '0.00'
  const num = parseFloat(balance.value)
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  })
})

const formattedAllowance = computed(() => {
  if (currentAllowance.value === null) return '-'
  const num = parseFloat(currentAllowance.value)
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  })
})

// 验证规则
const validateAddress = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入被授权地址'))
  } else if (!/^0x[a-fA-F0-9]{40}$/.test(value)) {
    callback(new Error('地址格式不正确'))
  } else {
    callback()
  }
}

const validateAmount = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入授权金额'))
  } else if (isNaN(value) || parseFloat(value) <= 0) {
    callback(new Error('请输入有效的金额'))
  } else {
    callback()
  }
}

const rules = {
  spender: [{ validator: validateAddress, trigger: 'blur' }],
  amount: [{ validator: validateAmount, trigger: 'blur' }],
}

const loadBalance = async () => {
  if (!isConnected.value) return

  try {
    const account = walletService.getAccount()
    balance.value = await tokenService.getBalance(account)
  } catch (error) {
    console.error('加载余额失败:', error)
  }
}

const loadAllowance = async () => {
  if (!isConnected.value || !form.spender) {
    currentAllowance.value = null
    return
  }

  try {
    const owner = walletService.getAccount()
    currentAllowance.value = await tokenService.allowance(owner, form.spender)
  } catch (error) {
    console.error('加载授权额度失败:', error)
    currentAllowance.value = null
  }
}

const loadTokenInfo = async () => {
  try {
    const info = await tokenService.getTokenInfo()
    tokenSymbol.value = info.symbol
  } catch (error) {
    console.error('加载代币信息失败:', error)
  }
}

const handleApprove = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (!isConnected.value) {
      ElMessage.warning('请先连接钱包')
      return
    }

    approving.value = true
    txHash.value = ''

    try {
      const tx = await tokenService.approve(form.spender, form.amount)
      txHash.value = tx.hash
      ElMessage.success('交易已提交，等待确认...')

      // 等待交易确认
      const receipt = await tokenService.waitForTransaction(tx.hash)
      if (receipt.status === 1) {
        ElMessage.success('授权成功！')
        // 重置表单
        form.amount = ''
        txHash.value = ''
        // 刷新授权额度
        await loadAllowance()
      } else {
        ElMessage.error('交易失败')
      }
    } catch (error) {
      console.error('授权失败:', error)
      ElMessage.error(error.message || '授权失败')
    } finally {
      approving.value = false
    }
  })
}

watch(
  () => form.spender,
  () => {
    loadAllowance()
  }
)

watch(isConnected, (connected) => {
  if (connected) {
    loadBalance()
    loadTokenInfo()
  }
})

onMounted(() => {
  if (isConnected.value) {
    loadBalance()
    loadTokenInfo()
  }

  walletService.on('accountsChanged', () => {
    loadBalance()
    loadAllowance()
  })
})
</script>

<style scoped>
.token-approve {
  min-height: 300px;
}

:deep(.el-form-item__label) {
  color: #030213;
}

:deep(.custom-input .el-input__wrapper) {
  background: #f3f3f5;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

:deep(.custom-input .el-input__inner) {
  color: #030213;
}
</style>

