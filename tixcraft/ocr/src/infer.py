import argparse
from pathlib import Path

import pandas as pd
import torch
from model import CaptchaModel
from PIL import Image
from torchvision import transforms
from utils import CHARACTER_SET, decode_prediction

# ----- 路徑設定 -----
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / "ocr_captcha_dataset" / "dataset" / "images"
LABEL_CSV = BASE_DIR / "ocr_captcha_dataset" / "dataset" / "labels.csv"
MODEL_PATH = BASE_DIR / "output" / "best_model.pth"  # EarlyStopping 儲存的檔名

# ----- 圖片 Preprocess （要和 train 時一致） -----
transform = transforms.Compose(
    [transforms.Grayscale(), transforms.Resize((100, 120)), transforms.ToTensor()]
)


def predict_one(image_path: Path, model: CaptchaModel, device: torch.device) -> str:
    """對單張圖片做預測，回傳解碼後的字串"""
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0).to(device)  # (1, C, H, W)

    with torch.no_grad():
        logits = model(x)  # (B=1, T, C)
        ctc_in = logits.log_softmax(2).permute(1, 0, 2)  # (T, B, C)
    return decode_prediction(ctc_in)[0]  # 取第 0 張的字串


def load_model(device: torch.device) -> CaptchaModel:
    """載入模型並回傳"""
    model = CaptchaModel(num_classes=len(CHARACTER_SET))
    # weights_only=True 可以避免 pickle 安全風險（PyTorch 2.3+）
    state = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model.load_state_dict(state)
    return model.to(device).eval()


def batch_evaluate(model: CaptchaModel, device: torch.device):
    """對整個 dataset 做預測並計算 sequence-level accuracy"""
    df = pd.read_csv(LABEL_CSV)
    total = len(df)
    correct = 0
    for _, row in df.iterrows():
        img_path = IMG_DIR / row["filename"]
        pred = predict_one(img_path, model, device)
        if pred == row["label"]:
            correct += 1
    acc = correct / total if total > 0 else 0
    print(f"\n▶️ 批次預測結果： {correct}/{total}，準確率 = {acc:.2%}")


def main():
    parser = argparse.ArgumentParser(description="Captcha OCR Inference")
    parser.add_argument(
        "--image", "-i", type=str, help="要預測的圖片檔案路徑（相對或絕對）"
    )
    parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="啟用整批預測並計算準確率（會讀 labels.csv）",
    )
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 使用裝置：{device}")

    model = load_model(device)

    if args.batch:
        batch_evaluate(model, device)
    else:
        # 單張預測
        img_path = Path(args.image) if args.image else IMG_DIR / "captcha_1361.png"
        if not img_path.exists():
            raise FileNotFoundError(f"找不到圖片：{img_path}")
        pred = predict_one(img_path, model, device)
        print(f"\n🖼  圖片：{img_path.name}\n🔤 辨識結果：{pred}")


if __name__ == "__main__":
    main()
