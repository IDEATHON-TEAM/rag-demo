"""
SFT 训练数据集构造（alpaca 格式，供 LlamaFactory 使用）

三类样本混合，对应四个训练目标：
  A. InsQABench 保险问答      -> 学会理解中文保险问题、保险条款风格作答
  B. 条款片段 RAG 样本         -> 学会「答案从检索到的条款里来」，配合 RAG 生成
  C. 拒答负样本               -> 学会条款不足以回答时明说，不乱编

产出:
  data/insurance_sft.json  (alpaca: instruction / input / output / system)

用法:
  python build_dataset.py \
      --insqa path/to/InsQABench.jsonl \
      --clauses ./clauses \
      --out data/insurance_sft.json
"""
import argparse
import json
import os
import random
import re

import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
GEN_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # 造数用的模型，与被微调的模型无关

# 与部署时 Modelfile 的 SYSTEM 保持一致，训练/推理同一个 system prompt
SYSTEM_PROMPT = (
    "你是一名专业的保险问答助手。请用准确、严谨的保险条款风格回答用户问题；"
    "如果提供了保险条款内容，回答必须严格依据条款原文；"
    "如果条款内容不足以回答问题，请明确说明无法确认，建议用户核对保单原文，不要编造。"
)

RAG_INPUT_PREFIX = "以下是检索到的保险条款内容：\n"

# 拒答话术模板（多个变体，避免模型学成一句死话）
REFUSAL_TEMPLATES = [
    "根据当前提供的条款内容，无法确认这个问题的答案。建议您核对保单原文中的相关条款，或咨询您的保险公司客服，以免产生理解偏差。",
    "现有条款片段中没有涉及该问题的规定，我不能凭空推断。请以您的保单原文为准，必要时联系保险公司确认。",
    "抱歉，所提供的条款内容与您的问题不匹配，无法据此给出可靠回答。建议查阅保单中对应章节或向承保公司核实。",
]

GEN_PROMPT = """你是保险领域的数据标注专家。请根据下面这段保险条款内容，生成 {n} 组高质量的中文问答对，用于训练保险问答模型。

要求：
1. 问题必须是投保人/被保险人读到这段条款时可能真实提出的问题
2. 答案必须严格依据条款原文，用严谨的保险条款风格表述，不引入条款之外的信息
3. 只输出 JSON 数组，格式: [{{"question": "...", "answer": "..."}}]，不要输出其他内容

条款内容：
{chunk}
"""


# ---------- A. InsQABench 预处理 ----------

def load_insqa(path: str, q_field: str, a_field: str, max_n: int):
    """兼容 json 数组 / jsonl 两种存储，字段名可配置"""
    records = []
    with open(path, encoding="utf-8") as f:
        head = f.read(1)
        f.seek(0)
        if head == "[":
            records = json.load(f)
        else:
            records = [json.loads(line) for line in f if line.strip()]

    samples = []
    for r in records:
        q, a = r.get(q_field), r.get(a_field)
        if not q or not a:
            continue
        samples.append({
            "instruction": str(q).strip(),
            "input": "",
            "output": str(a).strip(),
            "system": SYSTEM_PROMPT,
        })
    if max_n and len(samples) > max_n:
        random.shuffle(samples)
        samples = samples[:max_n]
    return samples


# ---------- B. 条款片段 RAG 样本 ----------

def read_document(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        import fitz  # pymupdf
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    if ext in (".txt", ".md"):
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def split_chunks(text: str, chunk_size: int = 800, overlap: int = 100):
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if len(chunk) > 200:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def gen_qa_pairs(chunk: str, n: int):
    resp = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": GEN_MODEL,
            "messages": [{"role": "user", "content": GEN_PROMPT.format(n=n, chunk=chunk)}],
            "stream": False,
            "options": {"temperature": 0.7},
        },
        timeout=300,
    )
    resp.raise_for_status()
    content = resp.json()["message"]["content"]
    # R1/带思维链的模型会输出 <think>，先剥掉，再取 JSON 数组
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.S)
    match = re.search(r"\[.*\]", content, re.S)
    if not match:
        return []
    try:
        pairs = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [p for p in pairs if isinstance(p, dict) and p.get("question") and p.get("answer")]


