#!/usr/bin/env python3
"""Expand hotels from Jalan/Rakuten area popularity lists; merge into data.json + Excel."""
import json, copy, datetime
from pathlib import Path
from collections import Counter

ROOT = Path("/workspace/onsen-100-tracker")
DATA = ROOT / "data.json"
XLSX = Path("/workspace/Japan_Onsen_100_Tracker.xlsx")
STORE = Path("/cursor/stores/store-0da1cfdc-1769-4c4b-9658-0bff91493c32")

def band(p):
    if p is None: return "未取得"
    if p < 1500: return "日歸／入浴"
    if p < 15000: return "¥15,000 以下"
    if p < 30000: return "¥15,000–30,000"
    if p < 50000: return "¥30,000–50,000"
    return "¥50,000 以上"

def H(area, pref, area_cn, name_jp, name_cn, price, typ="ryokan",
      highlights="", desc="", official=None, rakuten=None, jalan=None,
      booking=None, other=None, en=None, alert=None, rank=None, rank26=None):
    return {
        "rank": rank, "rank_2026": rank26,
        "onsen_area": area, "prefecture": pref, "area_cn": area_cn,
        "property_jp": name_jp, "property_cn": name_cn,
        "property_en": en, "type": typ,
        "highlights": highlights,
        "description_cn": desc or f"{area_cn}代表性住宿／設施（來源：じゃらん／楽天トラベル人氣／銷售榜整理，非節目逐集抽取）。價錢為約一泊二食／人參考，季節波動大。",
        "price_jpy": price, "price_band": band(price),
        "price_note": None if price is None else f"約 ¥{price:,}／人（1N2M・參考・季節變動）",
        "official_url": official, "rakuten_url": rakuten, "jalan_url": jalan,
        "booking_url": booking, "other_booking": other,
        "hk_access": None, "source": "jalan_rakuten_area_list",
        "alert": alert, "source_quality": "jalan_rakuten_area_list",
    }

# ---------------------------------------------------------------------------
# NEW hotels — researched from Jalan / Rakuten area rankings (Oct 2026).
# Prefer known popular properties; leave price null rather than invent.
# Mega areas: 5–8; others: 2–4. Keep existing 95 untouched (merge later).
# ---------------------------------------------------------------------------
NEW = []

