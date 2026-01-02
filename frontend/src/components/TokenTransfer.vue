<template>
  <div class="token-transfer bg-white rounded-xl border border-gray-200 p-6">
    <h3 class="text-xl text-gray-900 font-semibold mb-6">转账</h3>
    
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" class="token-form">
      <el-form-item label="接收地址" prop="to">
        <el-input
          v-model="form.to"
          placeholder="0x..."
          :disabled="transferring"
          class="custom-input"
        />
      </el-form-item>
      
      <el-form-item label="金额" prop="amount">
        <el-input
          v-model="form.amount"
          placeholder="0.0"
          :disabled="transferring"
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
          @click="handleTransfer"
          :loading="transferring"
          :disabled="!isConnected"
          class="w-full"
        >
          确认转账
        </el-button>
      </el-form-item>
    </el-form>
    
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
const transferring = ref(false)
const txHash = ref('')
const balance = ref('0')
const tokenSymbol = ref('UTIL')
const blockExplorerUrl = BLOCK_EXPLORER_URL

const form = reactive({
  to: '',
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

// 验证规则
const validateAddress = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入接收地址'))
  } else if (!/^0x[a-fA-F0-9]{40}$/.test(value)) {
    callback(new Error('地址格式不正确'))
  } else {
    callback()
  }
}

const validateAmount = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入转账金额'))
  } else if (isNaN(value) || parseFloat(value) <= 0) {
    callback(new Error('请输入有效的金额'))
  } else if (parseFloat(value) > parseFloat(balance.value)) {
    callback(new Error('余额不足'))
  } else {
    callback()
  }
}

const rules = {
  to: [{ validator: validateAddress, trigger: 'blur' }],
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

const loadTokenInfo = async () => {
  try {
    const info = await tokenService.getTokenInfo()
    tokenSymbol.value = info.symbol
  } catch (error) {
    console.error('加载代币信息失败:', error)
  }
}

const handleTransfer = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (!isConnected.value) {
      ElMessage.warning('请先连接钱包')
      return
    }

    transferring.value = true
    txHash.value = ''

    try {
      const tx = await tokenService.transfer(form.to, form.amount)
      txHash.value = tx.hash
      ElMessage.success('交易已提交，等待确认...')

      // 等待交易确认
      const receipt = await tokenService.waitForTransaction(tx.hash)
      if (receipt.status === 1) {
        ElMessage.success('转账成功！')
        // 重置表单
        form.to = ''
        form.amount = ''
        txHash.value = ''
        // 刷新余额
        await loadBalance()
      } else {
        ElMessage.error('交易失败')
      }
    } catch (error) {
      console.error('转账失败:', error)
      ElMessage.error(error.message || '转账失败')
    } finally {
      transferring.value = false
    }
  })
}

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
  })
})
</script>

<style scoped>
.token-transfer {
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

