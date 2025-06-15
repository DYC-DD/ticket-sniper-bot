"""
產生 OCR 驗證碼圖片與 labels.csv 檔案。
字體：Spicy Rice；背景藍 #036CDF；字體白色 #FFFFFF；
每張圖為 120x100，含 4 個小寫字母，帶隨機字體大小、旋轉與輕度重疊。
圖片名稱從 captcha_1.png 開始。
"""

import csv
import math
import os
import random
import string
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# ===== 參數設定 =====
NUM_IMAGES = 30000  # 圖片總數
IMG_SIZE: Tuple[int, int] = (120, 100)  # 單張圖片像素
BG_COLOR: str = "#036CDF"  # 圖片背景顏色
FONT_COLOR: str = "#FFFFFF"  # 字體顏色
CHARS = string.ascii_lowercase  # 驗證碼字元集
CHARS_PER_IMAGE = 4  # 每張字元數
FONT_SIZE_RANGE = (56, 66)  # 隨機選擇的字體大小（單位為像素）
ROTATE_RANGE = (-8, 8)  # 隨機旋轉的角度範圍（單位為度）
MAX_NEG_OVERLAP = 11  # 相鄰字元間最大負間距（單位為像素）
SCALE = 2  # 高解析再縮回避免鋸齒

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = (
    BASE_DIR.parent / ".." / "data" / "font" / "SpicyRice-Regular.ttf"
)  # 字體路徑
OUTPUT_DIR = BASE_DIR / ".." / ".." / "data" / "captcha_generate"  # 輸出主資料夾
CSV_PATH = OUTPUT_DIR / "labels.csv"  # 標籤 CSV 檔案
IMAGE_DIR = OUTPUT_DIR / "images"  # 圖片輸出資料夾


def random_text(length: int = CHARS_PER_IMAGE) -> str:
    return "".join(random.choices(CHARS, k=length))


def render_letter(char: str, font: ImageFont.FreeTypeFont) -> Image.Image:
    bbox = font.getbbox(char)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    letter_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(letter_img)
    draw.text((-bbox[0], -bbox[1]), char, font=font, fill=FONT_COLOR)
    return letter_img


def compose_captcha(text: str, base_size: Tuple[int, int]) -> Image.Image:
    w0, h0 = base_size
    w_img, h_img = w0 * SCALE, h0 * SCALE

    char_imgs: List[Image.Image] = []
    total_w = 0
    max_h = 0
    for ch in text:
        fs = random.randint(*FONT_SIZE_RANGE) * SCALE
        font = ImageFont.truetype(FONT_PATH, fs)
        img_ch = render_letter(ch, font).rotate(
            random.randint(*ROTATE_RANGE), resample=Image.BICUBIC, expand=True
        )
        char_imgs.append(img_ch)
        total_w += img_ch.width
        max_h = max(max_h, img_ch.height)

    overlaps = [
        random.randint(-MAX_NEG_OVERLAP * SCALE, 4 * SCALE)
        for _ in range(len(text) - 1)
    ]
    total_w += sum(overlaps)

    max_angle = max(abs(ROTATE_RANGE[0]), abs(ROTATE_RANGE[1])) * math.pi / 180
    max_font = max(FONT_SIZE_RANGE) * SCALE
    margin = int(max_font * math.sin(max_angle)) + 2

    big_w, big_h = w_img * 3, h_img * 3
    big = Image.new("RGBA", (big_w, big_h), BG_COLOR)

    start_x = (big_w - total_w) // 2
    start_y = (big_h - max_h) // 2
    x = start_x
    for i, img_ch in enumerate(char_imgs):
        big.alpha_composite(img_ch, dest=(x, start_y))
        x += img_ch.width + (overlaps[i] if i < len(overlaps) else 0)

    cx0 = (big_w - w_img) // 2 - margin
    cy0 = (big_h - h_img) // 2 - margin
    cx1 = cx0 + w_img + 2 * margin
    cy1 = cy0 + h_img + 2 * margin
    cropped = big.crop((cx0, cy0, cx1, cy1))

    return cropped.resize((w0, h0), resample=Image.LANCZOS).convert("RGB")


def generate_dataset():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["filename", "label"])

        for idx in tqdm(range(1, NUM_IMAGES + 1), desc="產生驗證碼圖片中"):
            text = random_text()
            img = compose_captcha(text, IMG_SIZE)
            fname = f"captcha_{idx:05d}.png"
            img.save(IMAGE_DIR / fname, format="PNG", optimize=True)
            writer.writerow([fname, text])


if __name__ == "__main__":
    if not Path(FONT_PATH).exists():
        raise FileNotFoundError(f"❌ 找不到字型檔：{FONT_PATH}")
    generate_dataset()
    print(
        f"\n✅ 成功產生 {NUM_IMAGES} 張驗證碼圖片與標籤檔！\n📂 輸出資料夾：{OUTPUT_DIR.resolve()}"
    )
