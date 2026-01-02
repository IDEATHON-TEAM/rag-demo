<template>
  <div class="nft-marketplace min-h-screen bg-white p-6">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-4xl text-gray-900 mb-8">
        NFT 市场
      </h1>
      
      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 mb-6 shadow-sm">
        <div class="flex gap-4 items-center flex-wrap">
          <el-input
            v-model="searchQuery"
            placeholder="搜索NFT..."
            class="flex-1 min-w-[200px]"
            clearable
          />
          <el-select v-model="sortBy" placeholder="排序方式" class="w-[150px]">
            <el-option label="最新" value="recent" />
            <el-option label="价格" value="price" />
            <el-option label="销量" value="sales" />
          </el-select>
          <el-button type="primary" @click="loadNFTs">搜索</el-button>
        </div>
      </div>
      
      <!-- NFT列表 -->
      <div v-loading="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="nft in nfts"
          :key="nft.token_id"
          class="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 transition-all cursor-pointer shadow-sm"
          @click="viewNFTDetail(nft)"
        >
          <div class="mb-4">
            <div class="text-sm text-gray-500 mb-2">Token ID: {{ nft.token_id }}</div>
            <div class="text-lg text-gray-900 font-semibold mb-2">RAG ID: {{ nft.rag_id }}</div>
            <div class="text-sm text-gray-700 line-clamp-2">
              IPFS CID: {{ nft.ipfsCID?.slice(0, 20) }}...
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
        <div class="text-gray-500 text-lg">暂无NFT</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ethers } from 'ethers'

const API_BASE = 'http://localhost:8000'

const nfts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('recent')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)

const formatPrice = (price) => {
  if (!price) return '0'
  try {
    const priceInEth = ethers.formatEther(price.toString())
    return parseFloat(priceInEth).toFixed(6)
  } catch (e) {
    return price.toString()
  }
}

const loadNFTs = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
      sort_by: sortBy.value
    })
    
    const resp = await fetch(`${API_BASE}/v1/nft/marketplace?${params}`)
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

const viewNFTDetail = (nft) => {
  // 可以导航到NFT详情页
  console.log('View NFT:', nft)
  ElMessage.info('NFT详情功能开发中')
}

onMounted(() => {
  loadNFTs()
})
</script>

<style scoped>
:deep(.el-input__wrapper) {
  background: #f3f3f5 !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-input__inner) {
  color: #030213 !important;
}

:deep(.el-select .el-input__wrapper) {
  background: #f3f3f5 !important;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

