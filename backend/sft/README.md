# SFT 微调流水线（保险问答 · LlamaFactory 版）

对 **DeepSeek-R1-Distill-Qwen-7B** 做 LoRA 监督微调，训练目标不是让模型背下所有保险知识，而是学会四件事：

1. 理解中文保险问题（InsQABench 问答样本）
2. 按保险条款风格作答（条款片段 grounded 样本）
3. 条款不足以回答时明说、不乱编（拒答负样本）
4. 配合 RAG 检索结果生成答案（样本格式 = 问题 + 检索到的条款片段 → 依据片段的回答，与线上推理格式一致）

微调后量化（约 14GB → 4.4GB），通过 Ollama 接回主服务本地私有化部署，主链路代码零改动。

## 流程总览

```
InsQABench (~10万条保险QA) ──┐
                             ├─ build_dataset.py ──> data/insurance_sft.json (alpaca 格式)
自整理保险条款片段 (clauses/) ─┘        │                A. 问答样本 + B. 条款RAG样本 + C. 拒答负样本
                                      ▼
                    llamafactory-cli train train_lora.yaml     LoRA SFT (r=16, 单卡24G)
                                      │
                                      ▼
                    llamafactory-cli export merge_lora.yaml    合并 LoRA 权重 -> output/merged
                                      │
                                      ▼
                    llama.cpp 转 GGUF + q4_k_m 量化            ~14GB -> ~4.4GB
                                      │
                                      ▼
                    ollama create deepseek-r1-7b-ins-sft       设 OLLAMA_MODEL 环境变量生效
```

## 步骤

```bash
cd backend/sft
pip install -r requirements-sft.txt

# 1. 构造数据集（InsQABench + 条款目录，至少提供一个）
#    条款 RAG 样本的问答对由本机 Ollama 合成，需先拉好造数模型（默认 qwen2.5:7b）
python build_dataset.py \
    --insqa /path/to/InsQABench.jsonl \
    --clauses ./clauses \
    --out data/insurance_sft.json
# InsQABench 字段名不同时用 --q-field/--a-field 指定；全量 10 万条会稀释条款样本，
# 可用 --max-insqa 30000 采样，让三类样本比例大致均衡

# 2. LoRA 微调（GPU 机器）
llamafactory-cli train train_lora.yaml

# 3. 合并 LoRA 权重
llamafactory-cli export merge_lora.yaml

# 4. 转 GGUF 并量化（需要 clone llama.cpp）
python /path/to/llama.cpp/convert_hf_to_gguf.py output/merged --outfile output/merged-f16.gguf
/path/to/llama.cpp/llama-quantize output/merged-f16.gguf output/deepseek-r1-7b-ins-q4_k_m.gguf q4_k_m

# 5. 注册到 Ollama
ollama create deepseek-r1-7b-ins-sft -f Modelfile

# 6. 主服务切换到微调模型（docker-compose 已透传该变量）
OLLAMA_MODEL=deepseek-r1-7b-ins-sft docker compose up -d backend
```

## 与检索链路的关系

rerank 与 SFT 是互补的两层，互不耦合：

```
用户问题 -> bge-small-zh-v1.5 向量粗召回 top10
         -> bge-reranker-base 交叉编码器精排 top3      <- rerank 管「喂给模型的条款准不准」
         -> SFT 后的 deepseek-r1-7b-ins-sft 生成回答   <- SFT 管「模型拿到条款后答得像不像样」
```

reranker 作用在检索侧，与生成模型无关，换 SFT 模型不需要动 `rag_builder.py` 的 rerank 配置；
训练数据 B 类样本的格式（问题 + 条款片段 → 回答）就是模拟 rerank 之后交给模型的输入。

## 设计说明

- **LoRA 而非全参**：资源有限 + 私有化部署目标，全参微调需多卡且小数据易过拟合；LoRA 只训低秩适配矩阵（~0.5% 参数），冻结原始权重，适合 hackathon/prototype。
- **拒答样本的构造方式**：取真实问题 + 错配另一份文档的无关条款，输出为「无法确认，请核对保单」。占 B 类样本约 12%（`--refusal-ratio` 可调）。不造这批样本，"不乱编"这个目标不会自动实现。
- **R1 思维链的取舍**：训练数据不带 `<think>` 段，微调后模型基本不再输出思维链，对齐成直接作答——保险问答 + RAG 场景不需要长推理，还省推理 token。若要保留思维链，需用 R1 生成带 `<think>` 的训练数据再喂回去。
- **训练/推理 prompt 一致**：`build_dataset.py` 的 SYSTEM_PROMPT 与 `Modelfile` 的 SYSTEM 相同，B 类样本的 input 前缀与线上 RAG 拼 prompt 的格式对应，避免训练态/推理态分布不一致。
