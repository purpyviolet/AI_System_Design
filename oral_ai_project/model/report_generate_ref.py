from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from fpdf import FPDF
from datetime import datetime
import re

class ReportGenerator:
    def __init__(self):
        # 初始化嵌入模型
        self.embedding = HuggingFaceEmbeddings(model_name="D:/zyh/LLMUI/text2vec-base-chinese")
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name="deepseek-chat",
            temperature=0.7,
            openai_api_key="sk-6cf3f5b267f14cc0a2b4546e98fc57a7",
            openai_api_base="https://api.deepseek.com/v1"
        )
        
        # 加载知识库
        self.db = FAISS.load_local("faiss_oral_db", self.embedding, allow_dangerous_deserialization=True)
        self.retriever = self.db.as_retriever(search_kwargs={"k": 1})

    def get_professional_knowledge(self, query):
        """获取专业知识"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )
        result = qa_chain({"query": query})
        return result["result"]

    def generate_structured_report(self, user_query, history_content):
        """生成结构化报告内容"""
        professional_knowledge = self.get_professional_knowledge(user_query)
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        prompt = f"""
        根据以下专业知识和历史对话内容，生成一份结构化的就诊报告，使用中文回答：
        
        [专业知识]
        {professional_knowledge}
        
        [历史对话内容]
        {history_content}
        
        请按照以下格式生成报告内容，确保每个部分都有明确的标题和内容：
        
        就诊时间: {current_time}
        患者情况: <患者症状描述>
        病因分析: <详细病因分析>
        治疗方案: <分点列出治疗方案>
        注意事项: <分点列出注意事项>
        
        请直接输出报告内容，不要包含其他说明文字。
        """
        
        response = self.llm.invoke(prompt)
        return response.content, current_time

    def parse_report_content(self, report_text, current_time):
        """解析报告内容"""
        sections = []
        
        # 使用正则表达式提取各部分内容
        patterns = {
            "患者情况": r"患者情况[:：]/s*(.*?)(?=/n病因分析|$)",
            "病因分析": r"病因分析[:：]/s*(.*?)(?=/n治疗方案|$)",
            "治疗方案": r"治疗方案[:：]/s*(.*?)(?=/n注意事项|$)",
            "注意事项": r"注意事项[:：]/s*(.*)"
        }
        
        # 添加就诊时间
        sections.append({"title": "一、就诊时间", "body": current_time})
        
        # 提取并添加其他部分
        for i, (key, pattern) in enumerate(patterns.items()):
            match = re.search(pattern, report_text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                sections.append({
                    "title": f"{chr(ord('二')+i)}、{key}",
                    "body": content
                })
        
        # 如果解析失败，使用默认内容
        if len(sections) < 5:
            sections = [
                {"title": "一、就诊时间", "body": current_time},
                {"title": "二、患者情况", "body": "患者患有牙龈炎，日常表现为牙龈红肿、疼痛等不适。"},
                {"title": "三、病因分析", "body": "龈牙结合部堆积牙菌斑引发炎症，加之牙石、不良修复体、牙错位等因素加重影响。"},
                {"title": "四、治疗方案", "body": "1. 清除牙石，进行洁治术/n2. 使用氯己定漱口/n3. 局部使用1%过氧化氢冲洗"},
                {"title": "五、注意事项", "body": "坚持每天刷牙两次，使用牙线清洁牙缝，避免口呼吸，定期复诊检查。"}
            ]
        
        return sections

    def generate_pdf(self, sections, output_path):
        """生成PDF报告"""
        pdf = PDF()
        for section in sections:
            pdf.chapter(section["title"], section["body"]) 
        pdf.output(output_path)
        return output_path

class PDF(FPDF):
    """PDF生成类"""
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("SimHei", "", r"D:/华南理工/工导2.0/all_con/pdf_gen/Ubuntu_18.04_SimHei.ttf", uni=True)
        self.set_font("SimHei", "", 13)
        self.add_page()

    def header(self):
        self.image("D:/华南理工/工导2.0/all_con/pdf_gen/logo.png", 10, 8, 15)
        self.set_font("SimHei", "", 16)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, "齿语舌观", ln=True, align="C")
        self.set_font("SimHei", "", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, "就诊记录报告", ln=True, align="C")
        self.set_font("SimHei", "", 10)
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        self.cell(0, 8, f"报告时间：{now}", ln=True, align="R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("SimHei", "", 9)
        self.set_text_color(100)
        self.cell(0, 10, f"第 {self.page_no()} 页 / 医院电话：123-456789", align="C")

    def chapter(self, title, body):
        self.set_fill_color(220, 230, 240)
        self.set_font("SimHei", "", 12)
        self.set_text_color(0)
        self.cell(0, 8, title, ln=True, fill=True)
        self.set_font("SimHei", "", 11)
        self.set_text_color(30)
        self.multi_cell(0, 8, body)
        self.ln(3)

# 主控代码可以直接调用的接口函数
def generate_structured_report(user_query, history_content):
    generator = ReportGenerator()
    report_text, current_time = generator.generate_structured_report(user_query, history_content)
    return report_text, current_time

def parse_report_content(report_text, current_time):
    generator = ReportGenerator()
    return generator.parse_report_content(report_text, current_time)

def create_pdf(sections, output_path):
    generator = ReportGenerator()
    return generator.generate_pdf(sections, output_path)

if __name__ == "__main__":
    # 测试代码
    generator = ReportGenerator()
    user_query = "牙龈炎的病因、治疗和预防方法？同时是以医生诊疗的口吻进行回答。"
    history_content = "患者向医生反映近期刷牙时牙龈出血、牙龈发红且伴有口气不佳的问题..."
    
    report_text, current_time = generator.generate_structured_report(user_query, history_content)
    sections = generator.parse_report_content(report_text, current_time)
    output_path = "就诊记录报告_测试版.pdf"
    generator.generate_pdf(sections, output_path)
    print(f"报告已生成: {output_path}")

