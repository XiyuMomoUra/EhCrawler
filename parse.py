from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

def parse_rating(rating_text):
    opacity = rating_text[rating_text.index('opacity:') + len('opacity:'):].replace(' ', '').replace(';', '').strip()
    is_valid = False
    if opacity == '1':
        is_valid = True

    rating_text = rating_text[rating_text.index('background-position:') + len('background-position:'):rating_text.index(';')].strip()
    rating_main = int(rating_text[:rating_text.index('px')])
    rating_text = rating_text[rating_text.index('px') + len('px'):].strip()
    rating_sub = int(rating_text[:rating_text.index('px')])
    rating = 5 + rating_main / 16
    if rating_sub == -21:
        rating -= 0.5

    return {'rating': rating, 'is_valid': is_valid}

def parse_page(driver):
    infos = []
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gltm"))
    )
    # 找到所有行（<tr>）
    rows = table.find_elements(By.TAG_NAME, "tr")
    # 遍历每一行
    rows = rows[1:]
    for row in rows:
        info = {}

        # 获取类型
        type_text = row.find_element(By.CLASS_NAME, 'gl1m').text.strip()
        info['type'] = type_text

        # 获取发布时间
        release_time_text = row.find_element(By.CLASS_NAME, 'gl2m').text.strip()
        info['time'] = release_time_text

        # 获取title与链接
        resource_info = row.find_element(By.CLASS_NAME, 'glname')
        resource_link = resource_info.find_element(By.TAG_NAME, 'a').get_attribute("href")
        title = resource_info.find_element(By.CLASS_NAME, 'glink').text
        info['title'] = title
        info['link'] = resource_link

        # 获取评分
        rating_text = row.find_element(By.CLASS_NAME, 'ir').get_attribute("style")
        rating = parse_rating(rating_text)
        info['rating'] = rating['rating']
        info['rating_valid'] = rating['is_valid']

        # 获取上传者
        try:
            uploader = row.find_element(By.CLASS_NAME, 'gl5m').find_element(By.TAG_NAME, 'a').get_attribute(
                "href").strip()
            uploader = uploader[30:]
        except:
            uploader = '(Disowned)'
        info['uploader'] = uploader

        # print(info, '\n', '=' * 100)
        infos.append(info)

    return infos

def can_prev(driver):
    timeout0 = 60
    step = 1
    timeout1 = 240
    find_time = 0

    elements = []
    while find_time < timeout1:
        elements = driver.find_elements(By.ID, "dprev")
        if elements:
            break
        else:
            find_time += step
        if find_time % timeout0 == 0:
            driver.refresh()
        time.sleep(step)

    if find_time >= timeout1:
        print('エロ発生！！Pre page time out!')
        return True
    tag = elements[0].tag_name
    return tag == 'a'