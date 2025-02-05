import pyautogui
import time
import xlrd
import pyperclip
import random
import copy
import cv2
from plyer import notification
import os
from functools import reduce
from concurrent.futures import ThreadPoolExecutor
import subprocess
import uiautomator2 as u2
import numpy as np

# import pytesseract

#定义鼠标事件

#pyautogui库其他用法 https://blog.csdn.net/qingfengxd1/article/details/108270159
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def mouseClick(img_path, conf=0.7):
    #只在截图中寻找单一元素点击    
    # 读取截图和目标图片集
    d.screenshot("shot.png")
    screen = cv2.imread("shot.png", 0)  # 灰度读取
    for img_i in os.listdir(img_path):
        try:
            template = cv2.imread(img_path + img_i, 0)
            # cv2.imwrite("resized_image.jpg", template)
            # template = cv2.imread(img_path + img_i, 0)  # 目标按钮的图片
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= conf:
                x, y = max_loc  # 匹配到的左上角坐标
                w, h = template.shape[::-1]  # 获取模板宽高，这里会受到图片缩放比例的影响吗？
                center_x, center_y = x + w // 2, y + h // 2  # 计算中心坐标
                
                # 点击
                d.click(center_x, center_y)
                print("找到{0}，点击坐标: {1},{2}".format(img_i, center_x, center_y))
                break
            else:
                print(img_path + img_i, "匹配度不足，仅为{0}".format(max_val))
        except:
            print(img_path + img_i, "匹配失败")
            continue
            # notification.notify(
            # title="没找到{0}".format(img_i),
            # message="这是一个跨平台的通知，适配 Windows 11。",
            # app_name="我的应用",
            # timeout=0.5)
            # continue
        
def findElement(img_path, conf=0.6, notice=False):
    #寻找指定图片样本是否在屏幕中，这一函数的执行效率对于购买速度至关重要，需要重点优化
    # 1.尽量将高匹配度的图片放在文件夹最前面；2.这个函数内部不一定需要加并行化，因为很有可能第一个样本就匹配完毕了
    # find_tic = time.time()
    d.screenshot("shot.png")
    screen = cv2.imread("shot.png", 0)  # 灰度读取
    for img_i in os.listdir(img_path):
        try:
            template = cv2.imread(img_path + img_i, 0)  # 目标按钮的图片
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= conf:
                print('找到了{0}'.format(img_i))
                if notice:
                    notification.notify(
                            title="找到了{0}！".format(img_i),
                            message="这是一个跨平台的通知，适配 Windows 11。",
                            app_name="我的应用",
                            timeout=0.5)
                return True
        except:
            continue
    if notice:
        notification.notify(
                title="没找到{0}".format(img_i),
                message="这是一个跨平台的通知，适配 Windows 11。",
                app_name="我的应用",
                timeout=0.5)
        
    # find_toc = time.time()
    # print('全屏幕寻找{0}单一元素耗时{1}秒'.format(img_path, find_toc-find_tic))
    return False

# def getCurrentPage():
#     #获取当前页码（因为页码太小，识别效果不佳，暂时废止）
#     screenshot = pyautogui.screenshot(region=(1933,74,23,23))
#     text = pytesseract.image_to_string(screenshot, lang="eng", config="--psm 6 digits")
#     return text.strip()
    # current_page = 3
    # while not findElement('page_'+str(current_page)+'.png', confidence=0.5):
    #     current_page += 2
    #     if current_page >= 11:
    #         print('当前是最后一页')
    #         return 11
    # print('当前是第{0}页'.format(current_page))

    # return current_page

def calc_dist(match_i, match_j):
    # match_i, match_j都是[center_x, center_y]格式
    #计算两个样本之间的距离
    dist = abs(match_i[0] - match_j[0]) + abs(match_i[1] - match_j[1])

    return dist

def clear_matches(matches, dist = 40):
    #清除距离较近的样本
    if matches == []: 
        return []
    matches_temp = [matches[0]]
    for match in matches[1:]:
        dist_list = [calc_dist(match, match_i) for match_i in matches_temp]
        if min(dist_list) > dist:
            matches_temp.append(match)
    # print('清除{0}份样本'.format(len(matches) - len(matches_temp)))
    
    return matches_temp

