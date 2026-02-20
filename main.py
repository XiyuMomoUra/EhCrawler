from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime, timedelta
import time
import json
import math

from parse import *

DEBUG_MODE = False

# 开始搜寻的日期
# g_start_searching_date = 'earliest'       # 使用'earliest'会从最早开始搜索，跳转到末页
# g_start_searching_date = '07-06-04'       # 指定日期搜索
g_start_searching_date = 'auto'             # 根据现有的json文件从最新数据的前一天开始搜索

g_page_interval_time = 1.0
max_page_count = 100000

with open('eh_cookies.json', 'r', encoding='utf-8') as f:
    origin_cookies = json.load(f)

g_output_path = 'base_infos.json'
g_base_infos = []
try:
    with open(g_output_path, 'r', encoding='utf-8') as f:
        try:
            g_base_infos = json.load(f)
        except:
            pass
except FileNotFoundError:
    pass

infos_count = len(g_base_infos)
start_count = infos_count
print('Load origin infos successfully. There are ' + str(infos_count) + ' infos now.')

g_base_infos.sort(key=lambda x: x['time'])
lastday = (datetime.strptime(g_base_infos[-1]['time'], "%Y-%m-%d %H:%M")- timedelta(days=1)).strftime("%Y-%m-%d")

# === 指定 msedgedriver 的绝对路径 ===
edge_driver_path = r"edgedriver_win64_v143/msedgedriver.exe"  # Windows 示例

# === 配置 Edge 选项（显示浏览器窗口）===
edge_options = Options()
if not DEBUG_MODE:
    edge_options.add_argument("--headless")  # 无头模式

# === 创建 Service 对象并指定 driver 路径 ===
service = Service(executable_path=edge_driver_path)

# === 启动浏览器 ===
driver = webdriver.Edge(service=service, options=edge_options)

# === 访问目标网站（必须先访问域名才能设置cookies）===
target_url = "https://exhentai.org/"
driver.get(target_url)

eh_cookies = []
for cookie in origin_cookies:
    tmp = {}
    tmp['name'] = cookie['name']
    tmp['value'] = cookie['value']
    tmp['path'] = cookie['path']
    tmp['domain'] = cookie['domain']
    eh_cookies.append(tmp)

for cookie in eh_cookies:
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print(f"添加 Cookie 失败: {cookie['name']}, 错误: {e}")

# 刷新使 cookies 生效
driver.refresh()

# 等待页面加载完成
WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "dp")))

# 获取当前exhentai总条目数，用于估计剩余时间
total_infos_text = driver.find_element(By.CLASS_NAME, "searchtext").text.replace('Found', '').replace('results.', '').replace(',', '').strip()
total_infos = int(total_infos_text)
total_pages = math.ceil(total_infos / 25)
print('ExHentai total items: ' + str(total_infos))

# 若时间设置为最早，则跳转到末页
if g_start_searching_date == 'earliest':
    link_id = 'dlast'
    link = driver.find_element(By.ID, link_id)
    link.click()
# 其他情况跳转至指定日期
else:
    if g_start_searching_date == 'auto':
        g_start_searching_date = lastday
        print('Auto date mode, will start searching from ' + lastday)
    link_id = 'djump'
    link = driver.find_element(By.ID, link_id)
    link.click()
    time.sleep(0.5)
    date_input = driver.find_element(By.ID, "djump")
    date_input.send_keys(g_start_searching_date)
    link_id = 'dnext'
    link = driver.find_element(By.ID, link_id)
    link.click()

def update_info(infos, new_info):
    for i, info in enumerate(infos):
        if info['link'] == new_info['link']:
            info['rating'] = new_info['rating']
            info['rating_valid'] = new_info['rating_valid']
            print('Info is already exist, updating successfully.')
            return True
    infos.append(new_info)
    return False

page_count = 0
start_time = time.time()
try:
    while page_count < max_page_count and can_prev(driver):
        infos = parse_page(driver)
        new_info = 0
        for info in infos:
            if update_info(g_base_infos, info):
                if DEBUG_MODE:
                    print('Info is already exist, updating successfully.')
            else:
                new_info += 1
        page_count += 1
        infos_count += new_info
        print(str(new_info) + ' infos have been added successfully! ' + str(page_count) + ' pages have been processed. There are ' + str(infos_count) + ' infos now.', end='')

        pass_time = time.time() - start_time
        speed = page_count / pass_time
        print(' Process speed: ' + format(speed, '.2f') + ' pages/s.', end='')

        remain_count = total_infos - infos_count
        try:
            remain_time = remain_count / 25 / speed
            days = timedelta(seconds=int(remain_time)).days
            hours, remainder = divmod(timedelta(seconds=int(remain_time)).seconds, 3600)
            minutes, secs = divmod(remainder, 60)
            remain_str = f"{days}d - {hours:02d}:{minutes:02d}:{secs:02d}"
        except:
            remain_str = 'NaN'
            pass

        print(' Remain: ' + remain_str + '.')

        if page_count % 500 == 0:
            with open(g_output_path, 'w', encoding='utf-8') as f:
                json.dump(g_base_infos, f, ensure_ascii=False, indent=4)
            print('500 pages have been processed! Saving files now.')

        time.sleep(g_page_interval_time)
        driver.find_element(By.ID, 'dprev').click()
        time.sleep(0.5)
except KeyboardInterrupt:
    print('Got user interrupt, now trying to save the file')
    pass
except Exception as e:
    print('エロ発生！！Now trying to save the file')
    print('ERROR: ', e)
    pass

try:
    with open(g_output_path, 'w', encoding='utf-8') as f:
        json.dump(g_base_infos, f, ensure_ascii=False, indent=4)
    print('Infos saved successfully! Quit.')
except Exception as e:
    print('Save infos fail!! ERROR: ', e)
    pass

driver.quit()