# model/llm_interface.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

_model = None
_tokenizer = None

def load_llm_model():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        model_dir = r"your/path/to/model"
        _tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
        _model = AutoModelForCausalLM.from_pretrained(
            model_dir,
            device_map="cuda:0",
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )
        _model.eval()


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
        f"回答不要有答案什么的关键词，也不要重复prompt里的内容。。。"
    )
    # print(prompt)
    return prompt


def chat_with_llm(message, history=None):
    load_llm_model()
    inputs = _tokenizer(message, return_tensors="pt").to(_model.device)
    generation_output = _model.generate(**inputs, max_new_tokens=256)
    response = _tokenizer.decode(generation_output[0], skip_special_tokens=True)
    return response

