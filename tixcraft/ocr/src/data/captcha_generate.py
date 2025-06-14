"""
產生 OCR 驗證碼圖片與 labels.csv 檔案。
字體：Spicy Rice；背景藍 #036CDF；字體白色 #FFFFFF；
每張圖為 120x100，含 4 個小寫字母，帶隨機字體大小、旋轉與輕度重疊。
圖片名稱從 captcha_1.png 開始。
"""

import csv
import os
import random
import string
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# ===== 參數設定 =====
NUM_IMAGES = 10000  # 圖片總數
IMG_SIZE: Tuple[int, int] = (120, 100)  # 單張圖片像素
BG_COLOR: str = "#036CDF"  # 圖片背景顏色
FONT_COLOR: str = "#FFFFFF"  # 字體顏色
CHARS = string.ascii_lowercase  # 驗證碼字元集
CHARS_PER_IMAGE = 4  # 每張字元數
FONT_SIZE_RANGE = (42, 58)  # 隨機選擇的字體大小（單位為像素）
ROTATE_RANGE = (-15, 15)  # 隨機旋轉的角度範圍（單位為度）
MAX_NEG_OVERLAP = 12  # 相鄰字元間最大負間距（單位為像素）
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
    w_img, h_img = base_size[0] * SCALE, base_size[1] * SCALE
    base = Image.new("RGBA", (w_img, h_img), BG_COLOR)

    char_imgs: List[Image.Image] = []
    total_width = 0

    for ch in text:
        font_size = random.randint(*FONT_SIZE_RANGE) * SCALE
        font = ImageFont.truetype(FONT_PATH, font_size)
        ch_img = render_letter(ch, font)
        angle = random.randint(*ROTATE_RANGE)
        ch_img = ch_img.rotate(angle, resample=Image.BICUBIC, expand=True)
        char_imgs.append(ch_img)
        total_width += ch_img.width

    overlaps = [
        random.randint(-MAX_NEG_OVERLAP * SCALE, 4 * SCALE)
        for _ in range(len(text) - 1)
    ]
    total_width += sum(overlaps)

    x = (w_img - total_width) // 2
    y = (h_img - max(img.height for img in char_imgs)) // 2

    for i, ch_img in enumerate(char_imgs):
        base.alpha_composite(ch_img, dest=(x, y))
        x += ch_img.width + (overlaps[i] if i < len(overlaps) else 0)

    final = base.resize(base_size, resample=Image.LANCZOS).convert("RGB")
    return final


def generate_dataset():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(["filename", "label"])

        for idx in tqdm(range(1, NUM_IMAGES + 1), desc="產生驗證碼圖片中"):
            text = random_text()
            img = compose_captcha(text, IMG_SIZE)
            fname = f"captcha_{idx:04d}.png"
            img.save(IMAGE_DIR / fname, format="PNG", optimize=True)
            writer.writerow([fname, text])


if __name__ == "__main__":
    if not Path(FONT_PATH).exists():
        raise FileNotFoundError(f"❌ 找不到字型檔：{FONT_PATH}")
    generate_dataset()
    print(
        f"\n✅ 成功產生 {NUM_IMAGES} 張驗證碼圖片與標籤檔！\n📂 輸出資料夾：{OUTPUT_DIR.resolve()}"
    )
