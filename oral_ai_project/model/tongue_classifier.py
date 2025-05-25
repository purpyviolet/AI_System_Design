import torch
from PIL import Image
import numpy as np

from yolov5 import load
from segment_anything import sam_model_registry, SamPredictor
from model.resnet import ResNetPredictor  # 注意路径是否正确


class TongueAnalyzer:
    def __init__(self,
                 yolo_path='model/weights/yolov5.pt',
                 sam_path='model/weights/sam_vit_b_01ec64.pth',
                 resnet_path=[
                     'model/weights/tongue_color.pth',
                     'model/weights/tongue_coat_color.pth',
                     'model/weights/thickness.pth',
                     'model/weights/rot_and_greasy.pth'
                 ]):
        self.device = torch.device('cuda:0')

        # 加载模型
        self.yolo = load(yolo_path, device='cuda:0')
        self.sam = sam_model_registry["vit_b"](checkpoint=sam_path)
        self.resnet = ResNetPredictor(resnet_path)

    def analyze(self, img_path):
        """
        对图像进行舌体检测、分割、分析，返回最终结果
        :param img_path: 图像路径
        :return: 包含舌色、苔色、厚薄、腐腻的结果字典
        """
        predict_img = Image.open(img_path).convert("RGB")
        print("开始舌体检测...")

        # 舌体检测
        self.yolo.eval()
        with torch.no_grad():
            pred = self.yolo(predict_img)

        if len(pred.xyxy[0]) < 1:
            print("图片不合法：未检测到舌头")
            return {"code": 201}
        elif len(pred.xyxy[0]) > 1:
            print("图片不合法：检测到多个舌头")
            return {"code": 202}

        print("舌体分割中...")
        x1, y1, x2, y2 = (pred.xyxy[0][0, 0].item(), pred.xyxy[0][0, 1].item(),
                          pred.xyxy[0][0, 2].item(), pred.xyxy[0][0, 3].item())

        # 初始化 SAM 并设置图像
        predictor = SamPredictor(self.sam)
        predictor.set_image(np.array(predict_img))

        # 获取 mask
        masks, _, _ = predictor.predict(box=np.array([x1, y1, x2, y2]))
        original_img = np.array(predict_img)
        masks = np.transpose(masks, (1, 2, 0))
        pred_mask = original_img * masks

        # 裁剪舌体区域
        result = Image.fromarray(pred_mask).crop((x1, y1, x2, y2)).convert("RGB")
        tongue_cropped = np.array(result)

        print("舌体特征分析中...")
        result = self.resnet.predict(tongue_cropped)

        return {
            "code": 0,
            "tongue_color": result[0],
            "coating_color": result[1],
            "thickness": result[2],
            "rot_greasy": result[3]
        }


# 封装用于主系统调用的函数
def classify_tongue(image_path):
    """
    调用 TongueAnalyzer 对舌象图片进行分类
    :param image_path: 舌象图片路径
    :return: 若成功返回结果 dict；否则返回 {"error": msg}
    """
    analyzer = TongueAnalyzer()
    result = analyzer.analyze(image_path)

    if result["code"] != 0:
        return {"error": f"舌象分析失败，错误码 {result['code']}"}

    return {
        "tongue_color": result["tongue_color"],
        "coating_color": result["coating_color"],
        "thickness": result["thickness"],
        "rot_greasy": result["rot_greasy"]
    }


# 本地测试（可选）
if __name__ == "__main__":
    image_path = "D:\\zyh\\舌象\\淡白舌黄苔\\淡白舌黄苔厚苔非腻苔\\1809.jpg"
    result = classify_tongue(image_path)
    print("舌象分析结果：", result)
