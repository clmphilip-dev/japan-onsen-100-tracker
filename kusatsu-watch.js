(function () {
  "use strict";

  var DATA_URL = "kusatsu-watch-data.json?v=20261105b";
  var STATUS = {
    open: "有房",
    full: "滿房",
    unchecked: "未查",
    non_stay: "非住宿",
    need_official: "需官網",
  };
  var STATUS_CLASS = {
    open: "open",
    full: "full",
    unchecked: "unchecked",
    non_stay: "non-stay",
    need_official: "need-official",
  };

  var state = {
    data: null,
    filter: "all",
    sort: "open_desc",
  };

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatYen(n) {
    if (n == null || isNaN(n)) return null;
    return "¥" + Number(n).toLocaleString("en-US");
  }

  function checkMap(checks) {
    var m = {};
    checks.forEach(function (c) {
      m[c.hotel_id + "|" + c.window_id] = c;
    });
    return m;
  }

  function openCountFor(hotelId, cmap, windows) {
    var n = 0;
    windows.forEach(function (w) {
      var c = cmap[hotelId + "|" + w.id];
      if (c && c.status === "open") n++;
    });
    return n;
  }

  function minOpenPrice(hotelId, cmap, windows) {
    var min = null;
    windows.forEach(function (w) {
      var c = cmap[hotelId + "|" + w.id];
      if (c && c.status === "open" && c.price_jpy != null) {
        if (min == null || c.price_jpy < min) min = c.price_jpy;
      }
    });
    return min;
  }

  function bestWindows(hotelId, cmap, windows) {
    return windows.filter(function (w) {
      var c = cmap[hotelId + "|" + w.id];
      return c && c.status === "open";
    });
  }

  function syncDrawer() {
    var narrow = window.matchMedia && window.matchMedia("(max-width: 700px)").matches;
    $$(".filter-drawer").forEach(function (d) {
      if (narrow) {
        if (!d.dataset.userToggled) d.open = false;
      } else {
        d.open = true;
      }
    });
  }

  function bindDrawerToggle() {
    $$(".filter-drawer").forEach(function (d) {
      d.addEventListener("toggle", function () {
        d.dataset.userToggled = "1";
      });
    });
    if (window.matchMedia) {
      window.matchMedia("(max-width: 700px)").addEventListener("change", function () {
        $$(".filter-drawer").forEach(function (d) { delete d.dataset.userToggled; });
        syncDrawer();
      });
    }
  }

  function filteredHotels() {
    var hotels = state.data.hotels.slice();
    var cmap = checkMap(state.data.checks);
    var windows = state.data.windows;

    if (state.filter === "open") {
      hotels = hotels.filter(function (h) {
        return openCountFor(h.id, cmap, windows) > 0;
      });
    } else if (state.filter === "stay") {
      hotels = hotels.filter(function (h) { return !h.skip_rooms; });
    }

    if (state.sort === "open_desc") {
      hotels.sort(function (a, b) {
        var da = openCountFor(b.id, cmap, windows) - openCountFor(a.id, cmap, windows);
        if (da !== 0) return da;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      });
    } else if (state.sort === "price_asc") {
      hotels.sort(function (a, b) {
        var pa = minOpenPrice(a.id, cmap, windows);
        var pb = minOpenPrice(b.id, cmap, windows);
        if (pa == null && pb == null) {
          return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
        }
        if (pa == null) return 1;
        if (pb == null) return -1;
        if (pa !== pb) return pa - pb;
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      });
    } else if (state.sort === "name") {
      hotels.sort(function (a, b) {
        return String(a.property_jp).localeCompare(String(b.property_jp), "ja");
      });
    }

    return { hotels: hotels, cmap: cmap, windows: windows };
  }

  function cellInner(c, label) {
    var cls = STATUS_CLASS[c.status] || "unchecked";
    var priceStr = (c.status === "open" && c.price_jpy != null) ? formatYen(c.price_jpy) : null;
    var titleBits = [c.note_zh || label];
    if (c.stock != null) titleBits.push("殘約 " + c.stock);
    if (priceStr) {
      titleBits.push(priceStr + "（2人2泊最低）");
      if (c.price_per_person_jpy != null) {
        titleBits.push("一人 " + formatYen(c.price_per_person_jpy));
      }
    }
    var title = escapeHtml(titleBits.join(" · "));
    var chip = "<span class=\"kw-chip " + cls + "\">" + escapeHtml(label) + "</span>";
    var priceHtml = priceStr
      ? "<span class=\"kw-price\">" + escapeHtml(priceStr) + "</span>"
      : "";
    var stack = "<span class=\"kw-cell-stack\">" + chip + priceHtml + "</span>";
    if (c.source_url && (c.status === "open" || c.status === "full" || c.status === "need_official" || c.status === "unchecked")) {
      return "<a class=\"kw-cell-link\" href=\"" + escapeHtml(c.source_url) +
        "\" target=\"_blank\" rel=\"noopener\" title=\"" + title + "\">" + stack + "</a>";
    }
    return "<span title=\"" + title + "\">" + stack + "</span>";
  }

  function renderMatrix() {
    var pack = filteredHotels();
    var hotels = pack.hotels;
    var cmap = pack.cmap;
    var windows = pack.windows;
    var thead = $("#kw-thead");
    var tbody = $("#kw-tbody");

    var head = "<tr><th class=\"kw-hotel-col\">旅館</th>";
    windows.forEach(function (w) {
      head += "<th title=\"" + escapeHtml(w.checkin + " → " + w.checkout) + "\">" +
        escapeHtml(w.label_zh) + "</th>";
    });
    head += "</tr>";
    thead.innerHTML = head;

    var rows = hotels.map(function (h) {
      var oc = openCountFor(h.id, cmap, windows);
      var minP = minOpenPrice(h.id, cmap, windows);
      var badge = h.in_show ? "<span class=\"kw-badge-show\">節目</span>" : "";
      var ocLabel = (!h.skip_rooms && oc > 0)
        ? "<span class=\"kw-open-count\">" + oc + " 窗</span>"
        : "";
      var priceLabel = (minP != null)
        ? "<span class=\"kw-min-price\">起 " + escapeHtml(formatYen(minP)) + "</span>"
        : "";
      var cells = windows.map(function (w) {
        var c = cmap[h.id + "|" + w.id] || { status: "unchecked" };
        var label = (state.data.status_labels_zh && state.data.status_labels_zh[c.status]) || STATUS[c.status] || c.status;
        return "<td>" + cellInner(c, label) + "</td>";
      }).join("");

      return "<tr>" +
        "<td class=\"kw-hotel-col\">" +
          "<span class=\"kw-hotel-name\">" + escapeHtml(h.property_jp) + badge + ocLabel + "</span>" +
          "<span class=\"kw-hotel-cn\">" + escapeHtml(h.property_cn) +
            (h.type === "day-onsen" ? " · 日歸" : "") +
            (priceLabel ? " · " + priceLabel : "") + "</span>" +
        "</td>" + cells + "</tr>";
    }).join("");

    tbody.innerHTML = rows || "<tr><td colspan=\"" + (windows.length + 1) + "\">沒有符合篩選的旅館</td></tr>";

    var openHotels = state.data.hotels.filter(function (h) {
      return openCountFor(h.id, checkMap(state.data.checks), state.data.windows) > 0;
    }).length;
    var openCells = state.data.checks.filter(function (c) { return c.status === "open"; }).length;
    var pricedCells = state.data.checks.filter(function (c) {
      return c.status === "open" && c.price_jpy != null;
    }).length;
    $("#kw-stats").textContent =
      "顯示 " + hotels.length + "／" + state.data.hotels.length + " 間 · " +
      "目前快照有房：" + openCells + " 格（" + openHotels + " 間）· " +
      "已標價：" + pricedCells + "／" + openCells + " · " +
      "價錢＝2人2泊合計最低（點芯片開じゃらん核對）";
  }

  function linkBtn(href, label) {
    if (!href) return "";
    return "<a href=\"" + escapeHtml(href) + "\" target=\"_blank\" rel=\"noopener\">" + escapeHtml(label) + "</a>";
  }

  function renderCards() {
    var pack = filteredHotels();
    var cmap = pack.cmap;
    var windows = pack.windows;
    var html = pack.hotels.map(function (h) {
      var best = bestWindows(h.id, cmap, windows);
      var bestText;
      if (h.skip_rooms) {
        bestText = "非住宿／日歸溫泉 — 不查空室。";
      } else if (best.length === 0) {
        var anyNeed = windows.some(function (w) {
          var c = cmap[h.id + "|" + w.id];
          return c && c.status === "need_official";
        });
        bestText = anyNeed
          ? "此快照未能自動查庫存 — 請用下方連結手動確認。"
          : "此快照 10 個視窗均無じゃらん空室（年末常見）。";
      } else {
        var parts = best.map(function (w) {
          var c = cmap[h.id + "|" + w.id];
          var p = (c && c.price_jpy != null) ? " " + formatYen(c.price_jpy) : "";
          return w.label_zh + p;
        });
        var minP = minOpenPrice(h.id, cmap, windows);
        bestText = "有房視窗：" + parts.join("、") +
          "（共 " + best.length + "／10）" +
          (minP != null ? " · 最低 " + formatYen(minP) + "（2人2泊）" : "");
      }
      var typeLabel = h.type === "day-onsen" ? "日歸溫泉" : (h.type === "ryokan" ? "旅館" : "酒店");
      var show = h.in_show ? "<span class=\"kw-badge-show\">節目推薦</span>" : "";
      return "<article class=\"kw-card\" id=\"hotel-" + escapeHtml(h.id) + "\">" +
        "<h3>" + escapeHtml(h.property_jp) + show + "</h3>" +
        "<p class=\"kw-meta\">" + escapeHtml(h.property_cn) + " · " + typeLabel + "</p>" +
        "<p class=\"kw-best\">" + escapeHtml(bestText) + "</p>" +
        "<div class=\"kw-links\">" +
          linkBtn(h.official_url, "官網") +
          linkBtn(h.jalan_url, "じゃらん") +
          linkBtn(h.rakuten_url, "楽天") +
          linkBtn(h.booking_url, "Booking") +
          linkBtn(h.other_booking, "其他") +
        "</div></article>";
    }).join("");
    $("#kw-cards").innerHTML = html;
  }

  function renderAll() {
    renderMatrix();
    renderCards();
    var hint = $("#kw-filter-hint");
    if (hint) {
      var parts = [];
      if (state.filter !== "all") parts.push($("#kw-filter").selectedOptions[0].textContent);
      if (state.sort !== "open_desc") parts.push($("#kw-sort").selectedOptions[0].textContent);
      if (parts.length) {
        hint.hidden = false;
        hint.textContent = parts.join(" · ");
      } else {
        hint.hidden = true;
        hint.textContent = "";
      }
    }
  }

  function bindControls() {
    $("#kw-filter").addEventListener("change", function (e) {
      state.filter = e.target.value;
      renderAll();
    });
    $("#kw-sort").addEventListener("change", function (e) {
      state.sort = e.target.value;
      renderAll();
    });
    $("#kw-reset").addEventListener("click", function () {
      state.filter = "all";
      state.sort = "open_desc";
      $("#kw-filter").value = "all";
      $("#kw-sort").value = "open_desc";
      renderAll();
    });
  }

  function formatChecked(iso) {
    if (!iso) return "—";
    try {
      var d = new Date(iso);
      if (isNaN(d.getTime())) return iso;
      var opts = { timeZone: "Asia/Hong_Kong", year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", hour12: false };
      return d.toLocaleString("zh-HK", opts) + "（香港時間）";
    } catch (e) {
      return iso;
    }
  }

  function boot(data) {
    state.data = data;
    var meta = data.meta || {};
    $("#kw-updated").textContent = meta.last_checked_label_zh || ("最後檢查：" + formatChecked(meta.last_checked_at));
    $("#kw-edition").textContent =
      (meta.stay_window_start || "") + " ～ " + (meta.stay_window_end || "") +
      " · 2 晚 · 2 大人 · 含價錢";
    syncDrawer();
    bindDrawerToggle();
    bindControls();
    renderAll();
  }

  fetch(DATA_URL, { cache: "no-store" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(boot)
    .catch(function (err) {
      $("#kw-stats").textContent = "無法載入監控資料：" + err.message;
      $("#kw-updated").textContent = "載入失敗";
    });
})();
