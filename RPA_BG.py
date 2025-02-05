import pygetwindow as gw
import win32gui
import win32ui
import win32con
from PIL import Image

def get_screenshot_by_title(window_title):
    # 获取窗口句柄
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        raise Exception(f"窗口标题 '{window_title}' 未找到")

    # 获取窗口大小
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    print('窗口宽度为{0}，窗口高度为{1}。'.format(width,height))

    # 获取窗口设备上下文
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # 创建位图对象
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bmp)

    # 将窗口内容拷贝到位图
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # 转换为图像
    bmp_info = bmp.GetInfo()
    bmp_str = bmp.GetBitmapBits(True)
    image = Image.frombuffer(
        'RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']),
        bmp_str, 'raw', 'BGRX', 0, 1
    )

    # # 清理
    # win32gui.ReleaseDC(hwnd, hwnd_dc)
    # save_dc.DeleteDC()
    # mfc_dc.DeleteDC()
    # bmp.DeleteObject()

    return image



# 示例用法
try:
    window_list = []
    for window in gw.getAllTitles():
        if window.strip():  # 排除空白标题
            print(window)
            window_list.append(window)
    title = '雷電模擬器'  # 替换为模拟器窗口的标题
    print(title)
    screenshot = get_screenshot_by_title(title)
    screenshot.show()
    screenshot.save("simulator_screenshot.png")
except Exception as e:
    print(e)
