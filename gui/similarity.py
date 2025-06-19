import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import os
import shutil
import cv2
import numpy as np
from gonyou import *


# 加载预训练的 ResNet 模型
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.eval()

# 定义图像预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def load_image(file_path):
    # 加载图片
    image = Image.open(file_path).convert('RGB')
    return image

def extract_features(image):
    # 预处理图片
    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)  # 创建一个 mini-batch
    
    with torch.no_grad():
        # 提取特征
        features = model(input_batch)
    
    return features

def calculate_similarity(features1, features2):
    # 计算特征向量之间的余弦相似度
    similarity = F.cosine_similarity(features1, features2, dim=1)
    return similarity.item()


    
 
    # print(f"两张图片的相似度分数: {similarity_score:.4f}")

# 从文件夹读取图片
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path):
            images.append(img_path)
    return images

# 分组图片
def group_images(image_paths):
    grouped_images = []
    visited = [False] * len(image_paths)

    for i in range(len(image_paths)):
        if visited[i]:
            continue

        current_group = [image_paths[i]]
        visited[i] = True

        for j in range(i + 1, len(image_paths)):
            if visited[j]:
                continue
            image1 = load_image(image_paths[i])
            image2 = load_image(image_paths[j])
              # 提取特征
            features1 = extract_features(image1)
            features2 = extract_features(image2)
            
            # 计算相似度
            similarity_score = calculate_similarity(features1, features2)
    
            if similarity_score>0.8:
                current_group.append(image_paths[j])
                visited[j] = True

        grouped_images.append(current_group)

    return grouped_images


# 保存分组后的图片
def save_grouped_images(groups, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 指定输出文件夹路径
    folder = os.path.join(output_folder, "Classified")

    # 创建子文件夹，如果已经存在则不会抛出异常
    try:
        os.makedirs(folder, exist_ok=True)
        print(f"文件夹已创建或已存在: {folder}")
    except OSError as e:
        print(f"创建文件夹时发生错误")
    for idx, group in enumerate(groups):
        group_folder = os.path.join(folder, f"group_{idx + 1}")
        os.makedirs(group_folder, exist_ok=True)
        for img_path in group:
            shutil.copy(img_path, group_folder)


# 主函数
def main(input_folder, output_folder):
    try:

        image_paths = load_images_from_folder(input_folder)
        groups = group_images(image_paths)
        save_grouped_images(groups, output_folder)
        print(f"已将图片分组并保存到: {output_folder}")
        set_status(True)
    except ValueError as e:
        print(e)
        set_status(False,e)

if __name__ == "__main__":
    input_folder = r"D:/picture"  # 输入图片文件夹路径
    output_folder = r"D:/Out"  # 输出分组文件夹路径
    main(input_folder, output_folder)