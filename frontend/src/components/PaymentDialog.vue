<template>
  <el-dialog 
    v-model="dialogVisible" 
    title="购买访问权限" 
    width="500px"
    :close-on-click-modal="false"
  >
    <div class="payment-info">
      <el-alert
        title="您需要购买访问权限才能查询此知识库"
        type="warning"
        :closable="false"
        class="mb-4"
      />
      
      <div v-if="paymentInfo" class="nft-info bg-gray-50 rounded-xl border border-gray-200 p-4 mb-4">
        <div class="space-y-2 text-sm text-gray-700">
          <div class="flex justify-between">
            <span>Token ID:</span>
            <code class="bg-gray-200 px-2 py-1 rounded">{{ paymentInfo.token_id }}</code>
          </div>
          <div class="flex justify-between">
            <span>价格:</span>
            <span class="font-semibold text-gray-900">{{ formatPrice(paymentInfo.price) }} ETH</span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-2 justify-end">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handlePurchase"
          :loading="purchasing"
        >
          确认购买
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ethers } from 'ethers'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  paymentInfo: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'purchase'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const purchasing = ref(false)

const formatPrice = (price) => {
  if (!price) return '0'
  try {
    // 将wei转换为ETH
    const priceInEth = ethers.formatEther(price.toString())
    return parseFloat(priceInEth).toFixed(6)
  } catch (e) {
    return price.toString()
  }
}

const handlePurchase = async () => {
  purchasing.value = true
  try {
    emit('purchase')
  } finally {
    purchasing.value = false
  }
}
</script>

<style scoped>
.payment-info {
  color: #030213;
}

:deep(.el-dialog) {
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

:deep(.el-dialog__header) {
  color: #030213;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

:deep(.el-dialog__body) {
  color: #030213;
}

:deep(.el-alert) {
  background: #fef3c7 !important;
  border: 1px solid #fbbf24 !important;
}

:deep(.el-alert__title) {
  color: #92400e !important;
}
</style>

