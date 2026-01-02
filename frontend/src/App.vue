<template>
  <div class="min-h-screen bg-white relative overflow-hidden">
    <!-- 导航栏 -->
    <nav class="relative z-10 px-6 py-4 flex justify-between items-center border-b border-gray-200 bg-white">
      <div class="flex items-center gap-2">
        <div class="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>
        <span class="text-gray-900 text-xl font-semibold">RAG 知识变现平台</span>
      </div>
      <div class="flex items-center gap-4">
        <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="web3-tabs">
          <el-tab-pane label="RAG功能" name="rag"></el-tab-pane>
          <el-tab-pane label="NFT市场" name="marketplace"></el-tab-pane>
          <el-tab-pane label="我的NFT" name="my-nfts"></el-tab-pane>
          <el-tab-pane label="查询历史" name="query-history"></el-tab-pane>
          <el-tab-pane label="代币管理" name="token"></el-tab-pane>
        </el-tabs>
        <WalletConnect />
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="relative z-10 container mx-auto px-6 py-12">
      <div class="max-w-4xl mx-auto">
        <!-- RAG功能页面 -->
        <div v-if="activeTab === 'rag'">
          <!-- 步骤 1: 文件上传 -->
          <div v-if="!currentRagId" class="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
          <div class="text-center mb-8">
            <h2 class="text-3xl text-gray-900 mb-4">
              第一步：上传您的知识文件
            </h2>
            <p class="text-gray-600">支持 PDF、Word、PPT、TXT 文件，生成您的专属知识库</p>
          </div>
          
          <div class="upload-container">
            <el-upload
              class="upload-demo"
              drag
              :action="uploadUrlWithParams"
              :on-success="handleRagCreated"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              v-loading="loading"
            >
              <div class="flex flex-col items-center justify-center py-12">
                <div class="w-16 h-16 bg-gray-900 rounded-xl flex items-center justify-center mb-4">
                  <el-icon class="text-white text-3xl"><upload-filled /></el-icon>
                </div>
                <div class="text-gray-900 text-lg mb-2">
                  将文件拖到此处，或 <em class="text-gray-700">点击上传</em>
                </div>
                <div class="text-gray-500 text-sm">
                  支持 PDF、Word、PPT、TXT 文件
                </div>
              </div>
            </el-upload>
            <div v-if="loading" class="mt-6 text-center">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg border border-gray-200">
                <div class="w-2 h-2 bg-gray-600 rounded-full animate-pulse"></div>
                <span class="text-gray-700">正在为您构建知识库，请稍候...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2: 问答测试 -->
        <div v-else class="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-3xl text-gray-900">
              第二步：测试您的 RAG 智能体
            </h2>
            <el-button 
              type="primary" 
              link 
              @click="reset"
              class="text-gray-700 hover:text-gray-900"
            >
              重新上传
            </el-button>
          </div>
          
          <div class="chat-container bg-gray-50 rounded-xl border border-gray-200 p-6 mb-6 min-h-[300px] max-h-[400px] overflow-y-auto">
            <div v-if="chatHistory.length === 0" class="flex items-center justify-center h-full text-gray-500">
              <div class="text-center">
                <div class="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <p>试着问一些关于文档的问题吧！</p>
              </div>
            </div>
            <div v-for="(msg, index) in chatHistory" :key="index" class="message-item mb-4">
              <div :class="[
                'message-bubble px-4 py-3 rounded-xl max-w-[80%]',
                msg.role === 'user' 
                  ? 'bg-gray-900 text-white ml-auto' 
                  : 'bg-white text-gray-900 border border-gray-200'
              ]">
                <strong class="mr-2">{{ msg.role === 'user' ? '你' : 'AI' }}:</strong> 
                <span>{{ msg.content }}</span>
              </div>
              <!-- NFT铸造按钮 -->
              <div v-if="msg.role === 'bot' && msg.queryRecord" class="mint-nft-section mt-2 flex justify-end">
                <el-button 
                  size="small" 
                  @click="mintQueryAsNFT(msg.queryRecord)"
                  :loading="mintingQueryId === msg.queryRecord.query_id"
                  :disabled="!isWalletConnected"
                  type="success"
                >
                  {{ mintingQueryId === msg.queryRecord.query_id ? '铸造中...' : '铸造为NFT' }}
                </el-button>
              </div>
            </div>
          </div>

          <div class="input-area mb-6">
            <el-input
              v-model="question"
              placeholder="请输入您的问题..."
              @keyup.enter="ask"
              :disabled="asking"
              size="large"
              class="custom-input"
            >
              <template #append>
                <el-button 
                  @click="ask" 
                  :loading="asking"
                  type="primary"
                >
                  发送
                </el-button>
              </template>
            </el-input>
          </div>

          <div class="border-t border-gray-200 pt-6">
            <!-- 步骤 3: NFT铸造 -->
            <div class="pricing-section text-center">
              <h3 class="text-2xl text-gray-900 mb-6">觉得满意吗？铸造为NFT知识资产</h3>
              
              <!-- 显示铸造数据 -->
              <div v-if="mintData && !mintingNFT && !mintedTokenId" class="mint-data bg-gray-50 rounded-xl border border-gray-200 p-6 max-w-2xl mx-auto">
                <el-alert
                  title="铸造数据已准备就绪"
                  type="info"
                  :closable="false"
                  class="mb-4"
                />
                <div class="text-left space-y-2 text-sm text-gray-700 mb-4">
                  <div>IPFS CID: <code class="bg-gray-200 px-2 py-1 rounded break-all">{{ mintData.ipfs_cid }}</code></div>
                  <div>向量哈希: <code class="bg-gray-200 px-2 py-1 rounded break-all">{{ mintData.vector_hash_hex.slice(0, 20) }}...</code></div>
                  <div>价格: {{ formatPrice(mintData.price) }} wei</div>
                  <div v-if="!isWalletConnected" class="text-yellow-600 text-xs mt-2">
                    ⚠️ 请先连接钱包才能铸造NFT
                  </div>
                </div>
                <el-button 
                  type="success" 
                  size="large" 
                  @click="mintNFT"
                  :loading="mintingNFT"
                  :disabled="!isWalletConnected"
                  class="w-full"
                >
                  {{ isWalletConnected ? '确认铸造NFT' : '请先连接钱包' }}
                </el-button>
              </div>
              
              <!-- 铸造中 -->
              <div v-if="mintingNFT" class="minting-status text-center">
                <el-icon class="is-loading text-gray-600 text-4xl mb-4"><Loading /></el-icon>
                <div class="text-gray-700">正在铸造NFT，请等待交易确认...</div>
                <div v-if="mintTxHash" class="mt-2">
                  <a :href="`https://sepolia.etherscan.io/tx/${mintTxHash}`" target="_blank" class="text-gray-600 hover:text-gray-900 text-sm">
                    查看交易: {{ mintTxHash.slice(0, 10) }}...
                  </a>
                </div>
              </div>
              
              <!-- 铸造成功 -->
              <div v-if="mintedTokenId" class="mint-success bg-green-50 border border-green-200 rounded-xl p-6 max-w-md mx-auto">
                <el-alert
                  :title="`NFT铸造成功！Token ID: ${mintedTokenId}`"
                  type="success"
                  :closable="false"
                  show-icon
                  class="mb-4"
                />
                <div class="text-center space-y-2">
                  <div v-if="mintTxHash">
                    <a :href="`https://sepolia.etherscan.io/tx/${mintTxHash}`" target="_blank" class="text-green-600 hover:text-green-700 text-sm">
                      查看交易详情
                    </a>
                  </div>
                  <el-button 
                    type="primary" 
                    @click="resetMintStatus"
                    class="mt-4"
                  >
                    重新铸造
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>

        <!-- NFT市场页面 -->
        <div v-if="activeTab === 'marketplace'">
          <NFTMarketplace />
        </div>

        <!-- 我的NFT页面 -->
        <div v-if="activeTab === 'my-nfts'">
          <MyNFTs />
        </div>

        <!-- 查询历史页面 -->
        <div v-if="activeTab === 'query-history'">
          <QueryHistory />
        </div>

        <!-- 代币管理页面 -->
        <div v-if="activeTab === 'token'" class="space-y-6">
          <div class="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
            <h2 class="text-3xl text-gray-900 mb-6">
              UtilityToken 代币管理
            </h2>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- 余额显示 -->
              <TokenBalance :show-total-supply="true" />
              
              <!-- 转账 -->
              <TokenTransfer />
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              <!-- 授权 -->
              <TokenApprove />
              
              <!-- 铸造（仅owner） -->
              <TokenMint />
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 支付对话框 -->
    <PaymentDialog 
      v-model:visible="paymentDialogVisible"
      :payment-info="paymentInfo"
      @purchase="handlePurchase"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Loading } from '@element-plus/icons-vue'
