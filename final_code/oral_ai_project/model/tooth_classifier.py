import torch
import torch.nn as nn
from torchvision.models import efficientnet_b3
from PIL import Image
import torchvision.transforms as transforms
import warnings

warnings.filterwarnings("ignore")

class CustomEfficientNet(nn.Module):
    def __init__(self, num_classes, weight_path=None):
        super(CustomEfficientNet, self).__init__()
        self.model = efficientnet_b3(weights='EfficientNet_B3_Weights.IMAGENET1K_V1')

        if weight_path is not None:
            state_dict = torch.load(weight_path, map_location='cpu')
            self.model.load_state_dict(state_dict)

        self.model.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(self.model.classifier[1].in_features, num_classes)
        )

    def forward(self, x):
        return self.model(x)
    
class TeethClassifier:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 model_path='D:\\华南理工\\工导2.0\\oral_ai_project\\oral_ai_project\\model\\weight\\best_model.pth',
                #  pretrained_weight_path='model/weights/efficientnet_b3_rwightman-cf984f9c.pth',
                 num_classes=6):
        if self._initialized:
            return

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 初始化模型结构
        # self.model = CustomEfficientNet(num_classes=num_classes, weight_path=pretrained_weight_path)
        self.model = CustomEfficientNet(num_classes=num_classes)
        self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.model.to(self.device)
        self.model.eval()

        # 预处理 pipeline
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # 分类名称
        self.class_names = [
            'Calculus', 'Caries', 'Gingivitis',
            'Ulcers', 'Tooth Discoloration', 'Hypodontia'
        ]

        TeethClassifier._initialized = True

    def predict(self, image_path):
        """
        输入图片路径，返回预测类别名和置信度
        """
        image = Image.open(image_path).convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)

        predicted_class = self.class_names[predicted_idx.item()]
        confidence_score = confidence.item()

        return predicted_class, confidence_score

# 对外暴露函数，符合 app.py 现有调用格式，返回字符串label
def classify_tooth(image_path):
    classifier = TeethClassifier()
    pred_class, conf = classifier.predict(image_path)
    label = f"{pred_class} (置信度: {conf:.2f})"
    print(label)
    return label


if __name__ == "__main__":
    classifier = TeethClassifier()
    result = classifier.predict("D:/zyh/teeth_dataset/Data caries/Data caries/caries orignal data set/done/2.jpg")
    print(f"Predicted class: {result['predicted_class']}, Confidence: {result['confidence']:.4f}")
