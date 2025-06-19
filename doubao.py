# coding:utf-8
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from PIL import Image, ImageTk
from volcenginesdkarkruntime import Ark

def select_save_path():
    global save_path
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])
    if save_path:
        save_path_label.config(text=f"保存路径: {save_path}")
    else:
        save_path_label.config(text="未选择保存路径")

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return save_path
        else:
            messagebox.showerror("失败", f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        messagebox.showerror("错误", f"请求过程中发生错误: {e}")
        return None

def show_image_in_new_window(image_path):
    new_window = tk.Toplevel(root)
    new_window.title("生成的图片")
    img = Image.open(image_path)
    img = img.resize((512, 512), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(new_window, image=img_tk)
    label.image = img_tk
    label.pack(pady=10)

def generate_and_download_image():
    prompt = prompt_entry.get()
    if not prompt or not save_path:
        messagebox.showwarning("警告", "请输入提示词并选择保存路径")
        return


    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.environ.get("ARK_API_KEY"),
    )

    try:
        imagesResponse = client.images.generate(
            model="doubao-seedream-3-0-t2i-250415",
            prompt=prompt
        )
        if imagesResponse.data and imagesResponse.data[0].url:
            image_url = imagesResponse.data[0].url
            image_path = download_image(image_url, save_path)
            if image_path:
                show_image_in_new_window(image_path)
        else:
            messagebox.showerror("失败", "请求成功，但没有找到有效的图像 URL")
    except Exception as e:
        messagebox.showerror("错误", f"请求过程中发生错误: {e}")

# 创建主窗口
root = tk.Tk()
root.title("图像生成器")

prompt_label = tk.Label(root, text="输入提示词:")
prompt_label.pack(pady=5)
prompt_entry = tk.Entry(root, width=50)
prompt_entry.pack(pady=5)

select_path_button = tk.Button(root, text="选择保存路径", command=select_save_path)
select_path_button.pack(pady=10)

save_path_label = tk.Label(root, text="未选择保存路径")
save_path_label.pack(pady=5)

generate_button = tk.Button(root, text="生成图片", command=generate_and_download_image)
generate_button.pack(pady=20)

root.mainloop()