def exclude_matches(matches, matches_exclude, dist=40):
    #清除不符合条件的样本
    if len(matches_exclude) == 0: 
        return matches
    matches_temp = []
    for match_i in matches:
        dist_list = [calc_dist(match_i, match_j) for match_j in matches_exclude]
        if min(dist_list) > dist:
            matches_temp.append(match_i)

    return matches_temp

def checkFirstPage():
    #监测商店有没有被更新
    # mouseClick(1,"left",'pictures/common/mail/')
    # time.sleep(1)
    firstPagePath = 'pictures/common/first_page_sign/'
    if findElement(firstPagePath):
        # mouseClick(1,"left",'pictures/common/close_news/')
        print('找到了第一页的痕迹！')
        return True
    else:
        # mouseClick(1,"left",'pictures/common/close_news/')
        return False


def flipOver():
    #向后翻页
    # time.sleep(1)
    # location = pyautogui.locateCenterOnScreen('pictures/common/close_news/',confidence=0.7) #定位关闭商店按钮
    # pyautogui.moveTo(location[0]-560, location[1]) #将光标转移到报纸上
    # time.sleep(1)
    # pyautogui.dragTo(location[0]-1400, location[1], duration=0.3, button='left')
    # print('翻页成功！')

    d.drag(1110, 40, 1110-700, 40, duration=0.3)
    print('翻页成功！')


def locateAllOnScreen(img_path, conf=0.7):
    # 获取所有匹配对象的中心坐标，返回[[center_x1, center_y1],[center_x2, center_y2],...]
    d.screenshot("shot.png")
    screen = cv2.imread("shot.png", 0)  # 灰度读取
    matches = []
    for img_i in os.listdir(img_path):
        try:
            template = cv2.imread(img_path + img_i, 0)  # 目标按钮的图片
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            loc = np.where(res >= conf)
            for pt in zip(*loc[::-1]):
                x, y = pt  # 匹配到的左上角坐标
                w, h = template.shape[::-1]  # 获取模板宽高，这里会受到图片缩放比例的影响吗？
                center_x, center_y = x + w // 2, y + h // 2  # 计算中心坐标
                matches.append([center_x, center_y])
        except:
            continue
    return matches

def locateOnScreen(img_path, conf=0.7):
    #在截图中寻找单一元素的中心位置    
    # 读取截图和目标图片集
    d.screenshot("shot.png")
    screen = cv2.imread("shot.png", 0)  # 灰度读取
    for img_i in os.listdir(img_path):
        try:
            template = cv2.imread(img_path + img_i, 0)
            # cv2.imwrite("resized_image.jpg", template)
            # template = cv2.imread(img_path + img_i, 0)  # 目标按钮的图片
            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= conf:
                x, y = max_loc  # 匹配到的左上角坐标
                w, h = template.shape[::-1]  # 获取模板宽高，这里会受到图片缩放比例的影响吗？
                center_x, center_y = x + w // 2, y + h // 2  # 计算中心坐标
                
                # 点击
                print("找到{0}，点击坐标: {1},{2}".format(img_i, center_x, center_y))
                return [center_x, center_y]
                break
            else:
                print(img_path + img_i, "匹配度不足，仅为{0}".format(max_val))
        except:
            print(img_path + img_i, "匹配失败")
            continue
            # notification.notify(
            # title="没找到{0}".format(img_i),
            # message="这是一个跨平台的通知，适配 Windows 11。",
            # app_name="我的应用",
            # timeout=0.5)
            # continue
    return None

def checkEndPage(notice = False):
    coin_sign_path = 'pictures/common/coin_sign/'
    items = locateAllOnScreen(coin_sign_path, conf=0.9)
    items = clear_matches(items)
    print('识别出{0}个金币'.format(len(items)))
    if notice:
        notification.notify(title="识别出{0}个商品".format(len(items)),
                            message="这是一个跨平台的通知，适配 Windows 11。",
                            app_name="我的应用",
                            timeout=1)
    if len(items) <= 6: #不超过6个，就认定是最后一页
        return True
    else:
        return False
