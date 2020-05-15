import base64
import random
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from io import BytesIO

driver = webdriver.Chrome()
WAIT = WebDriverWait(driver, 10)
url = 'https://passport.bilibili.com/login'


def mergy_Image(image_file, location_list):
    """
    将原始图片进行合成
    :param image_file: 图片文件
    :param location_list: 图片位置
    :return: 合成新的图片
    """

    # 存放上下部分的各个小块
    upper_half_list = []
    down_half_list = []

    image = Image.open(image_file)

    # 通过 y 的位置来判断是上半部分还是下半部分,然后切割
    for location in location_list:
        if location['y'] == -58:
            # 间距为10，y：58-116
            im = image.crop((abs(location['x']), 58, abs(location['x'])+10, 116))
            upper_half_list.append(im)
        if location['y'] == 0:
            # 间距为10，y：0-58
            im = image.crop((abs(location['x']), 0, abs(location['x']) + 10, 58))
            down_half_list.append(im)

    # 创建一张大小一样的图片
    new_image = Image.new('RGB', (260, 116))

    # 粘贴好上半部分 y坐标是从上到下（0-116）
    offset = 0
    for im in upper_half_list:
        new_image.paste(im, (offset, 0))
        offset += 10

    # 粘贴好下半部分
    offset = 0
    for im in down_half_list:
        new_image.paste(im, (offset, 58))
        offset += 10

    return new_image


def get_distance(bg_Image, fullbg_Image):

    # 阈值
    threshold = 200

    print(bg_Image.size[0])
    print(bg_Image.size[1])


    for i in range(60, bg_Image.size[0]):
        for j in range(bg_Image.size[1]):
            bg_pix = bg_Image.getpixel((i, j))
            fullbg_pix = fullbg_Image.getpixel((i, j))
            r = abs(bg_pix[0] - fullbg_pix[0])
            g = abs(bg_pix[1] - fullbg_pix[1])
            b = abs(bg_pix[2] - fullbg_pix[2])
            #根据实际情况微调返回值
            if r + g + b > threshold:
               return i-10



#模拟人拖动的路径
def get_path(distance):
    track = []
    current = 0
    mid = distance * 3 / 4
    t = random.randint(2, 3) / 10
    v = 0
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move))
    return track


        # '''
        #     :param distance: (Int)缺口离滑块的距离
        #     :return: (List)移动轨迹
        #     '''
        #
        # # 创建存放轨迹信息的列表
        # trace = []
        # # 设置加速的距离
        # faster_distance = distance * (4 / 5)
        # # 设置初始位置、初始速度、时间间隔
        # start, v0, t = 0, 0, 0.2
        # # 当尚未移动到终点时
        # while start < distance:
        #     # 如果处于加速阶段
        #     if start < faster_distance-10:
        #         # 设置加速度为2
        #         a = 2
        #     # 如果处于减速阶段
        #     else:
        #         # 设置加速度为-3
        #         a = -3
        #     # 移动的距离公式
        #     move = v0 * t + 1 / 2 * a * t * t
        #     # 此刻速度
        #     v = v0 + a * t
        #     # 重置初速度
        #     v0 = v
        #     # 重置起点
        #     start += move
        #     # 将移动的距离加入轨迹列表
        #     trace.append(round(move))
        # # 返回轨迹信息
        # return trace



#开始拖拽
def start_drag(driver, distance):

    # 被妖怪吃掉了
    # knob =  WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gc-box > div > div.gt_slider > div.gt_slider_knob.gt_show")))
    # ActionChains(driver).click_and_hold(knob).perform()
    # ActionChains(driver).move_by_offset(xoffset=distance, yoffset=0.1).perform()
    # time.sleep(0.5)
    # ActionChains(driver).release(knob).perform()

    # 被妖怪吃掉了
    # ActionChains(driver).drag_and_drop_by_offset(knob, distance-10, 0).perform()

    knob = WAIT.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div/div[1]/div[2]/div[2]")))
    result = get_path(distance)
    ActionChains(driver).click_and_hold(knob).perform()

    for x in result:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()

    time.sleep(0.5)
    ActionChains(driver).release(knob).perform()


def newstart_drag(driver,distance):
    track_list = get_path(distance + 3)
    time.sleep(2)
    slideblock = WAIT.until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div/div[1]/div[2]/div[2]")))
    ActionChains(driver).click_and_hold(slideblock).perform()
    time.sleep(0.2)
    # 根据轨迹拖拽圆球
    for track in track_list:
        ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
    # 模拟人工滑动超过缺口位置返回至缺口的情况，数据来源于人工滑动轨迹，同时还加入了随机数，都是为了更贴近人工滑动轨迹
    imitate = ActionChains(driver).move_by_offset(xoffset=-1, yoffset=0)
    time.sleep(0.015)
    imitate.perform()
    time.sleep(random.randint(6, 10) / 10)
    imitate.perform()
    time.sleep(0.04)
    imitate.perform()
    time.sleep(0.012)
    imitate.perform()
    time.sleep(0.019)
    imitate.perform()
    time.sleep(0.033)
    ActionChains(driver).move_by_offset(xoffset=1, yoffset=0).perform()
    # 放开圆球
    ActionChains(driver).pause(random.randint(6, 14) / 10).release(slideblock).perform()
    time.sleep(2)

