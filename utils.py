import os
import sys

def input_number():
    try:
        return int(input())
    except ValueError:
        print("输入错误,请输入有效整数")  # 这里默认处理非"int"类型的异常，可根据需要细化
        return input_number()  # 递归调用自身直到获得有效输入

# 清空屏幕
def clear_screen():
    if sys.platform == "win32":
        os.system('cls')  # Windows系统
    else:
        os.system('clear')  # Unix/Linux系统和其他系统
