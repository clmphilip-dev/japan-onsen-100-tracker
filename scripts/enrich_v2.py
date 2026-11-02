#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enrich data.json: areas[], region, hk_access inheritance, bath flags, Aso gap, meta."""
from __future__ import annotations
import json, re, copy
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from area_knowledge import PREF_REGION, PREF_CN, PREF_DEFAULTS, AREA_SPEC

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data.json"
HKT = ZoneInfo("Asia/Hong_Kong")

# Evidence-based facility flags: property_jp -> (day_bath, private_bath)
# day_bath: yes|no|unknown ; private_bath: kashikiri|room_roten|both|unknown|no
FACILITY_EVIDENCE = {
    # day facilities / alerts already in data
    "西の河原露天風呂": ("yes", "unknown"),
    "風風の湯": ("yes", "unknown"),
    "飛鳥乃湯泉": ("yes", "unknown"),
    "観音岩温泉": ("yes", "kashikiri"),  # 貸切専門・日歸
    "たまて箱温泉": ("yes", "unknown"),
    "指宿温泉 砂むし会館 砂楽": ("yes", "unknown"),
    "長門湯本温泉 恩湯": ("yes", "unknown"),
    "四万温泉 日向見温泉 共同浴場": ("yes", "unknown"),
    "下風呂温泉 海峡の湯": ("yes", "unknown"),
    "こうの湯": ("yes", "unknown"),  # 入湯手形 day use known
    # highlights / public listing evidence
    "ひらゆの森": ("unknown", "kashikiri"),
    "皆生游月": ("unknown", "room_roten"),
    "滝乃家": ("unknown", "room_roten"),
    "楓と樹 -FUTOKI-": ("unknown", "room_roten"),
    "妙乃湯": ("unknown", "kashikiri"),
    "城崎温泉 但馬屋": ("unknown", "kashikiri"),
    "旅館 永澤平八": ("unknown", "kashikiri"),
    "熱海温泉ホテル 夢いろは": ("unknown", "kashikiri"),
    "中村屋旅館": ("unknown", "kashikiri"),
    # Jalan public pages (湯巡追荘: 日帰り湯 + 貸切 + 露天付客室)
    "阿蘇内牧温泉 湯巡追荘": ("yes", "both"),
    "湯巡追荘": ("yes", "both"),
}

def build_areas(d: dict) -> list:
    by = {}
    def upsert(area_jp, area_cn, pref, pref_cn=None, r24=None, r26=None):
        if area_jp not in by:
            by[area_jp] = {
                "area_jp": area_jp,
                "area_cn": area_cn,
                "prefecture": pref,
                "prefecture_cn": pref_cn or PREF_CN.get(pref, pref),
                "rank_2024": r24,
                "rank_2026": r26,
            }
        else:
            cur = by[area_jp]
            if area_cn and not cur.get("area_cn"):
                cur["area_cn"] = area_cn
            if pref_cn:
                cur["prefecture_cn"] = pref_cn
            if r24 is not None and cur.get("rank_2024") is None:
                cur["rank_2024"] = r24
            if r26 is not None and cur.get("rank_2026") is None:
                cur["rank_2026"] = r26

    for r in d.get("ranking_2024", []):
        upsert(r["area"], r.get("area_cn"), r["prefecture"], r.get("prefecture_cn"), r24=r["rank"])
    for r in d.get("ranking_2026", []):
        upsert(r["area"], r.get("area_cn"), r["prefecture"], r.get("prefecture_cn"), r26=r["rank"])
    for r in d.get("ranking_compare", []):
        upsert(r["area_jp"], r.get("area_cn"), r["prefecture"], None,
               r24=r.get("rank_2024"), r26=r.get("rank_2026"))

    areas = []
    for a in by.values():
        pref = a["prefecture"]
        region = PREF_REGION.get(pref)
        defaults = PREF_DEFAULTS.get(pref, {})
        spec = AREA_SPEC.get(a["area_jp"], {})
        access_zh = spec.get("access_zh") or defaults.get("access_zh")
        # short hk_access line for hotel inheritance
        hub = spec.get("hk_hub") or defaults.get("hk_hub")
        tband = spec.get("travel_time_band")
        if tband and hub:
            hk_line = f"via {hub}｜{tband}"
        elif hub:
            hk_line = f"via {hub}"
        else:
            hk_line = None
        areas.append({
            "area_jp": a["area_jp"],
            "area_cn": a.get("area_cn") or a["area_jp"],
            "prefecture": pref,
            "prefecture_cn": a.get("prefecture_cn") or PREF_CN.get(pref, pref),
            "region": region,
            "hk_hub": hub,
            "nearest_station": spec.get("nearest_station"),
            "access_zh": access_zh,
            "travel_time_band": tband,
            "rail_pass_note": spec.get("rail_pass_note", defaults.get("rail_pass_note")),
            "best_season_zh": spec.get("best_season_zh") or defaults.get("best_season_zh"),
            "crowd_note_zh": spec.get("crowd_note_zh") or defaults.get("crowd_note_zh"),
            "hk_access_line": hk_line,
            "rank_2024": a.get("rank_2024"),
            "rank_2026": a.get("rank_2026"),
        })
    areas.sort(key=lambda x: (
        x.get("rank_2024") is None,
        x.get("rank_2024") or 9999,
        x["area_jp"],
    ))
    return areas


