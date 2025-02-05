import time
import cv2
from plyer import notification
import os
from functools import reduce
from concurrent.futures import ThreadPoolExecutor
import uiautomator2 as u2
import cv2
import numpy as np
import subprocess

# import pytesseract

d = u2.connect("127.0.0.1:5555")  # 连接模拟器
print(d.info)
scaling = 1600/2560

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
def findElement(img_path, conf=0.8, notice=False):
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
            if findElement(goods_forsale): #如果找到指定货物
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

def getAllPicPath(img_path_list):
    #输入多个图片文件夹组成的列表，返回一个包含所有图片路径的列表
    return [img_path + img_i for img_path in img_path_list for img_i in os.listdir(img_path)]

if __name__ == '__main__':
    # mouseClick('pictures/common/store/', conf=0.5) #点击商店
    max_try = 1000
    try_i = 0
    init = True
    find_items = ['xiaomai/']
    sell_items = ['xiaomai/']
    ignore_expen = True #是否不购买太贵的商品
    # for try_i in range(20):
    while try_i < max_try:
        print('这是第{0}次尝试'.format(try_i))
        tic = time.time()
        if init:
            time.sleep(1)
            #鼠标左击邮箱
            mail_path = 'pictures/common/mail/' #邮箱图片存储路径
            mouseClick(mail_path, conf=0.7)
        # print("单击左键",img)

        #寻找小麦直到该页有小麦，点进去
        page = 3
        while page < 13:
            time.sleep(1) #避免截图不完整
            print("进入第{0}页".format(page))
            print(findElement('pictures/xiaomai/player/'))
            full = False

            # 为了不漏掉目标，尽量多进少出，所以matches和matches_buyable使用confidence=0.8, 删除时使用confidence=0.9
            # if any(ThreadPoolExecutor().map(findElement, ['pictures/' + find_item +'player/' for find_item in find_items])):
            if any([findElement('pictures/' + find_item +'player/') for find_item in find_items]):
                matches = reduce(lambda x, y: x + y, \
                                 ThreadPoolExecutor().map(locateAllOnScreen, \
                                                          ['pictures/' + find_item +'player/' for find_item in find_items])) #一个对象可能被匹配到多次
                # print('删除前，本页找到{0}个可以出售商品的玩家'.format(len(matches)))
                matches = clear_matches(matches)
                if ignore_expen and len(matches) > 0 and \
                    any(ThreadPoolExecutor().map(lambda find_item: findElement(find_item, conf=0.9), \
                                                 ['pictures/' + find_item +'player/' for find_item in find_items])): #如果找到的玩家中有价高的，排除这些价高的玩家
                # if False:
                    players_expen = reduce(lambda x, y: x + y, \
                                ThreadPoolExecutor().map(lambda k: locateAllOnScreen(k, conf=0.9), \
                                                         ['pictures/' + find_item +'player_expen/' for find_item in find_items]))
                    players_expen = clear_matches(players_expen)
                    matches = exclude_matches(matches, players_expen, 200)
                # notification.notify(title='删除后，本页找到{0}个可以出售便宜商品的玩家'.format(len(matches)),
                #                     message="这是一个跨平台的通知，适配 Windows 11。",
                #                     app_name="我的应用",
                #                     timeout=0.5)
                print('删除后，本页找到{0}个可以出售便宜商品的玩家'.format(len(matches)))
                for i in range(len(matches)):
                    match = [int(x) for x in matches[i]]
                    d.click(match[0], match[1])
                    print(f"玩家中心坐标为: {match}")
                    time.sleep(3) #这里等待玩家商店打开，2秒被测试是不够的，需要根据网络状况设定这一等待时间

                    matches_buyable = reduce(lambda x, y: x + y, \
                            ThreadPoolExecutor().map(locateAllOnScreen, \
                                                         ['pictures/' + find_item +'shelf_buyable/' for find_item in find_items]))
                    print('删除前可以买{0}个'.format(len(matches_buyable)))
                    matches_buyable = clear_matches(matches_buyable)
                    if len(matches_buyable) > 0 and \
                        any(ThreadPoolExecutor().map(findElement, ['pictures/' + find_item +'shelf_sold/' for find_item in find_items])): #如果找到的商品有部分或者全部出售的，去掉这些出售的
                        matches_sold = reduce(lambda x, y: x + y, \
                            ThreadPoolExecutor().map(lambda k: locateAllOnScreen(k, conf=0.9), \
                                                         ['pictures/' + find_item +'shelf_sold/' for find_item in find_items]))
                        matches_sold = clear_matches(matches_sold)
                        matches_buyable = exclude_matches(matches_buyable, matches_sold, dist=100)
                    if ignore_expen and len(matches_buyable) > 0 and \
                        any(ThreadPoolExecutor().map(lambda find_item: findElement(find_item, conf=0.9), \
                                                     ['pictures/' + find_item +'shelf_expen/' for find_item in find_items])): #如果找到的商品太贵，去掉这些太贵的
                        matches_expen = reduce(lambda x, y: x + y, \
                            ThreadPoolExecutor().map(lambda k: locateAllOnScreen(k, conf=0.9), \
                                                         ['pictures/' + find_item +'shelf_expen/' for find_item in find_items]))
                        matches_expen = clear_matches(matches_expen)
                        matches_buyable = exclude_matches(matches_buyable, matches_expen, dist=100)
                    # notification.notify(title='本玩家可以出售{0}份便宜商品'.format(len(matches_buyable)),
                    #                 message="这是一个跨平台的通知，适配 Windows 11。",
                    #                 app_name="我的应用",
                    #                 timeout=0.5)
                    print('本玩家可以出售{0}份便宜商品'.format(len(matches_buyable)))
                    for match_buyable in matches_buyable: #逐个点击所有匹配对象
                        d.click(int(match_buyable[0]), int(match_buyable[1]))
                        print(f"小麦中心坐标为: {match_buyable}")
                        time.sleep(0.5)
                        #如果弹出仓库已满，进入售货流程（售货流程单独写一个函数接进来）
                        
                        if findElement('pictures/common/warehouse_full_notice/'):
                            full = True
                            # notification.notify(
                            #         title="仓库已满",
                            #         message="这是一个跨平台的通知，适配 Windows 11。",
                            #         app_name="我的应用",
                            #         timeout=1)
                            break
                        
                    if full:
                        break

                    # mouseClick(1,"left",'pictures/common/close_store/') #关闭该用户的商店
                    d.click(1350,70)
                    time.sleep(0.5)
                    mouseClick(mail_path, conf=0.7) #再次进入商店

                    time.sleep(1)
                    if page > 3 and checkFirstPage(): #？？无法避免一种情况：在第三页出现两个及以上符合条件的商家，在准备购买第二个商家物品的时候更新了
                        page = 3 #商店已被更新，页数重置
                        break #之前定位的玩家坐标失效，跳出循环重新定位玩家坐标
                    
            if full:
                # notification.notify(title="进入售卖流程",
                #     message="这是一个跨平台的通知，适配 Windows 11。",
                #     app_name="我的应用",
                #     timeout=1)
                # mouseClick(1,"left",['close_full_notice.png']) #(2150,160)
                d.click(1400,80) #关闭满仓通知

                time.sleep(0.5)
                mouseClick('pictures/common/close_store/') #关闭玩家商店
                time.sleep(0.5)
                mouseClick('pictures/common/back_home/') #点击回家按钮
                time.sleep(3)

                mouseClick('pictures/common/store/', conf=0.4) #点击商店
                for sell_item in sell_items: #逐样售卖待售物品
                    # time.sleep(30)
                    sell_goods('pictures/' + sell_item + 'goods_forsale/') #这一步填满货架
                # 此时不存在可操作的售空货架或者空货架，关闭自己的商店
                # pyautogui.click(2160,125,clicks=1,interval=0.2,duration=0.2,button='left') #关闭上架界面(点击上架的时候，该界面就自动被关闭了)
                mouseClick('pictures/common/close_store/') # 1410,60
                # d.click(1410,60)

                print("上货完毕")
                time.sleep(1)
                mouseClick(mail_path,conf=0.7) #点击邮箱（为简化操作，之前那页作废，后面继续执行翻页）
                time.sleep(1)
                if page > 3 and checkFirstPage():
                    page = 3

            # checkEndPage(notice=True)
            if page < 11: #只要不是尾页，都执行翻页
                flipOver()
            
            page += 2
            
        time.sleep(1)
        mouseClick('pictures/common/close_news/')
        toc = time.time()

        # notification.notify(
        #     title="这一轮操作花费时间{}秒".format(toc - tic),
        #     message="这是一个跨平台的通知，适配 Windows 11。",
        #     app_name="我的应用",
        #     timeout=1
        # )
        
        while True: #每隔5秒检测一次商店是否更新
            mouseClick(mail_path,conf=0.7)
            time.sleep(1)
            if checkFirstPage(): # 如果检测出来是第一页，那么不用关闭商店，一种优化速度的手段
                init = False
                break
            mouseClick('pictures/common/close_news/') # 如果检测出来不是第一页，那么关闭商店
            time.sleep(2)

        # notification.notify(
        #     title="商店已更新！",
        #     message="这是一个跨平台的通知，适配 Windows 11。",
        #     app_name="我的应用",
        #     timeout=1
        # )
        try_i += 1
            
            
        # # 获取等待结束时刻的时间戳
        # end_timestamp = time.time() + 3*60-(toc-tic)
        # # 转换为本地时间
        # end_time = time.localtime(end_timestamp)
        # formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", end_time)
        # # 显示通知
        # notification.notify(
        #     title=formatted_time,
        #     message="这是一个跨平台的通知，适配 Windows 11。",
        #     app_name="我的应用",
        #     timeout=3*60-(toc-tic)
        # )
        # time.sleep(3*60-(toc-tic)+0.5)