import WalletConnect from './components/WalletConnect.vue'
import TokenBalance from './components/TokenBalance.vue'
import TokenTransfer from './components/TokenTransfer.vue'
import TokenApprove from './components/TokenApprove.vue'
import TokenMint from './components/TokenMint.vue'
import PaymentDialog from './components/PaymentDialog.vue'
import NFTMarketplace from './views/NFTMarketplace.vue'
import MyNFTs from './views/MyNFTs.vue'
import QueryHistory from './views/QueryHistory.vue'
import walletService from './services/walletService.js'
import knowledgeNFTService from './services/knowledgeNFTService.js'

// 配置后端 API 地址
const API_BASE = 'http://localhost:8000';

// NFT铸造相关状态
const enableNFTMint = ref(false)
const mintData = ref(null)
const mintingNFT = ref(false)
const mintTxHash = ref('')
const mintedTokenId = ref(null)
const nftForm = ref({
  price: 0
})

// 查询结果NFT铸造相关状态
const mintingQueryId = ref(null)
const paymentDialogVisible = ref(false)
const paymentInfo = ref(null)

const isWalletConnected = computed(() => walletService.isConnected())

// 动态生成上传URL（包含NFT参数）
const uploadUrlWithParams = computed(() => {
  let url = `${API_BASE}/v1/rag/`
  if (enableNFTMint.value) {
    url += `?mint_nft=true`
    if (nftForm.value.price > 0) {
      url += `&price=${nftForm.value.price}`
    }
  }
  return url
})

