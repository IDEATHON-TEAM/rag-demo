# RAG与KnowledgeNFT完整部署和使用指南

## 概述

本指南提供了完整的部署流程，将RAG服务与KnowledgeNFT智能合约连接，实现文档上传→IPFS存储→向量索引哈希计算→NFT铸造的完整流程。

## 前置要求

1. 安装 Node.js 和 npm
2. 安装 MetaMask 浏览器扩展
3. 准备 Sepolia 测试网 ETH（用于支付 gas 费用）
   - 可以从 [Sepolia Faucet](https://sepoliafaucet.com/) 获取测试 ETH
4. Python 3.8+ 环境（用于后端服务）

---

## 第一部分：合约部署

### UtilityToken 合约部署

#### 1. 编译合约

使用 Remix IDE 或 Hardhat 编译 `contract/five_smart_contracts_B.sol` 中的 `UtilityToken` 合约。

##### 使用 Remix IDE（推荐）

1. 访问 [Remix IDE](https://remix.ethereum.org/)
2. 创建新文件，复制 `UtilityToken` 合约代码（包括 `Ownable` 抽象合约）
3. 选择 Solidity 编译器版本 `0.8.17` 或更高
4. 点击 "Compile" 编译合约
5. 编译成功后，在 "Artifacts" 中找到 ABI

##### 使用 Hardhat

```bash
# 安装 Hardhat
npm install --save-dev hardhat

# 初始化项目
npx hardhat init

# 编译合约
npx hardhat compile
```

#### 2. 部署到 Sepolia 测试网

##### 使用 Remix IDE

1. 在 Remix 中切换到 "Deploy & Run Transactions" 标签
2. 环境选择 "Injected Provider - MetaMask"
3. 确保 MetaMask 连接到 Sepolia 测试网
4. 选择 `UtilityToken` 合约
5. 点击 "Deploy"
6. 在 MetaMask 中确认交易
7. 等待交易确认后，复制合约地址

##### 使用 Hardhat

创建部署脚本 `scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const UtilityToken = await hre.ethers.getContractFactory("UtilityToken");
  const utilityToken = await UtilityToken.deploy();

  await utilityToken.waitForDeployment();

  console.log("UtilityToken deployed to:", await utilityToken.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

运行部署：

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

#### 3. 更新前端配置

部署成功后，更新 `frontend/src/config/contractConfig.js`:

```javascript
export const CONTRACT_ADDRESS = '0x你的合约地址' // 替换为实际部署的地址
```

#### 4. 获取合约 ABI

如果使用 Remix：
- 编译后在 "Artifacts" 中找到 `UtilityToken.json`
- 复制其中的 `abi` 字段

如果使用 Hardhat：
- 编译后在 `artifacts/contracts/` 目录下找到 JSON 文件
- 复制其中的 `abi` 字段

**注意**: 当前 `contractConfig.js` 中已包含基本 ABI，如果编译后的 ABI 不同，请更新配置文件。

#### 5. 验证部署

1. 在 [Sepolia Etherscan](https://sepolia.etherscan.io/) 搜索你的合约地址
2. 确认合约已成功部署
3. 在前端应用中连接钱包，应该能看到代币信息

---

### KnowledgeNFT 合约部署

#### 前置要求

1. 已完成 UtilityToken 合约部署
2. 准备 Sepolia 测试网 ETH（用于支付 gas 费用）
3. 准备一些 UtilityToken 代币（用于测试购买功能）

#### 1. 编译合约

使用 Remix IDE 或 Hardhat 编译 `contract/five_smart_contracts_B.sol` 中的 `KnowledgeNFT` 合约。

**注意**: KnowledgeNFT 合约依赖 `UtilityToken` 合约，需要先部署 UtilityToken。

##### 使用 Remix IDE（推荐）

1. 访问 [Remix IDE](https://remix.ethereum.org/)
2. 创建新文件，复制以下合约代码：
   - `Ownable` 抽象合约
   - `UtilityToken` 合约（或使用已部署的地址）
   - `KnowledgeNFT` 合约
3. 选择 Solidity 编译器版本 `0.8.17` 或更高
4. 点击 "Compile" 编译合约

#### 2. 部署到 Sepolia 测试网

##### 使用 Remix IDE

1. 在 Remix 中切换到 "Deploy & Run Transactions" 标签
2. 环境选择 "Injected Provider - MetaMask"
3. 确保 MetaMask 连接到 Sepolia 测试网
4. 选择 `KnowledgeNFT` 合约
5. 在构造函数参数中填入：
   - `_utilityToken`: UtilityToken 合约地址
   - `_platform`: 平台地址（用于接收平台费用）
   - `_dao`: DAO 地址（可选，可以填 0x0000000000000000000000000000000000000000）
6. 点击 "Deploy"
7. 在 MetaMask 中确认交易
8. 等待交易确认后，复制合约地址

##### 使用 Hardhat

创建部署脚本 `scripts/deploy_knowledge_nft.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const utilityTokenAddress = "0x..."; // UtilityToken 合约地址
  const platformAddress = "0x..."; // 平台地址
  const daoAddress = "0x0000000000000000000000000000000000000000"; // DAO地址（可选）

  const KnowledgeNFT = await hre.ethers.getContractFactory("KnowledgeNFT");
  const knowledgeNFT = await KnowledgeNFT.deploy(
    utilityTokenAddress,
    platformAddress,
    daoAddress
  );

  await knowledgeNFT.waitForDeployment();

  console.log("KnowledgeNFT deployed to:", await knowledgeNFT.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

运行部署：

```bash
npx hardhat run scripts/deploy_knowledge_nft.js --network sepolia
```

---

## 第二部分：后端环境配置

### 1. 配置环境变量

部署成功后，更新后端环境变量配置：

1. 复制 `backend/.env.example` 为 `backend/.env`（如果存在）
2. 填写以下配置：

```bash
# IPFS配置
IPFS_API_URL=http://localhost:5001

# 区块链配置
RPC_URL=https://rpc.sepolia.org
CHAIN_ID=11155111
KNOWLEDGE_NFT_CONTRACT_ADDRESS=0x你的KnowledgeNFT合约地址

# 注意：后端不再需要私钥！
# NFT铸造由前端用户自己签名完成，更安全
# 如果之前配置了PRIVATE_KEY，可以删除或注释掉

# 平台地址（用于分账，仅用于信息展示）
PLATFORM_ADDRESS=0x平台地址
DAO_ADDRESS=0xDAO地址（可选）
```

### 2. 启动IPFS节点（可选）

如果使用本地IPFS节点：

```bash
# 安装IPFS
# macOS
brew install ipfs

# Linux
wget https://dist.ipfs.io/go-ipfs/v0.20.0/go-ipfs_v0.20.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.20.0_linux-amd64.tar.gz
cd go-ipfs
sudo ./install.sh

# 初始化并启动
ipfs init
ipfs daemon
```

或者使用远程IPFS服务（如 Pinata、Infura 等）。

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 第三部分：API使用说明

### 1. 上传文档并创建RAG（可选NFT铸造）

**请求**:
```bash
POST /v1/rag/
Content-Type: multipart/form-data

file: <文件>
price: <NFT价格，可选，单位：wei>
mint_nft: true  # 是否铸造NFT
```

**响应**:
```json
{
  "rag_id": "rag_1",
  "message": "RAG 创建成功",
  "mint_data": {
    "ipfs_cid": "Qm...",
    "vector_hash_hex": "0x...",
    "vector_hash_bytes32": "0x...",
    "price": 1000000000000000000,
    "contract_address": "0x...",
    "chain_id": 11155111,
    "function_name": "mintKnowledgeNFT",
    "function_params": [...]
  },
  "ipfs_cid": "Qm..."
}
```

**注意**: 如果启用了NFT铸造（`mint_nft=true`），后端会返回 `mint_data`，包含铸造所需的所有信息。实际铸造由前端完成，用户自己签名交易。

**示例**:
```bash
curl -X POST "http://localhost:8000/v1/rag/?price=1000000000000000000&mint_nft=true" \
  -F "file=@document.pdf"
```

### 2. 查询（带权限验证）

**请求**:
```bash
POST /v1/chat/
Content-Type: application/json

{
  "rag_id": "rag_1",
  "question": "文档的主要内容是什么？",
  "user_address": "0x用户钱包地址"  # 可选，如果提供则进行权限验证
}
```

**响应（有权限）**:
```json
{
  "answer": "文档的主要内容是..."
}
```

**响应（无权限）**:
```json
{
  "detail": {
    "error": "Access denied",
    "message": "You do not have access to this knowledge asset. Please purchase access first.",
    "token_id": 1,
    "price": 1000000000000000000,
    "purchase_required": true
  }
}
```

### 3. 获取NFT信息

**请求**:
```bash
GET /v1/nft/{rag_id}
```

**响应**:
```json
{
  "rag_id": "rag_1",
  "token_id": 1,
  "owner": "0x...",
  "ipfsCID": "Qm...",
  "vectorHash": "0x...",
  "price": 1000000000000000000,
  "isActive": true,
  "createdAt": 1234567890,
  "totalSales": 0,
  "revenue": 0
}
```

### 4. 购买访问权限

**请求**:
```bash
POST /v1/nft/{token_id}/purchase?user_address=0x用户地址
```

**响应**:
```json
{
  "message": "Please complete the purchase transaction on-chain",
  "token_id": 1,
  "price": 1000000000000000000,
  "has_access": false,
  "contract_address": "0x合约地址",
  "purchase_function": "purchaseAccess(uint256 tokenId)"
}
```

**注意**: 实际的支付交易需要在链上完成（前端调用智能合约的 `purchaseAccess` 函数）。

---

## 第四部分：工作流程

### 文档上传流程

1. 用户上传文档到 `/v1/rag/`
2. 后端保存文件并调用RAG构建器
3. RAG构建器：
   - 解析文档并分块
   - 向量化存储到ChromaDB
   - （如果启用）上传原始文件到IPFS → 获得CID
   - 计算向量索引哈希
4. （如果启用NFT铸造）调用KnowledgeNFT合约铸造NFT
5. 存储 `rag_id` 与 `token_id` 的映射关系
6. 返回 `rag_id` 和 `token_id`

### 查询流程

1. 用户发起查询，提供 `rag_id` 和 `user_address`
2. 后端根据 `rag_id` 查找对应的 `token_id`
3. 调用合约的 `hasAccess` 函数检查权限
4. 有权限：执行RAG查询并返回答案
5. 无权限：返回支付信息

---

## 第五部分：测试

### UtilityToken 测试

部署完成后，在前端应用中：

1. 连接 MetaMask 钱包（确保在 Sepolia 网络）
2. 切换到 "代币管理" 标签页
3. 查看代币余额（初始为 0）
4. 如果部署账户是 owner，可以尝试铸造一些代币
5. 测试转账功能

### KnowledgeNFT 测试流程

#### 1. 上传文档并铸造NFT

```bash
POST /v1/rag/?price=1000000000000000000&mint_nft=true
Content-Type: multipart/form-data

file: <文档文件>
```

响应应包含 `token_id` 和 `tx_hash`。

#### 2. 查询NFT信息

```bash
GET /v1/nft/{rag_id}
```

#### 3. 测试权限验证

```bash
POST /v1/chat/
Content-Type: application/json

{
  "rag_id": "rag_1",
  "question": "文档的主要内容是什么？",
  "user_address": "0x用户地址"
}
```

#### 4. 购买访问权限（前端）

在前端调用 KnowledgeNFT 合约的 `purchaseAccess(tokenId)` 函数。

---

## 第六部分：常见问题和故障排除

### MetaMask 相关问题

#### MetaMask 未检测到网络

如果 MetaMask 中没有 Sepolia 网络，可以手动添加：
- 网络名称: Sepolia
- RPC URL: https://rpc.sepolia.org
- Chain ID: 11155111
- 货币符号: ETH
- 区块浏览器: https://sepolia.etherscan.io

#### 交易失败

- 确保账户有足够的 Sepolia ETH 支付 gas
- 检查网络是否正确（Sepolia）
- 查看 MetaMask 中的错误信息

#### 合约地址未更新

确保更新了 `contractConfig.js` 中的 `CONTRACT_ADDRESS`，并重新加载前端应用。

### IPFS 相关问题

#### IPFS连接失败

- 检查IPFS节点是否运行：`ipfs swarm peers`
- 验证 `IPFS_API_URL` 配置是否正确
- 如果使用远程服务，检查API密钥配置
- 检查网络连接

**注意**: 如果IPFS服务不可用，NFT铸造功能将被禁用，但RAG功能仍可正常使用。

### Web3 相关问题

#### Web3连接失败

- 检查RPC端点是否可访问
- 验证 `RPC_URL` 和 `CHAIN_ID` 配置
- 检查合约地址是否正确

**注意**: 
- 后端Web3服务只用于只读操作（查询NFT信息、检查权限），不需要私钥
- NFT铸造由前端完成，用户自己签名交易，更安全
- 如果Web3服务未配置或初始化失败，NFT相关功能将被禁用，但RAG功能仍可正常使用

### NFT 相关问题

#### NFT铸造失败

- 确保钱包有足够的ETH支付gas
- 验证UtilityToken合约地址是否正确
- 检查合约构造函数参数是否正确
- 检查合约是否已部署
- 查看交易回执中的错误信息

#### 权限检查失败

- 确保用户地址格式正确
- 验证token_id是否存在
- 检查合约状态

#### 向量哈希计算失败

- 确保ChromaDB集合存在
- 检查集合中是否有数据
- 查看后端日志中的错误信息

### 其他注意事项

1. **权限验证**: 如果查询时未提供 `user_address`，将跳过权限验证，直接执行查询（仅用于测试）。

2. **Gas费用**: NFT铸造需要支付gas费用，用户在前端签名交易时，确保钱包有足够的ETH。

3. **向量哈希**: 向量哈希基于ChromaDB集合中的所有向量数据计算，确保数据一致性。

4. **前端签名**: NFT铸造由前端完成，用户通过MetaMask签名交易，后端不存储私钥，更安全。

---

## 第七部分：完整部署检查清单

- [ ] UtilityToken 合约已部署
- [ ] KnowledgeNFT 合约已部署
- [ ] 前端配置已更新（contractConfig.js）
- [ ] 后端环境变量已配置
- [ ] IPFS节点已启动（或使用远程服务）
- [ ] 后端依赖已安装
- [ ] 后端服务已启动
- [ ] 测试文档上传成功
- [ ] 测试NFT铸造成功
- [ ] 测试权限验证正常
- [ ] 测试购买功能正常

---

## 第八部分：后续优化建议

1. **数据库持久化**: 使用PostgreSQL存储映射关系，替代内存字典
2. **异步处理**: IPFS上传和合约交易异步化，提升响应速度
3. **错误重试**: 添加IPFS上传失败的重试机制
4. **监控日志**: 记录所有链上交易和权限检查日志
5. **缓存优化**: 缓存NFT元数据，减少链上查询

---

## 下一步

部署完成后，可以：
1. 集成前端，实现完整的用户界面
2. 测试端到端流程：上传→铸造→查询→购买→查询
3. 部署其他合约（GovernanceToken, ReputationManager, TaskManager 等）
4. 优化性能和错误处理
5. 铸造一些测试代币
6. 测试转账功能
7. 测试授权功能
