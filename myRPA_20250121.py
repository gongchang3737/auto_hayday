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

# import pytesseract

#定义鼠标事件

#pyautogui库其他用法 https://blog.csdn.net/qingfengxd1/article/details/108270159
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def mouseClick(clickTimes,lOrR,img_path):
    #只在截图中寻找单一元素点击
    for img_i in os.listdir(img_path):
        try:
            location=pyautogui.locateCenterOnScreen(img_path + img_i,confidence=0.7)
            if location is not None:
                pyautogui.click(location.x,location.y,clicks=clickTimes,interval=0.2,duration=0.2,button=lOrR)
                break
        except:
            # notification.notify(
            # title="没找到{0}".format(img_i),
            # message="这是一个跨平台的通知，适配 Windows 11。",
            # app_name="我的应用",
            # timeout=0.5)
            continue
        # print("未找到匹配图片,0.1秒后重试")
        # time.sleep(0.1)
        
def findElement(img_path, conf=0.8, notice=False):
    #寻找指定图片样本是否在屏幕中，这一函数的执行效率对于购买速度至关重要，需要重点优化
    find_tic = time.time()
    for img_i in os.listdir(img_path):
        try:
            _ = pyautogui.locateCenterOnScreen(img_path + img_i, confidence=conf)
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
        
    find_toc = time.time()
    print('全屏幕寻找{0}单一元素耗时{1}秒'.format(img_path, find_toc-find_tic))
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
    #计算两个样本之间的距离
    dist = abs(pyautogui.center(match_i).x - pyautogui.center(match_j).x) + abs(pyautogui.center(match_i).y - pyautogui.center(match_j).y)

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

    pyautogui.moveTo(1730, 100) #将光标转移到报纸上
    pyautogui.dragTo(1730-1400, 100, duration=0.3, button='left')
    print('翻页成功！')

def locateAllOnScreen(img_path, confidence): #??改为与指定路径下的图片匹配
    matches = []
    for img_i in os.listdir(img_path):
        try:
            matches += list(pyautogui.locateAllOnScreen(img_path + img_i, confidence=confidence))
        except:
            continue
    return matches

def checkEndPage(notice = False): #??改为与指定路径下的图片匹配
    coin_sign_path = 'pictures/common/coin_sign/'
    items = locateAllOnScreen(coin_sign_path, confidence=0.9)
    items = clear_matches(items)
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
    #按照最贵的价格销售一波指定商品集，最后关闭自己的商店
    mouseClick(1,"left",'pictures/common/store/')
    time.sleep(1)
    #只销售一波
    if findElement('pictures/common/shelf_sold/'): 
        shelves_sold = locateAllOnScreen('pictures/common/shelf_sold/', confidence=0.8)
        shelves_sold = clear_matches(shelves_sold)
        print('售空货架有{0}个'.format(len(shelves_sold)))
        for shelf_sold in shelves_sold:
            center = pyautogui.center(shelf_sold)
            # print(f"售空货架中心坐标为: {center}")
            pyautogui.click(center)

    time.sleep(1)

    # 定位空货架，逐个点击上货
    if findElement('pictures/common/shelf_empty/'):
        shelves_empty = locateAllOnScreen('pictures/common/shelf_empty/', confidence=0.8)
        shelves_empty = clear_matches(shelves_empty)
        print('空货架有{0}个'.format(len(shelves_empty)))
        for k in range(len(shelves_empty)):
            shelf_empty = shelves_empty[k]
            center = pyautogui.center(shelf_empty)
            pyautogui.click(center) #点击空货架
            time.sleep(1)
            if findElement(goods_forsale): #如果找到小麦
                mouseClick(1,"left",goods_forsale)# 点击小麦
            else:# 没有找到小麦，说明小麦数量已经不多了，退出售卖流程
                # print('没有找到小麦，说明小麦已经全部售完')
                break
            time.sleep(1)
            # mouseClick(1,"left",'pictures/common/max_price/')# 拉满价格(1960,720)
            pyautogui.click(1960,720,clicks=1,interval=0.2,duration=0.2,button='left')
            time.sleep(0.5)
            # 在第一个空货架或者最后一个空货架处做if，如果有广告，点击广告，否则不
            if k == 0 and (not findElement('pictures/common/ad_notavaliable/')):
                # mouseClick(1,"left",'pictures/common/ad_available/')
                pyautogui.click(1680,1050,clicks=1,interval=0.2,duration=0.2,button='left')
            time.sleep(0.5)
            mouseClick(1,"left",'pictures/common/on_shelf/')# 点击上架
            time.sleep(0.5)
    # 此时不存在可操作的售空货架或者空货架，关闭自己的商店
    mouseClick(1,"left",'pictures/common/close_store/')

