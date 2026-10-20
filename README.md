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
