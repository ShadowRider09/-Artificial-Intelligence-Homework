import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from alibabacloud_imagerecog20190930.client import Client
from alibabacloud_imagerecog20190930.models import TaggingImageAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

# 阿里云配置
access_key_id = ''
access_key_secret = ''

# 确保AccessKey ID和AccessKey Secret不为空
if not access_key_id or not access_key_secret:
    raise ValueError("AccessKey ID and AccessKey Secret must be set")

# 配置AccessKey ID和AccessKey Secret
config = Config(
    access_key_id=access_key_id,
    access_key_secret=access_key_secret,
    endpoint='imagerecog.cn-shanghai.aliyuncs.com',
    region_id='cn-shanghai'
)

# 初始化Client
client = Client(config)

# 图片文件夹路径
folder_path = ""

# 创建主窗口
root = tk.Tk()
root.title("图像分类器")

# 选择文件夹按钮
def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_label.config(text=f"选择的文件夹: {folder_path}")

# 开始运行按钮
def start_processing():
    if not folder_path:
        messagebox.showwarning("警告", "请选择一个文件夹！")
        return
    
    # 创建一个新的窗口来显示结果
    result_window = tk.Toplevel(root)
    result_window.title("图像分类结果")
    
    # 创建一个Canvas和Scrollbar
    canvas = tk.Canvas(result_window)
    scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 遍历文件夹中的所有图片文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            result = process_image(file_path)
            if result:
                # 显示图片
                img = Image.open(file_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                
                label_img = tk.Label(scrollable_frame, image=img_tk)
                label_img.image = img_tk
                label_img.pack(pady=5)
                
                # 显示类别和置信度
                label_text = tk.Label(scrollable_frame, text=f"类别: {result['Value']}, 置信度: {result['Confidence']}%")
                label_text.pack(pady=5)

# 提取最高置信度的类别和置信度
def get_highest_confidence_tag(response):
    response_dict = response.to_map()
    tags = response_dict['body']['Data']['Tags']
    highest_confidence_tag = max(tags, key=lambda x: x['Confidence'])
    return highest_confidence_tag

# 处理单个图片
def process_image(file_path):
    img = open(file_path, 'rb')
    #场景二：使用任意可访问的url
    tagging_image_request = TaggingImageAdvanceRequest()
    tagging_image_request.image_urlobject = img
    runtime = RuntimeOptions()
    
    try:
        response = client.tagging_image_advance(tagging_image_request, runtime)
        highest_confidence_tag = get_highest_confidence_tag(response)
        return highest_confidence_tag
    except Exception as error:
        print(f"Error processing {file_path}: {error}")
        return None

# 选择文件夹按钮
select_button = tk.Button(root, text="选择文件夹", command=select_folder)
select_button.pack(pady=10)

# 文件夹路径显示
folder_label = tk.Label(root, text="选择的文件夹: ")
folder_label.pack(pady=10)

# 开始运行按钮
start_button = tk.Button(root, text="开始运行", command=start_processing)
start_button.pack(pady=10)

# 运行主循环
root.mainloop()