const activeTab = ref('rag')
const currentRagId = ref('')
const question = ref('')
const chatHistory = ref([])
const asking = ref(false)
const loading = ref(false)
const priceOptions = ref(null)


const handleTabChange = (tabName) => {
  activeTab.value = tabName
}

const formatPrice = (price) => {
  if (!price) return '0'
  return BigInt(price).toString()
}

const prepareMintNFT = async () => {
  if (!currentRagId.value) {
    ElMessage.warning('请先上传文档并创建RAG')
    return
  }
  
  if (!isWalletConnected.value) {
    ElMessage.warning('请先连接钱包')
    return
  }
  
  try {
    const price = nftForm.value.price || 0
    const resp = await fetch(`${API_BASE}/v1/rag/?price=${price}&mint_nft=true`, {
      method: 'POST',
      body: new FormData().append('file', new Blob()) // 这里需要重新上传文件，或者后端支持通过rag_id获取
    })
    
    // 实际上应该调用一个专门的接口来准备铸造数据
    // 这里简化处理，假设后端返回了mint_data
    const data = await resp.json()
    if (data.mint_data) {
      mintData.value = data.mint_data
      ElMessage.success('铸造数据准备成功')
    } else {
      ElMessage.error('获取铸造数据失败')
    }
  } catch (e) {
    ElMessage.error('准备铸造数据失败: ' + e.message)
  }
}

