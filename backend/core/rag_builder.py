import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

class RagBuilder:
    def __init__(self):
        # 获取 Ollama Host，默认为 localhost
        ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # 配置 LLM (连接 Ollama)
        self.llm = Ollama(
            model="qwen2.5:7b", 
            base_url=ollama_base_url,
            request_timeout=120.0 # 增加超时时间以防首次加载慢
        )
        Settings.llm = self.llm

        # 配置嵌入模型
        # 注意：首次运行会自动下载模型，需要确保网络畅通或已预下载
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-zh-v1.5"
        )

        # 配置文本分块器
        Settings.text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

        # 初始化 Chroma 客户端
        # 使用容器内的绝对路径，确保与 docker-compose 的挂载点一致
        self.chroma_client = chromadb.PersistentClient(path="/app/chroma_db")

    def build_from_file(self, file_path: str):
        # 1. 读取文档（LlamaIndex 支持多种格式）
        # SimpleDirectoryReader 默认支持 .pdf, .docx, .pptx, .txt 等
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

        # 2. 创建向量存储集合
        # 使用文件路径的 hash 作为 collection name，确保唯一性
        collection_name = f"rag_{abs(hash(file_path))}"
        # 确保 collection name 符合 chroma 规范（通常要求 alphanumeric, underscores, hyphens）
        # 这里简单处理一下
        
        chroma_collection = self.chroma_client.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # 3. 构建索引
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            show_progress=True
        )

        # 4. 创建查询引擎
        query_engine = index.as_query_engine(similarity_top_k=3)
        
        return query_engine

