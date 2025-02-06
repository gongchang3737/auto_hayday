import subprocess
import gzip
import struct
from PIL import Image
import io
import uiautomator2 as u2
import cv2
import numpy as np
import sqlite3
# import weditor

def capture_screenshot(adb_path, mode="RawByNc"):
    """
    从 Android 模拟器获取截图，支持 RawByNc、RawWithGzip 和 Encode 模式。
    
    :param mode: 截图模式，支持 "RawByNc", "RawWithGzip", "Encode"
    :return: 截图的 PIL.Image 对象
    """
    if mode == "RawByNc":
        return capture_raw_by_nc(adb_path)
    elif mode == "RawWithGzip":
        return capture_raw_with_gzip(adb_path)
    elif mode == "Encode":
        return capture_encode(adb_path)
    else:
        raise ValueError("Unsupported mode! Use 'RawByNc', 'RawWithGzip', or 'Encode'.")

def capture_raw_by_nc(adb_path):
    """使用 RawByNc 模式从设备获取截图"""
    # ADB 命令：直接拉取屏幕的原始帧缓冲区数据
    raw_data = subprocess.run(
        [adb_path, "exec-out", "screencap"],
        stdout=subprocess.PIPE
    ).stdout

    # 转换为图像
    return convert_raw_to_image(raw_data)

def capture_raw_with_gzip(adb_path):
    """使用 RawWithGzip 模式从设备获取截图"""
    # ADB 命令：拉取 gzip 压缩的帧缓冲区数据
    raw_data = subprocess.run(
        [adb_path, "exec-out", "screencap | gzip"],
        stdout=subprocess.PIPE
    ).stdout

    # 解压 gzip 数据
    decompressed_data = gzip.decompress(raw_data)

    # 转换为图像
    return convert_raw_to_image(decompressed_data)

def capture_encode(adb_path):
    """使用 Encode 模式从设备获取截图"""
    # ADB 命令：拉取已编码的图像（PNG 格式）
    encoded_data = subprocess.run(
        [adb_path, "exec-out", "screencap -p"],
        stdout=subprocess.PIPE
    ).stdout

    # 使用 PIL 直接读取 PNG 数据
    return Image.open(io.BytesIO(encoded_data))

def convert_raw_to_image(raw_data):
    """
    将原始帧缓冲区数据转换为图像
    :param raw_data: 原始二进制数据
    :return: PIL.Image 对象
    """
    # 原始数据的前 12 字节是宽度、高度和像素格式（RGBA）
    width, height, _ = struct.unpack_from('<III', raw_data, 0)
    pixel_data = raw_data[12:]

    # 创建图像对象
    image = Image.frombytes("RGBA", (width, height), pixel_data)

    return image

def check_adb_devices(adb_path, simulator_path):
    """检查是否有设备或模拟器连接"""
    result = subprocess.run([adb_path, 'devices'], stdout=subprocess.PIPE, text=True)
    devices = result.stdout.strip().splitlines()[1:]  # 跳过第一行的标题
    connected_devices = [line for line in devices if line.strip() and not line.startswith("offline")]
    # if not connected_devices:
    #     raise RuntimeError("No devices/emulators found. Please connect a device or start an emulator.")
    print(f"Connected devices: {connected_devices}")

# 示例：使用不同的模式获取截图
if __name__ == "__main__":

    # adb_path = "D:/LDPlayer/LDPlayer9/adb.exe"
    # simulator_name = "dnplayer"
    # simulator_path = "D:/LDPlayer/LDPlayer9/dnplayer.exe"
    # check_adb_devices(adb_path, simulator_path)
    
    # try:
    #     mode = "RawByNc"  # 替换为 "RawWithGzip" 或 "Encode" 测试其他模式
    #     screenshot = capture_screenshot(adb_path, mode)
    #     screenshot.show()  # 显示截图
    #     screenshot.save(f"screenshot_{mode}.png")  # 保存截图
    #     print(f"Screenshot saved in {mode} mode!")
    # except Exception as e:
    #     print(f"Error: {e}")

    # 连接到 HayDayDB.sqlite 数据库
    db_path = "HayDayDB.sqlite"  # 请确保该文件在你的 Python 运行目录下
    conn = sqlite3.connect(db_path)  # 连接数据库
    cursor = conn.cursor()  # 创建游标对象

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())


    # 1. 获取数据库中的所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表：", tables)

    # 2. 读取某个表（假设表名是 'items'）
    table_name = "sqlite_sequence"  # 你可以把它改成数据库中实际存在的表
    cursor.execute(f"SELECT * FROM {table_name};")

    # 3. 获取所有行
    rows = cursor.fetchall()

    # 4. 打印数据
    for row in rows:
        print(row)

    # 5. 关闭数据库连接
    cursor.close()
    conn.close()

    # # 点击屏幕上的 (500, 1000) 坐标
    # tap_screen(500, 500)

