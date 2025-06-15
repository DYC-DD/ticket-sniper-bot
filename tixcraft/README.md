# Tixcraft

## 搶票流程

1. 該場網站，點擊 `立即購票`
2. 選擇場次，點選 `立即訂購`
3. 選擇票價與區域，點選 `某區`
4. 數量選擇 `1~4`
5. `勾選` 已詳細閱讀...
6. `輸入驗證碼`
7. 點擊 `確認張數`
   > 如果 `輸入驗證碼` 輸入錯誤，跳回第 4 步驟

[拓元搶票練習小工具](https://ticket-training.onrender.com/)

## Tixcraft 網站架構

- 背後伺服器使用 AWS：[AWS 負載平衡](https://aws.amazon.com/tw/elasticloadbalancing/)
- 查找電腦背後是連到哪個伺服器 IP：使用 [nslookup](https://www.nslookup.io/) 來查詢
