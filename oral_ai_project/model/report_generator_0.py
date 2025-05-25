import json
import os
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

    def generate_tongue_report(self, tongue_result, chat_history):
        """生成舌头检查报告"""
        # 转换数字标签为文字描述
        converted_result = self.convert_numeric_labels(tongue_result)
        
        # 使用舌色获取舌头信息
        tongue_info = self.get_tongue_info(converted_result.get('color', ''))
        
        if not tongue_info:
            print(f"未找到舌头信息: {converted_result['label']}")
            return None

        # 构建报告内容
        report = {
            'title': '舌诊检查报告',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': [
                {
                    'title': '检查结果',
                    'content': f"舌象：{converted_result['label']}\n"
                             f"舌色：{converted_result.get('color', '未检测')}\n"
                             f"苔色：{converted_result.get('coating_color', '未检测')}\n"
                             f"厚薄：{converted_result.get('thickness', '未检测')}\n"
                             f"腐腻：{converted_result.get('rot_greasy', '未检测')}"
                },
                {
                    'title': '病因分析',
                    'content': tongue_info.get('病因', '暂无相关信息')
                },
                {
                    'title': '症状表现',
                    'content': tongue_info.get('症状', {}).get('典型表现', '暂无相关信息')
                },
                {
                    'title': '治疗方案',
                    'content': f"中医治疗：{tongue_info.get('治疗', {}).get('中医治疗', '暂无相关信息')}\n"
                             f"西医治疗：{tongue_info.get('治疗', {}).get('西医治疗', '暂无相关信息')}"
                },
                {
                    'title': '预防建议',
                    'content': f"生活方式：{tongue_info.get('预防', {}).get('生活方式', '暂无相关信息')}\n"
                             f"饮食调理：{tongue_info.get('预防', {}).get('饮食调理', '暂无相关信息')}"
                }
            ]
        }

        # 添加对话记录（如果有）
        if chat_history:
            dialogue_content = []
            for msg in chat_history:
                if isinstance(msg, dict):
                    if msg.get('type') == 'image_analysis':
                        continue  # 跳过图片分析记录
                    if 'content' in msg:
                        role = '医生' if msg.get('role') == 'bot' else '患者'
                        dialogue_content.append(f"{role}: {msg['content']}")
            
            if dialogue_content:
                report['sections'].append({
                    'title': '对话记录',
                    'content': '\n'.join(dialogue_content)
                })
        
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

        # 构建报告内容
        report = {
            'title': '牙科检查报告',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sections': [
                {
                    'title': '检查结果',
                    'content': f"诊断：{converted_result['label']}\n"
                             f"置信度：{converted_result['confidence']}"
                },
                {
                    'title': '病因分析',
                    'content': tooth_info.get('病因', '暂无相关信息')
                },
                {
                    'title': '症状表现',
                    'content': tooth_info.get('症状', '暂无相关信息')
                },
                {
                    'title': '治疗方案',
                    'content': tooth_info.get('治疗', '暂无相关信息')
                },
                {
                    'title': '预防建议',
                    'content': tooth_info.get('预防', '暂无相关信息')
                }
            ]
        }

        # 添加对话记录（如果有）
        if chat_history:
            dialogue_content = []
            for msg in chat_history:
                if isinstance(msg, dict):
                    if msg.get('type') == 'image_analysis':
                        continue  # 跳过图片分析记录
                    if 'content' in msg:
                        role = '医生' if msg.get('role') == 'bot' else '患者'
                        dialogue_content.append(f"{role}: {msg['content']}")
            
            if dialogue_content:
                report['sections'].append({
                    'title': '对话记录',
                    'content': '\n'.join(dialogue_content)
                })
        
        return report

    def create_pdf(self, report, output_path):
        """生成PDF报告"""
        pdf = FPDF()
        pdf.add_page()
        
        # 设置中文字体
        pdf.add_font('SimSun', '', 'static/Ubuntu_18.04_SimHei.ttf', uni=True)
        pdf.set_font('SimSun', '', 12)
        
        # 添加标题
        pdf.set_font('SimSun', '', 16)
        pdf.cell(0, 10, report['title'], ln=True, align='C')
        pdf.set_font('SimSun', '', 12)
        pdf.cell(0, 10, f"检查时间：{report['timestamp']}", ln=True)
        pdf.ln(10)
        
        # 添加各个部分
        for section in report['sections']:
            # 添加小标题
            pdf.set_font('SimSun', '', 14)
            pdf.cell(0, 10, section['title'], ln=True)
            pdf.set_font('SimSun', '', 12)
            
            # 处理内容文本
            content = section['content']
            # 计算每行可以容纳的字符数（假设每个中文字符宽度为12）
            chars_per_line = int(pdf.w / 12)
            
            # 按段落分割
            paragraphs = content.split('\n')
            for paragraph in paragraphs:
                # 处理每个段落
                words = paragraph.split()
                current_line = ''
                
                for word in words:
                    # 如果当前行加上新词不超过每行限制，则添加到当前行
                    if len(current_line + word) <= chars_per_line:
                        current_line += word + ' '
                    else:
                        # 输出当前行并开始新行
                        pdf.cell(0, 10, current_line.strip(), ln=True)
                        current_line = word + ' '
                
                # 输出最后一行
                if current_line:
                    pdf.cell(0, 10, current_line.strip(), ln=True)
                
                # 段落之间添加空行
                pdf.ln(5)
            
            # 部分之间添加更多空行
            pdf.ln(10)
        
        # 保存PDF
        pdf.output(output_path)

if __name__ == '__main__':
    # 测试数据
    test_tongue_result = {
        'tongue_color': 3,  # 绛舌
        'coating_color': 2,  # 灰黑苔
        'thickness': 1,  # 厚
        'rot_greasy': 1  # 腐
    }
    
    test_tooth_result = {
        'label': 'Caries (置信度: 0.91)'
    }
    
    test_chat_history = [
        {'role': 'user', 'content': '我的牙齿有点疼'},
        {'role': 'bot', 'content': '根据检查结果，您可能患有龋齿。建议及时就医治疗。'}
    ]
    
    # 创建报告生成器实例
    generator = ReportGenerator()
    
    # 生成报告
    report = generator.generate_tooth_report(test_tooth_result, test_chat_history)
    
    if report:
        # 创建输出目录
        output_dir = 'test_output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成PDF
        output_path = os.path.join(output_dir, 'test_report.pdf')
        generator.create_pdf(report, output_path)
        print(f"报告已生成：{output_path}")
    else:
        print("报告生成失败") 