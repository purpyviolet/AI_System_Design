from openai import OpenAI

# 初始化 API 客户端
client = OpenAI(
    api_key="sk-6cf3f5b267f14cc0a2b4546e98fc57a7",  # ⚠️替换为你的真实 Key
    base_url="https://api.deepseek.com"
)


# 舌象标签映射表
feature_map = {
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

def init_prompt_with_tooth_result(label):
    return (
        f"你是一位牙科诊断专家。用户上传了牙齿图片，经 AI 识别结果为：“{label}”。\n"
        f"请你用专业但通俗的语言分析这种牙科症状可能的成因、风险与注意事项，"
        f"并提出可行的治疗建议或生活调理方案。请尽量分点说明，避免重复内容。"
    )

def init_prompt_with_tongue_result(result):
    if "code" in result and result["code"] != 0:
        return "上传的图片无法识别，请上传清晰的舌头图片。"

    tongue_color = feature_map["舌色"].get(result.get("tongue_color"), "未知")
    coating_color = feature_map["舌苔颜色"].get(result.get("coating_color"), "未知")
    thickness = feature_map["厚薄"].get(result.get("thickness"), "未知")
    rot_greasy = feature_map["腐腻"].get(result.get("rot_greasy"), "未知")

    prompt = (
        f"你是一位中医问诊专家。用户上传了一张舌头图片，AI分析得出如下四项特征：\n"
        f"1. 舌色：{tongue_color}；\n"
        f"2. 苔色：{coating_color}；\n"
        f"3. 苔厚薄：{thickness}；\n"
        f"4. 腐腻情况：{rot_greasy}。\n"
        f"请用专业但易懂的语言，逐项分析这些舌象可能反映出的健康状态，并提供生活调养建议。"
        f"请避免重复 prompt 内容，也不必说“根据您的描述”或“结合上述信息”这些套话，直接进入分析即可。"
    )
    return prompt

def chat_with_llm(message, history=None):
    """
    调用 DeepSeek Chat 接口，返回模型回复。
    """
    # 构造 messages 格式（保留 history 支持）
    messages = []

    # 可选系统提示（设定 AI 角色）
    messages.append({"role": "system", "content": "你是一位严谨、专业、通俗易懂的医生，请用中文回答问题。"})

    # 加入历史记录
    if history:
        messages.extend(history)

    # 当前用户消息
    messages.append({"role": "user", "content": message})

    # 调用 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    return response.choices[0].message.content