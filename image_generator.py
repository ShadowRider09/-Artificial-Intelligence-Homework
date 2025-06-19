import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from PIL import Image, ImageTk
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
from dotenv import load_dotenv
import os

load_dotenv()
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is not set")

class ImageGeneratorApp:
    def __init__(self, root):

    
        self.root = root
        self.root.title("图像生成器")
        self.root.geometry('500x300') 
        # 创建输入框和按钮
        self.prompt_label = tk.Label(root, text="请输入你想生成的图像:")
        self.prompt_label.pack()
        
        self.prompt_entry = tk.Entry(root, width=50)
        self.prompt_entry.pack()
        
        self.generate_button = tk.Button(root, text="生成图像", command=self.generate_images)
        self.generate_button.pack()
        
        self.save_path_button = tk.Button(root, text="选择保存路径", command=self.select_save_path)
        self.save_path_button.pack()
        
        self.save_path = "./"
        
    def __check_api(self):
        pass

    def select_save_path(self):
        self.save_path = filedialog.askdirectory()
        if not self.save_path:
            self.save_path = "./"

    def generate_images(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            messagebox.showerror("错误", "请输入提示！")
            return
        
        try:
            rsp = ImageSynthesis.call(
                model=ImageSynthesis.Models.wanx_v1,
                prompt=prompt,
                n=2,
                size='1024*1024',
                api_key=DASHSCOPE_API_KEY
            )
            
            if rsp.status_code == HTTPStatus.OK:
                self.display_images(rsp.output.results)
                self.save_images(rsp.output.results)
            else:
                messagebox.showerror("错误", f"请求失败，状态码: {rsp.status_code}, 代码: {rsp.code}, 消息: {rsp.message}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def display_images(self, results):
        if len(results) < 2:
            messagebox.showerror("错误", "生成的图片数量不足2张！")
            return
        
        # 创建一个新的 Toplevel 窗口来显示图片
        image_window = tk.Toplevel(self.root)
        image_window.title("生成的图片")
        
        # 下载并显示第一张图片
        image1_url = results[0].url
        image1 = Image.open(requests.get(image1_url, stream=True).raw)
        image1.thumbnail((400, 400))
        photo1 = ImageTk.PhotoImage(image1)
        
        # 下载并显示第二张图片
        image2_url = results[1].url
        image2 = Image.open(requests.get(image2_url, stream=True).raw)
        image2.thumbnail((400, 400))
        photo2 = ImageTk.PhotoImage(image2)
        
        # 创建两个标签来显示图片
        label1 = tk.Label(image_window, image=photo1)
        label1.image = photo1  # 保持引用，防止垃圾回收
        label1.grid(row=0, column=0, padx=10, pady=10)
        
        label2 = tk.Label(image_window, image=photo2)
        label2.image = photo2  # 保持引用，防止垃圾回收
        label2.grid(row=0, column=1, padx=10, pady=10)

    def save_images(self, results):
        for result in results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            file_path = f"{self.save_path}/{file_name}"
            with open(file_path, 'wb') as f:
                f.write(requests.get(result.url).content)
            print(f"保存图片: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageGeneratorApp(root)
    root.mainloop()