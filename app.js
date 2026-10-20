(function () {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function fmtPrice(p) {
    if (p == null || p === "") return "價錢待查";
    const n = Number(p);
    if (!isFinite(n)) return "價錢待查";
    return "約 ¥" + n.toLocaleString("ja-JP") + "／人";
  }

  function linkBtn(url, label) {
    if (!url) return `<a class="disabled" href="#">${esc(label)}</a>`;
    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}</a>`;
  }

  function fmtRank(r) {
    return r == null || r === "" ? "—" : "#" + r;
  }

  function rankPairText(h) {
    const a = h.rank == null ? "—" : "#" + h.rank;
    const b = h.rank_2026 == null ? "—" : "#" + h.rank_2026;
    return `2024 ${a}　／　2026 ${b}`;
  }

  /** Positive = improved (rank number went down). null if either year missing. */
  function rankDelta(r24, r26) {
    if (r24 == null || r26 == null || r24 === "" || r26 === "") return null;
    return Number(r24) - Number(r26);
  }

  function renderRanks(list, mount) {
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
      <article class="card" data-pref="${esc(h.prefecture || "")}" data-band="${esc(h.price_band || "")}">
        <div class="rank-badge">
          <span class="rank-line">2024 ${esc(fmtRank(h.rank))}</span>
          <span class="rank-line">2026 ${esc(fmtRank(h.rank_2026))}</span>
        </div>
        <div>
          <span class="area">${esc(h.area_cn || "")}</span>
          <h3>${esc(h.property_cn || h.property_en || h.property_jp)}</h3>
          <div class="jp">${esc(h.property_jp)}${h.property_en ? " · " + esc(h.property_en) : ""}</div>
          <div class="rank-pair">${esc(rankPairText(h))} ${deltaChip}</div>
          <div class="meta">
            <span class="chip price">${esc(fmtPrice(h.price_jpy))}</span>
            <span class="chip">${esc(h.price_band || "")}</span>
            <span class="chip">${esc(h.type || "")}</span>
            <span class="chip">${esc(h.source || "")}</span>
            <span class="chip">${esc(
              h.source_quality === "web_summary_crosschecked" ? "多源交叉核對" :
              h.source_quality === "web_summary_not_watched" ? "網摘／未觀看" :
              (h.source_quality || "")
            )}</span>
            ${alertChip(h)}
          </div>
          <p class="desc">${esc(h.description_cn || "")}</p>
          ${h.highlights ? `<p class="hl">節目／已知賣點：${esc(h.highlights)}</p>` : ""}
          <div class="links">
            ${linkBtn(h.official_url, "官方")}
            ${linkBtn(h.rakuten_url, "樂天旅遊")}
            ${linkBtn(h.jalan_url, "Jalan")}
            ${linkBtn(h.booking_url, "Booking")}
            ${linkBtn(h.other_booking, "其他預約")}
          </div>
        </div>
      </article>`;
    }).join("");
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
        // largest positive delta first; missing delta last
        const da = rankDelta(a.rank, a.rank_2026);
        const db = rankDelta(b.rank, b.rank_2026);
        const va = da == null ? -inf : da;
        const vb = db == null ? -inf : db;
        if (va !== vb) return vb - va;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      }
      if (mode === "drop") {
        // most negative delta first (largest fall)
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

  function applyFilters(data) {
    const q = ($("#q").value || "").trim().toLowerCase();
    const pref = $("#pref").value;
    const band = $("#band").value;
    const mode = ($("#sort") && $("#sort").value) || "rank2024";
    let list = data.hotels.slice();
    if (pref) list = list.filter(h => h.prefecture === pref);
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
    $("#stats").textContent = `顯示 ${list.length} / ${data.hotels.length} 間住宿／設施 · 排序：${($("#sort").selectedOptions[0] || {}).textContent || mode}`;
    renderCards(list);
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
    $("#compare-stats").textContent = `顯示 ${list.length} / ${data.ranking_compare.length} 個溫泉地 · 排序：${sortLabel}`;
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

  function init(data) {
    $("#updated").textContent = data.meta.updated_label;
    const sb = $("#source-banner");
    if (sb && data.meta.source_banner_zh) {
      sb.textContent = data.meta.source_banner_zh;
      sb.classList.remove("hidden");
    }

    $("#hoy-link").href = data.meta.hoy_url;
    $("#ep-note").textContent = data.meta.episodes.note_zh;

    const alerts = $("#alerts");
    alerts.innerHTML = data.meta.alerts.map(a =>
      `<div class="banner ${esc(a.level)}">${esc(a.zh)}</div>`
    ).join("");

    renderRanks(data.ranking_2024_top10, $("#rank-mount"));
    $$("#panel-top10 .tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        $$("#panel-top10 .tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const year = btn.dataset.year;
        renderRanks(year === "2024" ? data.ranking_2024_top10 : data.ranking_2026_top10, $("#rank-mount"));
        $("#rank-caption").textContent = year === "2024"
          ? "2024 年版（HOY《日本溫泉100強》來源）前 10 名溫泉地"
          : "2026 年 2 月電視東京特番前 10 名溫泉地（名單與 2024 不同）";
      });
    });

    function showPanel(panelId) {
      $$(".section-tab").forEach(b => {
        const on = b.dataset.panel === panelId;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
      $$(".content-panel").forEach(p => {
        const on = p.dataset.panel === panelId;
        p.classList.toggle("is-active", on);
        p.classList.toggle("hidden", !on);
      });
      // Keep nodes; refresh visible panel data if needed
      if (panelId === "compare") applyCompareFilters(data);
      if (panelId === "hotels") applyFilters(data);
    }
    $$(".section-tab").forEach(btn => {
      btn.addEventListener("click", () => showPanel(btn.dataset.panel));
    });

    const prefs = unique(data.hotels.map(h => h.prefecture));
    const prefSel = $("#pref");
    prefs.forEach(p => {
      const o = document.createElement("option");
      o.value = p; o.textContent = p;
      prefSel.appendChild(o);
    });
    const bands = ["日歸／入浴", "¥15,000 以下", "¥15,000–30,000", "¥30,000–50,000", "¥50,000 以上", "未取得"];
    const bandSel = $("#band");
    bands.forEach(b => {
      const o = document.createElement("option");
      o.value = b; o.textContent = b;
      bandSel.appendChild(o);
    });

    ["q", "pref", "band", "sort"].forEach(id => {
      const el = $(`#${id}`);
      if (!el) return;
      el.addEventListener("input", () => applyFilters(data));
      el.addEventListener("change", () => applyFilters(data));
    });
    $("#reset").addEventListener("click", () => {
      $("#q").value = "";
      $("#pref").value = "";
      $("#band").value = "";
      if ($("#sort")) $("#sort").value = "rank2024";
      applyFilters(data);
    });

    if ($("#compare-filter")) {
      ["compare-filter", "compare-q", "compare-sort"].forEach(id => {
        const el = $(`#${id}`);
        if (!el) return;
        el.addEventListener("input", () => applyCompareFilters(data));
        el.addEventListener("change", () => applyCompareFilters(data));
      });
      applyCompareFilters(data);
    }

    $("#disclaimer").textContent = data.meta.disclaimer_zh;
    applyFilters(data);
  }

  const embedded = window.ONSEN_DATA;
  if (embedded) {
    init(embedded);
  } else {
    fetch("data.json").then(r => r.json()).then(init).catch(err => {
      $("#cards").innerHTML = `<p class="banner danger">無法載入資料：${esc(err.message)}</p>`;
    });
  }
})();