#使用碎片的拖动验证码
def recognize_code(driver):
    """
    识别滑动验证码
    :param driver: selenium驱动
    :return:
    """

    bs = BeautifulSoup(driver.page_source,'lxml')
    # 找到背景图片和缺口图片的div
    bg_div = bs.find_all(class_='gt_cut_bg_slice')
    fullbg_div = bs.find_all(class_='gt_cut_fullbg_slice')

    # 获取缺口背景图片url
    bg_url = re.findall('background-image:\surl\("(.*?)"\)',bg_div[0].get('style'))
    # 获取背景图片url
    fullbg_url = re.findall('background-image:\surl\("(.*?)"\)',fullbg_div[0].get('style'))

    # 存放每个合成缺口背景图片的位置
    bg_location_list = []
    # 存放每个合成背景图片的位置
    fullbg_location_list = []

    for bg in bg_div:
        location = {}
        location['x'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][0])
        location['y'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', bg.get('style'))[0][1])
        bg_location_list.append(location)

    for fullbg in fullbg_div:
        location = {}
        location['x'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', fullbg.get('style'))[0][0])
        location['y'] = int(re.findall('background-position:\s(.*?)px\s(.*?)px;', fullbg.get('style'))[0][1])
        fullbg_location_list.append(location)

    print(bg_location_list)
    print(fullbg_location_list)

    # 将图片格式存为 jpg 格式
    bg_url = bg_url[0].replace('webp', 'jpg')
    fullbg_url = fullbg_url[0].replace('webp', 'jpg')
    # print(bg_url)
    # print(fullbg_url)

    # 下载图片
    bg_image = requests.get(bg_url).content
    fullbg_image = requests.get(fullbg_url).content
    print('完成图片下载')

    # 写入图片
    bg_image_file = BytesIO(bg_image)
    fullbg_image_file = BytesIO(fullbg_image)

    # 合成图片
    bg_Image = mergy_Image(bg_image_file, bg_location_list)
    fullbg_Image = mergy_Image(fullbg_image_file, fullbg_location_list)
    # bg_Image.show()
    # fullbg_Image.show()

    # 计算缺口偏移距离
    distance = get_distance(bg_Image, fullbg_Image)
    print('得到距离：%s' % str(distance))

    newstart_drag(driver, distance)

#使用canvas结构的拖动验证码
def newrecognize_code(driver):

    # 下面的js代码根据canvas文档说明而来
    print("开始获取图片1")
    JS = 'return document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL("image/png");'
    # 执行 JS 代码并拿到图片 base64 数据
    im_info = driver.execute_script(JS)  # 执行js文件得到带图片信息的图片数据
    im_base64 = im_info.split(',')[1]  # 拿到base64编码的图片信息
    im_bytes = base64.b64decode(im_base64)  # 转为bytes类型


    with open('../bg1.jpg', 'wb') as f:  # 保存图片到本地
        f.write(im_bytes)
    bg_image_file=Image.open('../bg1.jpg')
    print("开始获取图片2")
    JS2full = 'return document.getElementsByClassName("geetest_canvas_fullbg geetest_fade geetest_absolute")[0].toDataURL("image2/png");'
    # 执行 JS 代码并拿到图片 base64 数据
    im_info = driver.execute_script(JS2full)  # 执行js文件得到带图片信息的图片数据
    im_base64 = im_info.split(',')[1]  # 拿到base64编码的图片信息
    im_bytes2 = base64.b64decode(im_base64)  # 转为bytes类型
    with open('../bg2.jpg', 'wb') as f:  # 保存图片到本地
        f.write(im_bytes2)
    fullbg_image_file = Image.open('../bg2.jpg')


        # 计算缺口偏移距离
    distance = get_distance(bg_image_file, fullbg_image_file)
    print('得到距离：%s' % str(distance))

    newstart_drag(driver, distance)


def inputform():
    #等到登录界面出现
    print('获取登录窗口数据')
    # 等到下一页按钮可点再点击
    inputusername = WAIT.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-username"]')))
    inputpass = WAIT.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-passwd"]')))
    submit = WAIT.until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="geetest-wrap"]/div/div[5]/a[1]')))

    inputusername.send_keys('username')
    inputpass.send_keys('password')
    submit.click()
    time.sleep(1)


if __name__ == '__main__':

    # 获取滑块按钮
    driver.get(url)
    inputform()
    #slider = WAIT.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#gc-box > div > div.gt_slider > div.gt_slider_knob.gt_show")))

    newrecognize_code(driver)


    driver.close()

