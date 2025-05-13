import json

# 输入输出路径
input_file = "multi_QA_口腔溃疡.json"
output_file = "alpaca_multi_QA_口腔溃疡_1.json"

# 固定 normalizedTag
normalized_tag = "口腔溃疡"

# 读取原始数据
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

converted = []
sample_id = 1
dialogue_id = 1

for item in data:
    dialogue = item["dialogue"]

    # 删除第一个 assistant 消息（如果有）
    first_assistant_index = next((i for i, m in enumerate(dialogue) if m["role"] == "assistant"), None)
    if first_assistant_index is not None:
        dialogue = dialogue[first_assistant_index + 1:]
    else:
        continue  # 若没有 assistant，跳过该条

    # 添加固定 system 信息
    system_msg = {
        "role": "system",
        "content": "你是一位专业的口腔科医生，擅长诊断龋齿等常见牙病，能通过患者描述判断病情并提供科学治疗建议。"
    }

    current_messages = [system_msg]

    for msg in dialogue:
        # 替换 user 内容中的“assistant”为“医生”
        if msg["role"] == "user":
            msg = msg.copy()
            msg["content"] = msg["content"].replace("assistant", "医生")

        current_messages.append(msg)

        if msg["role"] == "assistant":
            converted.append({
                "id": dialogue_id,
                "sample_id": sample_id,
                "normalizedTag": normalized_tag,
                "messages": current_messages.copy()
            })
            sample_id += 1

    dialogue_id += 1

# 保存结果
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(converted, f, ensure_ascii=False, indent=4)

print(f"✅ 转换完成，共生成 {len(converted)} 条样本，输出文件：{output_file}")


# import json

# # 输入输出文件路径
# input_file = "multi_QA_龋齿.json"
# output_file = "converted_alpaca_format.json"

# # 固定 normalizedTag
# normalized_tag = "龋齿"

# # 加载原始数据
# with open(input_file, "r", encoding="utf-8") as f:
#     data = json.load(f)

# converted = []
# sample_id = 1
# dialogue_id = 1

# for item in data:
#     dialogue = item["dialogue"]
#     case_tag = normalized_tag

#     # 找到第一个 assistant 的索引
#     first_assistant_index = next((i for i, m in enumerate(dialogue) if m["role"] == "assistant"), None)
#     if first_assistant_index is None:
#         continue  # 没有 assistant 就跳过该对话

#     # 删除第一个 assistant
#     dialogue = dialogue[first_assistant_index + 1:]

#     # 初始化 messages，包含固定 system message
#     system_msg = {
#         "role": "system",
#         "content": "你是一位专业的口腔科医生，擅长诊断龋齿等常见牙病，能通过患者描述判断病情并提供科学治疗建议。"
#     }

#     current_messages = [system_msg]
#     for msg in dialogue:
#         current_messages.append(msg)
#         if msg["role"] == "assistant":
#             # 每遇到一个 assistant，记录当前上下文为一个完整 sample
#             converted.append({
#                 "id": dialogue_id,
#                 "sample_id": sample_id,
#                 "normalizedTag": case_tag,
#                 "messages": current_messages.copy()
#             })
#             sample_id += 1

#     dialogue_id += 1

# # 保存到文件
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(converted, f, ensure_ascii=False, indent=4)

# print(f"转换完成，共生成 {len(converted)} 条样本，输出文件：{output_file}")
