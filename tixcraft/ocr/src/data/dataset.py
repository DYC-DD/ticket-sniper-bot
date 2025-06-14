import pandas as pd
import torch
from model.utils import char2idx
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class CaptchaDataset(Dataset):
    def __init__(self, csv_path, image_dir):
        self.data = pd.read_csv(csv_path)
        self.image_dir = image_dir
        self.transform = transforms.Compose(
            [
                transforms.Grayscale(),  # 灰階
                transforms.Resize((100, 120)),
                transforms.ToTensor(),
            ]
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image_path = f"{self.image_dir}/{row['filename']}"
        label = row["label"]

        image = Image.open(image_path)
        image = self.transform(image)

        label_tensor = torch.tensor([char2idx[c] for c in label], dtype=torch.long)
        return image, label_tensor
