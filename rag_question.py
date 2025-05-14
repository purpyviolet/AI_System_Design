from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# 嵌入模型（保持不变）
embedding = HuggingFaceEmbeddings(model_name="C:/Users/ZOE/Desktop/text2vec-base-chinese")

# 加载向量数据库（确保路径正确）
db = FAISS.load_local(
    "faiss_oral_db", 
    embedding, 
    allow_dangerous_deserialization=True  # 允许反序列化
)

# 构建检索器
retriever = db.as_retriever(search_kwargs={"k": 1})

# 配置第三方代理访问 GPT-4
llm = ChatOpenAI(
    model_name="deepseek-chat",  # 确保代理支持 GPT-4
    temperature=0.7,
    openai_api_key="sk-c317348a89df4b4faa79adaff8d688e2",  # 替换为你的代理 API Key
    openai_api_base="https://api.deepseek.com/v1"  # 替换为代理地址，如 OneAPI
)

# 构建 QA 问答链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,  # 使用配置好的 LLM
    retriever=retriever,
    return_source_documents=True
)

# 示例问答
query = "牙结石是怎么形成的？怎么治疗？"
result = qa_chain({"query": query})

print("💬 回答：", result["result"])
print("📚 参考来源：", [doc.metadata for doc in result["source_documents"]])