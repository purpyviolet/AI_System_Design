from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression

analysis_bp = Blueprint('analysis', __name__)

# 标签文件路径
LABELS_DIR = {
    'tongue': 'database/labels/tongue',
    'tooth': 'database/labels/tooth'
}

LABEL_FILES = {
    'tongue': 'tongue_labels.json',
    'tooth': 'tooth_labels.json'
}

def load_labels(check_type):
    """加载标签数据"""
    try:
        file_path = os.path.join(LABELS_DIR[check_type], LABEL_FILES[check_type])
        if not os.path.exists(file_path):
            print(f"标签文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"成功加载数据: {len(data)} 条记录")
            return data
    except Exception as e:
        print(f"加载标签数据失败: {str(e)}")
        return []

def filter_by_time_range(records, time_range):
    """根据时间范围过滤记录"""
    now = datetime.now()
    
    if time_range == 'week':
        start_date = now - timedelta(days=7)
    elif time_range == 'two-weeks':
        start_date = now - timedelta(days=14)
    elif time_range == 'month':
        start_date = now - timedelta(days=30)
    elif time_range == 'three-months':
        start_date = now - timedelta(days=90)
    else:  # all
        return records
    
    return [
        record for record in records
        if datetime.strptime(record['timestamp'], '%Y-%m-%d_%H-%M-%S') >= start_date
    ]

def calculate_tongue_scores(records):
    """计算舌诊评分"""
    dates = []
    overall_scores = []
    dimension_scores = {
        'tongueColor': [],
        'coating': [],
        'shape': [],
        'state': []
    }
    
    # 舌色评分标准
    tongue_color_scores = {
        0: 60,   # 淡白舌
        1: 100,  # 淡红舌
        2: 80,   # 红舌
        3: 40,   # 绛舌
        4: 20    # 青紫舌
    }
    
    # 舌苔颜色评分标准
    coating_color_scores = {
        0: 100,  # 白苔
        1: 60,   # 黄苔
        2: 20    # 灰黑苔
    }
    
    # 舌苔厚度评分标准
    thickness_scores = {
        0: 100,  # 薄
        1: 40    # 厚
    }
    
    # 舌苔腻度评分标准
    rot_greasy_scores = {
        0: 40,   # 腻
        1: 100   # 腐
    }
    
    for record in records:
        data = record['data']
        # 将时间戳转换为日期格式
        date = datetime.strptime(record['timestamp'], '%Y-%m-%d_%H-%M-%S').strftime('%Y-%m-%d')
        
        # 计算各维度评分
        scores = []
        dimension_scores_list = []
        
        # 舌色评分
        if 'tongue_color' in data:
            score = tongue_color_scores.get(data['tongue_color'], 60)
            scores.append(score)
            dimension_scores_list.append(('tongueColor', score))
        
        # 舌苔颜色评分
        if 'coating_color' in data:
            score = coating_color_scores.get(data['coating_color'], 60)
            scores.append(score)
            dimension_scores_list.append(('coating', score))
        
        # 舌苔厚度评分
        if 'thickness' in data:
            score = thickness_scores.get(data['thickness'], 60)
            scores.append(score)
            dimension_scores_list.append(('shape', score))
        
        # 舌苔腻度评分
        if 'rot_greasy' in data:
            score = rot_greasy_scores.get(data['rot_greasy'], 60)
            scores.append(score)
            dimension_scores_list.append(('state', score))
        
        if scores:
            # 计算总体评分（加权平均）
            weights = [0.3, 0.3, 0.2, 0.2]  # 各维度的权重
            weighted_scores = [score * weight for score, weight in zip(scores, weights)]
            overall_score = sum(weighted_scores) / sum(weights[:len(scores)])
            
            dates.append(date)
            overall_scores.append(overall_score)
            
            # 更新各维度评分
            for dim, score in dimension_scores_list:
                dimension_scores[dim].append(score)
    
    return {
        'dates': dates,
        'scores': overall_scores,
        'dimensions': dimension_scores
    }

def calculate_frequency_stats(records):
    """计算特征频率统计"""
    stats = {
        'tongue_color': {},
        'coating_color': {},
        'thickness': {},
        'rot_greasy': {}
    }
    
    # 特征名称映射
    feature_names = {
        'tongue_color': {
            0: '淡白舌',
            1: '淡红舌',
            2: '红舌',
            3: '绛舌',
            4: '青紫舌'
        },
        'coating_color': {
            0: '白苔',
            1: '黄苔',
            2: '灰黑苔'
        },
        'thickness': {
            0: '薄',
            1: '厚'
        },
        'rot_greasy': {
            0: '腻',
            1: '腐'
        }
    }
    
    for record in records:
        data = record['data']
        for key in stats:
            if key in data:
                value = data[key]
                stats[key][value] = stats[key].get(value, 0) + 1
    
    # 转换为饼图数据格式
    pie_data = []
    for feature, values in stats.items():
        for value, count in values.items():
            # 使用中文名称
            display_name = feature_names[feature].get(value, str(value))
            pie_data.append({
                'name': f"{display_name}",
                'value': count
            })
    
    return pie_data

def predict_future_trend(dates, scores, days=7):
    """预测未来趋势"""
    if len(dates) < 2:
        return {
            'dates': dates,
            'historical': scores,
            'predicted': []
        }
    
    # 将日期转换为数值
    x = np.array(range(len(dates))).reshape(-1, 1)
    y = np.array(scores)
    
    # 训练线性回归模型
    model = LinearRegression()
    model.fit(x, y)
    
    # 预测未来趋势
    future_x = np.array(range(len(dates), len(dates) + days)).reshape(-1, 1)
    future_y = model.predict(future_x)
    
    # 生成未来日期
    last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
    future_dates = [
        (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
        for i in range(days)
    ]
    
    return {
        'dates': dates + future_dates,
        'historical': scores + [None] * days,
        'predicted': [None] * len(dates) + list(future_y)
    }

def generate_summary(scores, dimensions):
    """生成分析总结"""
    if not scores:
        return "暂无数据可供分析"
    
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # 分析趋势
    if len(scores) >= 2:
        trend = "上升" if scores[-1] > scores[0] else "下降"
        trend_strength = abs(scores[-1] - scores[0]) / max(scores)
    else:
        trend = "稳定"
        trend_strength = 0
    
    # 维度名称映射
    dimension_names = {
        'tongueColor': '舌色',
        'coating': '舌苔',
        'shape': '舌形',
        'state': '舌态'
    }
    
    # 生成总结文本
    summary = f"""
    <p>总体评分：{avg_score:.1f}分（最高{max_score:.1f}分，最低{min_score:.1f}分）</p>
    <p>健康趋势：{trend}趋势{'明显' if trend_strength > 0.1 else '不明显'}</p>
    """
    
    # 添加各维度分析
    if dimensions:
        summary += "<p>各维度分析：</p><ul>"
        for dim, scores in dimensions.items():
            if scores:  # 确保有数据
                avg_dim_score = sum(scores) / len(scores)
                status = "良好" if avg_dim_score >= 80 else "一般" if avg_dim_score >= 60 else "需要关注"
                summary += f"<li>{dimension_names[dim]}：{avg_dim_score:.1f}分（{status}）</li>"
        summary += "</ul>"
    
    return summary

def load_tooth_data():
    """加载牙科标签数据"""
    try:
        file_path = os.path.join(LABELS_DIR['tooth'], LABEL_FILES['tooth'])
        if not os.path.exists(file_path):
            print(f"牙科标签文件不存在: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # print(f"成功加载牙科数据: {len(data)} 条记录")
            return data
    except Exception as e:
        print(f"加载牙科标签数据失败: {str(e)}")
        return []

def process_tooth_data(data):
    """处理牙科数据"""
    # 初始化数据结构
    dates = []
    scores = []
    disease_distribution = {}
    frequency = []
    prediction = {
        'dates': [],
        'historical': [],
        'predicted': []
    }
    
    # 处理数据
    for item in data:
        # 解析时间戳
        timestamp = item['timestamp']
        date = datetime.strptime(timestamp, '%Y-%m-%d_%H-%M-%S').strftime('%Y-%m-%d')
        dates.append(date)
        
        # 解析标签和置信度
        label_text = item['data']['label']
        label_parts = label_text.split(' (置信度: ')
        if len(label_parts) == 2:
            label = label_parts[0]
            confidence = label_parts[1].rstrip(')')
        else:
            label = label_text
            confidence = '1.0'
        
        # 计算评分
        score = calculate_tooth_score({'label': label, 'confidence': confidence})
        scores.append(score)
        
        # 统计疾病分布
        update_disease_distribution(disease_distribution, {'label': label})
        
        # 统计特征频率
        update_tooth_frequency_stats(frequency, {'label': label})
    
    # 生成预测数据
    if len(scores) > 0:
        prediction_data = predict_future_trend(dates, scores)
        prediction['dates'] = prediction_data['dates']
        prediction['historical'] = prediction_data['historical']
        prediction['predicted'] = prediction_data['predicted']
    
    # 生成分析总结
    summary = generate_tooth_summary(scores, disease_distribution)
    
    return {
        'overall': {'dates': dates, 'scores': scores},
        'disease_distribution': disease_distribution,
        'frequency': frequency,
        'prediction': prediction,
        'summary': summary
    }

def calculate_tooth_score(data):
    """计算牙科检查评分"""
    if not data:
        return 0
    
    # 根据疾病类型和置信度计算评分
    base_scores = {
        '少牙症': 60,
        '牙龈炎': 70,
        '口腔溃疡': 80,
        '牙结石': 75,
        '龋齿': 65,
        '牙齿变色': 85
    }
    
    label = data.get('label', '')
    confidence = float(data.get('confidence', '0').strip('%'))
    # print(label, confidence)
    
    base_score = base_scores.get(label, 70)
    return int(base_score * confidence)

def update_disease_distribution(distribution, data):
    """更新疾病分布统计"""
    if not data or 'label' not in data:
        return
    
    label = data['label']
    distribution[label] = distribution.get(label, 0) + 1

def update_tooth_frequency_stats(frequency, data):
    """更新牙科特征频率统计"""
    if not data:
        return
    
    # 统计疾病类型
    if 'label' in data:
        disease_type = data['label']
        found = False
        for item in frequency:
            if item['name'] == disease_type:
                item['value'] += 1
                found = True
                break
        if not found:
            frequency.append({'name': disease_type, 'value': 1})

def generate_tooth_summary(scores, disease_distribution):
    """生成牙科分析总结"""
    if not scores:
        return "暂无牙科检查数据"
    
    avg_score = sum(scores) / len(scores)
    most_common_disease = max(disease_distribution.items(), key=lambda x: x[1])[0] if disease_distribution else "未知"
    
    summary = f"""
    <p>根据历史数据分析：</p>
    <ul>
        <li>平均健康评分：{avg_score:.1f}分</li>
        <li>最常见的口腔问题：{most_common_disease}</li>
        <li>检查次数：{len(scores)}次</li>
    </ul>
    <p>建议：</p>
    <ul>
        <li>定期进行口腔检查</li>
        <li>保持良好的口腔卫生习惯</li>
        <li>发现问题及时就医</li>
    </ul>
    """
    
    return summary

@analysis_bp.route('/api/analysis')
def get_analysis():
    try:
        # 获取请求参数
        analysis_type = request.args.get('type', 'tongue')
        time_range = request.args.get('range', 'week')
        
        # 根据分析类型加载数据
        if analysis_type == 'tongue':
            records = load_labels('tongue')
            if not records:
                return jsonify({
                    'error': '没有可用的舌诊分析数据'
                }), 404
            
            # 按时间范围过滤
            filtered_records = filter_by_time_range(records, time_range)
            if not filtered_records:
                filtered_records = records  # 如果过滤后没有数据，使用全部数据
            
            # 计算评分
            scores_data = calculate_tongue_scores(filtered_records)
            
            # 计算频率统计
            frequency_data = calculate_frequency_stats(filtered_records)
            
            # 预测趋势
            prediction_data = predict_future_trend(
                scores_data['dates'],
                scores_data['scores']
            )
            
            # 生成总结
            summary = generate_summary(
                scores_data['scores'],
                scores_data['dimensions']
            )
            
            result = {
                'overall': {
                    'dates': scores_data['dates'],
                    'scores': scores_data['scores']
                },
                'dimensions': {
                    'dates': scores_data['dates'],
                    'tongueColor': scores_data['dimensions']['tongueColor'],
                    'coating': scores_data['dimensions']['coating'],
                    'shape': scores_data['dimensions']['shape'],
                    'state': scores_data['dimensions']['state']
                },
                'frequency': frequency_data,
                'prediction': prediction_data,
                'summary': summary
            }
            
        elif analysis_type == 'tooth':
            data = load_tooth_data()
            if not data:
                return jsonify({
                    'error': '没有可用的牙科分析数据'
                }), 404
            
            filtered_data = filter_by_time_range(data, time_range)
            if not filtered_data:
                filtered_data = data  # 如果过滤后没有数据，使用全部数据
            
            result = process_tooth_data(filtered_data)
            
        else:
            return jsonify({'error': '不支持的分析类型'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"分析失败: {str(e)}")
        return jsonify({'error': str(e)}), 500 