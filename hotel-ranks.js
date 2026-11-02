(function () {
  "use strict";

  var DATA_URL = "hotel-ranks-data.json?v=20261102b";
  var state = { hotels: [], meta: null, filtered: [], sort: "rank_asc" };

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function showError(msg) {
    var el = $("hr-error");
    if (!el) return;
    el.textContent = msg;
    el.classList.remove("hidden");
  }

  function fillSelect(sel, values, allLabel) {
    var cur = sel.value;
    sel.innerHTML = "";
    var o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = allLabel;
    sel.appendChild(o0);
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      sel.appendChild(o);
    });
    if (values.indexOf(cur) >= 0) sel.value = cur;
  }

  function uniqueSorted(arr) {
    var m = {};
    arr.forEach(function (x) {
      if (x) m[x] = true;
    });
    return Object.keys(m).sort(function (a, b) {
      return a.localeCompare(b, "zh-Hant");
    });
  }

  function sortKeyName(h) {
    return (h.property_cn || h.property_jp || "").toString();
  }
  function sortKeyArea(h) {
    return (h.onsen_area_cn || h.onsen_area_jp || "").toString();
  }
  function sortKeyPref(h) {
    return (h.prefecture_cn || h.prefecture_jp || "").toString();
  }

  function sortList(list, mode) {
    var out = list.slice();
    if (mode === "rank_desc") {
      out.sort(function (a, b) { return b.rank - a.rank; });
    } else if (mode === "name") {
      out.sort(function (a, b) {
        return sortKeyName(a).localeCompare(sortKeyName(b), "zh-Hant") || a.rank - b.rank;
      });
    } else if (mode === "area") {
      out.sort(function (a, b) {
        return sortKeyArea(a).localeCompare(sortKeyArea(b), "zh-Hant") || a.rank - b.rank;
      });
    } else if (mode === "pref") {
      out.sort(function (a, b) {
        return sortKeyPref(a).localeCompare(sortKeyPref(b), "zh-Hant") || a.rank - b.rank;
      });
    } else {
      out.sort(function (a, b) { return a.rank - b.rank; });
    }
    return out;
  }

  function applyFilters() {
    var q = ($("hr-q").value || "").trim().toLowerCase();
    var area = $("hr-area").value || "";
    var pref = $("hr-pref").value || "";
    var sortEl = $("hr-sort");
    state.sort = (sortEl && sortEl.value) || "rank_asc";
    var list = state.hotels.filter(function (h) {
      if (area && h.onsen_area_cn !== area && h.onsen_area_jp !== area) return false;
      if (pref && h.prefecture_cn !== pref && h.prefecture_jp !== pref) return false;
      if (!q) return true;
      var blob = [
        h.property_jp, h.property_cn,
        h.onsen_area_jp, h.onsen_area_cn,
        h.prefecture_jp, h.prefecture_cn,
        h.description_cn,
        String(h.rank)
      ].join(" ").toLowerCase();
      return blob.indexOf(q) >= 0;
    });
    state.filtered = sortList(list, state.sort);
    render();
  }

  function updateHint() {
    var hint = $("hr-filter-hint");
    if (!hint) return;
    var q = ($("hr-q").value || "").trim();
    var area = $("hr-area").value || "";
    var pref = $("hr-pref").value || "";
    var sortEl = $("hr-sort");
    var sortLabel = sortEl && sortEl.options[sortEl.selectedIndex]
      ? sortEl.options[sortEl.selectedIndex].text
      : "";
    var parts = [];
    if (q) parts.push("「" + q + "」");
    if (area) parts.push(area);
    if (pref) parts.push(pref);
    if (sortLabel && state.sort !== "rank_asc") parts.push(sortLabel);
    if (parts.length) {
      hint.hidden = false;
      hint.textContent = parts.join(" · ");
    } else {
      hint.hidden = true;
      hint.textContent = "";
    }
  }

  function render() {
    var body = $("hr-body");
    var stats = $("hr-stats");
    var list = state.filtered;
    if (stats) {
      stats.textContent = "顯示 " + list.length + "／" + state.hotels.length + " 間";
    }
    updateHint();
    if (!body) return;
    if (!list.length) {
      body.innerHTML = '<tr><td colspan="5" class="hr-muted">沒有符合條件的旅館。</td></tr>';
      return;
    }
    body.innerHTML = list.map(function (h) {
      var name = esc(h.property_cn || h.property_jp);
      var nameJp = h.property_jp && h.property_jp !== h.property_cn
        ? '<div class="prop-jp">' + esc(h.property_jp) + "</div>"
        : "";
      var tips = [];
      if (h._area_travel) tips.push(h._area_travel);
      if (h._area_season) tips.push(h._area_season);
      if (h._hk_hub) tips.push("樞紐 " + h._hk_hub);
      var tipHtml = tips.length
        ? '<div class="area-tip">' + esc(tips.join(" · ")) + "</div>"
        : "";
      var accessExtra = h._area_access
        ? '<p class="hk-access">' + esc(h._area_access) + "</p>"
        : "";
      var desc = h.description_cn
        ? '<details class="hr-desc"><summary>簡介</summary><p>' + esc(h.description_cn) + "</p>" + accessExtra + "</details>"
        : (accessExtra ? '<details class="hr-desc"><summary>交通提示</summary>' + accessExtra + "</details>" : "");
      desc = tipHtml + desc;
      var area = esc(h.onsen_area_cn || h.onsen_area_jp || "—");
      var areaJp = h.onsen_area_jp && h.onsen_area_jp !== h.onsen_area_cn
        ? '<div class="area-jp">' + esc(h.onsen_area_jp) + "</div>"
        : "";
      var pref = esc(h.prefecture_cn || h.prefecture_jp || "—");
      var link = h.url
        ? '<a class="hr-link" href="' + esc(h.url) + '" target="_blank" rel="noopener">官網</a>'
        : '<span class="hr-muted">—</span>';
      return (
        "<tr>" +
        '<td class="rk">' + esc(h.rank) + "</td>" +
        '<td><div class="prop-cn">' + name + "</div>" + nameJp + desc + "</td>" +
        '<td><div class="area-cn">' + area + "</div>" + areaJp + "</td>" +
        "<td>" + pref + "</td>" +
        "<td>" + link + "</td>" +
        "</tr>"
      );
    }).join("");
  }

  function bind() {
    ["hr-q", "hr-area", "hr-pref", "hr-sort"].forEach(function (id) {
      var el = $(id);
      if (!el) return;
      el.addEventListener("input", applyFilters);
      el.addEventListener("change", applyFilters);
    });
    var reset = $("hr-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        $("hr-q").value = "";
        $("hr-area").value = "";
        $("hr-pref").value = "";
        if ($("hr-sort")) $("hr-sort").value = "rank_asc";
        applyFilters();
      });
    }
  }

  function attachAreaTips(hotels, areas) {
    if (!areas || !areas.length) return hotels;
    var by = {};
    areas.forEach(function (a) { if (a && a.area_jp) by[a.area_jp] = a; });
    hotels.forEach(function (h) {
      var key = h.onsen_area_jp || "";
      var a = by[key];
      if (!a) {
        // soft match: area name contained
        Object.keys(by).some(function (k) {
          if (key && (key.indexOf(k) >= 0 || k.indexOf(key) >= 0)) { a = by[k]; return true; }
          return false;
        });
      }
      if (!a) return;
      h._area_travel = a.travel_time_band || "";
      h._area_season = a.best_season_zh || "";
      h._area_access = a.access_zh || "";
      h._hk_hub = a.hk_hub || "";
    });
    return hotels;
  }

  function isMobileFilterView() {
    return window.matchMedia && window.matchMedia("(max-width: 700px)").matches;
  }

  function syncFilterDrawers() {
    var mobile = isMobileFilterView();
    document.querySelectorAll(".filter-drawer").forEach(function (d) {
      if (mobile) {
        if (!d.dataset.userToggled) d.open = false;
      } else {
        d.open = true;
        delete d.dataset.userToggled;
      }
    });
  }

  function bindFilterDrawerToggle() {
    document.querySelectorAll(".filter-drawer").forEach(function (d) {
      d.addEventListener("toggle", function () {
        if (isMobileFilterView()) d.dataset.userToggled = "1";
      });
    });
  }

  function init(data) {
    state.meta = data.meta || {};
    state.hotels = (data.hotels || []).slice().sort(function (a, b) {
      return a.rank - b.rank;
    });
    var ed = $("hr-edition");
    if (ed) {
      ed.textContent = (state.meta.edition || "") + " 綜合100選 · " + (state.meta.count || state.hotels.length) + " 間";
    }
    var upd = $("hr-updated");
    if (upd && state.meta.updated) {
      upd.textContent = "資料：" + state.meta.updated;
    }
    fillSelect($("hr-area"), uniqueSorted(state.hotels.map(function (h) {
      return h.onsen_area_cn || h.onsen_area_jp;
    })), "全部溫泉地");
    fillSelect($("hr-pref"), uniqueSorted(state.hotels.map(function (h) {
      return h.prefecture_cn || h.prefecture_jp;
    })), "全部");
    bind();
    bindFilterDrawerToggle();
    syncFilterDrawers();
    if (window.matchMedia) {
      var mq = window.matchMedia("(max-width: 700px)");
      var onMq = function () {
        document.querySelectorAll(".filter-drawer").forEach(function (d) { delete d.dataset.userToggled; });
        syncFilterDrawers();
      };
      if (mq.addEventListener) mq.addEventListener("change", onMq);
      else if (mq.addListener) mq.addListener(onMq);
    }
    applyFilters();
  }

  Promise.all([
    fetch(DATA_URL, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }),
    fetch("data.json?v=20261102b", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; })
  ])
    .then(function (pair) {
      var data = pair[0];
      var main = pair[1];
      if (main && main.areas) attachAreaTips(data.hotels || [], main.areas);
      init(data);
    })
    .catch(function (err) {
      showError("無法載入旅館排名資料：" + (err && err.message ? err.message : err));
    });
})();
