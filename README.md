# 《日本溫泉100強》追蹤

靜態站（GitHub Pages）：HOY TV／電視東京溫泉地排名對照＋代表性溫泉旅館一覽。

## 頁面

- [首頁](https://clmphilip-dev.github.io/japan-onsen-100-tracker/)
- [Top 10](https://clmphilip-dev.github.io/japan-onsen-100-tracker/ranks.html)
- [排名對照](https://clmphilip-dev.github.io/japan-onsen-100-tracker/compare.html)
- [住宿／設施](https://clmphilip-dev.github.io/japan-onsen-100-tracker/hotels.html)（預設：節目推薦）
- [節目推薦名單](https://clmphilip-dev.github.io/japan-onsen-100-tracker/hotels.html?list=show)
- [全部住宿](https://clmphilip-dev.github.io/japan-onsen-100-tracker/hotels.html?list=all)

## 資料

- `data.json`：排名＋旅館
  - `in_show: true` ≈ 95 間節目提及／交叉核對（HOY／電視東京）
  - `in_show: false` ≈ 溫泉地人氣宿（じゃらん／楽天區域榜擴充）
- 住宿範圍＝2024＋2026 榜上溫泉地之代表性旅館，**非**日本全國所有溫泉旅館
- `Japan_Onsen_100_Tracker.xlsx`：`Hotels_All` 含 `In_Show` 欄；`Hotels_Mentioned` 為節目名單

## 本地

用任意靜態伺服器開啟（需能讀 `data.json`），例如：`python3 -m http.server 8080`

## 2026-11-02 增補

- `data.areas[]`：全部排名溫泉地的香港客交通／季節／人潮提示
- 住宿頁：地方篩選、香港交通列、日歸／貸切・客室露天徽章與篩選
- 阿蘇溫泉鄉缺口：補上湯巡追荘（じゃらん公開頁）；HOY 重溫暫不可用提示

## 草津空室監控

- [草津監控](https://clmphilip-dev.github.io/japan-onsen-100-tracker/kusatsu-watch.html)：草津溫泉設施（資料檔動態載入） × 2026-12-28～2027-01-08 內任意連續 2 晚（2 大人）
- `kusatsu-watch-data.json`：旅館、視窗、checks[] 快照（可供 routine 覆寫）
- `kusatsu-watch-status.json`：`open_rooms` 摘要（有房組合）
- 重查：`python3 scripts/kusatsu_watch_check.py`（じゃらん ZAM 唯讀；不訂房；有房時寫入 2人2泊最低合計價）

## 九州空室監控

- [九州監控](https://clmphilip-dev.github.io/japan-onsen-100-tracker/kyushu-watch.html)：tracker 內全部九州旅館 × 2026-12-28～2027-01-08 內任意連續 2 晚（2 大人）
- `kyushu-watch-data.json`：旅館（含縣／溫泉地）、視窗、checks[] 快照
- `kyushu-watch-status.json`：`open_rooms` 摘要（有房組合＋價錢）
- 重查：`python3 scripts/kyushu_watch_check.py`（じゃらん ZAM 唯讀；不訂房；有房時寫入 2人2泊最低合計價）
- 日歸溫泉不查房；無じゃらん ID 者標「需官網」
