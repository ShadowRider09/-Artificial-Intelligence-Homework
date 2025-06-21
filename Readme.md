随便写了一个readme，老师要是想要在本地运行的话按照这个流程走就行了

# 智能图片处理与AI生成系统

本项目是一个基于 PyQt6 的图片智能处理平台，集成了图片查重分组、图片多类别细分、AI图片生成等功能

## 功能简介

- **图片查重分组**  
  利用深度学习模型（ResNet50）提取图片特征，自动分组相似图片，支持批量删除。

- **图片多类别细分**  
  使用自训练的 ResNet18 分类模型，将图片自动细分为22个类别，并按类别归档。

- **AI图片生成**  
  集成火山引擎豆包大模型，输入关键词即可生成高质量图片，并支持本地保存和浏览。

## 目录结构

```
gui/
├── gonyou.py           # 全局状态管理
├── part_two.py         # 图片多类别细分
├── similarity.py       # 图片查重分组
├── test.py             # 主界面与功能入口（PyQt6）
├── resnet18_classified.pth  # 细分类模型权重
├── .env                # 环境变量配置（如API Key）
└── ...
```

## 依赖环境

- Python 3.8+
- PyQt6
- torch, torchvision
- pillow
- requests
- volcengine-python-sdk[ark]（火山引擎豆包AI）
- 其它依赖详见 `requirements.txt`

## 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **准备模型文件**
   - 将 `resnet18_classified.pth` 放在 `gui/` 目录下。

3. **配置API Key**
   - 在 `gui/.env` 文件中填写你的豆包API Key（ARK_API_KEY）。

4. **运行主程序**
   ```bash
   cd gui
   python test.py
   ```
