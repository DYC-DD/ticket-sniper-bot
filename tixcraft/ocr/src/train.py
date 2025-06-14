import os
from pathlib import Path

import torch
from dataset import CaptchaDataset
from model import CaptchaModel
from torch.nn import CTCLoss
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from utils import CHARACTER_SET, decode_prediction

BASE_DIR = Path(__file__).resolve().parent.parent
csv_path = BASE_DIR / "ocr_captcha_dataset" / "dataset" / "labels.csv"
img_dir = BASE_DIR / "ocr_captcha_dataset" / "dataset" / "images"
output_dir = BASE_DIR / "output"
os.makedirs(output_dir, exist_ok=True)

# 加強資料增強：訓練 vs 驗證
train_transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.Resize((100, 120)),
        transforms.RandomAffine(15, translate=(0.1, 0.1), scale=(0.9, 1.1), shear=5),
        transforms.ColorJitter(brightness=0.2),
        transforms.ToTensor(),
    ]
)
val_transform = transforms.Compose(
    [
        transforms.Grayscale(),
        transforms.Resize((100, 120)),
        transforms.ToTensor(),
    ]
)


# 自訂 Dataset，可接收不同 transform
class CaptchaDatasetWithAug(CaptchaDataset):
    def __init__(self, csv_path, image_dir, transform):
        super().__init__(csv_path, image_dir)
        self.transform = transform


def collate_fn(batch):
    imgs, labels = zip(*batch)
    imgs = torch.stack(imgs)
    lengths = [len(l) for l in labels]
    labels = torch.cat(labels)
    return imgs, labels, lengths


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("使用裝置：", device)

    full_ds = CaptchaDatasetWithAug(csv_path, img_dir, train_transform)
    val_size = int(len(full_ds) * 0.2)
    train_ds, val_ds = random_split(full_ds, [len(full_ds) - val_size, val_size])
    # val_ds 用 val_transform 覆蓋
    val_ds.dataset.transform = val_transform

    train_loader = DataLoader(
        train_ds, batch_size=64, shuffle=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collate_fn)

    model = CaptchaModel(num_classes=len(CHARACTER_SET)).to(device)
    criterion = CTCLoss(blank=0, zero_infinity=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = StepLR(optimizer, step_size=10, gamma=0.5)

    best_val_loss = float("inf")
    patience, counter = 5, 0

    for epoch in range(1, 51):
        # ———— train ————
        model.train()
        total_loss = 0
        for imgs, labels, L in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs).log_softmax(2).permute(1, 0, 2)
            input_lens = torch.full(
                (outputs.size(1),), outputs.size(0), dtype=torch.long
            )
            loss = criterion(outputs, labels, input_lens, torch.tensor(L))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        train_loss = total_loss / len(train_loader)

        # ———— validate ————
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for imgs, labels, L in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs).log_softmax(2).permute(1, 0, 2)
                input_lens = torch.full(
                    (outputs.size(1),), outputs.size(0), dtype=torch.long
                )
                val_loss += criterion(
                    outputs, labels, input_lens, torch.tensor(L)
                ).item()
                preds = decode_prediction(outputs)
                # 計算 Sequence-level 準確
                for p, t in zip(
                    preds, val_loader.dataset.dataset.data["label"].iloc[: len(preds)]
                ):
                    correct += p == t
                    total += 1
        val_loss /= len(val_loader)
        val_acc = correct / total

        print(
            f"Epoch {epoch:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.3f}"
        )

        # Scheduler & EarlyStopping
        scheduler.step()
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            counter = 0
            torch.save(model.state_dict(), output_dir / "best_model.pth")
        else:
            counter += 1
            if counter >= patience:
                print("EarlyStopping!")
                break

    print("訓練結束，最佳模型已儲存。")


if __name__ == "__main__":
    train()