def sell_goods(goods_forsale):
    #按照最贵的价格销售一波指定商品集
    time.sleep(1)
    #只销售一波
    if findElement('pictures/common/shelf_sold/'): 
        shelves_sold = locateAllOnScreen('pictures/common/shelf_sold/', conf=0.8)
        shelves_sold = clear_matches(shelves_sold)
        print('售空货架有{0}个'.format(len(shelves_sold)))
        for shelf_sold in shelves_sold:
            # print(f"售空货架中心坐标为: {center}")
            d.click(int(shelf_sold[0]), int(shelf_sold[1]))

    time.sleep(1)

    # 定位空货架，逐个点击上货
    if findElement('pictures/common/shelf_empty/'):
        shelves_empty = locateAllOnScreen('pictures/common/shelf_empty/', conf=0.8)
        shelves_empty = clear_matches(shelves_empty)
        print('空货架有{0}个'.format(len(shelves_empty)))
        for k in range(len(shelves_empty)):
            shelf_empty = shelves_empty[k]
            d.click(int(shelf_empty[0]), int(shelf_empty[1]))
            time.sleep(1)
            # 按照售卖品类出售商品，另外一种策略是选择最多的商品出售(最多的商品在全屏模式下坐标为(770,375))
            if findElement(goods_forsale, conf=0.7): #如果找到指定货物
                print('找到了' + goods_forsale)
                mouseClick(goods_forsale)# 点击指定货物？？大概率findElement找到了，但是在mouseclick时没找到
            else:# 没有找到指定货物，说明数量已经不多了，退出当前品类货物的售卖流程，但是此时界面停留在上架界面需要关闭
                d.click(1415,50)
                break
            time.sleep(1)
            # mouseClick(1,"left",'pictures/common/max_price/')# 拉满价格(1960,720)
            d.click(1280,450)
            time.sleep(0.5)
            # 在第一个空货架或者最后一个空货架处做if，如果有广告，点击广告，否则不
            if k == 0 and (not findElement('pictures/common/ad_notavaliable/')):
                # mouseClick(1,"left",'pictures/common/ad_available/')
                d.click(1075,675)
            time.sleep(0.5)
            mouseClick('pictures/common/on_shelf/')# 点击上架
            time.sleep(0.5)

def getAllPicPath(img_path_list):
    #输入多个图片文件夹组成的列表，返回一个包含所有图片路径的列表
    return [img_path + img_i for img_path in img_path_list for img_i in os.listdir(img_path)]

def restart():
    # 重启模拟器并启动hayday应用
    LDPLAYER_PATH = r"D:\LDPlayer\LDPlayer9\ldconsole.exe"
    LDPLAYER_EXE = r"D:\LDPlayer\LDPlayer9\dnplayer.exe"
    adb_path = r"D:\LDPlayer\LDPlayer9\adb.exe"
    # simulator_name = "LDPlayer"
    device_id = "127.0.0.1:5555"

    # output = subprocess.run([LDPLAYER_PATH, "list"], capture_output=True, text=True)
    # print("雷电模拟器列表：")
    # print(output.stdout)

    # 强制关闭雷电模拟器的主进程
    subprocess.run(["taskkill", "/F", "/IM", "dnplayer.exe"])
    # subprocess.run(["taskkill", "/F", "/IM", "LdVBoxHeadless.exe"])

    # 重新启动模拟器（适用于 Android Studio 模拟器）
    subprocess.Popen([LDPLAYER_EXE])
    time.sleep(20)  

    # 重新连接 UIAutomator2
    d = u2.connect(device_id)  # 连接模拟器
    print("模拟器重启完成！")
    time.sleep(5) 

    # 启动卡通农场应用（替换为实际的包名和活动名称）
    package_name = "com.supercell.hayday"
    activity_name = ".GameApp"

    # 启动应用
    # subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/{activity_name}"])
    # subprocess.run(["adb", "-s", device_id, "shell", "am", "start", "-n", f"{package_name}/{activity_name}"])
    subprocess.run([adb_path, "-s", device_id, "shell", "monkey", "-p", package_name, '-c', 'android.intent.category.LAUNCHER', '1'])
    time.sleep(10)
    print("卡通农场应用已启动！")

    # 下滑至指定位置（商场-邮箱那里）
    while not findElement('pictures/common/mail/'):
        width, height = d.window_size()
        print('当前屏幕尺寸为：宽{0}x高{1}'.format(width, height))
        d.drag(width*1/4,height*3/4, width/2,height/2, duration=0.3)
        time.sleep(1)
    location = locateOnScreen('pictures/common/mail/')
    d.drag(location[0], location[1], 1480, 600, duration=0.3)
    time.sleep(1)