def area_index(areas):
    return {a["area_jp"]: a for a in areas}


def infer_facility(h):
    name = h.get("property_jp") or ""
    if name in FACILITY_EVIDENCE:
        return FACILITY_EVIDENCE[name]
    # type / alert
    t = (h.get("type") or "").replace("-", "_")
    if t == "day_onsen" or h.get("alert") == "day_onsen":
        day = "yes"
    else:
        day = "unknown"
    priv = "unknown"
    blob = " ".join(str(h.get(k) or "") for k in ("highlights", "description_cn", "price_note"))
    has_kashi = bool(re.search(r"貸切", blob))
    has_roten = bool(re.search(r"露天風呂付客室|客室露天|部屋露天|露天風呂付き客室|専用露天", blob))
    if has_kashi and has_roten:
        priv = "both"
    elif has_kashi:
        priv = "kashikiri"
    elif has_roten:
        priv = "room_roten"
    # day mention in text for non-day types still leave unknown unless clear 日帰り入浴 facility
    if day == "unknown" and re.search(r"日帰り入浴|日歸入浴|立ち寄り湯", blob) and t in ("day_onsen", "day-onsen"):
        day = "yes"
    return day, priv


def enrich_hotels(hotels, areas_by):
    # alias map for Aso naming
    alias = {
        "阿蘇温泉郷": "阿蘇内牧＆地獄温泉",
        "阿蘇内牧＆地獄温泉／阿蘇温泉郷": "阿蘇内牧＆地獄温泉",
    }
    for h in hotels:
        pref = h.get("prefecture")
        h["region"] = PREF_REGION.get(pref)
        area_key = h.get("onsen_area")
        a = areas_by.get(area_key) or areas_by.get(alias.get(area_key, ""))
        if not h.get("hk_access"):
            if a and a.get("hk_access_line"):
                h["hk_access"] = a["hk_access_line"]
                h["hk_access_source"] = "area"
            elif a and a.get("access_zh"):
                # compact English-ish line already used historically; keep short ZH fallback
                hub = a.get("hk_hub") or ""
                band = a.get("travel_time_band") or ""
                h["hk_access"] = "｜".join(x for x in [f"via {hub}" if hub else "", band] if x) or a["access_zh"][:80]
                h["hk_access_source"] = "area"
            else:
                h["hk_access_source"] = None
        else:
            h["hk_access_source"] = h.get("hk_access_source") or "hotel"
        day, priv = infer_facility(h)
        # don't overwrite if already set
        if "day_bath" not in h or h.get("day_bath") in (None, "", "unknown"):
            h["day_bath"] = day
        if "private_bath" not in h or h.get("private_bath") in (None, "", "unknown"):
            h["private_bath"] = priv
        # attach lightweight area tips for UI (optional denormalized)
        if a:
            h.setdefault("area_travel_time_band", a.get("travel_time_band"))
            h.setdefault("area_best_season_zh", a.get("best_season_zh"))
    return hotels


