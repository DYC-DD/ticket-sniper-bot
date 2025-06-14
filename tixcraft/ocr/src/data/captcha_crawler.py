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

# 網站
BASE_URL = "https://ticket-training.onrender.com"
TARGET_URL = urljoin(
    BASE_URL, "/checking?seat=VIP%20搖滾站區&price=8800&color=%23e60122"
)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(CURRENT_DIR, "..", "..", "data", "captcha_crawler")
DOWNLOAD_COUNT = 1  # 張數

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

        # 點擊圖片以換下一張（觸發 fetch("/captcha")）
        img_element.click()
        time.sleep(0.2)  # 等待圖片換新速度

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        break

driver.quit()
print("🎉 所有圖片下載完成")
