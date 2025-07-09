from openai import OpenAI

# 初始化 API 客户端
client = OpenAI(
    api_key="sk-c317348a89df4b4faa79adaff8d688e2",  # ⚠️替换为你的真实 Key
    base_url="https://api.deepseek.com/v1"
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
    """
    根据牙齿识别结果，生成开启多轮问诊的初始prompt。
    """
    return (
        f"我的牙齿图片AI识别结果是'{label}'。\n"
        f"这是我的牙齿分析结果。请先告诉我这个结果是什么，然后向我提出一些相关问题来进一步了解情况。不要在我回答之前给出任何建议。"
    )

def init_prompt_with_tongue_result(result):
    if "code" in result and result["code"] != 0:
        return "上传的图片无法识别，请上传清晰的舌头图片。"

    tongue_color = feature_map["舌色"].get(result.get("tongue_color"), "未知")
    coating_color = feature_map["舌苔颜色"].get(result.get("coating_color"), "未知")
    thickness = feature_map["厚薄"].get(result.get("thickness"), "未知")
    rot_greasy = feature_map["腐腻"].get(result.get("rot_greasy"), "未知")

    prompt = (
        f"我的舌象图片AI分析结果如下：\n"
        f"- 舌色：{tongue_color}\n"
        f"- 苔色：{coating_color}\n"
        f"- 苔厚薄：{thickness}\n"
        f"- 腐腻情况：{rot_greasy}\n\n"
        f"这是我的舌象分析结果。请先告诉我这个结果指出了什么潜在问题，然后向我提出一些相关问题来进一步了解情况。不要在我回答之前给出任何调理建议。"
    )
    return prompt

def chat_with_llm(message, history=None, stream=False):
    """
    调用 DeepSeek Chat 接口，支持多轮对话和流式输出。
    """
    messages = []

    # 设定 AI 角色和对话风格
    system_prompt = (
        "你是一位专业的看诊牙齿症状和进行舌诊的医生。你的沟通风格应该简洁、温暖，既有专业性又让用户感到安心。\n"
        "不要说是牙科医生 或 舌科医生，我是你的专属助手。\n"
        "你的任务流程如下：\n"
        "1. **首次分析**: 当用户上传图片并得到AI分析结果后，你的第一步是：a. 简洁地告知用户分析结果是什么，指出了什么潜在问题。 b. **然后，只提出1-2个最关键的问题进行追问**，以便收集更多信息。c. **绝对不要在首次回复中给出任何治疗或调理建议**。\n"
        "2. **倾听与追问**: 在收到用户对你问题的回答后，用一句话简要确认（例如：'好的，了解了您的情况。'），如果需要，可以再提问，但尽量一次问完。\n"
        "3. **解释与建议**: 在收集到足够信息后，用通俗的语言解释病因，并给出清晰、可行的核心建议。\n"
        "4. **保持简洁**: 核心要求是**简洁**，但是要给够信息量，不能过于简短了。在表达关怀的同时，不要出现'关键问题'，这种类似字眼，要像一般的医生一样正常询问，避免不必要的客套和重复。回答应是连贯的段落，严禁使用分点列表。"
        "5. **深入询问**: 在收到用户回答后，用一句话确认理解，然后分步骤进行至少三轮提问，包括：a. 口腔症状的具体表现（如疼痛程度、持续时间等） b. 日常饮食习惯（如甜食频率、进食温度偏好等） c. 相关口腔护理习惯和身体健康状况（如刷牙频率、全身性疾病等）。\n"
        "6. **解释与建议**: 在收集到足够信息后，用通俗的语言解释病因，并给出清晰、可行的核心建议，包括日常护理和专业治疗建议。\n"
    )
    messages.append({"role": "system", "content": system_prompt})

    # 加入一个对话范例，让模型学习对话风格 (Few-shot example)
    # example_conversation = [
    #     {
    #         "role": "user",
    #         "content": "是啊！工作不顺心，经常发脾气，吃东西也不注意……"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "情绪因素和不良饮食习惯会诱发重型溃疡。需要系统治疗，调整生活方式。"
    #     },
    #     {
    #         "role": "user",
    #         "content": "那怎么治疗？会不会影响工作？"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "给您开糖皮质激素药膏、止痛喷雾，搭配口服免疫调节剂。治疗期间注意休息。"
    #     },
    #     {
    #         "role": "user",
    #         "content": "明白了！以后怎么预防复发？"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "要预防复发，主要还是得从生活习惯入手。首先要试着调节好自己的情绪，然后注意别吃太硬或者太刺激的东西。当然，保持规律的作息和适量的运动也很有帮助。"
    #     },
    #     {
    #         "role": "user",
    #         "content": "记下了！今天能开药吗？"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "可以！马上开电子处方。用药期间如果溃疡没有好转或者出现其他异常情况，要及时来复诊。"
    #     }
    # ]
    # messages.extend(example_conversation)

    # 加入历史记录
    if history:
        messages.extend(history)
        print("history: ",history)
        print("message: ",message)

    # 当前用户消息
    messages.append({"role": "user", "content": message})

    # 调用 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=stream
    )
    
    # if stream:
    #     return response  # 流式模式下返回生成器
    # else:
    #     return response.choices[0].message.content # 非流式模式下返回完整文本

    return response.choices[0].message.content


