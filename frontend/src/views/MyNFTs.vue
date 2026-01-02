<template>
  <div class="my-nfts min-h-screen bg-white p-6">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-4xl text-gray-900 mb-8">
        我的 NFT
      </h1>
      
      <div v-loading="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="nft in nfts"
          :key="nft.token_id"
          class="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 transition-all shadow-sm"
        >
          <div class="mb-4">
            <div class="text-sm text-gray-500 mb-2">Token ID: {{ nft.token_id }}</div>
            <div class="text-lg text-gray-900 font-semibold mb-2">RAG ID: {{ nft.rag_id }}</div>
            <div class="text-sm text-gray-700 line-clamp-2 mb-2">
              IPFS CID: {{ nft.ipfsCID?.slice(0, 20) }}...
            </div>
            <div class="text-xs text-gray-500">
              创建时间: {{ formatDate(nft.createdAt) }}
            </div>
          </div>
          
          <div class="flex justify-between items-center pt-4 border-t border-gray-200">
            <div>
              <div class="text-xs text-gray-500">价格</div>
              <div class="text-lg font-semibold text-gray-900">
                {{ formatPrice(nft.price) }} ETH
              </div>
            </div>
            <div class="text-right">
              <div class="text-xs text-gray-500">销量</div>
              <div class="text-lg font-semibold text-gray-900">
                {{ nft.totalSales || 0 }}
              </div>
            </div>
          </div>
          
          <div class="mt-4 flex gap-2">
            <el-button size="small" @click="viewDetail(nft)">查看详情</el-button>
            <el-button size="small" type="primary" @click="shareNFT(nft)">分享</el-button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="totalPages > 1" class="mt-6 flex justify-center">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && nfts.length === 0" class="text-center py-12">
        <div class="text-gray-500 text-lg">您还没有NFT</div>
        <div class="text-gray-400 text-sm mt-2">查询知识库后可以铸造NFT</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ethers } from 'ethers'
import walletService from '../services/walletService.js'

const API_BASE = 'http://localhost:8000'

const nfts = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)

const userAddress = computed(() => walletService.getAddress())

const formatPrice = (price) => {
  if (!price) return '0'
  try {
    const priceInEth = ethers.formatEther(price.toString())
    return parseFloat(priceInEth).toFixed(6)
  } catch (e) {
    return price.toString()
  }
}

const formatDate = (timestamp) => {
  if (!timestamp) return '未知'
  try {
    const date = new Date(Number(timestamp) * 1000)
    return date.toLocaleDateString('zh-CN')
  } catch (e) {
    return '未知'
  }
}

const loadNFTs = async () => {
  if (!userAddress.value) {
    ElMessage.warning('请先连接钱包')
    return
  }
  
  loading.value = true
  try {
    const params = new URLSearchParams({
      user_address: userAddress.value,
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString()
    })
    
    const resp = await fetch(`${API_BASE}/v1/nft/my_nfts?${params}`)
    if (!resp.ok) throw new Error('Failed to load NFTs')
    
    const data = await resp.json()
    nfts.value = data.nfts || []
    total.value = data.total || 0
    totalPages.value = data.total_pages || 0
  } catch (e) {
    console.error('加载NFT失败:', e)
    ElMessage.error('加载NFT失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadNFTs()
}

const viewDetail = (nft) => {
  console.log('View NFT detail:', nft)
  ElMessage.info('NFT详情功能开发中')
}

const shareNFT = async (nft) => {
  const shareUrl = `${window.location.origin}/nft/${nft.token_id}`
  try {
    await navigator.clipboard.writeText(shareUrl)
    ElMessage.success('分享链接已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

onMounted(() => {
  if (userAddress.value) {
    loadNFTs()
  } else {
    ElMessage.warning('请先连接钱包')
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

</style>

