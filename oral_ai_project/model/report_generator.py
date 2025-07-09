import json
import os
import re
from datetime import datetime
from fpdf import FPDF

class ReportGenerator:
    def __init__(self):
        # 加载oral.json数据
        with open('static/oral.json', 'r', encoding='utf-8') as f:
            self.oral_data = json.load(f)
        
        # 舌头标签映射
        self.tongue_label_mapping = {
            '白苔': '白苔',
            '薄苔': '薄苔',
            '淡白舌': '淡白舌',
            '淡红舌': '淡红舌',
            '非腻苔': '非腻苔',
            '黑苔': '黑苔',
            '红舌': '红舌',
            '厚苔': '厚苔',
            '舌苔黄': '舌苔黄',
            '绛舌': '绛舌'
        }

        # 牙齿标签映射
        self.tooth_label_mapping = {
            'Hypodontia': '少牙症',
            'Gingivitis': '牙龈炎',
            'Mouth Ulcer': '口腔溃疡',
            'Calculus': '牙结石',
            'Caries': '龋齿',
            'Tooth Discoloration': '牙齿变色'
        }

        # 特征映射表
        self.feature_map = {
            "舌色": {
                0: "淡白舌",
                1: "淡红舌",
                2: "红舌",
                3: "绛舌",
                4: "青紫舌"
            },
            "舌苔颜色": {
                0: "白苔",
                1: "黄苔",
                2: "灰黑苔"
            },
            "厚薄": {
                0: "薄",
                1: "厚"
            },
            "腐腻": {
                0: "腻",
                1: "腐"
            }
        }

    def convert_numeric_labels(self, tongue_result):
        """将数字标签转换为文字描述"""
        result = {}
        
        # 转换舌色
        if 'tongue_color' in tongue_result:
            color_num = tongue_result['tongue_color']
            result['color'] = self.feature_map['舌色'].get(color_num, '未检测')
        
        # 转换舌苔颜色
        if 'coating_color' in tongue_result:
            coating_num = tongue_result['coating_color']
            result['coating_color'] = self.feature_map['舌苔颜色'].get(coating_num, '未检测')
        
        # 转换厚薄
        if 'thickness' in tongue_result:
            thickness_num = tongue_result['thickness']
            result['thickness'] = self.feature_map['厚薄'].get(thickness_num, '未检测')
        
        # 转换腐腻
        if 'rot_greasy' in tongue_result:
            rot_greasy_num = tongue_result['rot_greasy']
            result['rot_greasy'] = self.feature_map['腐腻'].get(rot_greasy_num, '未检测')
        
        # 设置主要标签（使用四个维度的组合）
        label_parts = []
        if 'color' in result:
            label_parts.append(result['color'])
        if 'coating_color' in result:
            label_parts.append(result['coating_color'])
        if 'thickness' in result:
            label_parts.append(result['thickness'])
        if 'rot_greasy' in result:
            label_parts.append(result['rot_greasy'])
        
        if label_parts:
            result['label'] = '、'.join(label_parts)
        
        return result

    def convert_tooth_label(self, tooth_result):
        """转换牙齿标签"""
        if 'label' not in tooth_result:
            return None
            
        # 提取标签和置信度
        label_text = tooth_result['label']
        confidence = tooth_result.get('confidence', '100%')  # 如果没有confidence，默认为100%
        
        # 检查标签是否在映射表中
        if label_text in self.tooth_label_mapping:
            return {
                'label': self.tooth_label_mapping[label_text],
                'confidence': confidence
            }
        
        # 如果标签不在映射表中，尝试使用原始标签
        return {
            'label': label_text,
            'confidence': confidence
        }

    def get_tongue_info(self, label):
        """根据舌头标签获取相关信息"""
        if label in self.tongue_label_mapping:
            mapped_label = self.tongue_label_mapping[label]
            if mapped_label in self.oral_data:
                return self.oral_data[mapped_label]
        return None

    def get_tooth_info(self, label):
        """根据牙齿标签获取相关信息"""
        # 检查标签是否在映射表中
        if label in self.tooth_label_mapping:
            mapped_label = self.tooth_label_mapping[label]
        else:
            # 尝试反向查找
            for eng_label, chn_label in self.tooth_label_mapping.items():
                if chn_label == label:
                    mapped_label = label
                    break
            else:
                return None
        
        # 获取信息
        if mapped_label in self.oral_data:
            return self.oral_data[mapped_label]
        return None

    def parse_report_content(self, report_text, current_time):
        """解析报告内容"""
        sections = []
        
        # 使用正则表达式提取各部分内容
        patterns = {
            "患者情况": r"患者情况[:：]\s*(.*?)(?=\n病因分析|$)",
            "病因分析": r"病因分析[:：]\s*(.*?)(?=\n治疗方案|$)",
            "治疗方案": r"治疗方案[:：]\s*(.*?)(?=\n注意事项|$)",
            "注意事项": r"注意事项[:：]\s*(.*)"
        }
        
        # 中文数字映射
        chinese_numbers = ['一', '二', '三', '四', '五']
        
        # 添加就诊时间
        sections.append({"title": f"{chinese_numbers[0]}、就诊时间", "body": current_time})
        
        # 提取并添加其他部分
        for i, (key, pattern) in enumerate(patterns.items()):
            match = re.search(pattern, report_text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                sections.append({
                    "title": f"{chinese_numbers[i+1]}、{key}",
                    "body": content
                })
        
        # 如果解析失败，使用默认内容
        if len(sections) < 5:
            sections = [
                {"title": f"{chinese_numbers[0]}、就诊时间", "body": current_time},
                {"title": f"{chinese_numbers[1]}、患者情况", "body": "患者患有牙龈炎，日常表现为牙龈红肿、疼痛等不适。"},
                {"title": f"{chinese_numbers[2]}、病因分析", "body": "龈牙结合部堆积牙菌斑引发炎症，加之牙石、不良修复体、牙错位等因素加重影响。"},
                {"title": f"{chinese_numbers[3]}、治疗方案", "body": "1. 清除牙石，进行洁治术\n2. 使用氯己定漱口\n3. 局部使用1%过氧化氢冲洗"},
                {"title": f"{chinese_numbers[4]}、注意事项", "body": "坚持每天刷牙两次，使用牙线清洁牙缝，避免口呼吸，定期复诊检查。"}
            ]
        
        return sections

    def generate_tongue_report(self, tongue_result, chat_history):
        print("舌头报告生成中...")
        """生成舌头检查报告"""
        # 转换数字标签为文字描述
        converted_result = self.convert_numeric_labels(tongue_result)
        
        # 使用舌色获取舌头信息
        tongue_info = self.get_tongue_info(converted_result.get('color', ''))
        
        if not tongue_info:
            print(f"未找到舌头信息: {converted_result['label']}")
            return None

        # 构建提示词
        prompt = f"""
        你是一位专业的中医医生，请根据以下检查结果和对话记录，生成一份详细的舌诊报告。
        请使用中文回答，并严格按照以下格式输出：

        就诊时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
        患者情况: 舌象：{converted_result['label']}，舌色：{converted_result.get('color', '未检测')}，苔色：{converted_result.get('coating_color', '未检测')}，厚薄：{converted_result.get('thickness', '未检测')}，腐腻：{converted_result.get('rot_greasy', '未检测')}
        病因分析: {tongue_info.get('病因', '暂无相关信息')}
        治疗方案: {tongue_info.get('治疗', '暂无相关信息')}
        注意事项: {tongue_info.get('预防', '暂无相关信息')}

        [对话记录]
        {self._format_chat_history(chat_history)}
        不要有任何类似这样的内容：（请补充以下信息以便更精准判断：1.近期是否有乏力、怕冷等不适？2.日常饮食是否有偏嗜或食欲减退？）
        """

        # 调用大模型生成报告内容
        from model.llm_interface_api import chat_with_llm
        report_content = chat_with_llm(prompt)
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')

        # 解析报告内容
        sections = self.parse_report_content(report_content, current_time)

        # 构建报告结构
        report = {
            'title': '舌诊检查报告',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': sections
        }
        
        return report

    def generate_tooth_report(self, tooth_result, chat_history):
        """生成牙齿检查报告"""
        # 转换标签
        converted_result = self.convert_tooth_label(tooth_result)
        
        if not converted_result:
            return None

        # 获取牙齿相关信息
        tooth_info = self.get_tooth_info(converted_result['label'])
        
        if not tooth_info:
            return None

        # 构建提示词
        prompt = f"""
        你是一位专业的牙科医生，请根据以下检查结果和对话记录，生成一份详细的牙科检查报告。
        请使用中文回答，并严格按照以下格式输出：

        就诊时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
        患者情况: 诊断：{converted_result['label']}，置信度：{converted_result['confidence']}
        病因分析: {tooth_info.get('病因', '暂无相关信息')}
        治疗方案: {tooth_info.get('治疗', '暂无相关信息')}
        注意事项: {tooth_info.get('预防', '暂无相关信息')}

        [对话记录]
        {self._format_chat_history(chat_history)}
        """

        # 调用大模型生成报告内容
        from model.llm_interface_api import chat_with_llm
        report_content = chat_with_llm(prompt)
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')

        # 解析报告内容
        sections = self.parse_report_content(report_content, current_time)

        # 构建报告结构
        report = {
            'title': '牙科检查报告',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': sections
        }
        
        return report

    def _format_chat_history(self, chat_history):
        """格式化对话历史"""
        if not chat_history:
            return "暂无对话记录"
            
        dialogue_content = []
        for msg in chat_history:
            if isinstance(msg, dict):
                if msg.get('type') == 'image_analysis':
                    continue  # 跳过图片分析记录
                if 'content' in msg:
                    role = '医生' if msg.get('role') == 'bot' else '患者'
                    dialogue_content.append(f"{role}: {msg['content']}")
        
        return '\n'.join(dialogue_content) if dialogue_content else "暂无对话记录"

    def create_pdf(self, report, output_path):
        """生成PDF报告"""
        class PDF(FPDF):
            def __init__(self):
                super().__init__()
                self.set_auto_page_break(auto=True, margin=15)
                self.add_font("SimHei", "", "static/Ubuntu_18.04_SimHei.ttf", uni=True)
                self.set_font("SimHei", "", 13)
                self.add_page()

            def header(self):
                self.image("static/logo.png", 10, 8, 15)
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

        # 创建PDF实例
        pdf = PDF()
        
        # 添加各个部分
        for section in report['sections']:
            pdf.chapter(section['title'], section['body'])
        
        # 保存PDF
        pdf.output(output_path)

# if __name__ == '__main__':
#     # 测试数据
#     test_tongue_result = {
#         'tongue_color': 3,  # 绛舌
#         'coating_color': 2,  # 灰黑苔
#         'thickness': 1,  # 厚
#         'rot_greasy': 1  # 腐
#     }
    
#     test_tooth_result = {
#         'label': 'Caries (置信度: 0.91)'
#     }
    
#     test_chat_history = [
#         {'role': 'user', 'content': '我的牙齿有点疼'},
#         {'role': 'bot', 'content': '根据检查结果，您可能患有龋齿。建议及时就医治疗。'}
#     ]
    
#     # 创建报告生成器实例
#     generator = ReportGenerator()
    
#     # 生成报告
#     report = generator.generate_tooth_report(test_tooth_result, test_chat_history)
    
#     if report:
#         # 创建输出目录
#         output_dir = 'test_output'
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
        
#         # 生成PDF
#         output_path = os.path.join(output_dir, 'test_report.pdf')
#         generator.create_pdf(report, output_path)
#         print(f"报告已生成：{output_path}")
#     else:
#         print("报告生成失败") 