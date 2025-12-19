<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <h1>RAG 知识变现平台 (MVP)</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20" justify="center">
          <el-col :span="16">
            <!-- 步骤 1: 文件上传 -->
            <el-card class="box-card" v-if="!currentRagId">
              <template #header>
                <div class="card-header">
                  <span>第一步：上传您的知识文件</span>
                </div>
              </template>
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
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    将文件拖到此处，或 <em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、Word、PPT、TXT 文件，生成您的专属知识库
                    </div>
                  </template>
                </el-upload>
                <div v-if="loading" class="loading-text">正在为您构建知识库，请稍候...</div>
              </div>
            </el-card>

            <!-- 步骤 2: 问答测试 -->
            <el-card class="box-card" v-else>
              <template #header>
                <div class="card-header">
                  <span>第二步：测试您的 RAG 智能体</span>
                  <el-button type="primary" link @click="reset">重新上传</el-button>
                </div>
              </template>
              
              <div class="chat-container">
                <div v-if="chatHistory.length === 0" class="empty-chat">
                  试着问一些关于文档的问题吧！
                </div>
                <div v-for="(msg, index) in chatHistory" :key="index" class="message-item">
                  <div :class="['message-bubble', msg.role === 'user' ? 'user-msg' : 'bot-msg']">
                    <strong>{{ msg.role === 'user' ? '你' : 'AI' }}:</strong> {{ msg.content }}
                  </div>
                </div>
              </div>

              <div class="input-area">
                <el-input
                  v-model="question"
                  placeholder="请输入您的问题..."
                  @keyup.enter="ask"
                  :disabled="asking"
                >
                  <template #append>
                    <el-button @click="ask" :loading="asking">发送</el-button>
                  </template>
                </el-input>
              </div>

              <el-divider />

              <!-- 步骤 3: 定价预览 -->
              <div class="pricing-section">
                <h3>觉得满意吗？立即生成产品</h3>
                <el-button type="success" size="large" @click="showPricing" v-if="!priceOptions">
                  上架并设定价格
                </el-button>
                
                <div v-if="priceOptions" class="pricing-options">
                  <el-row :gutter="20">
                    <el-col :span="8" v-for="opt in priceOptions" :key="opt.type">
                      <el-card shadow="hover" class="price-card">
                        <h4>{{ opt.type }}</h4>
                        <div class="price-tag">{{ opt.price }}</div>
                        <el-button type="primary" plain size="small">选择此方案</el-button>
                      </el-card>
                    </el-col>
                  </el-row>
                  <div class="success-hint">
                    <el-alert
                      title="恭喜！您的知识库产品已准备就绪 (模拟)"
                      type="success"
                      :closable="false"
                      show-icon
                    />
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
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
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background-color: #f5f7fa;
}
.header {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.header h1 {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}
.el-main {
  padding-top: 40px;
}
.box-card {
  min-height: 500px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.upload-container {
  text-align: center;
  padding: 40px 0;
}
.loading-text {
  margin-top: 20px;
  color: #909399;
}
.chat-container {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #fafafa;
}
.message-item {
  margin-bottom: 15px;
}
.message-bubble {
  padding: 10px 15px;
  border-radius: 8px;
  display: inline-block;
  max-width: 80%;
  line-height: 1.5;
}
.user-msg {
  background-color: #ecf5ff;
  color: #409EFF;
  text-align: right;
  float: right;
  clear: both;
}
.bot-msg {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
  float: left;
  clear: both;
}
.input-area {
  margin-bottom: 30px;
}
.pricing-section {
  text-align: center;
  margin-top: 30px;
}
.pricing-options {
  margin-top: 20px;
}
.price-card {
  margin-bottom: 10px;
  cursor: pointer;
}
.price-tag {
  font-size: 20px;
  color: #F56C6C;
  margin: 10px 0;
  font-weight: bold;
}
.success-hint {
  margin-top: 20px;
}
</style>