def add_aso_hotel(hotels):
    names = {h.get("property_jp") for h in hotels}
    if "阿蘇内牧温泉 湯巡追荘" in names or "湯巡追荘" in names:
        return False
    # ranks from 2026 area 阿蘇温泉郷
    hotels.append({
        "rank": 36,
        "rank_2026": 4,
        "onsen_area": "阿蘇温泉郷",
        "prefecture": "熊本",
        "area_cn": "阿蘇溫泉鄉（熊本縣）",
        "property_jp": "阿蘇内牧温泉 湯巡追荘",
        "property_cn": "阿蘇內牧溫泉 湯巡追荘",
        "property_en": "Yumeoisou / 湯巡追荘",
        "type": "ryokan",
        "highlights": "15種貸切風呂；露天風呂付客室；日帰り立ち寄り湯プランあり（じゃらん掲載）",
        "description_cn": "阿蘇溫泉鄉（2026榜表記；與內牧・地獄同圈）人氣宿。湯巡追荘以多種貸切風呂與吃到飽方案著名，亦有日歸入浴方案（公開訂房頁）。經福岡／熊本進阿蘇；請查火山與道路資訊。",
        "price_jpy": None,
        "price_band": "未取得",
        "price_note": "價錢隨季節變動；請以じゃらん／官方當日為準（本站不臆造標價）。",
        "official_url": None,
        "rakuten_url": None,
        "jalan_url": "https://www.jalan.net/yad321249/",
        "booking_url": None,
        "other_booking": None,
        "hk_access": "via FUK｜福岡約2.5–3小時",
        "hk_access_source": "hotel",
        "source": "jalan_area_list",
        "alert": None,
        "source_quality": "jalan_public_listing",
        "in_show": False,
        "region": "九州",
        "day_bath": "yes",
        "private_bath": "both",
    })
    # also annotate existing Aso hotels' area_cn
    for h in hotels:
        if h.get("onsen_area") == "阿蘇内牧＆地獄温泉":
            cn = h.get("area_cn") or ""
            if "阿蘇溫泉鄉" not in cn and "阿蘇温泉郷" not in cn:
                h["area_cn"] = (cn.rstrip("）)") + "／2026亦稱阿蘇溫泉鄉）") if "（" in cn else "阿蘇內牧＆地獄溫泉／阿蘇溫泉鄉（熊本縣）"
    return True


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    areas = build_areas(d)
    areas_by = area_index(areas)
    d["areas"] = areas
    enrich_hotels(d["hotels"], areas_by)
    added = add_aso_hotel(d["hotels"])
    # re-enrich new hotel region tips
    enrich_hotels(d["hotels"], areas_by)

    now = datetime.now(HKT)
    d["meta"]["updated"] = now.strftime("%Y-%m-%d")
    hotel_n = len(d["hotels"])
    area_n = len(areas)
    d["meta"]["updated_label"] = (
        f"最後更新：{now.strftime('%Y-%m-%d %H:%M')} Asia/Hong_Kong (HKT, UTC+8)"
        f"｜旅館 {hotel_n} 間｜溫泉地資料 {area_n} 區｜含交通季節・日歸／貸切標籤"
    )
    alerts = d["meta"].setdefault("alerts", [])
    hoy_alert = "【HOY重溫】截至 2026-11-02，《日本溫泉100強》節目頁顯示暫無可播集數（整套 title 下架／重溫結束），非單一集到期。排名與旅館資料仍保留供行程規劃。"
    if not any(hoy_alert[:20] in (a.get("zh") or "") for a in alerts):
        alerts.insert(0, {"level": "warn", "zh": hoy_alert})
    # keep source banner honest
    d["meta"]["source_banner_zh"] = (
        f"資料品質：web_summary_crosschecked + jalan_rakuten_area_list + area_access_notes"
        f"｜旅館 {hotel_n} 間｜溫泉地 {area_n}｜交通／季節／日歸・貸切為公開來源交叉，未知標 unknown"
    )

    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # stats
    hotels = d["hotels"]
    print("hotels", len(hotels), "areas", len(areas), "aso_added", added)
    print("region fill", sum(1 for h in hotels if h.get("region")), "/", len(hotels))
    print("hk_access", sum(1 for h in hotels if h.get("hk_access")))
    print("hk_access_source hotel", sum(1 for h in hotels if h.get("hk_access_source")=="hotel"))
    print("hk_access_source area", sum(1 for h in hotels if h.get("hk_access_source")=="area"))
    print("day_bath yes", sum(1 for h in hotels if h.get("day_bath")=="yes"))
    print("private known", sum(1 for h in hotels if h.get("private_bath") not in (None,"unknown")))
    print("areas with travel_time", sum(1 for a in areas if a.get("travel_time_band")))
    print("areas with access_zh", sum(1 for a in areas if a.get("access_zh")))
    print("areas with season", sum(1 for a in areas if a.get("best_season_zh")))

if __name__ == "__main__":
    main()
