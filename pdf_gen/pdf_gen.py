from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("SimHei", "", r"pdf_gen/Ubuntu_18.04_SimHei.ttf", uni=True)
        self.set_font("SimHei", "", 13)
        self.add_page()

    def header(self):
        # Logo + 主标题
        self.image("pdf_gen/logo.png", 10, 8, 15)
        self.set_font("SimHei", "", 16)
        self.set_text_color(0, 70, 140)
        self.cell(0, 10, "齿语舌观", ln=True, align="C")

        self.set_font("SimHei", "", 14)
        self.set_text_color(50, 50, 50)
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

    def draw_border(self):
        # 页边框
        self.set_draw_color(180, 180, 180)
        self.rect(5, 5, self.w - 10, self.h - 10)

    def chapter(self, title, body):
        # 小节标题
        self.set_fill_color(235, 245, 255)  # 浅蓝背景
        self.set_text_color(0)
        self.set_font("SimHei", "", 12)
        self.cell(0, 10, title, ln=True, fill=True)

        # 正文内容
        self.set_text_color(50, 50, 50)
        self.set_font("SimHei", "", 11)
        self.multi_cell(0, 8, self.format_paragraph(body))
        self.ln(3)

    def format_paragraph(self, text):
        # 自动加圆点或编号美化
        lines = text.strip().split('\n')
        formatted = []
        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.")):
                formatted.append(f"● {line.strip()}")
            elif line.strip().startswith("-"):
                formatted.append(f"● {line.strip()[1:].strip()}")
            else:
                formatted.append(f"   {line.strip()}")
        return "\n".join(formatted)

# 获取当前时间并格式化为中文
now = datetime.now()
# am_pm = "上午" if now.hour < 12 else "下午"
hour = now.hour
formatted_time = f"{now.year}年{now.month}月{now.day}日 {hour}:{now.minute:02d}"

# 示例内容
sections = [
    {"title": "一、就诊时间", "body": formatted_time},
    {"title": "二、患者情况", "body": "患者患有牙龈炎，日常表现为牙龈红肿、疼痛等不适。"},
    {"title": "三、病因分析", "body": "龈牙结合部堆积牙菌斑引发炎症，加之牙石、不良修复体、牙错位等因素加重影响。"},
    {"title": "四、治疗方案", "body": "1. 清除牙石，进行洁治术\n2. 使用氯己定漱口\n3. 局部使用1%过氧化氢冲洗"},
    {"title": "五、注意事项", "body": "- 坚持每天刷牙两次\n- 使用牙线清洁牙缝\n- 避免口呼吸\n- 定期复诊检查"}
]

# 生成 PDF
pdf = PDF()
pdf.draw_border()  # 外框
for section in sections:
    pdf.chapter(section["title"], section["body"])
pdf.output("就诊记录报告_增强版.pdf")
print("✅ PDF 已生成，包含外框与美化设计")
