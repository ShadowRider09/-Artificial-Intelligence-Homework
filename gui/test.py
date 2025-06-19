from PyQt6.QtGui import QFont,QPixmap
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import sys
import os


import requests
from PIL import Image, ImageTk
from volcengine.visual.VisualService import VisualService
from volcenginesdkarkruntime import Ark
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from dashscope import ImageSynthesis
from dotenv import load_dotenv

import similarity
from gonyou import*
import part_two

load_dotenv()
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is not set")
def open1(path):
    if sys.platform == 'win32':
        os.startfile(path)
    if sys.platform == 'darwin':
        os.system(f"open '{path}'")

class preWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(600, 350, 500, 300)
        self.setWindowTitle("使用指南")
        label = QLabel("提示文本",self)
class AlertWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(600, 350, 500, 300)
        self.setWindowTitle("警告")
        self.label = QLabel("", self)

class Image(QWidget):
    def __init__(self,path):
        super().__init__()
        self.setGeometry(600, 350, 500, 300)
        self.path = path
        self.initUI()

        def initUI(self):
            self.setWindowTitle('Image Browser')
            self.setGeometry(100, 100, 800, 600)
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setGeometry(0, 0, 800, 600)
            self.scroll_area.setWidgetResizable(True)
            self.container = QWidget()
            self.layout = QVBoxLayout(self.container)
            self.container.setLayout(self.layout)
            self.scroll_area.setWidget(self.container)
            self.load_images()
            self.delete_button = QPushButton("Delete Selected", self)
            self.delete_button.clicked.connect(self.delete_images)
            self.layout.addWidget(self.delete_button)

    def load_images(self):
        images = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for image_path in images:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                label = QLabel(self)
                label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                label.setStyleSheet("QLabel { border: 1px solid black; }")
                checkbox = QCheckBox(self)
                checkbox.image_path = image_path  # Store the image path in the checkbox
                layout = QHBoxLayout()
                layout.addWidget(label)
                layout.addWidget(checkbox)
                self.layout.addLayout(layout)
    def delete_images(self):
        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isChecked():
                try:
                    os.remove(checkbox.image_path)
                except Exception as e:
                    print(f"Error deleting {checkbox.image_path}: {e}")
        self.close()


class ImageBrowser(QWidget):
    def __init__(self, folder_path,infolder,jueding):
        super().__init__()
        self.jueding = jueding
        self.folder_path = folder_path
        self.infolder = infolder
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Browser')
        self.setGeometry(100, 100, 800, 600)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 0, 800, 600)
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.container.setLayout(self.layout)
        self.scroll_area.setWidget(self.container)
        self.load_images()
        self.delete_button = QPushButton("Delete Selected", self)
        self.delete_button.clicked.connect(self.delete_images)
        self.layout.addWidget(self.delete_button)

    def load_images(self):
        way = os.path.join(self.folder_path, "Classified")
        items = os.listdir(way)
        subfolders = [item for item in items if os.path.isdir(os.path.join(way, item))]
        for subfolder in subfolders:
            way1 = os.path.join(way, subfolder)
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
            count = sum(os.path.splitext(filename)[1].lower() in image_extensions for filename in os.listdir(way1))
            if count >= 2:
                way2 = os.path.join(way, subfolder)
                images = [os.path.join(way2, f) for f in os.listdir(way2) if f.endswith(('.png', '.jpg', '.jpeg'))]
                for image_path in images:
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        label = QLabel(self)
                        label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                        label.setStyleSheet("QLabel { border: 1px solid black; }")
                        checkbox = QCheckBox(self)
                        checkbox.image_path = image_path  # Store the image path in the checkbox
                        layout = QHBoxLayout()
                        layout.addWidget(label)
                        layout.addWidget(checkbox)
                        self.layout.addLayout(layout)


    def delete_images(self):
        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isChecked():
                try:
                    if self.jueding:
                        file_name = os.path.basename(checkbox.image_path)
                        os.remove(os.path.join(self.infolder, file_name))

                    os.remove(checkbox.image_path)
                except Exception as e:
                    print(f"Error deleting {checkbox.image_path}: {e}")
        self.close()