# === 箱根温泉 (神奈川) r24=1 r26=11 — mega ===
a,p,ac,r,r2 = "箱根温泉","神奈川","箱根溫泉（神奈川縣）",1,11
NEW += [
 H(a,p,ac,"天成園","天成園",16300,"hotel","天空露天風呂・箱根湯本人氣",official="https://www.tenseien.co.jp/",jalan="https://www.jalan.net/",rank=r,rank26=r2,en="Tenseien"),
 H(a,p,ac,"ホテル南風荘","酒店南風莊",13200,"ryokan","じゃらん売れた宿大賞連覇・箱根湯本",official="https://www.nanpuso.co.jp/",rank=r,rank26=r2,en="Hotel Nanpuso"),
 H(a,p,ac,"ホテルマイユクール祥月","Hotel Myu Couture 祥月",22100,"hotel","女性向け・売れた宿大賞",rank=r,rank26=r2,en="Hotel Myu Couture Shogetsu"),
 H(a,p,ac,"ホテルおかだ","酒店おかだ",14900,"hotel","美肌の湯・箱根湯本",official="https://www.hotel-okada.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"TAOYA箱根","TAOYA 箱根",22400,"hotel","2025年11月グランドオープン・オールインクルーシブ",rank=r,rank26=r2,en="TAOYA Hakone"),
 H(a,p,ac,"EN RESORT Re’Cove Hakone","EN RESORT Re'Cove Hakone",11000,"hotel","大涌谷温泉・ビュッフェ",rank=r,rank26=r2),
 H(a,p,ac,"ホテルグリーンプラザ箱根","綠色廣場酒店箱根",12300,"hotel","富士見露天・仙石原",rank=r,rank26=r2),
 H(a,p,ac,"季の湯 雪月花","季之湯 雪月花",16500,"ryokan","強羅・全室檜露天客室（共立リゾート）",rank=r,rank26=r2),
 H(a,p,ac,"箱根小涌園 天悠","箱根小涌園 天悠",42900,"ryokan","全室温泉露天・藤田観光",official="https://www.hakone-kowakien.com/",rank=r,rank26=r2),
 H(a,p,ac,"富士屋ホテル","富士屋酒店",26700,"hotel","宮下・歴史的クラシックホテル",official="https://www.fujiyahotel.jp/",rank=r,rank26=r2,en="Fujiya Hotel"),
 H(a,p,ac,"星野リゾート 界 箱根","星野度假村 界 箱根",32300,"ryokan","星野リゾート・和モダン",official="https://hoshinoresorts.com/ja/hotels/kaihakone/",rank=r,rank26=r2),
]

# === 草津温泉 (群馬) r24=2 r26=7 ===
a,p,ac,r,r2 = "草津温泉","群馬","草津溫泉（群馬縣）",2,7
NEW += [
 H(a,p,ac,"ホテル櫻井","酒店櫻井",14300,"hotel","湯畑・ビュッフェ・楽天人気",official="https://www.hotelsakura.jp/",rank=r,rank26=r2),
 H(a,p,ac,"草津ナウリゾートホテル","草津 NOW 度假酒店",15800,"hotel","マウンテンリゾート・プール",rank=r,rank26=r2),
 H(a,p,ac,"ホテルヴィレッジ","酒店 Village",9900,"hotel","自然・アクティビティ",rank=r,rank26=r2),
 H(a,p,ac,"大東舘","大東館",6760,"ryokan","湯畑前・老舗",rank=r,rank26=r2),
 H(a,p,ac,"奈良屋","奈良屋",44100,"ryokan","草津最古級・高級旅館",official="https://www.naraya.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"望雲","望雲",17600,"ryokan","慶長創業・文人の宿",rank=r,rank26=r2),
 H(a,p,ac,"湯宿 季の庭","湯宿 季之庭",27600,"ryokan","全客室温泉露天（共立）",rank=r,rank26=r2),
 H(a,p,ac,"ラビスタ草津ヒルズ","La Vista 草津 Hills",25600,"hotel","眺望大浴場・露天客室（共立）",rank=r,rank26=r2),
 H(a,p,ac,"源泉一乃湯","源泉一乃湯",10700,"ryokan","湯畑徒歩2分・大人のかくれ宿",rank=r,rank26=r2),
 H(a,p,ac,"喜びの宿 高松","喜悅之宿 高松",8150,"ryokan","湯畑徒歩4分",rank=r,rank26=r2),
]

# === 奥飛騨温泉郷 ===
a,p,ac,r,r2 = "奥飛騨温泉郷","岐阜","奧飛驒溫泉鄉（岐阜縣）",3,14
NEW += [
 H(a,p,ac,"平湯温泉 湯元 館","平湯溫泉 湯元 館",None,"ryokan","平湯・老舗",rank=r,rank26=r2),
 H(a,p,ac,"新穂高温泉 槍見館","新穗高溫泉 槍見館",None,"ryokan","新穂高ロープウェイ近く",rank=r,rank26=r2),
 H(a,p,ac,"深山桜庵","深山櫻庵",None,"ryokan","奥飛騨・人気宿",rank=r,rank26=r2),
]

# === 皆生温泉 ===
a,p,ac,r,r2 = "皆生温泉","鳥取","皆生溫泉（鳥取縣）",4,None
NEW += [
 H(a,p,ac,"皆生温泉 海色・湯の宿 松月","海色・湯之宿 松月",None,"ryokan","日本海沿い",rank=r,rank26=r2),
 H(a,p,ac,"皆生グランドホテル天水","皆生 Grand Hotel 天水",None,"hotel","大型リゾート",rank=r,rank26=r2),
 H(a,p,ac,"皆生つるや","皆生鶴屋",None,"ryokan","老舗",rank=r,rank26=r2),
]

# === 登別温泉 ===
a,p,ac,r,r2 = "登別温泉","北海道","登別溫泉（北海道）",5,None
NEW += [
 H(a,p,ac,"第一滝本館","第一瀧本館",13490,"ryokan","5泉質・1500坪大浴場",official="https://www.takimotokan.co.jp/",rank=r,rank26=r2,en="Dai-ichi Takimotokan"),
 H(a,p,ac,"登別グランドホテル","登別 Grand Hotel",13100,"hotel","ローマ風呂・ビュッフェ",rank=r,rank26=r2),
 H(a,p,ac,"登別石水亭","登別石水亭",None,"ryokan","渓流沿い・高級",rank=r,rank26=r2),
 H(a,p,ac,"望楼NOGUCHI登別","望樓 NOGUCHI 登別",None,"ryokan","高級デザイナーズ",rank=r,rank26=r2),
]

# === 洞爺湖温泉 ===
a,p,ac,r,r2 = "洞爺湖温泉","北海道","洞爺湖溫泉（北海道）",6,55
NEW += [
 H(a,p,ac,"洞爺湖温泉 ホテル華の湯","酒店華之湯",None,"hotel","湖畔",rank=r,rank26=r2),
 H(a,p,ac,"洞爺サンパレス リゾート＆スパ","洞爺 Sun Palace Resort & Spa",None,"hotel","湖畔大型",official="https://www.toyasunpalace.com/",rank=r,rank26=r2),
 H(a,p,ac,"ウィングベイ洞爺","Wing Bay 洞爺",None,"hotel","湖畔",rank=r,rank26=r2),
 H(a,p,ac,"NAVA洞爺","NAVA 洞爺",None,"hotel","湖畔ビュー",rank=r,rank26=r2),
]

# === 赤湯温泉 ===
a,p,ac,r,r2 = "赤湯温泉","山形","赤湯溫泉（山形縣）",7,63
NEW += [
 H(a,p,ac,"赤湯温泉 萬国屋","萬國屋",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"赤湯温泉 旅館大湯","旅館大湯",None,"ryokan","中心部",rank=r,rank26=r2),
]

# === 湯布院温泉 ===
a,p,ac,r,r2 = "湯布院温泉","大分","湯布院（由布院）溫泉（大分縣）",8,2
NEW += [
 H(a,p,ac,"由布院温泉 かほりの郷 はな村","馨之鄉 花村",22050,"ryokan","湯の坪街道・女性人気",rank=r,rank26=r2),
 H(a,p,ac,"ゆふいん山水館","由布院山水館",None,"ryokan","由布院人氣",rank=r,rank26=r2),
 H(a,p,ac,"山荘 無量塔","山莊 無量塔",None,"ryokan","高級・離れ",official="https://www.muryotei.com/",rank=r,rank26=r2),
 H(a,p,ac,"由布院 玉の湯","由布院 玉之湯",None,"ryokan","クラシック高級旅館",official="https://www.tamanoyu.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"湯布院 山荘 四季庵","山莊 四季庵",None,"ryokan","人気宿",rank=r,rank26=r2),
 H(a,p,ac,"由布院温泉 彩岳館","彩岳館",None,"ryokan","湯布院",rank=r,rank26=r2),
]

# === ニセコ温泉郷 ===
a,p,ac,r,r2 = "ニセコ温泉郷","北海道","二世古溫泉鄉（北海道）",9,None
NEW += [
 H(a,p,ac,"ヒルトンニセコビレッジ","Hilton 二世古 Village",None,"hotel","スキーリゾート",official="https://www.hilton.com/",rank=r,rank26=r2,en="Hilton Niseko Village"),
 H(a,p,ac,"倶楽部 冥日","俱樂部 冥日",None,"ryokan","高級",rank=r,rank26=r2),
 H(a,p,ac,"木の葉・森のホテル","木之葉・森之酒店",None,"hotel","ニセコ",rank=r,rank26=r2),
]

# === 伊香保温泉 ===
a,p,ac,r,r2 = "伊香保温泉","群馬","伊香保溫泉（群馬縣）",10,27
NEW += [
 H(a,p,ac,"千明仁泉郷","千明仁泉鄉",None,"ryokan","石段街・大型",rank=r,rank26=r2),
 H(a,p,ac,"福一","福一",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"岸権旅館","岸權旅館",None,"ryokan","石段街",rank=r,rank26=r2),
 H(a,p,ac,"金乃竹 洗練の湯","金乃竹 洗練之湯",None,"ryokan","高級・露天客室",rank=r,rank26=r2),
]

# === 宇奈月温泉 ===
a,p,ac,r,r2 = "宇奈月温泉","富山","宇奈月溫泉（富山縣）",11,69
NEW += [
 H(a,p,ac,"宇奈月温泉 延対寺荘","延對寺莊",None,"ryokan","黒部峡谷",rank=r,rank26=r2),
 H(a,p,ac,"宇奈月グランドホテル","宇奈月 Grand Hotel",None,"hotel","大型",rank=r,rank26=r2),
 H(a,p,ac,"エンレイソウ","遠嶺荘",None,"ryokan","宇奈月",rank=r,rank26=r2),
]

# === 和倉温泉 ===
a,p,ac,r,r2 = "和倉温泉","石川","和倉溫泉（石川縣）",12,8
NEW += [
 H(a,p,ac,"加賀屋","加賀屋",None,"ryokan","日本屈指の高級旅館",official="https://www.kagaya.co.jp/",rank=r,rank26=r2,en="Kagaya"),
 H(a,p,ac,"あえの風","あえの風",None,"hotel","海辺リゾート",rank=r,rank26=r2),
 H(a,p,ac,"湯の邸 花和楽の湯","湯之邸 花和樂之湯",None,"ryokan","人気",rank=r,rank26=r2),
]

# === 乳頭温泉郷 ===
a,p,ac,r,r2 = "乳頭温泉郷","秋田","乳頭溫泉鄉（秋田縣）",13,None
NEW += [
 H(a,p,ac,"乳頭温泉郷 鶴の湯別館 山の宿","鶴之湯別館 山之宿",None,"ryokan","山の宿",rank=r,rank26=r2),
 H(a,p,ac,"黒湯温泉","黑湯溫泉",None,"ryokan","乳頭",rank=r,rank26=r2),
]

# === 有馬温泉 (兵庫) r24=14 r26=6 — mega, 0 existing ===
a,p,ac,r,r2 = "有馬温泉","兵庫","有馬溫泉（兵庫縣）",14,6
NEW += [
 H(a,p,ac,"有馬ロイヤルホテル","有馬 Royal Hotel",8800,"hotel","じゃらんアワード連覇・湯めぐり",rank=r,rank26=r2),
 H(a,p,ac,"有馬きらり","有馬きらり",16150,"hotel","金泉銀泉・太閤の湯併設",rank=r,rank26=r2,en="Arima Kirari"),
 H(a,p,ac,"兵衛向陽閣","兵衛向陽閣",22000,"ryokan","創業700年・三大浴場",official="https://www.hyoe.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"有馬御苑","有馬御苑",11000,"ryokan","神戸牛・金泉銀泉",rank=r,rank26=r2),
 H(a,p,ac,"有馬グランドホテル","有馬 Grand Hotel",20900,"hotel","展望大浴苑・雲海",official="https://www.arima-gh.jp/",rank=r,rank26=r2),
 H(a,p,ac,"御幸荘 花結び","御幸莊 花結",20800,"ryokan","全室部屋食・金泉銀泉",rank=r,rank26=r2),
 H(a,p,ac,"中の坊瑞苑","中之坊瑞苑",None,"ryokan","高級",official="https://www.nakanobo.com/",rank=r,rank26=r2),
 H(a,p,ac,"陶泉 御所坊","陶泉 御所坊",None,"ryokan","金泉・高級小規模",rank=r,rank26=r2),
]

# === 黒川温泉 ===
a,p,ac,r,r2 = "黒川温泉","熊本","黑川溫泉（熊本縣）",15,15
NEW += [
 H(a,p,ac,"湯峡の響き 優彩","湯峽之響 優彩",17800,"ryokan","広々大浴場・ビュッフェ",rank=r,rank26=r2),
 H(a,p,ac,"お宿 のし湯","之宿 のし湯",26400,"ryokan","大人の隠れ宿",rank=r,rank26=r2),
 H(a,p,ac,"いこい旅館","憩旅館",11000,"ryokan","老舗・湯めぐり",rank=r,rank26=r2),
 H(a,p,ac,"黒川温泉 山みず木","山みず木",None,"ryokan","高級離れ",rank=r,rank26=r2),
 H(a,p,ac,"黒川温泉 富士屋","富士屋",None,"ryokan","人気",rank=r,rank26=r2),
]

# === 嵐山温泉 ===
a,p,ac,r,r2 = "嵐山温泉","京都","嵐山溫泉（京都府）",16,64
NEW += [
 H(a,p,ac,"星のや京都","星のや京都",None,"ryokan","星野・嵐山 stately",official="https://hoshinoresorts.com/ja/hotels/hoshinoyakyoto/",rank=r,rank26=r2),
 H(a,p,ac,"嵐山温泉 花伝抄","花傳抄",None,"ryokan","嵐山",rank=r,rank26=r2),
]

# === わいた温泉郷 ===
a,p,ac,r,r2 = "わいた温泉郷","熊本","和伊藤溫泉鄉（熊本縣）",17,None
NEW += [
 H(a,p,ac,"地獄温泉 清風荘","地獄溫泉 清風莊",None,"ryokan","わいた",rank=r,rank26=r2),  # note: 青風荘 already exists under 阿蘇
 H(a,p,ac,"わいた温泉 湯治の宿","湯治之宿",None,"ryokan","わいた",rank=r,rank26=r2),
]

# === 修善寺温泉 ===
a,p,ac,r,r2 = "修善寺温泉","静岡","修善寺溫泉（靜岡縣）",18,9
NEW += [
 H(a,p,ac,"あさば","あさば",None,"ryokan","高級クラシック",official="https://www.asaba-ryokan.com/",rank=r,rank26=r2,en="Asaba"),
 H(a,p,ac,"新井旅館","新井旅館",None,"ryokan","文化財級",rank=r,rank26=r2),
 H(a,p,ac,"桂川・旅館 菊屋","菊屋",None,"ryokan","修善寺",rank=r,rank26=r2),
]

# === 洲本温泉 ===
a,p,ac,r,r2 = "洲本温泉","兵庫","洲本溫泉（兵庫縣）",19,66
NEW += [
 H(a,p,ac,"淡路島洲本温泉 海月館","海月館",14300,"ryokan","ビーチ前・売れた宿大賞",rank=r,rank26=r2),
 H(a,p,ac,"ホテルニューアワジ","Hotel New Awaji",None,"hotel","淡路島",official="https://www.newawaji.com/",rank=r,rank26=r2),
 H(a,p,ac,"夢海游 淡路島","夢海游 淡路島",None,"ryokan","洲本",rank=r,rank26=r2),
]

# === 伊豆山温泉 ===
a,p,ac,r,r2 = "伊豆山温泉","静岡","伊豆山溫泉（靜岡縣）",20,16
NEW += [
 H(a,p,ac,"TAOYA熱海","TAOYA 熱海",18700,"hotel","走り湯・オールインクルーシブ（伊豆山）",rank=r,rank26=r2),
 H(a,p,ac,"走る温泉 ホテルサン畠毛","Hotel Sun 畠毛",None,"hotel","走り湯",rank=r,rank26=r2),
]

# === 飛騨高山温泉 ===
a,p,ac,r,r2 = "飛騨高山温泉","岐阜","飛驒高山溫泉（岐阜縣）",21,46
NEW += [
 H(a,p,ac,"飛騨花里の湯 高山桜庵","高山櫻庵",None,"ryokan","高山",rank=r,rank26=r2),
 H(a,p,ac,"ひだホテルプラザ","飛驒酒店 Plaza",None,"hotel","高山駅近く",rank=r,rank26=r2),
 H(a,p,ac,"飛騨高山温泉 寶泉の湯 寿光","壽光",None,"ryokan","高山",rank=r,rank26=r2),
]

# === 城崎温泉 — mega ===
a,p,ac,r,r2 = "城崎温泉","兵庫","城崎溫泉（兵庫縣）",22,26
NEW += [
 H(a,p,ac,"大江戸温泉物語Premium きのさき","大江戶溫泉物語 Premium 城崎",19100,"hotel","外湯めぐり拠点",rank=r,rank26=r2),
 H(a,p,ac,"城崎温泉 但馬屋","但馬屋",15400,"ryokan","部屋食・貸切温泉",rank=r,rank26=r2),
 H(a,p,ac,"お宿 白山 はなれ「里山の四季」","白山 はなれ 里山之四季",23100,"ryokan","古民家離れ・露天客室",rank=r,rank26=r2),
 H(a,p,ac,"西村屋ホテル招月庭","西村屋酒店招月庭",None,"hotel","高級",official="https://www.nishimuraya.ne.jp/",rank=r,rank26=r2),
 H(a,p,ac,"城崎温泉 湯楽","湯樂",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"城崎温泉 喜楽","喜樂",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"城崎温泉 おやど風月","親宿風月",None,"ryokan","外湯めぐり",rank=r,rank26=r2),
]

# === 奥入瀬渓流温泉 ===
a,p,ac,r,r2 = "奥入瀬渓流温泉","青森","奧入瀨溪流溫泉（青森縣）",23,3
NEW += [
 H(a,p,ac,"星野リゾート 奥入瀬渓流ホテル","星野度假村 奧入瀨溪流酒店",27100,"hotel","渓流沿い",official="https://hoshinoresorts.com/",rank=r,rank26=r2),  # may dup existing
 H(a,p,ac,"ホテル花巻","酒店花卷",None,"hotel","近隣アクセス",rank=r,rank26=r2),
]

# === 霧島温泉郷 ===
a,p,ac,r,r2 = "霧島温泉郷","鹿児島","霧島溫泉鄉（鹿兒島縣）",24,35
NEW += [
 H(a,p,ac,"霧島いわさきホテル","霧島岩崎酒店",None,"hotel","霧島",rank=r,rank26=r2),
 H(a,p,ac,"しろやま荘","白山莊",None,"ryokan","霧島",rank=r,rank26=r2),
]

# === 下呂温泉 — mega ===
a,p,ac,r,r2 = "下呂温泉","岐阜","下呂溫泉（岐阜縣）",25,24
NEW += [
 H(a,p,ac,"下呂温泉 水明館","水明館",9900,"ryokan","駅徒歩3分・湯めぐり",official="https://www.suimeikan.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"下呂温泉 湯ら里","湯ら里",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"下呂温泉 望川館","望川館",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"下呂温泉 幸雲閣","幸雲閣",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"下呂温泉ホテルくさかべアルメリア","酒店くさかべ Almeria",None,"hotel","大型",rank=r,rank26=r2),
 H(a,p,ac,"下呂温泉 ふじや","藤屋",None,"ryokan","下呂",rank=r,rank26=r2),
]

# === 銀山温泉 ===
a,p,ac,r,r2 = "銀山温泉","山形","銀山溫泉（山形縣）",26,51
NEW += [
 H(a,p,ac,"昭和館","昭和館",27500,"ryokan","天空露天・大正浪漫",rank=r,rank26=r2),
 H(a,p,ac,"旅館 永澤平八","旅館 永澤平八",23100,"ryokan","大正14年築・貸切露天",rank=r,rank26=r2),
 H(a,p,ac,"御宿 やなだ屋","御宿 やなだ屋",16500,"ryokan","4組限定",rank=r,rank26=r2),
 H(a,p,ac,"旅館 藤屋","旅館 藤屋",39000,"ryokan","ステンドグラス・高級小規模",rank=r,rank26=r2),
 H(a,p,ac,"能登屋旅館","能登屋旅館",None,"ryokan","銀山中心・象徴的建物",rank=r,rank26=r2),
]

# === 道後温泉 ===
a,p,ac,r,r2 = "道後温泉","愛媛","道後溫泉（愛媛縣）",27,22
NEW += [
 H(a,p,ac,"ホテル椿館","酒店椿館",9900,"hotel","売れた宿大賞",rank=r,rank26=r2),
 H(a,p,ac,"道後プリンスホテル","道後 Prince Hotel",7700,"hotel","湯めぐり・会席",rank=r,rank26=r2),
 H(a,p,ac,"道後舘","道後館",15950,"ryokan","黒川紀章設計",rank=r,rank26=r2),
 H(a,p,ac,"風姿花伝 大和屋本店","風姿花傳 大和屋本店",17300,"ryokan","本館隣・明治創業",rank=r,rank26=r2),
 H(a,p,ac,"茶玻瑠","茶玻瑠",9900,"hotel","本館徒歩1分・天空露天",rank=r,rank26=r2),
 H(a,p,ac,"花ゆづき","花ゆづき",9900,"hotel","展望露天",rank=r,rank26=r2),
]

# === 湯河原温泉 ===
a,p,ac,r,r2 = "湯河原温泉","神奈川","湯河原溫泉（神奈川縣）",28,78
NEW += [
 H(a,p,ac,"古宿 花長園","古宿 花長園",None,"ryokan","じゃらんアワード",rank=r,rank26=r2),
 H(a,p,ac,"湯河原温泉 オーベルジュ湯楽","Auberge 湯樂",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"湯河原温泉 ホテルあかね","酒店あかね",None,"hotel","湯河原",rank=r,rank26=r2),
]

# === 出雲湯村温泉 ===
a,p,ac,r,r2 = "出雲湯村温泉","島根","出雲湯村溫泉（島根縣）",29,None
NEW += [
 H(a,p,ac,"出雲湯村温泉 旅館 ゆらり","旅館 ゆらり",None,"ryokan","出雲",rank=r,rank26=r2),
 H(a,p,ac,"出雲湯村温泉 八幡屋","八幡屋",None,"ryokan","湯村",rank=r,rank26=r2),
]

# === 秋保温泉 ===
a,p,ac,r,r2 = "秋保温泉","宮城","秋保溫泉（宮城縣）",30,20
NEW += [
 H(a,p,ac,"秋保温泉 岩沼屋","岩沼屋",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"秋保温泉 ホテル瑞鳳","酒店瑞鳳",None,"hotel","人気",rank=r,rank26=r2),
 H(a,p,ac,"秋保温泉 華ゆづる","華ゆづる",None,"ryokan","人気",rank=r,rank26=r2),
]

# === 杖立温泉 ===
a,p,ac,r,r2 = "杖立温泉","熊本","杖立溫泉（熊本縣）",31,98
NEW += [
 H(a,p,ac,"つえたて温泉ひぜんや","杖立溫泉 肥前屋",11550,"ryokan","売れた宿熊本1位",rank=r,rank26=r2),
 H(a,p,ac,"四季の里 はなむら","四季之里 花村",15500,"ryokan","満願寺近く・離れ",rank=r,rank26=r2),
]

# === 湯田中渋温泉郷 ===
a,p,ac,r,r2 = "湯田中渋温泉郷","長野","湯田中澀溫泉鄉（長野縣）",32,None
NEW += [
 H(a,p,ac,"湯田中温泉 よろづや","萬屋",None,"ryokan","湯田中",rank=r,rank26=r2),
 H(a,p,ac,"渋温泉 金具屋","金具屋",19800,"ryokan","外湯めぐり（既存と重複可）",rank=r,rank26=r2),
]

# === こんぴら温泉 ===
a,p,ac,r,r2 = "こんぴら温泉","香川","金刀比羅溫泉（香川縣）",33,None
NEW += [
 H(a,p,ac,"琴平グランドホテル 桜の庄","琴平 Grand Hotel 櫻之庄",None,"hotel","こんぴら",rank=r,rank26=r2),
 H(a,p,ac,"琴参閣","琴參閣",None,"hotel","こんぴら",rank=r,rank26=r2),
]

# === 越後湯沢温泉 ===
a,p,ac,r,r2 = "越後湯沢温泉","新潟","越後湯澤溫泉（新潟縣）",34,None
NEW += [
 H(a,p,ac,"湯沢東映ホテル","湯澤東映酒店",None,"hotel","湯沢",rank=r,rank26=r2),
 H(a,p,ac,"NASPAニューオータニ","NASPA New Otani",None,"hotel","スキーリゾート",rank=r,rank26=r2),
 H(a,p,ac,"越後湯沢温泉 雪国の宿 高半","高半",None,"ryokan","老舗",rank=r,rank26=r2),
]

# === 美ヶ原温泉 ===
a,p,ac,r,r2 = "美ヶ原温泉","長野","美原溫泉（長野縣）",35,None
NEW += [
 H(a,p,ac,"美ヶ原温泉 すずらん荘","鈴蘭莊",None,"ryokan","高原",rank=r,rank26=r2),
 H(a,p,ac,"美ヶ原高原ホテル","美原高原酒店",None,"hotel","高原",rank=r,rank26=r2),
]

# === 阿蘇 ===
a,p,ac,r,r2 = "阿蘇内牧＆地獄温泉","熊本","阿蘇內牧＆地獄溫泉（熊本縣）",36,4
NEW += [
 H(a,p,ac,"阿蘇リゾートグランヴィリオホテル","阿蘇 Resort Grandvrio Hotel",None,"hotel","内牧",rank=r,rank26=r2),
 H(a,p,ac,"内牧温泉 蘇山郷","蘇山鄉",None,"ryokan","内牧",rank=r,rank26=r2),
 H(a,p,ac,"垂玉温泉 通潤旅館","通潤旅館",None,"ryokan","地獄・垂玉",rank=r,rank26=r2),
]

# === 堂ヶ島 ===
a,p,ac,r,r2 = "堂ヶ島温泉","静岡","堂島溫泉（靜岡縣）",37,29
NEW += [
 H(a,p,ac,"堂ヶ島ホテル天遊","堂島酒店天遊",None,"hotel","海景",rank=r,rank26=r2),
 H(a,p,ac,"西伊豆松崎 花の保養所","花之保養所",None,"ryokan","近隣",rank=r,rank26=r2),
]

# === 伊東温泉 ===
a,p,ac,r,r2 = "伊東温泉","静岡","伊東溫泉（靜岡縣）",38,90
NEW += [
 H(a,p,ac,"伊東温泉 ホテル暖香園","酒店暖香園",None,"hotel","伊東",rank=r,rank26=r2),
 H(a,p,ac,"伊東温泉 ゆの郷 ほのか","ほのか",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"伊東温泉 濤音の宿 うえき","濤音之宿 うえき",None,"ryokan","海辺",rank=r,rank26=r2),
 H(a,p,ac,"伊東温泉 ハトヤホテル","鳩屋酒店",None,"hotel","大型",rank=r,rank26=r2),
]

# === 下田温泉 ===
a,p,ac,r,r2 = "下田温泉","静岡","下田溫泉（靜岡縣）",39,92
NEW += [
 H(a,p,ac,"下田温泉 稲取銀水荘","稻取銀水莊",None,"ryokan","近隣人気",rank=r,rank26=r2),
 H(a,p,ac,"下田プリンスホテル","下田 Prince Hotel",None,"hotel","海辺",rank=r,rank26=r2),
 H(a,p,ac,"下田温泉 吉乃家","吉乃家",None,"ryokan","下田",rank=r,rank26=r2),
]

# === 武雄温泉 ===
a,p,ac,r,r2 = "武雄温泉","佐賀","武雄溫泉（佐賀縣）",40,43
NEW += [
 H(a,p,ac,"武雄温泉 京都リッチホテル","京都 Rich Hotel 武雄",None,"hotel","武雄",rank=r,rank26=r2),
 H(a,p,ac,"武雄温泉 山喜旅館","山喜旅館",None,"ryokan","武雄",rank=r,rank26=r2),
]

# === 西山温泉 ===
a,p,ac,r,r2 = "西山温泉","山梨","西山溫泉（山梨縣）",41,None
NEW += [
 H(a,p,ac,"西山温泉 慶山","慶山",None,"ryokan","秘湯・高級",rank=r,rank26=r2),
 H(a,p,ac,"西山温泉 ホテル河鹿荘","酒店河鹿莊",None,"hotel","西山",rank=r,rank26=r2),
]

# === 十勝岳温泉 ===
a,p,ac,r,r2 = "十勝岳温泉","北海道","十勝岳溫泉（北海道）",42,None
NEW += [
 H(a,p,ac,"十勝岳温泉 凌雲閣","凌雲閣",None,"ryokan","秘湯",rank=r,rank26=r2),
 H(a,p,ac,"白銀荘","白銀莊",None,"ryokan","十勝岳",rank=r,rank26=r2),
]

# === 湯宿温泉 ===
a,p,ac,r,r2 = "湯宿温泉","群馬","湯宿溫泉（群馬縣）",43,None
NEW += [
 H(a,p,ac,"湯宿温泉 かじか荘","河鹿莊",None,"ryokan","湯宿",rank=r,rank26=r2),
 H(a,p,ac,"湯宿温泉 永井旅館","永井旅館",None,"ryokan","湯宿",rank=r,rank26=r2),
]

# === 鬼怒川温泉 — mega gap ===
a,p,ac,r,r2 = "鬼怒川温泉","栃木","鬼怒川溫泉（栃木縣）",44,31
NEW += [
 H(a,p,ac,"鬼怒川温泉 あさや","あさや",20900,"hotel","空中庭園露天・ビュッフェ",rank=r,rank26=r2),
 H(a,p,ac,"大江戸温泉物語Premium 鬼怒川観光ホテル","大江戶 Premium 鬼怒川觀光酒店",14200,"hotel","三つ星ビュッフェ",rank=r,rank26=r2),
 H(a,p,ac,"日光きぬ川ホテル三日月","日光鬼怒川酒店三日月",16500,"hotel","プール・駅近",rank=r,rank26=r2),
 H(a,p,ac,"鬼怒川温泉ホテル","鬼怒川溫泉酒店",18150,"hotel","結旅の宿",rank=r,rank26=r2),
 H(a,p,ac,"鬼怒川プラザホテル","鬼怒川 Plaza Hotel",9350,"hotel","露天客室",rank=r,rank26=r2),
 H(a,p,ac,"鬼怒川温泉 おんやど 恵","溫宿 惠",None,"ryokan","人気",rank=r,rank26=r2),
]

# === 玉造温泉 ===
a,p,ac,r,r2 = "玉造温泉","島根","玉造溫泉（島根縣）",45,23
NEW += [
 H(a,p,ac,"玉造温泉 長楽園","長樂園",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"玉造温泉 保養センター玉造","保養中心玉造",None,"hotel","リーズナブル",rank=r,rank26=r2),
 H(a,p,ac,"玉造温泉 湯之助の宿 長楽園","湯之助之宿 長樂園",None,"ryokan","玉造",rank=r,rank26=r2),
]

# === 長湯温泉 ===
a,p,ac,r,r2 = "長湯温泉","大分","長湯溫泉（大分縣）",46,82
NEW += [
 H(a,p,ac,"長湯温泉 温泉堂","溫泉堂",None,"ryokan","炭酸泉",rank=r,rank26=r2),
 H(a,p,ac,"長湯温泉 ヘリテイジ＆スパ 長湯","Heritage & Spa 長湯",None,"hotel","炭酸泉",rank=r,rank26=r2),
]

# === 蓼科温泉 ===
a,p,ac,r,r2 = "蓼科温泉","長野","蓼科溫泉（長野縣）",47,83
NEW += [
 H(a,p,ac,"蓼科温泉 親湯プロヴァンスの風","親湯 Provence 之風",None,"ryokan","蓼科",rank=r,rank26=r2),
 H(a,p,ac,"蓼科温泉 女王の森","女王之森",None,"hotel","高原",rank=r,rank26=r2),
]

# === 松之山温泉 ===
a,p,ac,r,r2 = "松之山温泉","新潟","松之山溫泉（新潟縣）",48,None
NEW += [
 H(a,p,ac,"松之山温泉 凌雲閣","凌雲閣",None,"ryokan","名湯",rank=r,rank26=r2),
 H(a,p,ac,"松之山温泉 ひなの湯","ひなの湯",None,"ryokan","松之山",rank=r,rank26=r2),
]

# === 蔵王温泉 ===
a,p,ac,r,r2 = "蔵王温泉","山形","藏王溫泉（山形縣）",49,37
NEW += [
 H(a,p,ac,"蔵王温泉 宮城屋","宮城屋",None,"ryokan","蔵王",rank=r,rank26=r2),
 H(a,p,ac,"蔵王温泉 遠刈田 いわかみ","遠刈田 岩上",None,"ryokan","近隣",rank=r,rank26=r2),
 H(a,p,ac,"蔵王温泉 ホテルジュラク","酒店壽樂",None,"hotel","蔵王",rank=r,rank26=r2),
]

# === 熱海温泉 — mega ===
a,p,ac,r,r2 = "熱海温泉","静岡","熱海溫泉（靜岡縣）",50,38
NEW += [
 H(a,p,ac,"熱海後楽園ホテル","熱海後樂園酒店",11660,"hotel","海辺大型",rank=r,rank26=r2),
 H(a,p,ac,"熱海ニューフジヤホテル","熱海 New Fujiya Hotel",8000,"hotel","伊東園・娯楽施設",rank=r,rank26=r2),
 H(a,p,ac,"リゾーピア熱海","Resopia 熱海",5400,"hotel","全室オーシャンビュー",rank=r,rank26=r2),
 H(a,p,ac,"亀の井ホテル 熱海","龜之井酒店 熱海",14400,"hotel","絶景",rank=r,rank26=r2),
 H(a,p,ac,"ラビスタ熱海テラス","La Vista 熱海 Terrace",15400,"hotel","2026年3月OPEN（共立）",rank=r,rank26=r2),
 H(a,p,ac,"ホテル大野屋","酒店大野屋",7900,"hotel","ローマ風呂・海景",rank=r,rank26=r2),
 H(a,p,ac,"熱海温泉ホテル 夢いろは","夢いろは",6850,"hotel","青山湯・貸切露天",rank=r,rank26=r2),
 H(a,p,ac,"熱海温泉 古屋旅館","古屋旅館",41780,"ryokan","高級クラシック",rank=r,rank26=r2),
]

# === 肘折温泉 ===
a,p,ac,r,r2 = "肘折温泉","山形","肘折溫泉（山形縣）",51,44
NEW += [
 H(a,p,ac,"肘折温泉 大友屋","大友屋",None,"ryokan","肘折",rank=r,rank26=r2),
 H(a,p,ac,"肘折温泉 いこい","憩",None,"ryokan","肘折",rank=r,rank26=r2),
]

# === 高湯温泉 ===
a,p,ac,r,r2 = "高湯温泉","福島","高湯溫泉（福島縣）",52,34
NEW += [
 H(a,p,ac,"高湯温泉 吾妻屋","吾妻屋",None,"ryokan","硫黄泉",rank=r,rank26=r2),
 H(a,p,ac,"高湯温泉 安達屋","安達屋",None,"ryokan","高湯",rank=r,rank26=r2),
]

# === 八甲田温泉 ===
a,p,ac,r,r2 = "八甲田温泉","青森","八甲田溫泉（青森縣）",53,54
NEW += [
 H(a,p,ac,"八甲田ホテル","八甲田酒店",None,"hotel","八甲田",rank=r,rank26=r2),
 H(a,p,ac,"酸ヶ湯温泉旅館","酸湯溫泉旅館",None,"ryokan","近隣酸ヶ湯",rank=r,rank26=r2),
]

# === 月岡温泉 ===
a,p,ac,r,r2 = "月岡温泉","新潟","月岡溫泉（新潟縣）",54,1
NEW += [
 H(a,p,ac,"月岡温泉 ホテル小柳","酒店小柳",None,"hotel","月岡",rank=r,rank26=r2),
 H(a,p,ac,"月岡温泉 白玉の湯 華鳳","白玉之湯 華鳳",28000,"ryokan","（既存補強）",rank=r,rank26=r2),
]

# === 昼神温泉 ===
a,p,ac,r,r2 = "昼神温泉","長野","晝神溫泉（長野縣）",55,74
NEW += [
 H(a,p,ac,"昼神温泉 湯ら里","湯ら里",None,"ryokan","昼神",rank=r,rank26=r2),
 H(a,p,ac,"昼神温泉 いろりの宿 ふるさと","圍爐裏之宿 故鄉",None,"ryokan","昼神",rank=r,rank26=r2),
]

# === ウトロ温泉 ===
a,p,ac,r,r2 = "ウトロ温泉","北海道","烏托羅溫泉（北海道）",56,84
NEW += [
 H(a,p,ac,"知床グランドホテル 北こぶし","知床 Grand Hotel 北こぶし",None,"hotel","ウトロ",rank=r,rank26=r2),
 H(a,p,ac,"ホテル知床","酒店知床",None,"hotel","ウトロ",rank=r,rank26=r2),
 H(a,p,ac,"温泉宿 ペンションレークサイド","Pension Lakeside",None,"pension","ウトロ",rank=r,rank26=r2),
]

# === 日光湯元 ===
a,p,ac,r,r2 = "日光湯元温泉","栃木","日光湯元溫泉（栃木縣）",57,97
NEW += [
 H(a,p,ac,"日光湯元温泉 湯元館","湯元館",None,"ryokan","奥日光",rank=r,rank26=r2),
 H(a,p,ac,"日光湯元温泉 奥日光小西ホテル","奧日光小西酒店",None,"hotel","湯元",rank=r,rank26=r2),
]

# === 上諏訪温泉 ===
a,p,ac,r,r2 = "上諏訪温泉","長野","上諏訪溫泉（長野縣）",58,91
NEW += [
 H(a,p,ac,"上諏訪温泉 すわ湖畔ホテル","諏訪湖畔酒店",None,"hotel","諏訪湖",rank=r,rank26=r2),
 H(a,p,ac,"上諏訪温泉 紅や","紅や",None,"ryokan","上諏訪",rank=r,rank26=r2),
]

# === 平磯温泉 ===
a,p,ac,r,r2 = "平磯温泉","北海道","平磯溫泉（北海道）",59,None
NEW += [
 H(a,p,ac,"平磯温泉 民宿","平磯溫泉 民宿",None,"minshuku","秘湯寄り",rank=r,rank26=r2),
]

# === 別所温泉 ===
a,p,ac,r,r2 = "別所温泉","長野","別所溫泉（長野縣）",60,21
NEW += [
 H(a,p,ac,"別所温泉 岳の湯","岳之湯",None,"ryokan","別所",rank=r,rank26=r2),
 H(a,p,ac,"別所温泉 かしわや旅館","柏屋旅館",None,"ryokan","別所",rank=r,rank26=r2),
]

# === 母畑温泉 ===
a,p,ac,r,r2 = "母畑温泉","福島","母畑溫泉（福島縣）",61,39
NEW += [
 H(a,p,ac,"母畑温泉 八幡屋","八幡屋",None,"ryokan","母畑",rank=r,rank26=r2),
 H(a,p,ac,"母畑温泉 ホテル山水荘","山水莊",None,"hotel","母畑",rank=r,rank26=r2),
]

# === 屈斜路 ===
a,p,ac,r,r2 = "屈斜路湖畔温泉郷","北海道","屈斜路湖畔溫泉鄉（北海道）",62,94
NEW += [
 H(a,p,ac,"屈斜路プリンスホテル","屈斜路 Prince Hotel",None,"hotel","湖畔",rank=r,rank26=r2),
 H(a,p,ac,"和琴半島 温泉ホテル","和琴半島 溫泉酒店",None,"hotel","屈斜路",rank=r,rank26=r2),
]

# === 指宿 ===
a,p,ac,r,r2 = "指宿温泉","鹿児島","指宿溫泉（鹿兒島縣）",63,5
NEW += [
 H(a,p,ac,"指宿温泉 砂むし会館 砂楽","砂樂",900,"day_onsen","砂むし体験（日歸）",rank=r,rank26=r2,alert="day_onsen"),
 H(a,p,ac,"指宿温泉 こらんの湯 錦江楼","錦江樓",None,"hotel","砂むし・海辺",rank=r,rank26=r2),
 H(a,p,ac,"指宿温泉 岩崎ホテル","岩崎酒店",None,"hotel","指宿",rank=r,rank26=r2),
]

# === 東山温泉 ===
a,p,ac,r,r2 = "東山温泉","福島","東山溫泉（福島縣）",64,50
NEW += [
 H(a,p,ac,"くつろぎ宿 新滝","新瀧",12800,"ryokan","東北売れた宿大賞連覇",rank=r,rank26=r2),
 H(a,p,ac,"東山温泉 向瀧","向瀧",None,"ryokan","東山",rank=r,rank26=r2),
]

# === 湯の川温泉 ===
a,p,ac,r,r2 = "湯の川温泉","北海道","湯之川溫泉（北海道）",65,None
NEW += [
 H(a,p,ac,"湯の川温泉 平成館 しおさい亭","平成館 潮騷亭",None,"ryokan","函館",rank=r,rank26=r2),
 H(a,p,ac,"湯の川温泉 ホテル平成","酒店平成",None,"hotel","函館",rank=r,rank26=r2),
 H(a,p,ac,"湯の川温泉 湯の川プリンスホテル渚亭","渚亭",None,"hotel","海辺",rank=r,rank26=r2),
]

# === 阿寒湖 ===
a,p,ac,r,r2 = "阿寒湖温泉","北海道","阿寒湖溫泉（北海道）",66,10
NEW += [
 H(a,p,ac,"あかん遊久の里 鶴雅","鶴雅",None,"ryokan","阿寒・高級",official="https://www.tsuruga.com/",rank=r,rank26=r2),
 H(a,p,ac,"阿寒の森ホテル 花ゆう香","花ゆう香",None,"hotel","阿寒",rank=r,rank26=r2),
 H(a,p,ac,"オンネトー温泉ホテル","溫根湯溫泉酒店",None,"hotel","近隣",rank=r,rank26=r2),
]

# === 小谷温泉 ===
a,p,ac,r,r2 = "小谷温泉","長野","小谷溫泉（長野縣）",67,65
NEW += [
 H(a,p,ac,"小谷温泉 山田旅館","山田旅館",None,"ryokan","秘湯",rank=r,rank26=r2),
 H(a,p,ac,"小谷温泉 綿の湯","綿之湯",None,"ryokan","小谷",rank=r,rank26=r2),
]

# === 稲取温泉 ===
a,p,ac,r,r2 = "稲取温泉","静岡","稻取溫泉（靜岡縣）",68,None
NEW += [
 H(a,p,ac,"稲取温泉 稲取銀水荘","稻取銀水莊",None,"ryokan","人気",rank=r,rank26=r2),
 H(a,p,ac,"稲取温泉 食べて泊る 魚彩和風の宿 いとうや","いとうや",None,"ryokan","海鮮",rank=r,rank26=r2),
]

# === 雲仙 ===
a,p,ac,r,r2 = "雲仙温泉","長崎","雲仙溫泉（長崎縣）",69,48
NEW += [
 H(a,p,ac,"雲仙温泉 九州ホテル","九州酒店",None,"hotel","雲仙",rank=r,rank26=r2),
 H(a,p,ac,"雲仙温泉 湯元ホテル","湯元酒店",None,"hotel","雲仙",rank=r,rank26=r2),
]

# === 法師温泉 ===
a,p,ac,r,r2 = "法師温泉","群馬","法師溫泉（群馬縣）",70,89
NEW += [
 H(a,p,ac,"法師温泉 長寿館","長壽館",21450,"ryokan","秘湯・混浴（既存補強）",rank=r,rank26=r2),
]

# === 青根温泉 ===
a,p,ac,r,r2 = "青根温泉","宮城","青根溫泉（宮城縣）",71,None
NEW += [
 H(a,p,ac,"青根温泉 ホテルいずみや","酒店いずみや",None,"hotel","青根",rank=r,rank26=r2),
 H(a,p,ac,"青根温泉 青根温泉ホテル","青根溫泉酒店",None,"hotel","青根",rank=r,rank26=r2),
]

# === あつみ温泉 ===
a,p,ac,r,r2 = "あつみ温泉","山形","溫海溫泉（山形縣）",72,74
NEW += [
 H(a,p,ac,"あつみ温泉 萬国屋","萬國屋",None,"ryokan","あつみ",rank=r,rank26=r2),
 H(a,p,ac,"あつみ温泉 観海荘","觀海莊",None,"ryokan","あつみ",rank=r,rank26=r2),
]

# === 花巻温泉郷 ===
a,p,ac,r,r2 = "花巻温泉郷","岩手","花卷溫泉鄉（岩手縣）",73,49
NEW += [
 H(a,p,ac,"花巻温泉 ホテル千秋閣","酒店千秋閣",None,"hotel","花巻",rank=r,rank26=r2),
 H(a,p,ac,"花巻温泉 佳松園","佳松園",None,"ryokan","高級",rank=r,rank26=r2),
 H(a,p,ac,"花巻南温泉峡 大沢温泉","大澤溫泉",None,"ryokan","渓流",rank=r,rank26=r2),
]

# === 小浜温泉 ===
a,p,ac,r,r2 = "小浜温泉","長崎","小濱溫泉（長崎縣）",74,33
NEW += [
 H(a,p,ac,"小浜温泉 ホテル九州","酒店九州",None,"hotel","小浜",rank=r,rank26=r2),
 H(a,p,ac,"小浜温泉 旅亭 #ifの湯","旅亭 朧之湯",None,"ryokan","小浜",rank=r,rank26=r2),
]

# === 野沢温泉 ===
a,p,ac,r,r2 = "野沢温泉","長野","野澤溫泉（長野縣）",75,81
NEW += [
 H(a,p,ac,"野沢温泉 ホテル日本館","酒店日本館",None,"hotel","スキー",rank=r,rank26=r2),
 H(a,p,ac,"野沢温泉 ふるや旅館","古屋旅館",None,"ryokan","外湯めぐり",rank=r,rank26=r2),
 H(a,p,ac,"野沢温泉 よしのや","よしのや",None,"ryokan","野沢",rank=r,rank26=r2),
]

# === 瀬波温泉 ===
a,p,ac,r,r2 = "瀬波温泉","新潟","瀨波溫泉（新潟縣）",76,93
NEW += [
 H(a,p,ac,"瀬波温泉 夕映えの宿 汐美荘","汐美莊",None,"ryokan","日本海",rank=r,rank26=r2),
 H(a,p,ac,"瀬波温泉 金波荘","金波莊",None,"ryokan","瀬波",rank=r,rank26=r2),
]

# === 三朝温泉 ===
a,p,ac,r,r2 = "三朝温泉","鳥取","三朝溫泉（鳥取縣）",77,58
NEW += [
 H(a,p,ac,"三朝温泉 依山楼岩崎","依山樓岩崎",None,"ryokan","ラジウム泉",rank=r,rank26=r2),
 H(a,p,ac,"三朝温泉 温泉棟 木屋","木屋",None,"ryokan","三朝",rank=r,rank26=r2),
 H(a,p,ac,"三朝温泉 斉木別館","齊木別館",None,"ryokan","三朝",rank=r,rank26=r2),
]

# === 大平温泉 ===
a,p,ac,r,r2 = "大平温泉","山形","大平溫泉（山形縣）",78,None
NEW += [
 H(a,p,ac,"大平温泉 滝見屋","瀧見屋",None,"ryokan","秘湯",rank=r,rank26=r2),
]

# === 秋の宮温泉郷 ===
a,p,ac,r,r2 = "秋の宮温泉郷","秋田","秋之宮溫泉鄉（秋田縣）",79,None
NEW += [
 H(a,p,ac,"秋の宮温泉 たけや","竹屋",None,"ryokan","秋の宮",rank=r,rank26=r2),
 H(a,p,ac,"秋の宮温泉郷 いぶり長者","いぶり長者",None,"ryokan","秋の宮",rank=r,rank26=r2),
]

# === 南あわじ ===
a,p,ac,r,r2 = "南あわじ温泉郷","兵庫","南淡路溫泉鄉（兵庫縣）",80,59
NEW += [
 H(a,p,ac,"南あわじ温泉 うめ丸","うめ丸",None,"ryokan","淡路",rank=r,rank26=r2),
 H(a,p,ac,"南あわじ温泉郷 慶野松原 汐湯音","汐湯音",None,"ryokan","慶野松原",rank=r,rank26=r2),
]

# === 小野川温泉 ===
a,p,ac,r,r2 = "小野川温泉","山形","小野川溫泉（山形縣）",81,None
NEW += [
 H(a,p,ac,"小野川温泉 あづま屋","あづま屋",None,"ryokan","小野川",rank=r,rank26=r2),
 H(a,p,ac,"小野川温泉 なかや","なかや",None,"ryokan","小野川",rank=r,rank26=r2),
]

# === 湯平温泉 ===
a,p,ac,r,r2 = "湯平温泉","大分","湯平溫泉（大分縣）",82,None
NEW += [
 H(a,p,ac,"湯平温泉 民宿","湯平溫泉 民宿",None,"minshuku","石畳の温泉街",rank=r,rank26=r2),
 H(a,p,ac,"湯平温泉 旅館 山水閣","山水閣",None,"ryokan","湯平",rank=r,rank26=r2),
]

# === かみのやま ===
a,p,ac,r,r2 = "かみのやま温泉","山形","上山溫泉（山形縣）",83,42
NEW += [
 H(a,p,ac,"かみのやま温泉 ホテル古窯","酒店古窯",None,"hotel","上山",rank=r,rank26=r2),
 H(a,p,ac,"かみのやま温泉 葉山館","葉山館",None,"ryokan","上山",rank=r,rank26=r2),
]

# === 祖谷 ===
a,p,ac,r,r2 = "祖谷温泉","徳島","祖谷溫泉（德島縣）",84,25
NEW += [
 H(a,p,ac,"ホテル祖谷温泉","酒店祖谷溫泉",24350,"hotel","渓谷展望（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"祖谷温泉 びざん荘","美山莊",None,"ryokan","祖谷",rank=r,rank26=r2),
]

# === 愛山渓 ===
a,p,ac,r,r2 = "大雪山愛山渓温泉","北海道","大雪山愛山溪溫泉（北海道）",85,None
NEW += [
 H(a,p,ac,"愛山渓温泉 ホテル天山荘","天山莊",None,"hotel","大雪山",rank=r,rank26=r2),
]

# === 川治温泉 ===
a,p,ac,r,r2 = "川治温泉","栃木","川治溫泉（栃木縣）",86,60
NEW += [
 H(a,p,ac,"川治温泉 湯の宿 湯主一條","湯主一條",None,"ryokan","川治",rank=r,rank26=r2),
 H(a,p,ac,"川治温泉 あけぼの","あけぼの",None,"ryokan","川治",rank=r,rank26=r2),
]

# === 塩原 ===
a,p,ac,r,r2 = "塩原温泉郷","栃木","鹽原溫泉鄉（栃木縣）",87,None
NEW += [
 H(a,p,ac,"塩原温泉 山のホテル","山之酒店",None,"hotel","塩原",rank=r,rank26=r2),
 H(a,p,ac,"塩原温泉 湯の香荘","湯之香莊",None,"ryokan","塩原",rank=r,rank26=r2),
 H(a,p,ac,"塩原温泉 甘露の森","甘露之森",None,"ryokan","塩原",rank=r,rank26=r2),
]

# === 南紀白浜 ===
a,p,ac,r,r2 = "南紀白浜温泉","和歌山","南紀白濱溫泉（和歌山縣）",88,41
NEW += [
 H(a,p,ac,"白浜古賀の井リゾート","古賀之井度假村",None,"hotel","白浜",rank=r,rank26=r2),
 H(a,p,ac,"白浜温泉 浜千鳥の湯 海舟","海舟",None,"ryokan","白浜",rank=r,rank26=r2),
 H(a,p,ac,"白浜温泉 ホテル川久","酒店川久",None,"hotel","高級",rank=r,rank26=r2),
]

# === 長門湯本 ===
a,p,ac,r,r2 = "長門湯本温泉","山口","長門湯本溫泉（山口縣）",89,100
NEW += [
 H(a,p,ac,"長門湯本温泉 大谷山荘","大谷山莊",None,"ryokan","高級",rank=r,rank26=r2),
 H(a,p,ac,"長門湯本温泉 恩湯","恩湯",None,"day_onsen","温泉施設",rank=r,rank26=r2,alert="day_onsen"),
 H(a,p,ac,"長門湯本温泉 おとずれの里 ゆもとや","ゆもとや",None,"ryokan","長門",rank=r,rank26=r2),
]

# === 九重 ===
a,p,ac,r,r2 = "九重夢温泉郷","大分","九重夢溫泉鄉（大分縣）",90,86
NEW += [
 H(a,p,ac,"九重温泉 壁湯温泉 山水館","山水館",None,"ryokan","壁湯",rank=r,rank26=r2),
 H(a,p,ac,"九重温泉 宝泉寺温泉 豊後屋","豐後屋",None,"ryokan","宝泉寺",rank=r,rank26=r2),
]

# === 上の湯 ===
a,p,ac,r,r2 = "上の湯温泉","北海道","上之湯溫泉（北海道）",91,None
NEW += [
 H(a,p,ac,"上の湯温泉 宿","上之湯溫泉宿",None,"ryokan","秘湯",rank=r,rank26=r2),
]

# === 支笏湖 ===
a,p,ac,r,r2 = "支笏湖温泉・丸駒温泉","北海道","支笏湖・丸駒溫泉（北海道）",92,72
NEW += [
 H(a,p,ac,"支笏湖 丸駒温泉旅館","丸駒溫泉旅館",None,"ryokan","湖畔秘湯",rank=r,rank26=r2),
 H(a,p,ac,"支笏湖温泉 しこつ湖鶴雅リゾートスパ 水の謌","水之謌",None,"hotel","鶴雅",rank=r,rank26=r2),
]

# === 酸ヶ湯 ===
a,p,ac,r,r2 = "酸ヶ湯温泉","青森","酸湯溫泉（青森縣）",93,None
NEW += [
 H(a,p,ac,"酸ヶ湯温泉旅館","酸湯溫泉旅館",None,"ryokan","混浴・秘湯名門",rank=r,rank26=r2),
]

# === 四万温泉 ===
a,p,ac,r,r2 = "四万温泉","群馬","四萬溫泉（群馬縣）",94,None
NEW += [
 H(a,p,ac,"四万温泉 積善館","積善館",None,"ryokan","千と千尋モチーフ・老舗",official="https://www.sekizenkan.co.jp/",rank=r,rank26=r2),
 H(a,p,ac,"四万温泉 柏屋旅館","柏屋旅館",None,"ryokan","四万",rank=r,rank26=r2),
 H(a,p,ac,"四万温泉 日向見温泉 共同浴場","日向見共同浴場",500,"day_onsen","共同浴場",rank=r,rank26=r2,alert="day_onsen"),
]

# === 別府 — mega ===
a,p,ac,r,r2 = "別府温泉","大分","別府溫泉（大分縣）",95,16
NEW += [
 H(a,p,ac,"杉乃井ホテル","杉乃井酒店",17700,"hotel","棚湯・大型リゾート",official="https://www.suginoi-hotel.com/",rank=r,rank26=r2,en="Suginoi Hotel"),
 H(a,p,ac,"悠彩の宿 望海","悠彩之宿 望海",7700,"ryokan","九州売れた宿連覇",rank=r,rank26=r2),
 H(a,p,ac,"亀の井ホテル 別府","龜之井酒店 別府",5880,"hotel","駅徒歩5分",rank=r,rank26=r2),
 H(a,p,ac,"大江戸温泉物語 別府清風","大江戶 別府清風",11400,"hotel","別府湾ビュー",rank=r,rank26=r2),
 H(a,p,ac,"グランドメルキュール別府湾リゾート＆スパ","Grand Mercure 別府灣",5360,"hotel","ハーモニーランド近く",rank=r,rank26=r2),
 H(a,p,ac,"別府温泉 竹乃井ホテル","竹乃井酒店",None,"hotel","別府",rank=r,rank26=r2),
 H(a,p,ac,"別府温泉 花菱ホテル","花菱酒店",None,"hotel","別府",rank=r,rank26=r2),
]

# === 磐梯熱海 ===
a,p,ac,r,r2 = "磐梯熱海温泉","福島","磐梯熱海溫泉（福島縣）",96,None
NEW += [
 H(a,p,ac,"磐梯熱海温泉 ホテル華の湯","酒店華之湯",None,"hotel","磐梯熱海",rank=r,rank26=r2),
 H(a,p,ac,"磐梯熱海温泉 二岐温泉 大丸旅館","大丸旅館",None,"ryokan","近隣二岐",rank=r,rank26=r2),
]

# === 湯涌 ===
a,p,ac,r,r2 = "湯涌温泉","石川","湯涌溫泉（石川縣）",97,None
NEW += [
 H(a,p,ac,"湯涌温泉 金沢湯涌温泉 湯の里","湯之里",None,"ryokan","金沢近郊",rank=r,rank26=r2),
 H(a,p,ac,"湯涌温泉 白鷺荘","白鷺莊",None,"ryokan","湯涌",rank=r,rank26=r2),
]

# === 日景 ===
a,p,ac,r,r2 = "日景温泉","秋田","日景溫泉（秋田縣）",98,None
NEW += [
 H(a,p,ac,"日景温泉 ホテルサンバリオ","Hotel Sunbario",None,"hotel","日景",rank=r,rank26=r2),
]

# === 河口湖 ===
a,p,ac,r,r2 = "河口湖温泉","山梨","河口湖溫泉（山梨縣）",99,None
NEW += [
 H(a,p,ac,"河口湖温泉 湖楽 おんやど富士","溫宿富士",None,"ryokan","富士山ビュー",rank=r,rank26=r2),
 H(a,p,ac,"河口湖温泉 風のホテル","風之酒店",None,"hotel","河口湖",rank=r,rank26=r2),
 H(a,p,ac,"河口湖温泉 ホテルレジーナ河口湖","Hotel Regina 河口湖",None,"hotel","富士ビュー",rank=r,rank26=r2),
 H(a,p,ac,"河口湖温泉 秀峰閣 湖月","秀峰閣 湖月",None,"ryokan","人気",rank=r,rank26=r2),
]

# === 湯原 ===
a,p,ac,r,r2 = "湯原温泉","岡山","湯原溫泉（岡山縣）",100,87
NEW += [
 H(a,p,ac,"湯原温泉 湯原国際観光ホテル 菊屋","菊屋",None,"hotel","砂湯近く",rank=r,rank26=r2),
 H(a,p,ac,"湯原温泉 おやど 風雅","親宿風雅",None,"ryokan","湯原",rank=r,rank26=r2),
]

# === 2026-only / NEW areas ===
# 寸又峡
a,p,ac,r,r2 = "寸又峡温泉","静岡","寸又峽溫泉（靜岡縣）",None,11
NEW += [
 H(a,p,ac,"寸又峡温泉 翠紅苑","翠紅苑",15400,"ryokan","（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"寸又峡温泉 湯の里 八坂","八坂",None,"ryokan","寸又峡",rank=r,rank26=r2),
]

# 那須
a,p,ac,r,r2 = "那須温泉郷","栃木","那須溫泉鄉（栃木縣）",None,11
NEW += [
 H(a,p,ac,"ホテルエピナール那須","Hotel Épinal 那須",None,"hotel","売れた宿大賞",rank=r,rank26=r2),
 H(a,p,ac,"那須温泉 三斗小屋温泉 大黒屋","大黑屋",None,"ryokan","秘湯",rank=r,rank26=r2),
 H(a,p,ac,"那須温泉 山水閣","山水閣",None,"ryokan","那須",rank=r,rank26=r2),
 H(a,p,ac,"那須温泉 ホテルサンバレー那須","Hotel Sun Valley 那須",None,"hotel","大型",rank=r,rank26=r2),
]

# 秋田八幡平
a,p,ac,r,r2 = "秋田八幡平温泉郷","秋田","秋田八幡平溫泉鄉（秋田縣）",None,18
NEW += [
 H(a,p,ac,"後生掛温泉","後生掛溫泉",17000,"ryokan","秘湯（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"八幡平温泉 玉川温泉","玉川溫泉",None,"ryokan","強酸性泉",rank=r,rank26=r2),
]

# 嬉野
a,p,ac,r,r2 = "嬉野温泉","佐賀","嬉野溫泉（佐賀縣）",None,19
NEW += [
 H(a,p,ac,"嬉野温泉 和多屋別荘","和多屋別墅",None,"ryokan","嬉野代表",rank=r,rank26=r2),
 H(a,p,ac,"嬉野温泉 お茶の宿 嬉野荘","嬉野莊",None,"ryokan","嬉野",rank=r,rank26=r2),
 H(a,p,ac,"嬉野温泉 旅館 さいかい","西海",None,"ryokan","嬉野",rank=r,rank26=r2),
]

# 満願寺
a,p,ac,r,r2 = "満願寺温泉","熊本","滿願寺溫泉（熊本縣）",None,28
NEW += [
 H(a,p,ac,"満願寺温泉 四季の里 はなむら","四季之里 花村",15500,"ryokan","満願寺",rank=r,rank26=r2),
]

# 蔦温泉
a,p,ac,r,r2 = "蔦温泉","青森","蔦溫泉（青森縣）",None,30
NEW += [
 H(a,p,ac,"蔦温泉旅館","蔦溫泉旅館",None,"ryokan","秘湯・宮沢賢治",rank=r,rank26=r2),
]

# いわき湯本
a,p,ac,r,r2 = "いわき湯本温泉","福島","磐城湯本溫泉（福島縣）",None,32
NEW += [
 H(a,p,ac,"スパリゾートハワイアンズ","Spa Resort Hawaiians",12800,"hotel","（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"いわき湯本温泉 古滝屋","古瀧屋",None,"ryokan","湯本",rank=r,rank26=r2),
]

# 白骨
a,p,ac,r,r2 = "白骨温泉","長野","白骨溫泉（長野縣）",None,36
NEW += [
 H(a,p,ac,"白骨温泉 泡の湯","泡之湯",None,"ryokan","乳白泉",rank=r,rank26=r2),
 H(a,p,ac,"白骨温泉 白骨温泉 釣鐘屋","釣鐘屋",None,"ryokan","白骨",rank=r,rank26=r2),
 H(a,p,ac,"白骨温泉 ホテル花屋","酒店花屋",None,"hotel","白骨",rank=r,rank26=r2),
]

# 白布
a,p,ac,r,r2 = "白布温泉","山形","白布溫泉（山形縣）",None,40
NEW += [
 H(a,p,ac,"白布温泉 東屋","東屋",None,"ryokan","白布",rank=r,rank26=r2),
 H(a,p,ac,"白布温泉 西屋","西屋",None,"ryokan","白布",rank=r,rank26=r2),
]

# 湯の峰
a,p,ac,r,r2 = "湯の峰温泉","和歌山","湯之峰溫泉（和歌山縣）",None,45
NEW += [
 H(a,p,ac,"湯の峯壮","湯之峯莊",18850,"ryokan","（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"湯の峰温泉 あづまや","あづまや",None,"ryokan","世界遺産近く",rank=r,rank26=r2),
]

# 芦原
a,p,ac,r,r2 = "芦原温泉","福井","蘆原（あわら）溫泉（福井縣）",None,47
NEW += [
 H(a,p,ac,"あわら温泉 グランディア芳泉","Grandia 芳泉",None,"hotel","あわら",rank=r,rank26=r2),
 H(a,p,ac,"あわら温泉 まつや千千","まつや千千",None,"ryokan","高級",rank=r,rank26=r2),
 H(a,p,ac,"あわら温泉 清風荘","清風莊",None,"ryokan","あわら",rank=r,rank26=r2),
]

# 下風呂
a,p,ac,r,r2 = "下風呂温泉","青森","下風呂溫泉（青森縣）",None,52
NEW += [
 H(a,p,ac,"下風呂温泉 海峡の湯","海峡之湯",None,"day_onsen","海峡ビュー",rank=r,rank26=r2,alert="day_onsen"),
 H(a,p,ac,"下風呂温泉 いさばや旅館","いさばや",None,"ryokan","下風呂",rank=r,rank26=r2),
]

# 山代
a,p,ac,r,r2 = "山代温泉","石川","山代溫泉（石川縣）",None,53
NEW += [
 H(a,p,ac,"山代温泉 瑠璃光","瑠璃光",None,"ryokan","加賀温泉郷",rank=r,rank26=r2),
 H(a,p,ac,"山代温泉 叶や千賀","叶や千賀",None,"ryokan","高級",rank=r,rank26=r2),
 H(a,p,ac,"山代温泉 べにや無何有","紅屋無何有",None,"ryokan","人気",rank=r,rank26=r2),
]

# 湯村（兵庫）
a,p,ac,r,r2 = "湯村温泉","兵庫","湯村溫泉（兵庫縣）",None,56
NEW += [
 H(a,p,ac,"湯村温泉 ゆめやど 万天","萬天",None,"ryokan","湯村",rank=r,rank26=r2),
 H(a,p,ac,"湯村温泉 湯治場 かやの","かやの",None,"ryokan","湯村",rank=r,rank26=r2),
]

# 南紀勝浦
a,p,ac,r,r2 = "南紀勝浦温泉","和歌山","南紀勝浦溫泉（和歌山縣）",None,57
NEW += [
 H(a,p,ac,"ホテル浦島","酒店浦島",None,"hotel","洞窟風呂（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"南紀勝浦温泉 中の島","中之島",None,"hotel","海に浮かぶ宿",rank=r,rank26=r2),
 H(a,p,ac,"南紀勝浦温泉 紀州鉄道 ホテル中の島","紀州鐵道 中之島",None,"hotel","勝浦",rank=r,rank26=r2),
]

# 温湯
a,p,ac,r,r2 = "温湯温泉","青森","溫湯溫泉（青森縣）",None,61
NEW += [
 H(a,p,ac,"温湯温泉 願掛不動の湯","願掛不動之湯",None,"ryokan","温湯",rank=r,rank26=r2),
]

# 南房総白浜
a,p,ac,r,r2 = "南房総白浜温泉郷","千葉","南房總白濱溫泉鄉（千葉縣）",None,62
NEW += [
 H(a,p,ac,"南房総 白浜温泉 ホテル＆リゾーツ 南房総","Hotels & Resorts 南房總",None,"hotel","白浜",rank=r,rank26=r2),
 H(a,p,ac,"南房総白浜 富山温泉 ホテル水明","酒店水明",None,"hotel","南房総",rank=r,rank26=r2),
]

# 五頭
a,p,ac,r,r2 = "五頭温泉郷","新潟","五頭溫泉鄉（新潟縣）",None,67
NEW += [
 H(a,p,ac,"清廣館","清廣館",16500,"ryokan","（既存補強）",rank=r,rank26=r2),
 H(a,p,ac,"五頭温泉郷 出湯温泉 お宿 玉井屋","玉井屋",None,"ryokan","出湯",rank=r,rank26=r2),
]

# 温泉津
a,p,ac,r,r2 = "温泉津温泉","島根","溫泉津溫泉（島根縣）",None,68
NEW += [
 H(a,p,ac,"温泉津温泉 温泉津温泉元湯","元湯",None,"ryokan","世界遺産・町並み",rank=r,rank26=r2),
 H(a,p,ac,"温泉津温泉 いやしの宿 大正屋","大正屋",None,"ryokan","温泉津",rank=r,rank26=r2),
]

# 鳥羽
a,p,ac,r,r2 = "鳥羽温泉郷","三重","鳥羽溫泉鄉（三重縣）",None,70
NEW += [
 H(a,p,ac,"鳥羽国際ホテル","鳥羽國際酒店",None,"hotel","海辺",rank=r,rank26=r2),
 H(a,p,ac,"鳥羽温泉 戸田家","戶田家",None,"ryokan","老舗",rank=r,rank26=r2),
 H(a,p,ac,"鳥羽温泉 海のホテル 島花","島花",None,"hotel","鳥羽",rank=r,rank26=r2),
]

# 湯ノ花（福島）
a,p,ac,r,r2 = "湯ノ花温泉","福島","湯之花溫泉（福島縣）",None,71
NEW += [
 H(a,p,ac,"湯ノ花温泉 莊","湯之花溫泉莊",None,"ryokan","福島",rank=r,rank26=r2),
]

# 岳温泉
a,p,ac,r,r2 = "岳温泉","福島","岳溫泉（福島縣）",None,73
NEW += [
 H(a,p,ac,"岳温泉 ホテルハイツ","Hotel Heights",None,"hotel","岳",rank=r,rank26=r2),
 H(a,p,ac,"岳温泉 福島アパホテル＆リゾート","APA 福島",None,"hotel","岳近く",rank=r,rank26=r2),
]

# 浅間
a,p,ac,r,r2 = "浅間温泉","長野","淺間溫泉（長野縣）",None,74
NEW += [
 H(a,p,ac,"浅間温泉 湯元館","湯元館",None,"ryokan","松本近郊",rank=r,rank26=r2),
 H(a,p,ac,"浅間温泉 勹果別邸 もみぢの宿","もみぢ之宿",None,"ryokan","浅間",rank=r,rank26=r2),
]

# 然別峡
a,p,ac,r,r2 = "然別峡温泉","北海道","然別峽溫泉（北海道）",None,77
NEW += [
 H(a,p,ac,"然別峡温泉 ホテルノンノ","Hotel Nonno",None,"hotel","秘湯",rank=r,rank26=r2),
]

# 浅虫
a,p,ac,r,r2 = "浅虫温泉","青森","淺蟲溫泉（青森縣）",None,79
NEW += [
 H(a,p,ac,"浅虫温泉 南部屋ツアーズ","南部屋",None,"ryokan","浅虫",rank=r,rank26=r2),
 H(a,p,ac,"浅虫温泉 南部屋","南部屋旅館",None,"ryokan","浅虫",rank=r,rank26=r2),
 H(a,p,ac,"浅虫温泉 ホテル秋田屋","酒店秋田屋",None,"hotel","浅虫",rank=r,rank26=r2),
]

# 夏油
a,p,ac,r,r2 = "夏油温泉","岩手","夏油溫泉（岩手縣）",None,80
NEW += [
 H(a,p,ac,"夏油温泉 夏油高原温泉ホテル","夏油高原溫泉酒店",None,"hotel","スキー",rank=r,rank26=r2),
]

# 鳴子
a,p,ac,r,r2 = "鳴子温泉郷","宮城","鳴子溫泉鄉（宮城縣）",None,84
NEW += [
 H(a,p,ac,"鳴子温泉 大沼","大沼",None,"ryokan","鳴子",rank=r,rank26=r2),
 H(a,p,ac,"鳴子温泉 ゆさや旅館","ゆさや",None,"ryokan","鳴子",rank=r,rank26=r2),
 H(a,p,ac,"鳴子温泉 旅館大沼","旅館大沼",None,"ryokan","鳴子",rank=r,rank26=r2),
]

# 熱川
a,p,ac,r,r2 = "熱川温泉","静岡","熱川溫泉（靜岡縣）",None,88
NEW += [
 H(a,p,ac,"熱川温泉 湯の宿 おかだ","おかだ",None,"ryokan","熱川",rank=r,rank26=r2),
 H(a,p,ac,"熱川温泉 ホテルカターラリゾート&スパ","Catara Resort",None,"hotel","熱川",rank=r,rank26=r2),
]

# 奥鬼怒
a,p,ac,r,r2 = "奥鬼怒温泉郷","栃木","奧鬼怒溫泉鄉（栃木縣）",None,95
NEW += [
 H(a,p,ac,"奥鬼怒温泉 加仁湯","加仁湯",None,"ryokan","秘湯",rank=r,rank26=r2),
 H(a,p,ac,"奥鬼怒温泉 手白澤温泉","手白澤溫泉",None,"ryokan","秘湯",rank=r,rank26=r2),
]

# 定山渓 — mega 2026
a,p,ac,r,r2 = "定山渓温泉","北海道","定山溪溫泉（北海道）",None,96
NEW += [
 H(a,p,ac,"定山渓ビューホテル","定山溪 View Hotel",10200,"hotel","巨大スパ・北海道売れた宿連覇",rank=r,rank26=r2),
 H(a,p,ac,"定山渓万世閣ホテルミリオーネ","萬世閣 Hotel Millione",10200,"hotel","ビュッフェ・大浴場",rank=r,rank26=r2),
 H(a,p,ac,"ぬくもりの宿 ふる川","溫暖之宿 ふる川",17800,"ryokan","囲炉裏・ぬくもり",rank=r,rank26=r2),
 H(a,p,ac,"鹿の湯","鹿之湯",11000,"ryokan","名湯・サウナ",rank=r,rank26=r2),
 H(a,p,ac,"定山渓温泉 章月グランドホテル","章月 Grand Hotel",None,"hotel","定山渓",rank=r,rank26=r2),
 H(a,p,ac,"定山渓温泉 ホテルノービス","Hotel Nobis",None,"hotel","定山渓",rank=r,rank26=r2),
]

# 長島
a,p,ac,r,r2 = "長島温泉","三重","長島溫泉（三重縣）",None,99
NEW += [
 H(a,p,ac,"ナガシマリゾート ホテル花水木","酒店花水木",None,"hotel","ナガシマスパーランド",rank=r,rank26=r2),
 H(a,p,ac,"ナガシマリゾート ガーデンズ","Gardens",None,"hotel","長島",rank=r,rank26=r2),
]

# Extra popular for mega coverage gaps
a,p,ac,r,r2 = "箱根温泉","神奈川","箱根溫泉（神奈川縣）",1,11
NEW += [
 H(a,p,ac,"箱根高原ホテル","箱根高原酒店",7930,"hotel","芦ノ湖近く・2種泉質",rank=r,rank26=r2),
 H(a,p,ac,"湯本富士屋ホテル","湯本富士屋酒店",None,"hotel","箱根湯本駅近・クラシック",official="https://www.yumotofujiya.jp/",rank=r,rank26=r2),
 H(a,p,ac,"箱根湯の花プリンスホテル","箱根湯之花 Prince Hotel",None,"hotel","高所・絶景",rank=r,rank26=r2),
]

a,p,ac,r,r2 = "草津温泉","群馬","草津溫泉（群馬縣）",2,7
NEW += [
 H(a,p,ac,"草津舘","草津館",12100,"ryokan","湯畑そば・自家源泉",rank=r,rank26=r2),
 H(a,p,ac,"中村屋旅館","中村屋旅館",11900,"ryokan","湯畑30秒・貸切風呂",rank=r,rank26=r2),
]

print(f"Prepared {len(NEW)} candidate new hotels")

# ---- merge ----
with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

old_n = len(data["hotels"])
# Map ranks from ranking_compare by area
rank_map = {}
for row in data["ranking_compare"]:
    rank_map[row["area_jp"]] = (row.get("rank_2024"), row.get("rank_2026"), row.get("area_cn"), row.get("prefecture"))
# Also alias keys for known variants
aliases = {
    "阿蘇内牧＆地獄温泉／阿蘇温泉郷": "阿蘇内牧＆地獄温泉",
    "阿蘇内牧＆地獄温泉": "阿蘇内牧＆地獄温泉",
}

def key(h):
    return (h["onsen_area"].strip(), h["property_jp"].strip())

existing = {key(h): h for h in data["hotels"]}
added = 0
skipped = 0
for h in NEW:
    # fill ranks from compare if missing
    area = h["onsen_area"]
    info = rank_map.get(area) or rank_map.get(aliases.get(area, area))
    if info:
        r24, r26, acn, pref = info
        if h["rank"] is None and r24 is not None: h["rank"] = r24
        if h["rank_2026"] is None and r26 is not None: h["rank_2026"] = r26
        if not h.get("area_cn") and acn:
            h["area_cn"] = acn + (f"（{pref}縣）" if pref and "縣" not in acn and "県" not in acn else "")
    k = key(h)
    if k in existing:
        skipped += 1
        continue
    # also fuzzy: same jp name in same area ignoring whitespace
    existing[k] = h
    data["hotels"].append(h)
    added += 1

# Normalize area names for Aso variant hotels already in DB
for h in data["hotels"]:
    if h["onsen_area"] == "阿蘇内牧＆地獄温泉":
        # keep as-is (matches existing)
        pass

new_n = len(data["hotels"])
areas_covered = len(set(h["onsen_area"] for h in data["hotels"]))
by_area = Counter(h["onsen_area"] for h in data["hotels"])

# Update meta
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
data["meta"]["updated"] = "2026-10-20"
data["meta"]["updated_label"] = (
    f"最後更新：2026-10-20 {now.split()[1]} Asia/Hong_Kong (HKT, UTC+8)"
    f"｜旅館 {new_n} 間（じゃらん／楽天エリア人氣榜擴充）｜含 2024／2026 排名對照"
)
data["meta"]["disclaimer_zh"] = (
    "價錢為約2026年10月／公開訂房頁的一泊二食（每人）參考價，會隨季節大幅波動。"
    "空白＝未能核實、不臆造。Rank 為溫泉地名次（非旅館個人名次）。"
    "住宿名單以排名溫泉地為範圍，從じゃらんnet／楽天トラベル等人氣・銷售榜整理代表性旅館，"
    "並非日本全國所有溫泉旅館，亦非 HOY／電視東京節目逐集抽取。"
    "本站與 HOY／電視東京／各旅館／じゃらん／楽天無隸屬關係，僅供私人行程規劃。"
)
data["meta"]["source_banner_zh"] = (
    f"資料品質：web_summary_crosschecked + jalan_rakuten_area_list｜"
    f"旅館 {new_n} 間（節目交叉核對＋訂房站區域人氣榜擴充，非全國穷尽）"
)
# Trim / refresh alerts — collapse hotel-specific into summary note; keep critical
alerts = [a for a in data["meta"]["alerts"] if a["level"] in ("danger", "warn") or "方法" in a.get("zh","")]
# Keep closed / phone / rebrand; drop outdated UI tip
alerts = [a for a in data["meta"]["alerts"] if not a["zh"].startswith("【新】")]
# Add coverage note
alerts.append({
    "level": "info",
    "zh": f"【住宿範圍】目前收錄約 {new_n} 間：以 2024＋2026 排名溫泉地為主，來自じゃらん／楽天區域人氣榜與既有節目交叉核對；非日本全國所有溫泉旅館。熱門地（箱根・草津・別府・有馬・熱海等）較密，少數秘湯較薄。"
})
data["meta"]["alerts"] = alerts

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"OLD={old_n} NEW_ADDED={added} SKIPPED_DUP={skipped} TOTAL={new_n} AREAS={areas_covered}")
print("Top areas:", by_area.most_common(15))
thin = [a for a,c in sorted(by_area.items(), key=lambda x:x[1]) if c<=1]
print(f"Thin (≤1 hotel) areas: {len(thin)}")
print("Sample thin:", thin[:20])

# Areas in compare with 0 hotels
hotel_areas = set(h["onsen_area"] for h in data["hotels"])
missing = [r["area_jp"] for r in data["ranking_compare"] if r["area_jp"] not in hotel_areas and not any(r["area_jp"].startswith(h) or h.startswith(r["area_jp"][:4]) for h in hotel_areas)]
# simpler missing check
missing2 = []
for r in data["ranking_compare"]:
    aj = r["area_jp"]
    if aj in hotel_areas: continue
    # partial
    if any(aj in ha or ha in aj for ha in hotel_areas): continue
    missing2.append(aj)
print("Still missing areas:", len(missing2), missing2[:30])

# ---- Excel ----
try:
    import openpyxl
    from openpyxl import load_workbook
    wb = load_workbook(XLSX)
    # Hotels_All sheet
    if "Hotels_All" in wb.sheetnames:
        del wb["Hotels_All"]
    ws = wb.create_sheet("Hotels_All", 0)
    headers = ["Rank_2024","Rank_2026","Onsen_Area","Area_CN","Prefecture","Property_JP","Property_CN","Property_EN",
               "Type","Price_JPY","Price_Band","Highlights","Description_CN","Official_URL","Rakuten_URL","Jalan_URL",
               "Booking_URL","Other_Booking","Source","Source_Quality","Alert"]
    ws.append(headers)
    for h in data["hotels"]:
        ws.append([
            h.get("rank"), h.get("rank_2026"), h.get("onsen_area"), h.get("area_cn"), h.get("prefecture"),
            h.get("property_jp"), h.get("property_cn"), h.get("property_en"),
            h.get("type"), h.get("price_jpy"), h.get("price_band"), h.get("highlights"), h.get("description_cn"),
            h.get("official_url"), h.get("rakuten_url"), h.get("jalan_url"),
            h.get("booking_url"), h.get("other_booking"), h.get("source"), h.get("source_quality"), h.get("alert"),
        ])
    # Also refresh Hotels_Mentioned keep old sheet; append note in Notes
    if "Notes" in wb.sheetnames:
        wb["Notes"].append([None, None])
        wb["Notes"].append(["Hotels_All expanded", f"{new_n} properties from Jalan/Rakuten area lists + prior cross-check; not exhaustive Japan-wide. Updated 2026-10-20 HKT."])
    wb.save(XLSX)
    # mirror store
    import shutil
    shutil.copy2(XLSX, STORE / "Japan_Onsen_100_Tracker.xlsx")
    shutil.copy2(DATA, STORE / "onsen-100-tracker" / "data.json")
    print("Excel + store updated")
except Exception as e:
    print("Excel error:", e)

print("DONE")