if __name__ == '__main__':
    
    max_try = 20
    try_i = 0
    init = True
    find_items = ['xiaomai/', 'yumi/']
    sell_items = ['xiaomai/', 'yumi/']
    ignore_expen = True #是否不购买太贵的商品
    # for try_i in range(20):
    while try_i < max_try:
        print('这是第{0}次尝试'.format(try_i))
        tic = time.time()
        if init:
            time.sleep(5)
            #鼠标左击邮箱
            mail_path = 'pictures/common/mail/' #邮箱图片存储路径
            mouseClick(1,"left",mail_path)
        # print("单击左键",img)

        #寻找小麦直到该页有小麦，点进去
        page = 3
        while page < 13:
            time.sleep(1) #避免截图不完整
            full = False
            if any([findElement('pictures/' + find_item +'player/') for find_item in find_items]):
                matches = reduce(lambda x, y: x + y, 
                                [locateAllOnScreen('pictures/' + find_item +'player/', confidence=0.8)for find_item in  find_items]) #很容易一个对象被匹配到多次
                print('删除前，本页找到{0}个可以出售商品的玩家'.format(len(matches)))
                matches = clear_matches(matches)
                if ignore_expen and len(matches) > 0 and any([findElement('pictures/' + find_item +'player_expen/', conf=0.9) for find_item in find_items]): #如果找到的玩家中有价高的，排除这些价高的玩家
                # if False:
                    players_expen = reduce(lambda x, y: x + y, 
                                [locateAllOnScreen('pictures/' + find_item +'player_expen/', confidence=0.9) for find_item in find_items])
                    players_expen = clear_matches(players_expen)
                    matches = exclude_matches(matches, players_expen, 200)
                notification.notify(title='删除后，本页找到{0}个可以出售便宜商品的玩家'.format(len(matches)),
                                    message="这是一个跨平台的通知，适配 Windows 11。",
                                    app_name="我的应用",
                                    timeout=0.5)
                print('删除后，本页找到{0}个可以出售便宜商品的玩家'.format(len(matches)))
                for i in range(len(matches)):
                    match = matches[i]
                    center = pyautogui.center(match)
                    print(f"玩家中心坐标为: {center}")
                    pyautogui.click(center)
                    time.sleep(3) #这里等待玩家商店打开，2秒被测试是不够的，需要根据网络状况设定这一等待时间

                    matches_buyable = reduce(lambda x, y: x + y,
                            [locateAllOnScreen('pictures/' + find_item +'shelf_buyable/', confidence=0.8) for find_item in find_items]) #很容易一个对象被匹配到多次
                    matches_buyable = clear_matches(matches_buyable)
                    if len(matches_buyable) > 0 and any([findElement('pictures/' + find_item +'shelf_sold/') for find_item in find_items]): #如果找到的小麦有部分或者全部出售的，去掉这些出售的
                        matches_sold = reduce(lambda x, y: x + y,
                            [locateAllOnScreen('pictures/' + find_item +'shelf_sold/', confidence=0.9) for find_item in find_items])
                        matches_sold = clear_matches(matches_sold)
                        matches_buyable = exclude_matches(matches_buyable, matches_sold, dist=100)
                    if ignore_expen and len(matches_buyable) > 0 and any([findElement('pictures/' + find_item +'shelf_expen/',conf=0.9) for find_item in find_items]): #如果找到的小麦太贵，去掉这些太贵的
                    # if False:
                        matches_expen = reduce(lambda x, y: x + y,
                            [locateAllOnScreen('pictures/' + find_item +'shelf_expen/', confidence=0.9) for find_item in find_items])
                        matches_expen = clear_matches(matches_expen)
                        matches_buyable = exclude_matches(matches_buyable, matches_expen, dist=100)
                    notification.notify(title='本玩家可以出售{0}份便宜商品'.format(len(matches_buyable)),
                                    message="这是一个跨平台的通知，适配 Windows 11。",
                                    app_name="我的应用",
                                    timeout=0.5)
                    print('本玩家可以出售{0}份便宜商品'.format(len(matches_buyable)))
                    for match_buyable in matches_buyable: #逐个点击所有匹配对象
                        center_buyable = pyautogui.center(match_buyable)
                        # print(f"小麦中心坐标为: {center_buyable}")
                        pyautogui.click(center_buyable)
                        # time.sleep(0.5)
                        #如果弹出仓库已满，进入售货流程（售货流程单独写一个函数接进来）
                        
                        if findElement('pictures/common/warehouse_full_notice/'):
                            full = True
                            notification.notify(
                                    title="仓库已满",
                                    message="这是一个跨平台的通知，适配 Windows 11。",
                                    app_name="我的应用",
                                    timeout=1)
                            break
                        
                    if full:
                        break

                    # mouseClick(1,"left",'pictures/common/close_store/') #关闭该用户的商店
                    pyautogui.click(2075,150,clicks=1,interval=0.2,duration=0.2,button='left')
                    mouseClick(1,"left",mail_path) #再次进入商店

                    time.sleep(1)
                    if page>3 and checkFirstPage(): #？？无法避免一种情况：在第三页出现两个及以上符合条件的商家，在准备购买第二个商家物品的时候更新了
                        page = 3 #商店已被更新，页数重置
                        break #之前定位的玩家坐标失效，跳出循环重新定位玩家坐标
                    
            if full:
                notification.notify(title="进入售卖流程",
                    message="这是一个跨平台的通知，适配 Windows 11。",
                    app_name="我的应用",
                    timeout=1)
                # mouseClick(1,"left",['close_full_notice.png']) #(2150,160)
                pyautogui.click(2150,160,clicks=1,interval=0.2,duration=0.2,button='left') #关闭满仓通知

                time.sleep(0.5)
                mouseClick(1,"left",'pictures/common/close_store/') #关闭玩家商店
                time.sleep(0.5)
                mouseClick(1,"left",'pictures/common/back_home/') #点击回家按钮
                time.sleep(3)
                for sell_item in sell_items: #逐样售卖待售物品
                    sell_goods('pictures/' + sell_item + 'goods_forsale/') #这一步完成了从进入自己的商店，到一样商品上架结束关闭自己的商店
                print("上货完毕")
                mouseClick(1,"left",mail_path) #点击邮箱（为简化操作，之前那页作废，后面继续执行翻页）
                time.sleep(0.5)
                if checkFirstPage():
                    page = 3

            if not checkEndPage(): #只要不是尾页，都执行翻页
                flipOver() #
            
            page += 2
            print("进入第{0}页".format(page))
        time.sleep(1)
        mouseClick(1,"left",'pictures/common/close_news/')
        toc = time.time()

        notification.notify(
            title="这一轮操作花费时间{}秒".format(toc - tic),
            message="这是一个跨平台的通知，适配 Windows 11。",
            app_name="我的应用",
            timeout=1
        )
        
        while True: #每隔5秒检测一次商店是否更新
            mouseClick(1,"left", mail_path)
            time.sleep(1)
            if checkFirstPage(): # 如果检测出来是第一页，那么不用关闭商店，一种优化速度的手段
                init = False
                break
            mouseClick(1,"left",'pictures/common/close_news/') # 如果检测出来不是第一页，那么关闭商店
            time.sleep(2)

        notification.notify(
            title="商店已更新！",
            message="这是一个跨平台的通知，适配 Windows 11。",
            app_name="我的应用",
            timeout=1
        )
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