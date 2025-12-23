<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
    </div>

    <!-- 导航栏 -->
    <nav class="relative z-10 px-6 py-4 flex justify-between items-center border-b border-white/10 backdrop-blur-sm">
      <div class="flex items-center gap-2">
        <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>
        <span class="text-white text-xl font-semibold">RAG 知识变现平台</span>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="relative z-10 container mx-auto px-6 py-12">
      <div class="max-w-4xl mx-auto">
        <!-- 步骤 1: 文件上传 -->
        <div v-if="!currentRagId" class="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 p-8 shadow-2xl">
          <div class="text-center mb-8">
            <h2 class="text-3xl text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
              第一步：上传您的知识文件
            </h2>
            <p class="text-white/60">支持 PDF、Word、PPT、TXT 文件，生成您的专属知识库</p>
          </div>
          
          <div class="upload-container">
            <el-upload
              class="upload-demo"
              drag
              :action="uploadUrl"
              :on-success="handleRagCreated"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              v-loading="loading"
            >
              <div class="flex flex-col items-center justify-center py-12">
                <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-4">
                  <el-icon class="text-white text-3xl"><upload-filled /></el-icon>
                </div>
                <div class="text-white text-lg mb-2">
                  将文件拖到此处，或 <em class="text-purple-400">点击上传</em>
                </div>
                <div class="text-white/50 text-sm">
                  支持 PDF、Word、PPT、TXT 文件
                </div>
              </div>
            </el-upload>
            <div v-if="loading" class="mt-6 text-center">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/20 backdrop-blur-md rounded-lg border border-purple-500/30">
                <div class="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span class="text-white/80">正在为您构建知识库，请稍候...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤 2: 问答测试 -->
        <div v-else class="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 p-8 shadow-2xl">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-3xl text-white bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
              第二步：测试您的 RAG 智能体
            </h2>
            <el-button 
              type="primary" 
              link 
              @click="reset"
              class="text-purple-400 hover:text-purple-300"
            >
              重新上传
            </el-button>
          </div>
          
          <div class="chat-container bg-black/20 backdrop-blur-sm rounded-xl border border-white/10 p-6 mb-6 min-h-[300px] max-h-[400px] overflow-y-auto">
            <div v-if="chatHistory.length === 0" class="flex items-center justify-center h-full text-white/50">
              <div class="text-center">
                <div class="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white ml-auto' 
                  : 'bg-white/10 backdrop-blur-md text-white border border-white/20'
              ]">
                <strong class="mr-2">{{ msg.role === 'user' ? '你' : 'AI' }}:</strong> 
                <span>{{ msg.content }}</span>
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
                  class="bg-gradient-to-r from-purple-600 to-pink-600 border-0 text-white hover:from-purple-700 hover:to-pink-700"
                >
                  发送
                </el-button>
              </template>
            </el-input>
          </div>

          <div class="border-t border-white/10 pt-6">
            <!-- 步骤 3: 定价预览 -->
            <div class="pricing-section text-center">
              <h3 class="text-2xl text-white mb-6">觉得满意吗？立即生成产品</h3>
              <el-button 
                type="success" 
                size="large" 
                @click="showPricing" 
                v-if="!priceOptions"
                class="bg-gradient-to-r from-green-500 to-emerald-500 border-0 text-white hover:from-green-600 hover:to-emerald-600 px-8 py-3 rounded-xl"
              >
                上架并设定价格
              </el-button>
              
              <div v-if="priceOptions" class="pricing-options mt-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div 
                    v-for="opt in priceOptions" 
                    :key="opt.type"
                    class="bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-6 hover:border-purple-500/50 transition-all hover:scale-105 cursor-pointer"
                  >
                    <h4 class="text-white text-xl mb-4">{{ opt.type }}</h4>
                    <div class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-4">
                      {{ opt.price }}
                    </div>
                    <el-button 
                      type="primary" 
                      plain 
                      size="small"
                      class="w-full border-purple-500 text-purple-400 hover:bg-purple-500/20"
                    >
                      选择此方案
                    </el-button>
                  </div>
                </div>
                <div class="success-hint">
                  <el-alert
                    title="恭喜！您的知识库产品已准备就绪 (模拟)"
                    type="success"
                    :closable="false"
                    show-icon
                    class="bg-green-500/20 border-green-500/50 text-green-300"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

// 配置后端 API 地址
const API_BASE = 'http://localhost:8000'; 
const uploadUrl = `${API_BASE}/v1/rag/`;

const currentRagId = ref('')
const question = ref('')
const chatHistory = ref([])
const asking = ref(false)
const loading = ref(false)
const priceOptions = ref(null)

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
  
  const q = question.value;
  chatHistory.value.push({ role: 'user', content: q });
  question.value = '';
  asking.value = true;

  try {
    const resp = await fetch(`${API_BASE}/v1/chat/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({rag_id: currentRagId.value, question: q})
    });
    
    if (!resp.ok) throw new Error('Network response was not ok');
    
    const data = await resp.json();
    chatHistory.value.push({ role: 'bot', content: data.answer });
  } catch (e) {
    ElMessage.error('回答失败: ' + e.message);
    chatHistory.value.push({ role: 'bot', content: '抱歉，我遇到了一些问题，请稍后再试。' });
  } finally {
    asking.value = false;
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
}
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

/* 自定义 Element Plus 组件样式以适配 Web3 风格 */
:deep(.el-upload-dragger) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 2px dashed rgba(255, 255, 255, 0.2) !important;
  border-radius: 1rem !important;
  transition: all 0.3s ease !important;
}

:deep(.el-upload-dragger:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(168, 85, 247, 0.5) !important;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

:deep(.el-input__inner) {
  color: white !important;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5) !important;
}

:deep(.el-card) {
  background: transparent !important;
  border: none !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-loading-mask) {
  background: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(4px) !important;
}

:deep(.el-message) {
  background: rgba(0, 0, 0, 0.8) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

:deep(.el-alert) {
  background: rgba(16, 185, 129, 0.2) !important;
  border: 1px solid rgba(16, 185, 129, 0.5) !important;
}

:deep(.el-alert__title) {
  color: rgb(110, 231, 183) !important;
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
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(168, 85, 247, 0.5);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(168, 85, 247, 0.7);
}
</style>
