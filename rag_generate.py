import json
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# 加载 JSON 文件
with open("tooth.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 将每条病种内容转为 LangChain Document
docs = []
for disease, content in data.items():
    for section, text in content.items():
        doc = Document(
            page_content=f"{disease} - {section}：{text}",
            metadata={"disease": disease, "section": section}
        )
        docs.append(doc)

# 使用中文嵌入模型
embedding = HuggingFaceEmbeddings(model_name="C:/Users/ZOE/Desktop/text2vec-base-chinese")

# 构建向量数据库
vectorstore = FAISS.from_documents(docs, embedding)

# 保存数据库
vectorstore.save_local("faiss_oral_db")
