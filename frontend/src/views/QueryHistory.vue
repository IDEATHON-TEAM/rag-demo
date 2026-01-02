<template>
  <div class="query-history min-h-screen bg-white p-6">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-4xl text-gray-900 mb-8">
        查询历史
      </h1>
      
      <!-- 筛选 -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 mb-6 shadow-sm">
        <div class="flex gap-4 items-center flex-wrap">
          <el-input
            v-model="ragIdFilter"
            placeholder="过滤RAG ID..."
            class="flex-1 min-w-[200px]"
            clearable
          />
          <el-button type="primary" @click="loadHistory">刷新</el-button>
        </div>
      </div>
      
      <!-- 查询历史列表 -->
      <div v-loading="loading" class="space-y-4">
        <div
          v-for="query in queries"
          :key="query.query_id"
          class="bg-white rounded-xl border border-gray-200 p-6 hover:border-gray-300 transition-all shadow-sm"
        >
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <div class="text-sm text-gray-500 mb-2">
                Query ID: {{ query.query_id }} | RAG ID: {{ query.rag_id }}
              </div>
              <div class="text-lg text-gray-900 font-semibold mb-2">
                {{ query.question }}
              </div>
              <div class="text-gray-700 text-sm line-clamp-3 mb-2">
                {{ query.answer }}
              </div>
              <div class="text-xs text-gray-500">
                {{ formatDate(query.created_at) }}
              </div>
            </div>
            
            <div class="ml-4 flex flex-col gap-2">
              <el-button
                v-if="!query.minted_as_nft"
                size="small"
                type="success"
                @click="mintQuery(query)"
                :loading="mintingQueryId === query.query_id"
                :disabled="!isWalletConnected"
              >
                铸造为NFT
              </el-button>
              <el-tag v-else type="success" size="small">
                已铸造 (Token: {{ query.nft_token_id }})
              </el-tag>
              <el-button size="small" @click="viewDetail(query)">查看详情</el-button>
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
      <div v-if="!loading && queries.length === 0" class="text-center py-12">
        <div class="text-gray-500 text-lg">暂无查询历史</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import walletService from '../services/walletService.js'
import knowledgeNFTService from '../services/knowledgeNFTService.js'

const API_BASE = 'http://localhost:8000'

const queries = ref([])
const loading = ref(false)
const ragIdFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)
const mintingQueryId = ref(null)

const isWalletConnected = computed(() => walletService.isConnected())
const userAddress = computed(() => walletService.getAddress())

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch (e) {
    return '未知'
  }
}

const loadHistory = async () => {
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
    
    if (ragIdFilter.value) {
      params.append('rag_id', ragIdFilter.value)
    }
    
    const resp = await fetch(`${API_BASE}/v1/query/history?${params}`)
    if (!resp.ok) throw new Error('Failed to load query history')
    
    const data = await resp.json()
    queries.value = data.queries || []
    total.value = data.total || 0
    totalPages.value = data.total_pages || 0
  } catch (e) {
    console.error('加载查询历史失败:', e)
    ElMessage.error('加载查询历史失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadHistory()
}

const mintQuery = async (query) => {
  if (!isWalletConnected.value) {
    ElMessage.warning('请先连接钱包')
    return
  }
  
  const priceInput = prompt('请输入NFT价格（wei，0表示免费）:', '0')
  if (priceInput === null) return
  
  const price = parseInt(priceInput) || 0
  mintingQueryId.value = query.query_id
  
  try {
    // 调用后端接口准备铸造数据
    const resp = await fetch(`${API_BASE}/v1/nft/mint_query`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query_id: query.query_id,
        price: price,
        user_address: userAddress.value
      })
    })
    
    if (!resp.ok) {
      const errorData = await resp.json()
      throw new Error(errorData.detail || '准备铸造数据失败')
    }
    
    const mintData = await resp.json()
    
    // 调用合约铸造NFT
    const result = await knowledgeNFTService.mintNFT(
      mintData.ipfs_cid,
      mintData.vector_hash_hex,
      price
    )
    
    ElMessage.success(`NFT铸造成功！Token ID: ${result.tokenId}`)
    
    // 重新加载历史
    loadHistory()
    
  } catch (e) {
    console.error('铸造NFT失败:', e)
    ElMessage.error('铸造失败: ' + (e.message || '未知错误'))
  } finally {
    mintingQueryId.value = null
  }
}

const viewDetail = (query) => {
  console.log('View query detail:', query)
  ElMessage.info('查询详情功能开发中')
}

onMounted(() => {
  if (userAddress.value) {
    loadHistory()
  } else {
    ElMessage.warning('请先连接钱包')
  }
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

</style>

