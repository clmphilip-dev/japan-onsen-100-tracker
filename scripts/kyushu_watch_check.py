#!/usr/bin/env python3
"""Refresh kyushu-watch-data.json / kyushu-watch-status.json via Jalan ZAM.

Read-only. Does not book. Intended for a daily routine.
Hotels with jalan_id use ZAM; Tripla-only / no-jalan stay as need_official with deep links.
Captures lowestTotalPrice (2大人・2泊合計 JPY) when stock is open.
Run from repo root: python3 scripts/kyushu_watch_check.py
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "kyushu-watch-data.json"
STATUS_PATH = ROOT / "kyushu-watch-status.json"
API = "https://jlnzam.net/v2/search"
API_KEY = "XBgewN64LJ"
HKT = timezone(timedelta(hours=8))

PRICE_NOTE_OPEN = "2人2泊合計／じゃらん最低價（lowestTotalPrice）"
PRICE_NOTE_NONE = "未標價"
PRICE_NOTE_NA = None  # for non-open cells


def empty_price_fields(note: str | None = PRICE_NOTE_NA) -> dict:
    return {
        "price_jpy": None,
        "price_per_person_jpy": None,
        "price_note_zh": note,
        "currency": "JPY",
    }


def price_fields_from_summary(summary_row: dict | None, status: str) -> dict:
    """Extract prices only when status is open and API returns a number."""
    if status != "open" or not summary_row:
        return empty_price_fields(PRICE_NOTE_NA if status != "open" else PRICE_NOTE_NONE)
    raw = summary_row.get("lowestTotalPrice")
    if raw is None:
        return empty_price_fields(PRICE_NOTE_NONE)
    try:
        total = int(raw)
    except (TypeError, ValueError):
        return empty_price_fields(PRICE_NOTE_NONE)
    if total <= 0:
        return empty_price_fields(PRICE_NOTE_NONE)
    # adultPrice in roomPlans is per person per night; lowestTotalPrice is
    # 2 adults × 2 nights stay total. Per-person for the stay = total // 2.
    return {
        "price_jpy": total,
        "price_per_person_jpy": total // 2,
        "price_note_zh": PRICE_NOTE_OPEN,
        "currency": "JPY",
    }


def zam_check(jalan_id: str) -> dict:
    body = json.dumps(
        {
            "targets": [jalan_id],
            "targetType": "HOTEL_ID",
            "nights": 2,
            "rooms": [{"adults": 2}],
            "hotelTypes": [],
            "extras": [],
            "checkInDateSearchFrom": "2026-12-28",
            "checkInDateSearchTo": "2027-01-06",
        }
    ).encode()
    req = urllib.request.Request(
        API,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": API_KEY,
            "User-Agent": "Mozilla/5.0 KyushuWatch/1.0",
            "Origin": "https://www.jalan.net",
            "Referer": "https://www.jalan.net/",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    now = datetime.now(HKT)
    checked_at = now.isoformat(timespec="seconds")
    label = f"最後檢查：{now.strftime('%Y-%m-%d %H:%M:%S')}（香港時間）"
    windows = data["windows"]
    checks = []
    cache_bust = now.strftime("%Y%m%d%H%M")

    for h in data["hotels"]:
        if h.get("skip_rooms"):
            for w in windows:
                row = {
                    "hotel_id": h["id"],
                    "window_id": w["id"],
                    "status": "non_stay",
                    "source": None,
                    "source_url": h.get("official_url"),
                    "checked_at": checked_at,
                    "note_zh": "非住宿／日歸溫泉",
                    "stock": None,
                }
                row.update(empty_price_fields())
                checks.append(row)
            continue
        jid = h.get("jalan_id")
        if not jid:
            for w in windows:
                row = {
                    "hotel_id": h["id"],
                    "window_id": w["id"],
                    "status": "need_official",
                    "source": None,
                    "source_url": (
                        h.get("other_booking")
                        or h.get("booking_url")
                        or h.get("rakuten_url")
                        or h.get("official_url")
                    ),
                    "checked_at": checked_at,
                    "note_zh": "無じゃらん公開庫存 API；請開官網預約站／楽天確認",
                    "stock": None,
                }
                row.update(empty_price_fields())
                checks.append(row)
            continue
        try:
            resp = zam_check(jid)
            hotels = (resp.get("data") or {}).get("hotels") or []
            summary = {}
            if hotels:
                for s in hotels[0].get("summary") or []:
                    summary[s["checkInDate"]] = s
            for w in windows:
                y, m, d = w["checkin"].split("-")
                deep = (
                    f"https://www.jalan.net/yad{jid}/plan/"
                    f"?stayYear={y}&stayMonth={int(m)}&stayDay={int(d)}"
                    f"&stayCount=2&roomCount=1&adultNum=2"
                )
                srow = summary.get(w["checkin"])
                stock = None if srow is None else (srow.get("totalStock") or 0)
                if srow is None:
                    status, note = "full", "じゃらん（2大人・2泊）：該入住日無空室／未上架"
                elif stock > 0:
                    status, note = "open", f"じゃらん（2大人・2泊）：殘室約 {stock}"
                else:
                    status, note = "full", "じゃらん（2大人・2泊）：totalStock=0"
                row = {
                    "hotel_id": h["id"],
                    "window_id": w["id"],
                    "status": status,
                    "source": "jalan_zam",
                    "source_url": deep,
                    "checked_at": checked_at,
                    "note_zh": note,
                    "stock": stock,
                }
                row.update(price_fields_from_summary(srow, status))
                if status == "open" and row["price_jpy"] is not None:
                    row["note_zh"] = (
                        f"{note} · ¥{row['price_jpy']:,}（2人2泊最低）"
                    )
                checks.append(row)
            time.sleep(0.35)
        except Exception as e:  # noqa: BLE001
            for w in windows:
                y, m, d = w["checkin"].split("-")
                deep = (
                    f"https://www.jalan.net/yad{jid}/plan/"
                    f"?stayYear={y}&stayMonth={int(m)}&stayDay={int(d)}"
                    f"&stayCount=2&roomCount=1&adultNum=2"
                )
                row = {
                    "hotel_id": h["id"],
                    "window_id": w["id"],
                    "status": "unchecked",
                    "source": None,
                    "source_url": deep,
                    "checked_at": checked_at,
                    "note_zh": f"查詢失敗：{e}",
                    "stock": None,
                }
                row.update(empty_price_fields())
                checks.append(row)

    data["checks"] = checks
    data["meta"]["last_checked_at"] = checked_at
    data["meta"]["last_checked_label_zh"] = label
    data["meta"]["cache_bust"] = cache_bust
    data["meta"]["disclaimer_zh"] = (
        "空室與價錢以じゃらん公開庫存 API（ZAM）快照為準（2大人・1房・2泊合計最低價／"
        "lowestTotalPrice）。稅費以訂房頁顯示為準；年末假期變動快，請以訂房頁最終確認。"
        "非住宿設施不會查房。無じゃらん ID 者無自動價錢。"
    )
    data["meta"]["price_definition_zh"] = (
        "price_jpy＝じゃらん該入住日最低方案合計（2大人・2泊）；"
        "price_per_person_jpy＝合計÷2（一人2泊）。滿房／需官網／非住宿／未查 → 無價錢。"
    )
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    name_by = {h["id"]: h["property_jp"] for h in data["hotels"]}
    win_by = {w["id"]: w for w in windows}
    open_rooms = []
    priced = 0
    for c in checks:
        if c["status"] != "open":
            continue
        w = win_by[c["window_id"]]
        if c.get("price_jpy") is not None:
            priced += 1
        open_rooms.append(
            {
                "hotel_id": c["hotel_id"],
                "hotel_jp": name_by[c["hotel_id"]],
                "window_id": c["window_id"],
                "checkin": w["checkin"],
                "checkout": w["checkout"],
                "label_zh": w["label_zh"],
                "stock": c.get("stock"),
                "source_url": c.get("source_url"),
                "price_jpy": c.get("price_jpy"),
                "price_per_person_jpy": c.get("price_per_person_jpy"),
                "price_note_zh": c.get("price_note_zh"),
                "currency": c.get("currency") or "JPY",
            }
        )
    status = {
        "generated_at": checked_at,
        "timezone": "Asia/Hong_Kong",
        "open_rooms_count": len(open_rooms),
        "open_rooms_with_price": priced,
        "open_rooms": open_rooms,
        "full_cells": sum(1 for c in checks if c["status"] == "full"),
        "need_official_cells": sum(1 for c in checks if c["status"] == "need_official"),
        "non_stay_cells": sum(1 for c in checks if c["status"] == "non_stay"),
        "unchecked_cells": sum(1 for c in checks if c["status"] == "unchecked"),
        "total_cells": len(checks),
        "price_definition_zh": data["meta"]["price_definition_zh"],
        "note_zh": "供每日 routine 比對：若 open_rooms 出現新組合再通知 Philip。價錢為じゃらん 2人2泊最低合計。",
    }
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"open_rooms={status['open_rooms_count']} priced={priced} "
        f"full={status['full_cells']} need={status['need_official_cells']}"
    )


if __name__ == "__main__":
    main()
