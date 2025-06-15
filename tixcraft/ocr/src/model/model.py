import torch.nn as nn


class CaptchaModel(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.cnn = nn.Sequential(
            # Conv Block 1
            nn.Conv2d(1, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            # Conv Block 2
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            # Conv Block 3
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),  # H:100→50→25→12, W:120→60→30→15
        )
        # time steps = 15
        self.fc = nn.Linear(128 * 12, 256)
        self.dropout = nn.Dropout(0.3)
        self.rnn = nn.LSTM(
            input_size=256,
            hidden_size=128,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
            dropout=0.3,
        )
        self.output = nn.Linear(128 * 2, num_classes + 1)

    def forward(self, x):
        x = self.cnn(x)  # (B,128,12,15)
        x = x.permute(0, 3, 1, 2)  # (B, W=15, C=128, H=12)
        b, w, c, h = x.size()
        x = x.reshape(b, w, c * h)  # (B,15,128*12)
        x = self.fc(x)  # (B,15,256)
        x = self.dropout(x)
        x, _ = self.rnn(x)  # (B,15,256)
        x = self.output(x)  # (B,15,num_classes+1)
        return x
