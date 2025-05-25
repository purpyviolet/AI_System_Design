import random
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用于显示负号

# 定义舌诊维度及其评分映射（0~1）
health_score_map = {
    "舌色": {"淡白舌": 0.6, "淡红舌": 1.0, "红舌": 0.8, "绛舌": 0.4, "青紫舌": 0.2},
    "苔色": {"白苔": 1.0, "黄苔": 0.5, "黑苔": 0.2},
    "苔厚": {"薄苔": 1.0, "厚苔": 0.4},
    "苔腻": {"非腻苔": 1.0, "腻苔": 0.3}
}

choices = {
    "舌色": list(health_score_map["舌色"].keys()),
    "苔色": list(health_score_map["苔色"].keys()),
    "苔厚": list(health_score_map["苔厚"].keys()),
    "苔腻": list(health_score_map["苔腻"].keys()),
}

# 生成随机数据
def generate_random_data(days=14):
    records = []
    for i in range(days):
        record = {"日期": f"Day {i+1}"}
        for dim in choices:
            choice = random.choice(choices[dim])
            record[dim] = choice
            record[f"{dim}_评分"] = health_score_map[dim][choice]
        # 总体评分为四个维度之和
        record["总评分"] = sum(record[f"{dim}_评分"] for dim in choices)
        records.append(record)
    return pd.DataFrame(records)

# 趋势分析（返回趋势数组、是否改善、斜率）
def analyze_trend(values):
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(X, y)
    trend = model.predict(X)
    improvement = "改善中" if trend[-1] > trend[0] else "恶化中"
    return trend, improvement, model.coef_[0]

# 可视化所有趋势
def visualize_overall_only(df):
    plt.figure(figsize=(8, 5))
    plt.plot(df["日期"], df["总评分"], marker="o", label="总评分", color='blue')
    plt.plot(df["日期"], df["总评分_趋势"], linestyle="--", color='blue', label="总评分趋势")
    plt.title("总评分趋势图")
    plt.xlabel("日期")
    plt.ylabel("健康评分")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("tongue_health_overall_trend.png", dpi=300)
    plt.show()

def visualize_each_dim(df, trend_info):
    plt.figure(figsize=(12, 7))
    colors = {"舌色": "green", "苔色": "orange", "苔厚": "purple", "苔腻": "brown"}
    for dim in choices:
        plt.plot(df["日期"], df[f"{dim}_评分"], marker=".", label=f"{dim}评分", color=colors[dim])
        plt.plot(df["日期"], trend_info[dim]["趋势"], linestyle="--", color=colors[dim], label=f"{dim}趋势")
    plt.plot(df["日期"], df["总评分"], linestyle="-", color="blue", label="总评分")
    plt.plot(df["日期"], df["总评分_趋势"], linestyle="--", color="blue", label="总评分趋势")
    plt.title("各维度趋势图（含总评分）")
    plt.xlabel("日期")
    plt.ylabel("评分")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("tongue_health_each_dimension.png", dpi=300)
    plt.show()


def visualize_freq_stat(df):
    freq = {}
    for dim in choices:
        freq[dim] = df[dim].value_counts().idxmax()
    print("【维度频次统计】")
    for dim, val in freq.items():
        print(f"{dim}：最常出现的是 {val}")

    plt.figure(figsize=(8, 5))
    items = [df[dim].value_counts().idxmax() for dim in choices]
    counts = [df[dim].value_counts().max() for dim in choices]
    plt.bar(choices.keys(), counts, color='skyblue')
    plt.title("各维度最常出现类型的频次")
    for i, count in enumerate(counts):
        plt.text(i, count + 0.2, items[i], ha='center', fontsize=9)
    plt.ylabel("频次")
    plt.tight_layout()
    plt.savefig("tongue_health_frequent_types.png", dpi=300)
    plt.show()

def visualize_future_prediction(df, trend_info, future_days=7):
    plt.figure(figsize=(12, 7))
    colors = {"舌色": "green", "苔色": "orange", "苔厚": "purple", "苔腻": "brown", "总评分": "blue"}
    future_results = {}
    for dim in list(choices.keys()) + ["总评分"]:
        values = df[dim] if dim == "总评分" else df[f"{dim}_评分"]
        future = predict_future(values, future_days)
        future_results[dim] = future[-1]
        plt.plot(range(len(values), len(values) + future_days), future, linestyle="--", label=f"{dim}预测", color=colors[dim])
    plt.title("未来趋势预测图（未来7天）")
    plt.xlabel("预测天数")
    plt.ylabel("预测评分")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("tongue_health_future_prediction.png", dpi=300)
    plt.show()
    return future_results


# 输出维度变化分析
def print_analysis(trend_info):
    print("【维度趋势分析】")
    for dim, info in trend_info.items():
        print(f"{dim}：{info['变化']}（斜率：{info['斜率']:.3f}）")

# 生成建议
def give_advice(overall_slope):
    if overall_slope > 0.1:
        return "总体趋势明显改善，建议继续保持良好生活习惯。"
    elif overall_slope > 0:
        return "总体趋势略有改善，建议适度加强调理。"
    elif overall_slope > -0.1:
        return "总体健康评分略有下降，建议注意休息与饮食调节。"
    else:
        return "总体健康评分下降明显，建议及时就医并调整方案。"

# 未来预测（使用线性模型外推）
def predict_future(values, days=7):
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(X, y)
    future_X = np.arange(len(values), len(values) + days).reshape(-1, 1)
    future_y = model.predict(future_X)
    return future_y


# 健康阈值建议
def future_health_advice(pred_value):
    if pred_value >= 0.9:
        return "健康状态持续良好。"
    elif pred_value >= 0.7:
        return "轻微波动，建议保持观察与良好习惯。"
    elif pred_value >= 0.5:
        return "有下降趋势，建议调整作息饮食。"
    else:
        return "未来预测可能偏离健康，建议及早调理并考虑就医。"
    

# 主函数
if __name__ == "__main__":
    df = generate_random_data()
    
    trend_info = {}
    for dim in ["总评分"] + list(choices.keys()):
        values = df[dim] if dim == "总评分" else df[f"{dim}_评分"]
        trend, status, slope = analyze_trend(values)
        df[f"{dim}_趋势"] = trend
        trend_info[dim] = {
            "趋势": trend,
            "变化": status,
            "斜率": slope
        }

    print(df[["日期", "舌色", "苔色", "苔厚", "苔腻", "总评分"]])
    print()
    print_analysis(trend_info)
    print("\n【综合建议】")
    print(give_advice(trend_info["总评分"]["斜率"]))
        # 新增图：总评分趋势图
    visualize_overall_only(df)

    # 新增图：各维度趋势图
    visualize_each_dim(df, trend_info)

    # 维度频率统计图
    visualize_freq_stat(df)

    # 未来趋势预测并输出建议
    print("\n【未来7天评分预测结果】")
    future_results = visualize_future_prediction(df, trend_info, future_days=7)
    for dim, pred in future_results.items():
        advice = future_health_advice(pred)
        print(f"{dim}预测值：{pred:.3f} -> {advice}")