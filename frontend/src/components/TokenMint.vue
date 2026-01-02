<template>
  <div class="token-mint bg-white rounded-xl border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl text-gray-900 font-semibold">铸造代币</h3>
      <el-tag v-if="isOwner" type="success" size="small">Owner</el-tag>
      <el-tag v-else type="danger" size="small">非Owner</el-tag>
    </div>
    
    <el-alert
      v-if="!isOwner"
      title="只有合约所有者可以铸造代币"
      type="warning"
      :closable="false"
      class="mb-6"
    />
    
    <el-form
      v-if="isOwner"
      :model="form"
      :rules="rules"
      ref="formRef"
      label-width="100px"
      class="token-form"
    >
      <el-form-item label="接收地址" prop="to">
        <el-input
          v-model="form.to"
          placeholder="0x..."
          :disabled="minting"
          class="custom-input"
        />
      </el-form-item>
      
      <el-form-item label="铸造数量" prop="amount">
        <el-input
          v-model="form.amount"
          placeholder="0.0"
          :disabled="minting"
          class="custom-input"
        >
          <template #append>
            <span class="text-gray-600">{{ tokenSymbol }}</span>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          @click="handleMint"
          :loading="minting"
          :disabled="!isConnected"
          class="w-full"
        >
          确认铸造
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
const minting = ref(false)
const txHash = ref('')
const isOwner = ref(false)
const checkingOwner = ref(false)
const tokenSymbol = ref('UTIL')
const blockExplorerUrl = BLOCK_EXPLORER_URL

const form = reactive({
  to: '',
  amount: '',
})

const isConnected = computed(() => walletService.isConnected())

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
    callback(new Error('请输入铸造数量'))
  } else if (isNaN(value) || parseFloat(value) <= 0) {
    callback(new Error('请输入有效的数量'))
  } else {
    callback()
  }
}

const rules = {
  to: [{ validator: validateAddress, trigger: 'blur' }],
  amount: [{ validator: validateAmount, trigger: 'blur' }],
}

const checkOwner = async () => {
  if (!isConnected.value) {
    isOwner.value = false
    return
  }

  checkingOwner.value = true
  try {
    const account = walletService.getAccount()
    isOwner.value = await tokenService.isOwner(account)
  } catch (error) {
    console.error('检查owner失败:', error)
    isOwner.value = false
  } finally {
    checkingOwner.value = false
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

const handleMint = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (!isConnected.value) {
      ElMessage.warning('请先连接钱包')
      return
    }

    if (!isOwner.value) {
      ElMessage.error('只有合约所有者可以铸造代币')
      return
    }

    minting.value = true
    txHash.value = ''

    try {
      const tx = await tokenService.mint(form.to, form.amount)
      txHash.value = tx.hash
      ElMessage.success('交易已提交，等待确认...')

      // 等待交易确认
      const receipt = await tokenService.waitForTransaction(tx.hash)
      if (receipt.status === 1) {
        ElMessage.success('铸造成功！')
        // 重置表单
        form.to = ''
        form.amount = ''
        txHash.value = ''
      } else {
        ElMessage.error('交易失败')
      }
    } catch (error) {
      console.error('铸造失败:', error)
      ElMessage.error(error.message || '铸造失败')
    } finally {
      minting.value = false
    }
  })
}

watch(isConnected, (connected) => {
  if (connected) {
    checkOwner()
    loadTokenInfo()
  } else {
    isOwner.value = false
  }
})

onMounted(() => {
  if (isConnected.value) {
    checkOwner()
    loadTokenInfo()
  }

  walletService.on('accountsChanged', () => {
    checkOwner()
  })
})
</script>

<style scoped>
.token-mint {
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

:deep(.el-alert) {
  background: #fef3c7;
  border: 1px solid #fbbf24;
}

:deep(.el-alert__title) {
  color: #92400e;
}
</style>