const mintNFT = async () => {
  if (!mintData.value) {
    ElMessage.warning('请先准备铸造数据')
    return
  }
  
  mintingNFT.value = true
  mintTxHash.value = ''
  
  try {
    const result = await knowledgeNFTService.mintNFT(
      mintData.value.ipfs_cid,
      mintData.value.vector_hash_hex,
      mintData.value.price
    )
    
    mintTxHash.value = result.txHash
    mintedTokenId.value = result.tokenId
    
    // 注册NFT到后端
    try {
      await fetch(`${API_BASE}/v1/nft/register?rag_id=${currentRagId.value}&token_id=${result.tokenId}`, {
        method: 'POST'
      })
    } catch (e) {
      console.error('注册NFT失败:', e)
      // 不影响主流程
    }
    
    ElMessage.success('NFT铸造成功！')
  } catch (e) {
    console.error('铸造NFT失败:', e)
    ElMessage.error('铸造失败: ' + (e.message || '未知错误'))
  } finally {
    mintingNFT.value = false
  }
}

const resetMintStatus = () => {
  mintData.value = null
  mintTxHash.value = ''
  mintedTokenId.value = null
  enableNFTMint.value = false
  nftForm.value.price = 0
}

const beforeUpload = () => {
  loading.value = true;
  return true;
}

const handleUploadError = (err) => {
  loading.value = false;
  ElMessage.error('上传失败，请重试。后端服务是否已启动？');
  console.error(err);
}

const handleRagCreated = (response) => {
  loading.value = false;
  currentRagId.value = response.rag_id;
  ElMessage.success('知识库构建成功！');
}

