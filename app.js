(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function fmtPrice(p) {
    if (p == null || p === "") return "—";
    const n = Number(p);
    if (!isFinite(n)) return "—";
    return "約 ¥" + n.toLocaleString("ja-JP");
  }

  function linkBtn(url, label) {
    if (!url) return `<a class="disabled" href="#">${esc(label)}</a>`;
    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
  }

  function bookLinks(h) {
    const items = [];
    if (h.official_url) items.push(`<a href="${esc(h.official_url)}" target="_blank" rel="noopener">官方</a>`);
    if (h.rakuten_url) items.push(`<a href="${esc(h.rakuten_url)}" target="_blank" rel="noopener">楽天</a>`);
    if (h.jalan_url) items.push(`<a href="${esc(h.jalan_url)}" target="_blank" rel="noopener">Jalan</a>`);
    if (h.booking_url) items.push(`<a href="${esc(h.booking_url)}" target="_blank" rel="noopener">Booking</a>`);
    if (h.other_booking) items.push(`<a href="${esc(h.other_booking)}" target="_blank" rel="noopener">其他</a>`);
    if (!items.length) return '<span class="muted">連結待補</span>';
    return `<div class="book-links">${items.join("")}</div>`;
  }

  function fmtRank(r) {
    return r == null || r === "" ? "—" : "#" + r;
  }

  function rankPairText(h) {
    const a = h.rank == null ? "—" : "#" + h.rank;
    const b = h.rank_2026 == null ? "—" : "#" + h.rank_2026;
    return `2024 ${a}　／　2026 ${b}`;
  }

  function rankDelta(r24, r26) {
    if (r24 == null || r26 == null || r24 === "" || r26 === "") return null;
    return Number(r24) - Number(r26);
  }

  function renderRanks(list, mount) {
    if (!mount) return;
    mount.innerHTML = list.map(r => `
      <div class="rank-item">
        <div class="n">#${esc(r.rank)}</div>
        <div class="a">${esc(r.area_cn || r.area)}</div>
        <div class="p">${esc(r.prefecture_cn || r.prefecture || "")}</div>
      </div>`).join("");
  }

  function alertChip(h) {
    if (h.alert === "closed") return '<span class="chip alert-closed">休館中</span>';
    if (h.alert === "phone_only") return '<span class="chip alert-phone">僅電話預約</span>';
    if (h.alert === "rebranded") return '<span class="chip alert-rebrand">已改 Hilton</span>';
    if (h.alert === "day_onsen") return '<span class="chip">日歸入浴</span>';
    return "";
  }

  function changeClass(ch) {
    if (!ch) return "";
    if (ch === "NEW") return "new";
    if (ch === "DROPPED") return "dropped";
    if (ch === "SAME") return "same";
    if (String(ch).startsWith("+")) return "up";
    if (String(ch).startsWith("-")) return "down";
    return "";
  }

  function renderCards(hotels) {
    const mount = $("#cards");
    if (!mount) return;
    if (!hotels.length) {
      mount.innerHTML = '<p class="stats">沒有符合條件的住宿／設施。</p>';
      return;
    }
    mount.innerHTML = hotels.map(h => {
      const delta = rankDelta(h.rank, h.rank_2026);
      let deltaChip = "";
      if (delta != null) {
        if (delta > 0) deltaChip = `<span class="chip chip-up">↑${delta}</span>`;
        else if (delta < 0) deltaChip = `<span class="chip chip-down">↓${Math.abs(delta)}</span>`;
        else deltaChip = `<span class="chip">＝</span>`;
      }
      return `
      <article class="card">
        <div class="rank-badge">
          <span class="rank-line">2024 ${esc(fmtRank(h.rank))}</span>
          <span class="rank-line">2026 ${esc(fmtRank(h.rank_2026))}</span>
        </div>
        <div>
          <span class="area">${esc(h.area_cn || h.onsen_area || "")}</span>
          <h3>${esc(h.property_cn || h.property_en || h.property_jp)}</h3>
          <div class="jp">${esc(h.property_jp)}${h.property_en ? " · " + esc(h.property_en) : ""}</div>
          <div class="rank-pair">${esc(rankPairText(h))} ${deltaChip}</div>
          <div class="meta">
            <span class="chip price">${esc(fmtPrice(h.price_jpy))}${h.price_jpy != null ? "／人" : ""}</span>
            <span class="chip">${esc(h.price_band || "")}</span>
            <span class="chip">${esc(h.type || "")}</span>
            ${alertChip(h)}
          </div>
          <p class="desc">${esc(h.description_cn || "")}</p>
          ${h.highlights ? `<p class="hl">賣點：${esc(h.highlights)}</p>` : ""}
          <div class="links">
            ${linkBtn(h.official_url, "官方")}
            ${linkBtn(h.rakuten_url, "楽天")}
            ${linkBtn(h.jalan_url, "Jalan")}
            ${linkBtn(h.booking_url, "Booking")}
            ${linkBtn(h.other_booking, "其他")}
          </div>
        </div>
      </article>`;
    }).join("");
  }

  function renderHotelsTable(hotels) {
    const body = $("#hotels-body");
    if (!body) return;
    if (!hotels.length) {
      body.innerHTML = '<tr><td colspan="8">沒有符合條件的住宿／設施。</td></tr>';
      return;
    }
    body.innerHTML = hotels.map(h => `
      <tr>
        <td class="rk">${esc(fmtRank(h.rank))}</td>
        <td class="rk">${esc(fmtRank(h.rank_2026))}</td>
        <td>
          <div class="area-cn">${esc(areaCnShort(h))}</div>
          <div class="area-jp">${esc(h.onsen_area || "")}</div>
        </td>
        <td>
          <div class="prop-cn">${esc(h.property_cn || h.property_jp)}</div>
          <div class="prop-jp">${esc(h.property_jp)}${h.alert ? " · " + (
            h.alert === "closed" ? "休館中" :
            h.alert === "phone_only" ? "僅電話" :
            h.alert === "day_onsen" ? "日歸" : esc(h.alert)
          ) : ""}</div>
        </td>
        <td>${esc(h.prefecture || "")}</td>
        <td class="price">${esc(fmtPrice(h.price_jpy))}</td>
        <td>${esc(h.price_band || "未取得")}</td>
        <td>${bookLinks(h)}</td>
      </tr>`).join("");
  }

  function unique(arr) {
    return Array.from(new Set(arr.filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b), "zh-Hant"));
  }

  function sortHotels(list, mode) {
    const inf = 9999;
    const copy = list.slice();
    copy.sort((a, b) => {
      if (mode === "rank2024") {
        const ra = a.rank == null ? inf : Number(a.rank);
        const rb = b.rank == null ? inf : Number(b.rank);
        if (ra !== rb) return ra - rb;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "rank2026") {
        const ra = a.rank_2026 == null ? inf : Number(a.rank_2026);
        const rb = b.rank_2026 == null ? inf : Number(b.rank_2026);
        if (ra !== rb) return ra - rb;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "improve") {
        const da = rankDelta(a.rank, a.rank_2026);
        const db = rankDelta(b.rank, b.rank_2026);
        const va = da == null ? -inf : da;
        const vb = db == null ? -inf : db;
        if (va !== vb) return vb - va;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "drop") {
        const da = rankDelta(a.rank, a.rank_2026);
        const db = rankDelta(b.rank, b.rank_2026);
        const va = da == null ? inf : da;
        const vb = db == null ? inf : db;
        if (va !== vb) return va - vb;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "price_asc") {
        const pa = a.price_jpy == null ? inf : Number(a.price_jpy);
        const pb = b.price_jpy == null ? inf : Number(b.price_jpy);
        if (pa !== pb) return pa - pb;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "price_desc") {
        const pa = a.price_jpy == null ? -1 : Number(a.price_jpy);
        const pb = b.price_jpy == null ? -1 : Number(b.price_jpy);
        if (pa !== pb) return pb - pa;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "name_area") {
        const aa = a.area_cn || a.onsen_area || "";
        const bb = b.area_cn || b.onsen_area || "";
        const c = String(aa).localeCompare(String(bb), "zh-Hant");
        if (c !== 0) return c;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "name_prop") {
        const aa = a.property_cn || a.property_jp || "";
        const bb = b.property_cn || b.property_jp || "";
        return String(aa).localeCompare(String(bb), "zh-Hant");
      }
      return 0;
    });
    return copy;
  }

  let hotelView = "table";
  let hotelListMode = "show"; // all | show | area
  let hotelPage = 1;
  const HOTEL_PAGE_SIZE = 50;
  let lastFilteredHotels = [];

  function readListModeFromUrl() {
    try {
      const p = new URLSearchParams(location.search).get("list");
      if (p === "all" || p === "show" || p === "area") return p;
    } catch (e) {}
    return "show";
  }

  function syncListTabs() {
    $$(".list-tab").forEach(btn => {
      const on = btn.dataset.list === hotelListMode;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  function updatePagers(total, page, pageSize) {
    const pages = Math.max(1, Math.ceil(total / pageSize) || 1);
    const start = total ? (page - 1) * pageSize + 1 : 0;
    const end = Math.min(page * pageSize, total);
    const label = total ? `顯示 ${start}–${end} / ${total}` : "顯示 0 / 0";
    ["hotels-pager", "hotels-pager-bottom"].forEach(id => {
      const el = $(`#${id}`);
      if (!el) return;
      if (hotelView === "cards" || total <= pageSize) el.hidden = true;
      else el.hidden = false;
    });
    const info = $("#page-info");
    const infoB = $("#page-info-b");
    if (info) info.textContent = label;
    if (infoB) infoB.textContent = label;
    const prevDisabled = page <= 1;
    const nextDisabled = page >= pages;
    ["page-prev", "page-prev-b"].forEach(id => {
      const b = $(`#${id}`);
      if (b) b.disabled = prevDisabled;
    });
    ["page-next", "page-next-b"].forEach(id => {
      const b = $(`#${id}`);
      if (b) b.disabled = nextDisabled;
    });
  }

  function applyFilters(data) {
    try {
      if (!data || !data.hotels) return;
      if (!$("#hotels-body") && !$("#cards")) return;
      const q = (($("#q") && $("#q").value) || "").trim().toLowerCase();
      const pref = $("#pref") ? $("#pref").value : "";
      const area = $("#area") ? $("#area").value : "";
      const band = $("#band") ? $("#band").value : "";
      const mode = ($("#sort") && $("#sort").value) || "rank2024";
      let list = data.hotels.slice();
      if (hotelListMode === "show") list = list.filter(isShowHotel);
      else if (hotelListMode === "area") list = list.filter(h => !isShowHotel(h));
      if (pref) list = list.filter(h => h.prefecture === pref);
      if (area) list = list.filter(h => h.onsen_area === area);
      if (band) list = list.filter(h => h.price_band === band);
      if (q) {
        list = list.filter(h => {
          const blob = [
            h.property_jp, h.property_cn, h.property_en, h.area_cn,
            h.onsen_area, h.description_cn, h.highlights, h.prefecture
          ].join(" ").toLowerCase();
          return blob.includes(q);
        });
      }
      list = sortHotels(list, mode);
      lastFilteredHotels = list;

      const pages = Math.max(1, Math.ceil(list.length / HOTEL_PAGE_SIZE) || 1);
      if (hotelPage > pages) hotelPage = pages;
      if (hotelPage < 1) hotelPage = 1;

      const sortLabel = ($("#sort") && $("#sort").selectedOptions[0])
        ? $("#sort").selectedOptions[0].textContent : mode;
      const listLabel = hotelListMode === "show" ? "節目推薦"
        : hotelListMode === "area" ? "溫泉地人氣宿" : "全部";
      const stats = $("#stats");
      if (stats) {
        stats.textContent = `${listLabel} · 符合 ${list.length} / 全庫 ${data.hotels.length} 間 · 排序：${sortLabel}`;
      }

      // Prefer table when hotels-body exists; fall back to cards if table mount missing
      const hasTable = !!$("#hotels-body");
      const useCards = hotelView === "cards" || !hasTable;
      if (useCards) {
        renderCards(list);
        if ($("#hotels-table-wrap")) $("#hotels-table-wrap").classList.add("hidden");
        if ($("#cards")) $("#cards").classList.remove("hidden");
        updatePagers(list.length, 1, list.length || 1);
      } else {
        const start = (hotelPage - 1) * HOTEL_PAGE_SIZE;
        const pageSlice = list.slice(start, start + HOTEL_PAGE_SIZE);
        renderHotelsTable(pageSlice);
        if ($("#hotels-table-wrap")) $("#hotels-table-wrap").classList.remove("hidden");
        if ($("#cards")) $("#cards").classList.add("hidden");
        updatePagers(list.length, hotelPage, HOTEL_PAGE_SIZE);
      }
    } catch (err) {
      surfaceHotelError(err);
    }
  }

  function changeMagnitude(ch) {
    if (!ch || ch === "NEW" || ch === "DROPPED" || ch === "SAME") return 0;
    const n = parseInt(String(ch).replace("+", ""), 10);
    return isFinite(n) ? Math.abs(n) : 0;
  }

  function parseChangeNum(ch) {
    if (!ch || ch === "NEW" || ch === "DROPPED" || ch === "SAME") return null;
    const n = parseInt(String(ch).replace("+", ""), 10);
    return isFinite(n) ? n : null;
  }

  function sortCompare(list, mode) {
    const inf = 9999;
    const copy = list.slice();
    copy.sort((a, b) => {
      if (mode === "rank2024") {
        const ra = a.rank_2024 == null ? inf : Number(a.rank_2024);
        const rb = b.rank_2024 == null ? inf : Number(b.rank_2024);
        if (ra !== rb) return ra - rb;
        return String(a.area_jp).localeCompare(String(b.area_jp), "ja");
      }
      if (mode === "rank2026") {
        const ra = a.rank_2026 == null ? inf : Number(a.rank_2026);
        const rb = b.rank_2026 == null ? inf : Number(b.rank_2026);
        if (ra !== rb) return ra - rb;
        return String(a.area_jp).localeCompare(String(b.area_jp), "ja");
      }
      if (mode === "improve") {
        const da = parseChangeNum(a.change);
        const db = parseChangeNum(b.change);
        const va = da == null ? -inf : da;
        const vb = db == null ? -inf : db;
        if (va !== vb) return vb - va;
        return String(a.area_jp).localeCompare(String(b.area_jp), "ja");
      }
      if (mode === "drop") {
        const da = parseChangeNum(a.change);
        const db = parseChangeNum(b.change);
        const va = da == null ? inf : da;
        const vb = db == null ? inf : db;
        if (va !== vb) return va - vb;
        return String(a.area_jp).localeCompare(String(b.area_jp), "ja");
      }
      if (mode === "name") {
        return String(a.area_cn || a.area_jp).localeCompare(String(b.area_cn || b.area_jp), "zh-Hant");
      }
      return 0;
    });
    return copy;
  }

  function applyCompareFilters(data) {
    const body = $("#compare-body");
    if (!body || !data.ranking_compare) return;
    const mode = ($("#compare-filter") && $("#compare-filter").value) || "all";
    const q = (($("#compare-q") && $("#compare-q").value) || "").trim().toLowerCase();
    const sortMode = ($("#compare-sort") && $("#compare-sort").value) || "rank2024";
    let list = data.ranking_compare.slice();
    if (mode === "both") list = list.filter(r => r.rank_2024 != null && r.rank_2026 != null);
    else if (mode === "up") list = list.filter(r => String(r.change || "").startsWith("+"));
    else if (mode === "down") list = list.filter(r => String(r.change || "").startsWith("-"));
    else if (mode === "new") list = list.filter(r => r.change === "NEW");
    else if (mode === "dropped") list = list.filter(r => r.change === "DROPPED");
    else if (mode === "big") list = list.filter(r => changeMagnitude(r.change) >= 20);
    if (q) {
      list = list.filter(r => {
        const blob = [r.area_jp, r.area_cn, r.prefecture, r.change, r.note].join(" ").toLowerCase();
        return blob.includes(q);
      });
    }
    list = sortCompare(list, sortMode);
    const sortLabel = ($("#compare-sort") && $("#compare-sort").selectedOptions[0])
      ? $("#compare-sort").selectedOptions[0].textContent : sortMode;
    const stats = $("#compare-stats");
    if (stats) {
      stats.textContent = `顯示 ${list.length} / ${data.ranking_compare.length} 個溫泉地 · 排序：${sortLabel}`;
    }
    body.innerHTML = list.map(r => `
      <tr>
        <td class="rk">${esc(fmtRank(r.rank_2024))}</td>
        <td>
          <div class="area-cn">${esc(r.area_cn || r.area_jp)}</div>
          <div class="area-jp">${esc(r.area_jp || "")}${r.note ? " · " + esc(r.note) : ""}</div>
        </td>
        <td>${esc(r.prefecture || "")}</td>
        <td class="rk">${esc(fmtRank(r.rank_2026))}</td>
        <td><span class="change-pill ${changeClass(r.change)}">${esc(r.change || "")}</span></td>
      </tr>`).join("");
  }

  function fillSharedMeta(data) {
    const updated = $("#updated");
    if (updated && data.meta && data.meta.updated_label) {
      updated.textContent = data.meta.updated_label;
      updated.title = data.meta.updated_label;
    }
    const sb = $("#source-banner");
    if (sb && data.meta && data.meta.source_banner_zh) {
      sb.textContent = data.meta.source_banner_zh;
      sb.classList.remove("hidden");
    }
    const hoy = $("#hoy-link");
    if (hoy && data.meta && data.meta.hoy_url) hoy.href = data.meta.hoy_url;

    const ep = $("#ep-note");
    if (ep && data.meta && data.meta.episodes) {
      ep.textContent = data.meta.episodes.note_zh || "";
    }

    const alerts = $("#alerts");
    if (alerts && data.meta && data.meta.alerts) {
      alerts.innerHTML = data.meta.alerts.map(a =>
        `<div class="banner ${esc(a.level)}">${esc(a.zh)}</div>`
      ).join("");
    }

    const disc = $("#disclaimer");
    if (disc && data.meta && data.meta.disclaimer_zh) {
      disc.textContent = data.meta.disclaimer_zh;
    }
  }

  function initHome(data) {
    fillSharedMeta(data);
    const hotels = (data.hotels && data.hotels) || [];
    const hotelCount = hotels.length;
    const showCount = hotels.filter(isShowHotel).length;
    const compareCount = (data.ranking_compare && data.ranking_compare.length) || 0;
    const hc = $("#home-hotel-count");
    if (hc) hc.textContent = String(hotelCount);
    const sc = $("#home-show-count");
    if (sc) sc.textContent = String(showCount);
    const cc = $("#home-compare-count");
    if (cc) cc.textContent = String(compareCount);
  }

  function initRanks(data) {
    fillSharedMeta(data);
    const mount = $("#rank-mount");
    if (!mount) return;
    renderRanks(data.ranking_2024_top10 || [], mount);
    $$(".year-tabs .tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        $$(".year-tabs .tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const year = btn.dataset.year;
        renderRanks(
          year === "2024" ? (data.ranking_2024_top10 || []) : (data.ranking_2026_top10 || []),
          mount
        );
        const cap = $("#rank-caption");
        if (cap) {
          cap.textContent = year === "2024"
            ? "2024 年版（HOY《日本溫泉100強》來源）前 10 名溫泉地"
            : "2026 年 2 月電視東京特番前 10 名溫泉地（名單與 2024 不同）";
        }
      });
    });
  }

  function initCompare(data) {
    fillSharedMeta(data);
    if (!$("#compare-body")) return;
    ["compare-filter", "compare-q", "compare-sort"].forEach(id => {
      const el = $(`#${id}`);
      if (!el) return;
      el.addEventListener("input", () => applyCompareFilters(data));
      el.addEventListener("change", () => applyCompareFilters(data));
    });
    applyCompareFilters(data);
  }

  function areaLabel(h) {
    const cn = String(h.area_cn || "").replace(/（.*?）/g, "").trim();
    return cn ? `${cn}（${h.onsen_area || ""}）` : (h.onsen_area || "");
  }

  function areaCnShort(h) {
    const raw = String(h.area_cn || h.onsen_area || "");
    const stripped = raw.replace(/（.*?）/, "").trim();
    return stripped || String(h.onsen_area || "");
  }

  function isShowHotel(h) {
    if (h && h.in_show === true) return true;
    if (h && h.in_show === false) return false;
    const src = String(h && h.source || "");
    return src === "2024_HOY" || src === "2026_TVTokyo" || src === "2026_TVTokyo_guest";
  }

  function surfaceHotelError(err) {
    const msg = err && err.message ? err.message : String(err || "unknown error");
    const banner = $("#error-banner");
    if (banner) {
      banner.textContent = "住宿頁載入／篩選出錯：" + msg;
      banner.classList.remove("hidden");
    }
    const stats = $("#stats");
    if (stats) stats.textContent = "錯誤：" + msg;
    const body = $("#hotels-body");
    if (body && !body.children.length) {
      body.innerHTML = `<tr><td colspan="8">無法顯示住宿資料：${esc(msg)}</td></tr>`;
    }
    console.error("[hotels]", err);
  }

  function initHotels(data) {
    try {
      fillSharedMeta(data);
      if (!$("#hotels-body") && !$("#cards")) return;
      if (!data.hotels || !data.hotels.length) {
        surfaceHotelError(new Error("data.hotels 為空"));
        return;
      }

      hotelListMode = readListModeFromUrl();
      hotelPage = 1;
      hotelView = "table";
      syncListTabs();
      // Ensure table is visible by default
      if ($("#hotels-table-wrap")) $("#hotels-table-wrap").classList.remove("hidden");
      if ($("#cards")) $("#cards").classList.add("hidden");
      $$(".view-btn").forEach(b => {
        b.classList.toggle("is-active", (b.dataset.view || "") === "table");
      });

      const prefs = unique(data.hotels.map(h => h.prefecture));
      const prefSel = $("#pref");
      if (prefSel) {
        prefs.forEach(p => {
          const o = document.createElement("option");
          o.value = p; o.textContent = p;
          prefSel.appendChild(o);
        });
      }

      const areaSel = $("#area");
      if (areaSel) {
        const byArea = new Map();
        data.hotels.forEach(h => {
          if (!h.onsen_area) return;
          if (!byArea.has(h.onsen_area)) byArea.set(h.onsen_area, h);
        });
        const areas = Array.from(byArea.values()).sort((a, b) => {
          const ra = a.rank == null ? 9999 : Number(a.rank);
          const rb = b.rank == null ? 9999 : Number(b.rank);
          if (ra !== rb) return ra - rb;
          return String(a.onsen_area).localeCompare(String(b.onsen_area), "ja");
        });
        areas.forEach(h => {
          const o = document.createElement("option");
          o.value = h.onsen_area;
          o.textContent = areaLabel(h);
          areaSel.appendChild(o);
        });
      }

      const bands = ["日歸／入浴", "¥15,000 以下", "¥15,000–30,000", "¥30,000–50,000", "¥50,000 以上", "未取得"];
      const bandSel = $("#band");
      if (bandSel) {
        bands.forEach(b => {
          const o = document.createElement("option");
          o.value = b; o.textContent = b;
          bandSel.appendChild(o);
        });
      }

      const bumpFilter = () => { hotelPage = 1; applyFilters(data); };

      ["q", "pref", "area", "band", "sort"].forEach(id => {
        const el = $(`#${id}`);
        if (!el) return;
        el.addEventListener("input", bumpFilter);
        el.addEventListener("change", bumpFilter);
      });

      $$(".list-tab").forEach(btn => {
        btn.addEventListener("click", () => {
          hotelListMode = btn.dataset.list || "show";
          hotelPage = 1;
          syncListTabs();
          try {
            const url = new URL(location.href);
            if (hotelListMode === "show") url.searchParams.set("list", "show");
            else if (hotelListMode === "area") url.searchParams.set("list", "area");
            else url.searchParams.set("list", "all");
            history.replaceState(null, "", url.pathname + url.search + url.hash);
          } catch (e) {}
          applyFilters(data);
        });
      });

      const reset = $("#reset");
      if (reset) {
        reset.addEventListener("click", () => {
          if ($("#q")) $("#q").value = "";
          if ($("#pref")) $("#pref").value = "";
          if ($("#area")) $("#area").value = "";
          if ($("#band")) $("#band").value = "";
          if ($("#sort")) $("#sort").value = "rank2024";
          hotelPage = 1;
          applyFilters(data);
        });
      }

      $$(".view-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          $$(".view-btn").forEach(b => b.classList.remove("is-active"));
          btn.classList.add("is-active");
          hotelView = btn.dataset.view || "table";
          hotelPage = 1;
          applyFilters(data);
        });
      });

      const goPage = (delta) => {
        const pages = Math.max(1, Math.ceil(lastFilteredHotels.length / HOTEL_PAGE_SIZE) || 1);
        hotelPage = Math.min(pages, Math.max(1, hotelPage + delta));
        applyFilters(data);
        const wrap = $("#hotels-table-wrap");
        if (wrap && wrap.scrollIntoView) wrap.scrollIntoView({ behavior: "smooth", block: "start" });
      };
      ["page-prev", "page-prev-b"].forEach(id => {
        const b = $(`#${id}`);
        if (b) b.addEventListener("click", () => goPage(-1));
      });
      ["page-next", "page-next-b"].forEach(id => {
        const b = $(`#${id}`);
        if (b) b.addEventListener("click", () => goPage(1));
      });

      applyFilters(data);
    } catch (err) {
      surfaceHotelError(err);
    }
  }

  function init(data) {
    const page = (document.body && document.body.dataset.page) || "home";
    if (page === "ranks") initRanks(data);
    else if (page === "compare") initCompare(data);
    else if (page === "hotels") initHotels(data);
    else initHome(data);
  }

  function showLoadError(err) {
    const main = $("main") || document.body;
    const msg = `<p class="banner danger">無法載入資料：${esc(err && err.message ? err.message : err)}</p>`;
    if ($("#hotels-body")) {
      $("#hotels-body").innerHTML = `<tr><td colspan="8">${msg}</td></tr>`;
    } else if ($("#cards")) $("#cards").innerHTML = msg;
    else if ($("#compare-body")) {
      const wrap = $("#compare-wrap") || main;
      wrap.insertAdjacentHTML("beforebegin", msg);
    } else if ($("#rank-mount")) {
      $("#rank-mount").innerHTML = msg;
    } else {
      main.insertAdjacentHTML("afterbegin", msg);
    }
  }

  const embedded = window.ONSEN_DATA;
  if (embedded) {
    init(embedded);
  } else {
    fetch("data.json")
      .then(r => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(init)
      .catch(showLoadError);
  }
})();