def smooth_path(raw_path):
    #平滑路径
    new_path = [raw_path[0]]
    for point_i in raw_path[1:]:
        new_path.append([(new_path[-1][0]+point_i[0])//2, (new_path[-1][1]+point_i[1])//2])
        new_path.append(point_i)

    return new_path

def plant():
    #种植作物
    location_plant = locateOnScreen('pictures/zhongzhi/xiaomai_plant/',conf=0.7)
    print('xiaomai_plant所在位置为：[{0}, {1}]'.format(location_plant[0], location_plant[1]))

    # 移动到种植作物上并按下鼠标左键
    d.touch.down(location_plant[0], location_plant[1])  #点击种植作物

    # 按顺序经过每个点
    location_base = locateOnScreen(base_path, conf=0.6) # 重新定位地标，因为点击种植作物后，整个屏幕会调整位置
    points = [[location_base[0]-cell[0]*0.5, location_base[1]-cell[1]*2.5], [location_base[0]-cell[0]*2.5, location_base[1]-cell[1]*0.5], 
            [location_base[0]-cell[0]*2, location_base[1]], [location_base[0], location_base[1]-cell[1]*2]]
    points = smooth_path(smooth_path(points))
    for point_i in points:  
        d.touch.move(point_i[0] + bias[0], point_i[1] + bias[1]) # 需要控制滑动速度
        time.sleep(0.1)
    # 松开鼠标左键
    d.touch.up(location_base[0], location_base[1])
    time.sleep(0.5)
    d.click(points[-1][0], points[-1][1] - cell[1]) #点击轨迹终点上面一格的位置，避免遮挡地标
    time.sleep(1)
    print("种植完成")

def gain():
    #收获作物
    #按住镰刀按照固定轨迹拖，松开镰刀
    location_sickle = locateOnScreen('pictures/zhongzhi/sickle/',conf=0.6)
    print('sickle所在位置为：[{0}, {1}]'.format(location_sickle[0], location_sickle[1]))

    # 移动到镰刀上并按下鼠标左键
    d.touch.down(location_sickle[0], location_sickle[1]) #点击镰刀
    time.sleep(0.5)

    # 按顺序经过每个点
    location_base = locateOnScreen(base_path,conf=0.6)
    points = [[location_base[0]-cell[0]*0.5, location_base[1]-cell[1]*2.5], [location_base[0]-cell[0]*2.5, location_base[1]-cell[1]*0.5], 
            [location_base[0]-cell[0]*2, location_base[1]], [location_base[0], location_base[1]-cell[1]*2]]
    points = smooth_path(smooth_path(points))
    for point_i in points:
        d.touch.move(point_i[0] + bias[0], point_i[1] + bias[1])
        time.sleep(0.1)  # 控制滑动速度
    d.touch.up(location_base[0], location_base[1])
    time.sleep(1)
    print("收割完成")

if __name__ == '__main__':
    
    max_try = 1000
    try_i = 0
    init = True
    plant_items = ['xiaomai/']
    sell_items = ['xiaomai/']
    mature_time = 60*2 #作物成熟时间
    d = u2.connect("127.0.0.1:5555")  # 连接模拟器
    # print(d.info)
    # scaling = 1600/2560
    bias = [0, 45] #base元素中心点和其下地块有一定偏移,需要进行修正
    cell = [213, 108] #地块的宽高尺寸
    base_path = 'pictures/zhongzhi/base/'
    mail_path = 'pictures/common/mail/'
    # for try_i in range(20):
    while try_i < max_try: #在每一层循环里面完成多次种植收获、一次销售
        try:
            print('这是第{0}次尝试'.format(try_i))
            tic = time.time()
            time.sleep(3)

            #按住邮箱向左拖
            mail_path = 'pictures/common/mail/' #邮箱图片存储路径
            location = locateOnScreen(mail_path, conf=0.7)
            d.drag(location[0], location[1], location[0]-1000,location[1], duration=0.3)
            time.sleep(1) #防止屏幕拖动的缓冲影响后续因素定位，先等图片缓冲结束
            state = 'plant' #默认土地状态
            wait_time = 5 # 需要等待的时间
            while not findElement('pictures/common/warehouse_full_notice/'):
            # while True:
                time.sleep(wait_time) #设定久一点，以免上一个循环收割的小麦遮挡地标
                
                mouseClick(base_path) #将光标转移到地标上
                time.sleep(2)
                location_base = locateOnScreen(base_path, conf=0.6)
                d.click(location_base[0]-cell[0]*0.5+bias[0], location_base[1]-cell[1]*2.5+bias[1]) #点击第一排最右边的土地，这时屏幕会调整位置
                time.sleep(1)
                
                if findElement('pictures/zhongzhi/xiaomai_plant/'):
                    plant()
                    state = 'gain' #种植完成，下一步准备收获
                    wait_time = mature_time+5
                elif findElement('pictures/zhongzhi/sickle/'):
                    gain()
                    if findElement('pictures/common/warehouse_full_notice/'):
                        break
                    state = 'plant' #收获完成，下一步准备种植
                    wait_time = 5
                else: #说明没有识别成功，重启模拟器
                    restart() #进入下一个循环
                    continue
                
                #等待下一步操作的时间
                time.sleep(wait_time)

                #定位成熟土地位置，单击开始
                mouseClick(base_path)
                time.sleep(2)
                location_base = locateOnScreen(base_path, conf=0.6)
                d.click(location_base[0]-cell[0]*0.5+bias[0], location_base[1]-cell[1]*2.5+bias[1]) #点击第一排最右边的成熟土地，这时屏幕会调整位置
                time.sleep(1)

                if findElement('pictures/zhongzhi/xiaomai_plant/'):
                    plant()
                    state = 'gain' #种植完成，下一步准备收获
                    wait_time = mature_time+5
                elif findElement('pictures/zhongzhi/sickle/'):
                    gain()
                    if findElement('pictures/common/warehouse_full_notice/'):
                        break
                    state = 'plant' #收获完成，下一步准备种植
                    wait_time = 5
                else: #说明没有识别成功，重启模拟器
                    restart() #进入下一个循环
                    continue
                

            # 仓库满仓，进入售卖流程
            time.sleep(2)
            d.click(1400,80) #关闭满仓通知
            time.sleep(0.5)
            location = locateOnScreen(mail_path,conf=0.7) #定位邮箱图标位置
            time.sleep(1)
            d.drag(location[0], location[1], location[0]+1000,location[1], duration=0.3)
            time.sleep(1) #防止屏幕拖动的缓冲影响后续因素定位，先等图片缓冲结束
            mouseClick('pictures/common/store/', conf=0.5) #点击商店
            for sell_item in sell_items: #逐样售卖待售物品
                # time.sleep(5)
                sell_goods('pictures/' + sell_item + 'goods_forsale/') #这一步填满货架
            # 此时不存在可操作的售空货架或者空货架，关闭自己的商店
            # pyautogui.click(2160,125,clicks=1,interval=0.2,duration=0.2,button='left') #关闭上架界面(点击上架的时候，该界面就自动被关闭了)
            # mouseClick('pictures/common/close_store/')
            d.click(1350,70) #关闭商店

            notification.notify(
                title="商店已上货，今日下一个循环！",
                message="这是一个跨平台的通知，适配 Windows 11。",
                app_name="我的应用",
                timeout=1
            )
            try_i += 1
                
            # 获取等待结束时刻的时间戳
            toc = time.time()
            end_timestamp = time.time() + 3*60-(toc-tic)
            # 转换为本地时间
            end_time = time.localtime(end_timestamp)
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
            # 显示通知
            notification.notify(
                title=formatted_time,
                message="这是一个跨平台的通知，适配 Windows 11。",
                app_name="我的应用",
                timeout=3*60-(toc-tic)
            )

        except: #模拟器出现异常
            restart()
            continue

            # # 找到邮箱后，将其拖至指定位置(2300,1000)
            # for img_i in os.listdir(mail_path): #定位邮箱图标位置
            #     try:
            #         location=pyautogui.locateCenterOnScreen(mail_path + img_i,confidence=0.7)
            #     except:
            #         continue
            # pyautogui.moveTo(location[0], location[1]) #将光标转移到邮箱上
            # pyautogui.dragTo(2300,1000,duration=0.5)
            