def build_clause_samples(clauses_dir: str, pairs_per_chunk: int):
    """RAG 样本: instruction=问题, input=条款片段, output=依据条款的回答
    同时返回 (question, chunk_id) 供拒答负样本做错配"""
    samples, chunk_pool = [], []
    for name in sorted(os.listdir(clauses_dir)):
        path = os.path.join(clauses_dir, name)
        if not os.path.isfile(path):
            continue
        text = read_document(path)
        if not text:
            print(f"[skip] 不支持的格式或空文档: {name}")
            continue
        chunks = split_chunks(text)
        print(f"[条款] {name}: {len(chunks)} chunks")
        for chunk in chunks:
            chunk_pool.append((name, chunk))
            for pair in gen_qa_pairs(chunk, pairs_per_chunk):
                samples.append({
                    "instruction": pair["question"],
                    "input": RAG_INPUT_PREFIX + chunk,
                    "output": pair["answer"],
                    "system": SYSTEM_PROMPT,
                    "_src": name,  # 内部字段，构造完拒答样本后删除
                })
        print(f"  累计 RAG 样本 {len(samples)} 条")
    return samples, chunk_pool


# ---------- C. 拒答负样本 ----------

def build_refusal_samples(clause_samples, chunk_pool, ratio: float):
    """错配构造: 取一个真实问题，配上另一份文档的无关条款片段，输出=拒答。
    没有这批样本，模型在检索质量差时照样一本正经地编。"""
    n_refusal = int(len(clause_samples) * ratio)
    samples = []
    for _ in range(n_refusal):
        base = random.choice(clause_samples)
        # 尽量选不同文档的片段，保证「确实答不了」
        others = [c for c in chunk_pool if c[0] != base["_src"]]
        pool = others if others else chunk_pool
        _, wrong_chunk = random.choice(pool)
        samples.append({
            "instruction": base["instruction"],
            "input": RAG_INPUT_PREFIX + wrong_chunk,
            "output": random.choice(REFUSAL_TEMPLATES),
            "system": SYSTEM_PROMPT,
        })
    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--insqa", help="InsQABench 数据文件 (json/jsonl)")
    parser.add_argument("--q-field", default="question", help="InsQABench 问题字段名")
    parser.add_argument("--a-field", default="answer", help="InsQABench 答案字段名")
    parser.add_argument("--max-insqa", type=int, default=0, help="InsQABench 采样上限，0=全量")
    parser.add_argument("--clauses", help="保险条款文档目录 (pdf/txt/md)")
    parser.add_argument("--pairs-per-chunk", type=int, default=2)
    parser.add_argument("--refusal-ratio", type=float, default=0.12,
                        help="拒答样本数 = RAG 样本数 x 该比例")
    parser.add_argument("--out", default="data/insurance_sft.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    dataset = []

    if args.insqa:
        insqa = load_insqa(args.insqa, args.q_field, args.a_field, args.max_insqa)
        print(f"[A] InsQABench 问答样本: {len(insqa)} 条")
        dataset += insqa

    if args.clauses:
        clause_samples, chunk_pool = build_clause_samples(args.clauses, args.pairs_per_chunk)
        refusals = build_refusal_samples(clause_samples, chunk_pool, args.refusal_ratio)
        for s in clause_samples:
            s.pop("_src", None)
        print(f"[B] 条款 RAG 样本: {len(clause_samples)} 条")
        print(f"[C] 拒答负样本: {len(refusals)} 条")
        dataset += clause_samples + refusals

    if not dataset:
        raise SystemExit("没有产出任何样本：--insqa 和 --clauses 至少提供一个")

    random.shuffle(dataset)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"完成: 共 {len(dataset)} 条 -> {args.out}")
    print("下一步: llamafactory-cli train train_lora.yaml")


if __name__ == "__main__":
    main()
