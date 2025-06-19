import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn
import os
import shutil
def main(input_folder, output_dir):


# 设备设置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 加载模型
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 22)  # 确保输出层与训练时一致
    model.load_state_dict(torch.load('resnet18_classified.pth', map_location=device, weights_only=True))
    model.eval()  # 设置为评估模式

    # 定义与训练时相同的预处理变换
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 类别列表
    classes = [
        'Cultural landscape', 'Food feature', 'Food panorama', 'Group photo', 
        'Large group photo', 'Modern architecture', 'Multiple selfie', 'Portrait photo', 
        'Sunset glow', 'Text picture', 'cake', 'class', 'class with PPT', 'flowers', 
        'lakes', 'mountain', 'pet', 'seaway', 'selfie', 'sky', 'steppe', 'trees'
    ]

    # 创建输出文件夹
    # output_dir = r'C:\Users\tianz\Desktop\output_image'
    # os.makedirs(output_dir, exist_ok=True)

    # 从文件夹读取图片
    def load_images_from_folder(folder):
        images = []
        for filename in os.listdir(folder):
            img_path = os.path.join(folder, filename)
            if os.path.isfile(img_path):
                images.append(img_path)
        return images

    # 加载并处理多张测试图像
   
    image_paths = load_images_from_folder(input_folder)

    for image_path in image_paths:
        # 加载单张测试图像
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)  # 添加batch维度

        # 移动到合适的设备
        image_tensor = image_tensor.to(device)
        model = model.to(device)

        # 进行预测
        with torch.no_grad():  # 不需要计算梯度
            output = model(image_tensor)
            probabilities = torch.softmax(output, dim=1)  # 转换为概率分布
            max_prob, predicted = torch.max(probabilities, 1)

        # 输出预测结果和最大概率
        predicted_class = classes[predicted.item()]
        max_probability = max_prob.item()


        # 过滤概率小于0.85的图片
        if max_probability >= 0.9:
            # 确保目标文件夹存在
            target_folder = os.path.join(output_dir, predicted_class)
            os.makedirs(target_folder, exist_ok=True)

            # 将图片保存到对应的文件夹
            shutil.copy(image_path, target_folder)




