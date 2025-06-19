
status = False  # 初始状态为False，表示操作未成功

baocuo=""

outFolder=""

def set_Folder(val=""):
    global outFolder
    outFolder=val
def set_status(value,value2=""):
    global status
    global baocuo

    status = value
    baocuo = value2

def get_status():
    return status

def get_baocuo():
    return baocuo

def get_outFolder():
    return outFolder