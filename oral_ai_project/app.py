# app.py
from flask import Flask, request, render_template, jsonify, send_from_directory, send_file, Response
from model.tooth_classifier import classify_tooth
from model.tongue_classifier import classify_tongue
from model.llm_interface_api import init_prompt_with_tooth_result, init_prompt_with_tongue_result, chat_with_llm
from routes.analysis import analysis_bp
from speech_recognition import SpeechRecognition
import os
from datetime import datetime
import json
import tempfile
from model.report_generator import ReportGenerator
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(analysis_bp)

# 确保上传目录存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 历史记录文件路径
HISTORY_FILE = 'database/history.json'

# 标签保存目录
LABELS_DIR = {
    'tongue': 'database/labels/tongue',
    'tooth': 'database/labels/tooth'
}

# 标签文件名
LABEL_FILES = {
    'tongue': 'tongue_labels.json',
    'tooth': 'tooth_labels.json'
}

# 确保所有必要的目录存在
for dir_path in [UPLOAD_FOLDER, 'database', HISTORY_FILE.rsplit('/', 1)[0]] + list(LABELS_DIR.values()):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# 确保历史记录文件存在
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# 确保标签文件存在
for check_type in ['tongue', 'tooth']:
    label_file = os.path.join(LABELS_DIR[check_type], LABEL_FILES[check_type])
    if not os.path.exists(label_file):
        with open(label_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

# 添加音频缓存目录
AUDIO_CACHE_DIR = 'cache/audio'
if not os.path.exists(AUDIO_CACHE_DIR):
    os.makedirs(AUDIO_CACHE_DIR)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chat')
def chat_page():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/api/history')
def get_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<id>', methods=['DELETE'])
def delete_history(id):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 找到并删除指定记录
        history = [item for item in history if item['id'] != id]
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<id>', methods=['GET'])
def get_history_detail(id):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        # 用字符串比较，避免类型不一致
        record = next((item for item in history if str(item.get('id')) == str(id)), None)
        if record is None:
            return jsonify({'error': '记录不存在'}), 404
        return jsonify(record)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_labels(check_type, labels, timestamp):
    """保存标签到对应的JSON文件"""
    try:
        # 获取标签文件路径
        label_file = os.path.join(LABELS_DIR[check_type], LABEL_FILES[check_type])
        
        # 读取现有数据
        try:
            with open(label_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []
        
        # 添加新数据（包含时间戳）
        new_record = {
            'timestamp': timestamp,
            'data': labels
        }
        existing_data.append(new_record)
        
        # 保存更新后的数据
        with open(label_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
        return True
    except Exception as e:
        print(f"保存标签失败: {str(e)}")
        return False

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['image']
    check_type = request.form.get('check_type', 'tongue')
    print(f"收到上传请求，检查类型: {check_type}")
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file:
        try:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # 生成日期-时间格式的时间戳
            current_time = datetime.now()
            timestamp = current_time.strftime('%Y-%m-%d_%H-%M-%S')
            
            # 进行图片分析
            if check_type == 'tooth':
                label = classify_tooth(filepath)
                print(f"牙齿分类结果: {label}")  # 添加调试信息
                
                # 解析标签和置信度
                label_parts = label.split(' (置信度: ')
                if len(label_parts) == 2:
                    tooth_label = label_parts[0]
                    confidence = label_parts[1].rstrip(')')
                else:
                    tooth_label = label
                    confidence = '100%'
                
                initial_prompt = init_prompt_with_tooth_result(label)
                # 保存牙齿标签
                save_labels(check_type, {'label': tooth_label, 'confidence': confidence}, timestamp)
                result = {
                    'check_type': 'tooth',
                    'label': tooth_label,
                    'confidence': confidence
                }
            else:
                result = classify_tongue(filepath)
                if "error" in result:
                    return jsonify({"error": result["error"]})
                initial_prompt = init_prompt_with_tongue_result(result)
                # 保存舌苔标签
                save_labels(check_type, result, timestamp)
                result['check_type'] = 'tongue'
            
            # 获取AI分析结果
            response = chat_with_llm(initial_prompt)
            
            # 返回结果（不再写入历史）
            return jsonify({
                'response': response,
                'filename': filename,
                **result
            })
            
        except Exception as e:
            print(f"图片分析失败: {str(e)}")
            return jsonify({'error': f'分析失败：{str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])
    try:
        # 直接返回完整回复
        response = chat_with_llm(message, history)
        return jsonify({'response': response})
    except Exception as e:
        print(f'对话失败: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        history = data.get('history', [])
        print("收到生成报告请求")
        print(f"历史记录: {history}")
        
        # 获取最后一次上传的图片分析结果
        last_image_result = None
        image_url = None
        for msg in reversed(history):
            if msg.get('type') == 'image_analysis':
                last_image_result = msg.get('result')
                # 新增：优先用filename拼接图片地址
                filename = msg.get('filename') or (last_image_result.get('filename') if last_image_result else None)
                if filename:
                    image_url = f'/static/uploads/{filename}'
                else:
                    image_url = msg.get('image_url') if 'image_url' in msg else None
                break
        
        print(f"找到的图片分析结果: {last_image_result}")
        
        if not last_image_result:
            print("未找到图片分析结果")
            return jsonify({'error': '未找到图片分析结果'}), 400
        
        # 创建报告生成器
        report_generator = ReportGenerator()
        
        # 根据检查类型生成报告
        check_type = last_image_result.get('check_type')
        print(f"检查类型: {check_type}")
        if check_type == 'tongue':
            tongue_data = {
                'tongue_color': last_image_result.get('tongue_color'),
                'coating_color': last_image_result.get('coating_color'),
                'thickness': last_image_result.get('thickness'),
                'rot_greasy': last_image_result.get('rot_greasy')
            }
            report = report_generator.generate_tongue_report(tongue_data, history)
        elif check_type == 'tooth':
            tooth_data = {
                'label': last_image_result.get('label'),
                'confidence': last_image_result.get('confidence')
            }
            report = report_generator.generate_tooth_report(tooth_data, history)
        else:
            print(f"不支持的检查类型: {check_type}")
            return jsonify({'error': '暂不支持该类型的报告生成'}), 400
        
        if not report:
            print("报告生成器返回空结果")
            return jsonify({'error': '生成报告失败：报告生成器返回空结果'}), 500
        
        # 创建临时文件
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                #print("report: ", report)
                # 生成PDF
                report_generator.create_pdf(report, tmp.name)
                
                # ====== 新增：生成报告后写入历史 ======
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                history_item = {
                    'id': timestamp,
                    'image_url': image_url,
                    'check_type': check_type,
                    'created_at': datetime.now().isoformat(),
                    'title': report.get('title', f'{check_type}检查'),
                    'report': report
                }
                try:
                    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                        all_history = json.load(f)
                except Exception:
                    all_history = []
                all_history.append(history_item)
                with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump(all_history, f, ensure_ascii=False, indent=2)
                # ====== 新增结束 ======
                
                # 发送文件
                return send_file(
                    tmp.name,
                    mimetype='application/pdf'
                )
        except Exception as e:
            print(f"PDF生成失败: {str(e)}")
            return jsonify({'error': f'PDF生成失败：{str(e)}'}), 500
        
    except Exception as e:
        print(f"生成报告失败: {str(e)}")
        return jsonify({'error': f'生成报告失败：{str(e)}'}), 500

@app.route('/api/upload_audio', methods=['POST'])
def upload_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 生成安全的文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f'recording_{timestamp}.wav')
        filepath = os.path.join(AUDIO_CACHE_DIR, filename)
        
        # 保存文件
        audio_file.save(filepath)
        print(f"音频文件已保存: {filepath}")
        
        # 进行语音识别
        recognizer = SpeechRecognition()
        recognition_result = recognizer.recognize_audio(filepath)

        print(f"语音识别结果: {recognition_result}")
        if recognition_result:
            # 获取AI回复
            response = chat_with_llm(recognition_result)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'recognition_result': recognition_result,
                'response': response
            })
        else:
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'error': '语音识别失败'
            })
        
    except Exception as e:
        print(f"音频处理失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news')
def get_news():
    news = [
        {"title": "2024年\"全国爱牙日\"宣传主题发布", "url": "https://wjw.fj.gov.cn/xxgk/gzdt/mtbd/202409/t20240906_6512495.htm", "summary": "今年\"全国爱牙日\"主题为\"口腔健康全身健康\"，副主题\"全生命周期守护让健康从'齿'开始\"。各地将开展口腔健康宣传、义诊、科普等活动。", "image": "/static/aiya.png"},
        {"title": "智能舌诊系统：深度学习助力中医诊断", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9600321/", "summary": "基于深度学习的智能舌诊系统，集成YOLOv5、U-Net、MobileNetV3等模型，实现舌象检测、分割和特征分类，推动中医舌诊客观化、智能化。", "image": "/static/tongue_ai.png"},
        {"title": "儿童口腔健康：儿科医生干预可提升看牙率", "url": "https://www.nidcr.nih.gov/news-events/nidcr-news/2024/dental-visits-increase-support-pediatric-providers", "summary": "研究显示，儿科医生在体检时加强口腔健康教育和转诊，可显著提升儿童看牙率，减少龋齿等问题。", "image": "/static/child_tooth.png"},
        {"title": "上海市2024年\"全国爱牙日\"活动通知", "url": "https://www.shanghai.gov.cn/gwk/search/content/9896786ef3954a86ae469d0445be0780", "summary": "上海将于9月20日举办\"全国爱牙日\"主题宣传活动，现场义诊、游园、科普讲堂等，普及口腔健康知识。", "image": "/static/shanghai_aiya.png"},
        {"title": "中医舌诊在现代医学中的应用", "url": "https://agelessherbs.com/mouth-tongue/", "summary": "介绍舌象、舌苔、唇色等在中医诊断中的意义及常见健康提示。", "image": "/static/tcm_tongue.jpg"}
    ]
    return jsonify(news)

if __name__ == '__main__':
    app.run(debug=True)