const ask = async () => {
  if (!question.value.trim()) return;
  
  // 获取钱包地址
  const userAddress = walletService.getAddress();
  if (!userAddress) {
    ElMessage.warning('请先连接钱包');
    return;
  }
  
  const q = question.value;
  chatHistory.value.push({ role: 'user', content: q });
  question.value = '';
  asking.value = true;

  try {
    const resp = await fetch(`${API_BASE}/v1/chat/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        rag_id: currentRagId.value, 
        question: q,
        user_address: userAddress  // 传递钱包地址
      })
    });
    
    if (resp.status === 403) {
      // 权限不足，显示支付UI
      const errorData = await resp.json();
      paymentInfo.value = errorData.detail;
      paymentDialogVisible.value = true;
      return;
    }
    
    if (!resp.ok) throw new Error('Network response was not ok');
    
    const data = await resp.json();
    
    // 保存查询记录（包含query_id）
    const queryRecord = {
      query_id: data.query_id,
      question: q,
      answer: data.answer,
      sources: data.sources || [],
      rag_id: currentRagId.value,
      timestamp: new Date().toISOString()
    };
    
    chatHistory.value.push({ 
      role: 'bot', 
      content: data.answer,
      queryRecord: queryRecord  // 保存查询记录用于NFT铸造
    });
  } catch (e) {
    ElMessage.error('回答失败: ' + e.message);
    chatHistory.value.push({ role: 'bot', content: '抱歉，我遇到了一些问题，请稍后再试。' });
  } finally {
    asking.value = false;
  }
}

// 将查询结果铸造为NFT
const mintQueryAsNFT = async (queryRecord) => {
  if (!isWalletConnected.value) {
    ElMessage.warning('请先连接钱包');
    return;
  }
  
  const userAddress = walletService.getAddress();
  if (!userAddress) {
    ElMessage.warning('请先连接钱包');
    return;
  }
  
  // 显示价格输入对话框
  const priceInput = prompt('请输入NFT价格（wei，0表示免费）:', '0');
  if (priceInput === null) return; // 用户取消
  
  const price = parseInt(priceInput) || 0;
  
  mintingQueryId.value = queryRecord.query_id;
  
  try {
    // 调用后端接口准备铸造数据
    const resp = await fetch(`${API_BASE}/v1/nft/mint_query`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query_id: queryRecord.query_id,
        price: price,
        user_address: userAddress
      })
    });
    
    if (!resp.ok) {
      const errorData = await resp.json();
      throw new Error(errorData.detail || '准备铸造数据失败');
    }
    
    const mintData = await resp.json();
    
    // 调用合约铸造NFT
    const result = await knowledgeNFTService.mintNFT(
      mintData.ipfs_cid,
      mintData.vector_hash_hex,
      price
    );
    
    ElMessage.success(`NFT铸造成功！Token ID: ${result.tokenId}`);
    
    // 更新查询记录，标记为已铸造
    const msgIndex = chatHistory.value.findIndex(
      msg => msg.queryRecord && msg.queryRecord.query_id === queryRecord.query_id
    );
    if (msgIndex !== -1 && chatHistory.value[msgIndex].queryRecord) {
      chatHistory.value[msgIndex].queryRecord.minted_as_nft = true;
      chatHistory.value[msgIndex].queryRecord.nft_token_id = result.tokenId;
    }
    
  } catch (e) {
    console.error('铸造NFT失败:', e);
    ElMessage.error('铸造失败: ' + (e.message || '未知错误'));
  } finally {
    mintingQueryId.value = null;
  }
}

// 处理支付对话框的购买操作
const handlePurchase = async () => {
  if (!paymentInfo.value) return;
  
  try {
    const userAddress = walletService.getAddress();
    if (!userAddress) {
      ElMessage.warning('请先连接钱包');
      return;
    }
    
    // 调用合约购买访问权限
    const result = await knowledgeNFTService.purchaseAccess(paymentInfo.value.token_id);
    
    ElMessage.success('购买成功！');
    paymentDialogVisible.value = false;
    
    // 重新查询
    // 这里可以触发重新查询，或者提示用户重新提问
    ElMessage.info('购买成功，请重新提问');
    
  } catch (e) {
    console.error('购买失败:', e);
    ElMessage.error('购买失败: ' + (e.message || '未知错误'));
  }
}

const showPricing = async () => {
  try {
    const resp = await fetch(`${API_BASE}/v1/pricing_preview/?rag_id=${currentRagId.value}`);
    const data = await resp.json();
    priceOptions.value = data.price_options;
  } catch (e) {
    ElMessage.error('获取定价失败');
  }
}

const reset = () => {
  currentRagId.value = '';
  chatHistory.value = [];
  priceOptions.value = null;
  question.value = '';
  resetMintStatus();
}
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

/* 自定义 Element Plus 组件样式 - 全白简洁风格 */
:deep(.el-upload-dragger) {
  background: #f3f3f5 !important;
  border: 2px dashed rgba(0, 0, 0, 0.1) !important;
  border-radius: 0.625rem !important;
  transition: all 0.3s ease !important;
}

:deep(.el-upload-dragger:hover) {
  background: #e9ebef !important;
  border-color: rgba(0, 0, 0, 0.2) !important;
}

:deep(.custom-input .el-input__wrapper) {
  background: #f3f3f5 !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  box-shadow: none !important;
}

:deep(.custom-input .el-input__inner) {
  color: #030213 !important;
}

:deep(.custom-input .el-input__inner::placeholder) {
  color: #717182 !important;
}

:deep(.el-card) {
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-message) {
  background: #ffffff !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-alert) {
  background: #f0f9ff !important;
  border: 1px solid #bfdbfe !important;
}

:deep(.el-alert__title) {
  color: #1e40af !important;
}

/* 消息气泡样式优化 */
.message-item {
  display: flex;
  flex-direction: column;
}

.message-item .message-bubble.user-msg {
  margin-left: auto;
  text-align: right;
}

.message-item .message-bubble.bot-msg {
  margin-right: auto;
  text-align: left;
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: #ececf0;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 标签页样式 */
:deep(.web3-tabs .el-tabs__header) {
  margin: 0;
}

:deep(.web3-tabs .el-tabs__nav-wrap::after) {
  background-color: rgba(0, 0, 0, 0.1);
}

:deep(.web3-tabs .el-tabs__item) {
  color: #717182;
  border-bottom: 2px solid transparent;
}

:deep(.web3-tabs .el-tabs__item.is-active) {
  color: #030213;
  border-bottom-color: #030213;
}

:deep(.web3-tabs .el-tabs__item:hover) {
  color: #030213;
}

:deep(.web3-tabs .el-tabs__active-bar) {
  background-color: #030213;
}
</style>