class MainWindow(QWidget):
    judge=0#判断是否确认
    judge_up=0#判断上传路径是否选择
    judge_down=0#判断导出路径是否选择

    similarity.input_folder=""
    similarity.output_folder=""

#################################################################
    judge1 = 0  # 判断是否确认
    judge_up1 = 0  # 判断上传路径是否选择
    judge_down1 = 0  # 判断导出路径是否选择

    input_folder1 = ""
    output_folder1 = ""

    re=[]
##########################################################
    folder=""
    url=""
    xuanze=0

    shifolder=""
    shixuanze=0

############################################################
    def __init__(self):
        #主窗口设置
        super().__init__()
        self.setGeometry(350, 200, 1000, 650)
        self.setWindowTitle("图片查重删除系统")
        self.cebian()
        self.jiemian1()
        self.jiemain2()
        self.jiemian3()

        self.btn00=QPushButton("使用指南",self)
        self.btn00.setGeometry(0,610,100,40)
        self.btn00.clicked.connect(self.tishi)
        self.btn00.setStyleSheet("QPushButton{background-color:green;color:white;}"
                                 "QPushButton:hover{color:black;}")


        #创建按钮

    #创建侧边栏
    def cebian(self):
        self.inBtn1=QPushButton("图片查重",self)
        self.inBtn1.setGeometry(0,0,180,60)
        self.inBtn1.setStyleSheet("QPushButton{border:none;background-color:white}"
                                  "QPushButton:hover{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn1.setFont(QFont("",14))
        self.inBtn1.clicked.connect(self.qiehuan1)

        self.inBtn2=QPushButton("图片分类",self)
        self.inBtn2.setGeometry(0,60,180,60)
        self.inBtn2.setStyleSheet("QPushButton{border:none;}")
        self.inBtn2.setStyleSheet("QPushButton{border:none;background-color:white}"
                                  "QPushButton:hover{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn2.setFont(QFont("", 14))
        self.inBtn2.clicked.connect(self.qiehuan2)

        self.inBtn3=QPushButton("AI生成",self)
        self.inBtn3.setGeometry(0,120,180,60)
        self.inBtn3.setStyleSheet("QPushButton{border:none;background-color:white}"
                                  "QPushButton:hover{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn3.setFont(QFont("",14))
        self.inBtn3.clicked.connect(self.qiehuan3)

        self.h_line = QLabel("",self)
        self.h_line.setStyleSheet("background-color: black; width: 1px;")
        self.h_line.setGeometry(0,60,180,1)

        self.h_line1 = QLabel("",self)
        self.h_line1.setStyleSheet("background-color: black; width: 1px;")
        self.h_line1.setGeometry(0,120,180,1)

        self.h_line2 = QLabel("",self)
        self.h_line2.setStyleSheet("background-color: black; width: 1px;")
        self.h_line2.setGeometry(0,180,180,1)

        self.w_line = QLabel("",self)
        self.w_line.setStyleSheet("background-color: black; width: 1px;")
        self.w_line.setGeometry(180,0,1,650)

    #侧边栏切换
    def qiehuan1(self):
        self.inBtn1.setStyleSheet("QPushButton{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn2.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        self.inBtn3.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        for i in self.yuansu1:
            i.show()
        for i in self.yuansu2:
            i.hide()
        for i in self.yuansu3:
            i.hide()
    def qiehuan2(self):
        self.inBtn2.setStyleSheet("QPushButton{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn1.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        self.inBtn3.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        for i in self.yuansu1:
            i.hide()
        for i in self.yuansu2:
            i.show()
        for i in self.yuansu3:
            i.hide()
        self.btn231.hide()

    def qiehuan3(self):
        self.inBtn3.setStyleSheet("QPushButton{border:none;background-color:rgb(200, 230, 240);color:green}")
        self.inBtn1.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        self.inBtn2.setStyleSheet("QPushButton{border:none;background-color:white;color:black}")
        for i in self.yuansu1:
            i.hide()
        for i in self.yuansu2:
            i.hide()
        for i in self.yuansu3:
            i.show()

##########################################################################
    #界面1
    def jiemian1(self):
        #上传文件夹按钮
        self.btn1=QPushButton("上传文件",self)
        self.btn1.setGeometry(230, 70, 176, 140)
        self.btn1.clicked.connect(self.up)

        #导出文件夹
        self.btn2=QPushButton("选择导出文件夹",self)
        self.btn2.setGeometry(405, 70, 176, 140)
        self.btn2.clicked.connect(self.down)

        #开始按钮
        self.btn3 = QPushButton("开始", self)
        self.btn3.setGeometry(230,220,352,180)
        self.btn3.clicked.connect(self.start)

        #确认按钮
        self.btn4 = QPushButton("未确认",self)
        self.btn4.setGeometry(600,70,70,332)
        self.btn4.clicked.connect(self.queren)

        self.btn5=QPushButton("删除",self)
        self.btn5.setGeometry(230,420,440,80)
        self.btn5.clicked.connect(self.shanchu)



        self.btn7=QPushButton("打开文件夹",self)
        self.btn7.setGeometry(230,570,130,40)
        self.btn7.clicked.connect(self.dakai)

        #创建文本

        #上传文本
        self.label=QLabel("上传路径",self)
        self.label.setGeometry(790,81,90,30)
        self.label.setFont(QFont("",16))

        self.label1=QLabel("导出路径",self)
        self.label1.setGeometry(790,330,90,30)
        self.label1.setFont(QFont("",16))

        self.label2=QLabel("未选择",self)
        self.label2.setGeometry(700,165,350,50)

        #导出文本
        self.label3=QLabel("未选择",self)
        self.label3.setGeometry(700,400,350,50)

        #进度文本
        self.label4=QLabel("",self)
        self.label4.setGeometry(400,530,270,70)

        self.h_line = QLabel("",self)
        self.h_line.setStyleSheet("background-color: black; width: 1px;")
        self.h_line.setGeometry(670,310,330,1)

        self.yuansu1={self.btn1,self.btn2,self.btn3,self.btn4,self.btn5,self.btn7,self.label,self.label1,self.label2
                     ,self.label3,self.label4,self.h_line}

        for i in self.yuansu1:
            i.hide()

    #界面1事件函数

    #上传
    def up(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_selected:
            self.judge_up=1
            self.input_folder = folder_selected
            self.label2.setText(f"已选择上传路径{self.input_folder}")
            self.label2.setStyleSheet("background-color:white")
            self.label3.setText("未选择")
            self.label4.setText("")
            self.label4.setStyleSheet("background-color:white")

    #导出
    def down(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_selected:
            self.judge_down=1
            self.output_folder = folder_selected
            set_Folder(folder_selected)
            self.chuan=folder_selected
            self.label3.setText(f"已选择导出路径{self.output_folder}")
            self.label3.setStyleSheet("background-color:white")
    #确认按钮
    def queren(self):
        if self.judge:
            self.judge=0
            self.btn4.setText("未确认")
        else:
            self.judge=1
            self.btn4.setText("已确认")
            self.btn4.setStyleSheet("background-color:white")

    #开始
    def start(self):
        if self.judge&self.judge_up&self.judge_down:
            #调用执行
            similarity.main(self.input_folder,self.output_folder)
            if get_status():
                self.label4.setText(f"导出成功，导出位置为{self.output_folder+'/Classified'}")
                self.label4.setStyleSheet("background-color:rgb(200, 230, 240);color:red")
            else:
                self.alert2 = AlertWindow()
                self.alert2.label.setText(f"导出失败{get_status()}")
                self.alert2.show()

        else:
            #报错弹窗
            self.alert=AlertWindow()
            cuo=""
            if self.judge==0:
                self.btn4.setStyleSheet("background-color:brown")
                cuo+="你还没有确认 "
            if self.judge_up==0:
                self.label2.setStyleSheet("background-color:red")
                cuo+="未选择上传路径 "
            if self.judge_down==0:
                self.label3.setStyleSheet("background-color:red")
                cuo+="未选择导出路径 "
            self.alert.label.setText(cuo)
            self.alert.show()

    def dakai(self):
        open1(self.output_folder + "/Classified")

    def tishi(self):
        self.pre=preWindow()
        self.pre.show()

    #删除
    def shanchu(self):
        self.shan=ImageBrowser(self.output_folder,self.input_folder,1)
        self.shan.show()




#################################################################################################
    #界面2
    def jiemain2(self):
        self.btn21=QPushButton("选择上传文件夹",self)
        self.btn21.setGeometry(240,250,130,120)
        self.btn21.clicked.connect(self.up2)

        self.label23=QLabel("",self)
        self.label23.setGeometry(240,200,100,40)
        self.label23.setFont(QFont("DengXian", 14))

        self.btn22=QPushButton("选择导出文件夹",self)
        self.btn22.setGeometry(400,150,170,160)
        self.btn22.clicked.connect(self.down2)

        self.label24 = QLabel("", self)
        self.label24.setGeometry(400,100,150,40)
        self.label24.setFont(QFont("DengXian", 14))

        self.btn23=QPushButton("开始",self)
        self.btn23.setGeometry(380,340,110,100)
        self.btn23.clicked.connect(self.queren2)

        self.btn24=QPushButton("打开导出文件夹",self)
        self.btn24.setGeometry(270,400,90,90)
        self.btn24.clicked.connect(self.dakai1)

        self.label21=QLabel("分类结果",self)
        self.label21.setGeometry(760,50,120,30)
        self.label21.setFont(QFont("DengXian",16))

        self.label22=QLabel("分类成功",self)
        self.label22.setGeometry(390,510,120,30)
        self.label22.setFont(QFont("DengXian", 16))
        self.label22.hide()

        self.w_line1 = QLabel("", self)
        self.w_line1.setStyleSheet("background-color: black; width: 1px;")
        self.w_line1.setGeometry(595, 0, 1, 650)

        self.fenlei()

        self.yuansu2={self.btn21,self.btn22,self.btn23,self.btn24,self.btn210,self.btn211,self.btn212,self.btn213,self.btn214,self.btn215,self.btn216,
                          self.btn217,self.btn218,self.btn219,self.btn220,self.btn221,self.btn222,self.btn223,self.btn224,self.btn225,
                          self.btn226,self.btn227,self.btn228,self.btn229,self.btn230,self.btn231,self.w_line1,self.label21,self.label23,self.label24}

        self.tempyuan=[self.btn210,self.btn230,self.btn211,self.btn220,self.btn226,self.btn222,self.btn227,self.btn221,
                       self.btn217,self.btn225,self.btn218,self.btn223,self.btn224,self.btn219,self.btn212,self.btn213,self.btn228,self.btn214
                       ,self.btn229,self.btn231,self.btn215,self.btn216]

        for i in self.yuansu2:
            i.hide()

    #分类结果选择
    def fenlei(self):
        self.btn210=QPushButton("人文景观",self)
        self.btn210.setGeometry(680,100,100,35)
        self.btn210.clicked.connect(self.fenlei0)
        self.btn211=QPushButton("美食",self)
        self.btn211.setGeometry(620,140,100,35)
        self.btn211.clicked.connect(self.fenlei1)
        self.btn212=QPushButton("湖泊",self)
        self.btn212.setGeometry(680,180,100,35)
        self.btn212.clicked.connect(self.fenlei2)
        self.btn213=QPushButton("山脉",self)
        self.btn213.setGeometry(620,220,100,35)
        self.btn213.clicked.connect(self.fenlei3)
        self.btn214=QPushButton("海湾",self)
        self.btn214.setGeometry(680,260,100,35)
        self.btn214.clicked.connect(self.fenlei4)
        self.btn215=QPushButton("草原",self)
        self.btn215.setGeometry(620,300,100,35)
        self.btn215.clicked.connect(self.fenlei5)
        self.btn216=QPushButton("森林",self)
        self.btn216.setGeometry(680,340,100,35)
        self.btn216.clicked.connect(self.fenlei6)
        self.btn217=QPushButton("落日",self)
        self.btn217.setGeometry(620,380,100,35)
        self.btn217.clicked.connect(self.fenlei7)
        self.btn218=QPushButton("天空",self)
        self.btn218.setGeometry(680,420,100,35)
        self.btn218.clicked.connect(self.fenlei8)
        self.btn219=QPushButton("花朵",self)
        self.btn219.setGeometry(620,460,100,35)
        self.btn219.clicked.connect(self.fenlei9)
        self.btn220=QPushButton("集体照",self)
        self.btn220.setGeometry(680,500,100,35)
        self.btn220.clicked.connect(self.fenlei10)
        self.btn221=QPushButton("单人照",self)
        self.btn221.setGeometry(820,140,100,35)
        self.btn221.clicked.connect(self.fenlei11)
        self.btn222=QPushButton("建筑",self)
        self.btn222.setGeometry(880,180,100,35)
        self.btn222.clicked.connect(self.fenlei12)
        self.btn223=QPushButton("课堂",self)
        self.btn223.setGeometry(820,220,100,35)
        self.btn223.clicked.connect(self.fenlei13)
        self.btn224=QPushButton("PPT",self)
        self.btn224.setGeometry(880,260,100,35)
        self.btn224.clicked.connect(self.fenlei14)
        self.btn225=QPushButton("文本",self)
        self.btn225.setGeometry(820,300,100,35)
        self.btn225.clicked.connect(self.fenlei15)

##########################################################
        self.btn226=QPushButton("大型集体照",self)
        self.btn226.setGeometry(880,340,100,35)
        self.btn226.clicked.connect(self.fenlei16)
        self.btn227=QPushButton("多人自拍",self)
        self.btn227.setGeometry(820,380,100,35)
        self.btn227.clicked.connect(self.fenlei17)
        self.btn228=QPushButton("宠物",self)
        self.btn228.setGeometry(880,420,100,35)
        self.btn228.clicked.connect(self.fenlei18)
        self.btn229=QPushButton("自拍",self)
        self.btn229.setGeometry(820,460,100,35)
        self.btn229.clicked.connect(self.fenlei19)
        self.btn230=QPushButton("特色美食",self)
        self.btn230.setGeometry(880,500,100,35)
        self.btn230.clicked.connect(self.fenlei20)
        self.btn231=QPushButton("天空",self)
        self.btn231.setGeometry(880,100,100,35)
        self.btn231.hide()

    #界面2事件函数
    def up2(self):
        self.label22.hide()
        self.label24.setText("")
        for i in self.tempyuan:
            i.setEnabled(True)
            i.setStyleSheet("background-color: white;color:black;")
        self.btn24.setStyleSheet("background-color: white;color:black;")
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_selected:
            self.judge_up1 = 1
            self.input_folder1 = folder_selected
            self.label23.setText(self.input_folder1)
            self.btn21.setStyleSheet("QPushButton {background-color: green;color:white;}")

    def down2(self):
        self.label22.hide()
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_selected:
            self.judge_down1 = 1
            self.output_folder1 = folder_selected
            self.label24.setText(self.output_folder1)
            self.btn22.setStyleSheet("QPushButton {background-color: green;color:white;}")

    def queren2(self):
        if self.judge_up1==1&self.judge_down1==1:
            self.re=[]
            part_two.main(self.input_folder1,self.output_folder1)
            self.btn21.setStyleSheet("QPushButton {background-color:white;color:black;}")
            self.btn22.setStyleSheet("QPushButton {background-color:white;color:black;}")
            self.btn24.setStyleSheet("QPushButton {background-color:green;color:white;}")
            self.label22.show()

        items = os.listdir(self.output_folder1)
        subfolders = [item for item in items if os.path.isdir(os.path.join(self.output_folder1, item))]
        print(subfolders)
        classes = ['Cultural landscape','Food feature','Food panorama','Group photo','Large group photo','Modern architecture','Multiple selfie', 'Portrait photo','Sunset glow', 'Text picture', 'cake', 'class', 'class with PPT', 'flowers','lakes', 'mountain', 'pet', 'seaway', 'selfie', 'sky', 'steppe', 'trees']
        print(classes)
        for yuan in classes:
            self.ce=0
            for i in subfolders:
                if i==yuan:
                    self.ce=1

            if self.ce==1:
                self.re.append(True)
            else:
                self.re.append(False)
        wei=0
        for i in self.re:
            if i:
                self.tempyuan[wei].setStyleSheet("QPushButton{background-color:green;color:white;}")
            else:
                self.tempyuan[wei].setEnabled(False)
                self.tempyuan[wei].setStyleSheet("QPushButton{background-color:brown;color:brown;}")
            wei+=1



    def dakai1(self):
        open1(self.output_folder1)

    def fenlei0(self):
        open1(self.output_folder1+"/Cultural landscape")
    def fenlei1(self):
        open1(self.output_folder1 + "/Food panorama")
    def fenlei2(self):
        open1(self.output_folder1+"/Lakes")
    def fenlei3(self):
        open1(self.output_folder1+"/mountain")
    def fenlei4(self):
        open1(self.output_folder1+"/seaway")
    def fenlei5(self):
        open1(self.output_folder1+"/steppe")
    def fenlei6(self):
        open1(self.output_folder1+"/trees")
    def fenlei7(self):
        open1(self.output_folder1+"/Sunset glow")
    def fenlei8(self):
        open1(self.output_folder1+"/Sky")
    def fenlei9(self):
        open1(self.output_folder1+"/flowers")
    def fenlei10(self):
        open1(self.output_folder1+"/Group photo")
    def fenlei11(self):
        open1(self.output_folder1+"/Portrait photo")
    def fenlei12(self):
        open1(self.output_folder1+"/Modern architecture")
    def fenlei13(self):
        open1(self.output_folder1+"/class")
    def fenlei14(self):
        open1(self.output_folder1+"/class with PPT")
    def fenlei15(self):
        open1(self.output_folder1+"/Text picture")
    def fenlei16(self):
        open1(self.output_folder1+"/Large group photo")
    def fenlei17(self):
        open1(self.output_folder1+"/Multiple selfie")
    def fenlei18(self):
        open1(self.output_folder1+"/pet")
    def fenlei19(self):
        open1(self.output_folder1+"/Selfie")

    def fenlei20(self):
        open1(self.output_folder1 + "/Food feature")

    def fenlei21(self):
        open1(self.output_folder1 + "/Sky")
#############################################################################
    def jiemian3(self):
        self.text=QTextEdit(self)
        self.text.setPlaceholderText("请输入关键词")
        self.text.setGeometry(290,110,300,140)

        self.btn30=QPushButton("选择输出路径",self)
        self.btn30.setGeometry(260,290,145,145)
        self.btn30.clicked.connect(self.shanchu3)

        self.btn31=QPushButton("豆包AI生成",self)
        self.btn31.setGeometry(430,400,145,145)
        self.btn31.clicked.connect(self.kaishi)

        self.btn32=QPushButton("打开导出文件夹",self)
        self.btn32.setGeometry(300,470,100,100)
        self.btn32.clicked.connect(self.dakai3)

        self.label30=QLabel("",self)
        self.label30.setGeometry(420,300,160,60)

        self.w_line3 = QLabel("", self)
        self.w_line3.setStyleSheet("background-color: black; width: 1px;")
        self.w_line3.setGeometry(610, 300, 1, 230)

        self.btn33 = QPushButton("选择输出文件夹", self)
        self.btn33.setGeometry(640, 110, 100, 100)
        self.btn33.clicked.connect(self.shanchu4)

        self.btn34 = QPushButton("通义AI生成", self)
        self.btn34.setGeometry(630, 240, 150, 150)
        self.btn34.clicked.connect(self.kaishi4)

        self.btn35 = QPushButton("打开导出文件夹", self)
        self.btn35.setGeometry(810, 200, 100, 100)
        self.btn35.clicked.connect(self.dakai4)

        self.label31=QLabel("",self)
        self.label30.setGeometry(760,120,160,50)

        self.yuansu3=[self.text,self.btn30,self.btn31,self.btn32,self.label30,self.w_line3,self.btn33,self.btn34,self.btn35,self.label31]
        for i in self.yuansu3:
            i.hide()


    def dakai3(self):
        directory = os.path.dirname(self.folder)
        open1(directory)

    def dakai4(self):
        open1(self.shifolder)

    def shanchu3(self):
        global save_path
        folder_selected = save_path = QFileDialog.getSaveFileName(self, "Save File", "", "JPEG files (*.jpg);;PNG files (*.png);;All files (*.*)")[0]
        if folder_selected:
            self.xuanze = 1
            self.folder = folder_selected
            self.label30.setText(self.folder)
            self.btn31.setStyleSheet("QPushButton {background-color: green;color:white;}")

    def shanchu4(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_selected:
            self.shixuanze = 1
            self.shifolder = folder_selected
            self.label31.setText(self.shifolder)
            self.btn34.setStyleSheet("QPushButton {background-color: green;color:white;}")

    def kaishi4(self):
        prompt=self.text.toPlainText()
        try:
            rsp = ImageSynthesis.call(
                model=ImageSynthesis.Models.wanx_v1,
                prompt=prompt,
                n=2,
                size='1024*1024',
                api_key=DASHSCOPE_API_KEY
            )

            if rsp.status_code == HTTPStatus.OK:
                self.btn34.setStyleSheet("QPushButton {background-color: white;color:black;}")
                for result in rsp.output.results:
                    file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                    file_path = f"{self.shifolder}/{file_name}"
                    with open(file_path, 'wb') as f:
                        f.write(requests.get(result.url).content)

            else:
                self.label31.setText(f"请求失败，状态码: {rsp.status_code}, 代码: {rsp.code}, 消息: {rsp.message}")
        except Exception as e:
            self.label31.setText( str(e))


    def kaishi(self):
        if self.xuanze:
            self.btn31.setStyleSheet("QPushButton {background-color: white;color:black;}")
            self.generate_and_download_image()
        else:
            self.label30.setText("未选择导出路径")
            self.label30.setStyleSheet("background-color:red;color:white")

    def download_image(self,url, save_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path,"wb") as file:
                    file.write(response.content)
                return save_path
            else:
                self.label30.setText(f"请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            import traceback
            print(f"请求错误: {traceback.format_exc()}")
            return None

    def generate_and_download_image(self):


        prompt = self.text.toPlainText()
        if not prompt or not self.folder:
            self.label30.setText("请输入提示词并选择保存路径")
            self.label30.setStyleSheet("background-color:red;color:white")
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
                image_path = self.download_image(image_url, self.folder)
                if image_path:
                    directory = os.path.dirname(image_path)
                    self.chuan = Image(directory)
                    self.chuan.show()
            else:
                self.label30.setText("请求成功，但没有找到有效的图像 URL")
        except Exception as e:
            self.label30.setText(f"请求过程中发生错误: {e}")










app = QApplication(sys.argv)
#设置提示弹窗

#设置主窗口
mawindow = MainWindow()

mawindow.show()



sys.exit(app.exec())
