"""
搶票練習網爬蟲
"""

import os
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://ticket-training.onrender.com"
TARGET_URL = urljoin(
    BASE_URL, "/checking?seat=VIP%20搖滾站區&price=8800&color=%23e60122"
)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "captcha_crawler")
DOWNLOAD_COUNT = 100  # 張數

os.makedirs(SAVE_DIR, exist_ok=True)

# Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver.get(TARGET_URL)

# 等待驗證碼圖片載入
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "captcha-image"))
)

# 開始下載迴圈
for i in range(DOWNLOAD_COUNT):
    try:
        img_element = driver.find_element(By.ID, "captcha-image")
        img_url = img_element.get_attribute("src")

        # 若圖片路徑為相對路徑 轉換成絕對路徑
        full_url = urljoin(BASE_URL, img_url)

        # 使用 requests 下載圖片
        response = requests.get(full_url)
        if response.status_code == 200:
            with open(os.path.join(SAVE_DIR, f"captcha_{i+1:04}.png"), "wb") as f:
                f.write(response.content)
            print(f"✅ 已下載第 {i+1} 張驗證碼")
        img_element.click()
        time.sleep(0.2)  # 等待圖片換新速度

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        break

driver.quit()
print("🎉 所有圖片下載完成")


"""
==========================================================================================
官網爬蟲 注意可能被鎖 IP !!!
"""

# import os
# import subprocess
# import sys
# import time
# from pathlib import Path
# from urllib.parse import urljoin

# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from tqdm import tqdm

# os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# sys.stderr = open(os.devnull, "w")

# BASE_URL = "https://tixcraft.com"
# TARGET_URL = "https://tixcraft.com/ticket/ticket/25_xalive/19055/4/85"
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# SAVE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "captcha_crawler")
# DOWNLOAD_COUNT = 10

# os.makedirs(SAVE_DIR, exist_ok=True)

# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--log-level=3")

# service = Service()
# service.creationflags = subprocess.CREATE_NO_WINDOW
# service.log_path = os.devnull

# driver = webdriver.Chrome(service=service, options=chrome_options)
# driver.get(TARGET_URL)

# WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.ID, "TicketForm_verifyCode-image"))
# )

# for i in tqdm(range(DOWNLOAD_COUNT), desc="下載中"):
#     try:
#         WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "TicketForm_verifyCode-image"))
#         )
#         img_element = driver.find_element(By.ID, "TicketForm_verifyCode-image")
#         img_url = img_element.get_attribute("src")
#         full_url = urljoin(BASE_URL, img_url)

#         response = requests.get(full_url)
#         if response.status_code == 200:
#             save_path = os.path.join(SAVE_DIR, f"captcha_{i+1:04}.png")
#             with open(save_path, "wb") as f:
#                 f.write(response.content)

#         driver.execute_script("arguments[0].click();", img_element)
#         time.sleep(0.3)

#     except Exception as e:
#         tqdm.write(f"❌ 發生錯誤：{e}")
#         break

# driver.quit()
# print("🎉 所有圖片下載完成")
