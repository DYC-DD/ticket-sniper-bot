# 📂 `data` 資料夾說明

本資料夾包含 OCR 訓練與測試所需的各類資料來源，包含自動生成的訓練集、從網頁抓取的樣本、以及字型資源等。

## 📁 `captcha_generate/`

透過 [`captcha_generate.py`](../src/data/captcha_generate.py) 自動產生的訓練資料集，包含圖片與對應標籤。

- `images/`：系統自動產生的驗證碼圖片，命名格式為 `captcha_<編號>.png`
- `labels.csv`：每張圖片對應的正確標籤（4 個小寫英文字母）

**範例：**
| filename | label |
| ------------------ | ------ |
| `captcha_0001.png` | `dsbv` |
| `captcha_0002.png` | `utej` |
| `captcha_0003.png` | `qflk` |
| `captcha_0004.png` | `fogu` |
| `captcha_0005.png` | `qmzq` |

## 📁 `captcha_crawler/`

透過 [`captcha_crawler.py`](../src/data/captcha_crawler.py) 自動爬取[拓元搶票練習網站](https://ticket-training.onrender.com/)的驗證碼圖片。

- 爬取結果將儲存，命名格式為 `captcha_<編號>.png`
- 此資料夾僅為原始圖像蒐集，不含標註資訊
- 若需用於訓練，需人工建立 `labels.csv` 並對應標註每張圖片內容
