(function () {
  "use strict";

  var SCRIPT = document.currentScript;
  var BASE_URL = SCRIPT && SCRIPT.src ? new URL("..", SCRIPT.src).href : new URL("./", document.baseURI).href;
  var STATE = window.__fsiSearchHelper || {
    aliases: [],
    aliasesReady: false,
    observer: null,
    retryTimer: 0,
    updateTimer: 0,
    lastQuery: ""
  };
  window.__fsiSearchHelper = STATE;

  function normalize(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/&/g, " and ")
      .replace(/[\u2010-\u2015]/g, "-")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function tokens(value) {
    var stop = {
      a: true, an: true, and: true, are: true, can: true, for: true, how: true,
      i: true, in: true, is: true, of: true, on: true, the: true, to: true,
      what: true, when: true, where: true, who: true, with: true
    };
    return normalize(value).split(" ").filter(function (token) {
      return token && !stop[token];
    });
  }

  function scoreEntry(query, entry) {
    var q = normalize(query);
    var qTokens = tokens(query);
    if (!q || !qTokens.length) {
      return 0;
    }
    var phrases = [entry.term, entry.label].concat(entry.aliases || []);
    var best = 0;
    phrases.forEach(function (phrase) {
      var p = normalize(phrase);
      if (!p) {
        return;
      }
      if (q === p) {
        best = Math.max(best, 100);
      } else if (q.indexOf(p) !== -1 || p.indexOf(q) !== -1) {
        best = Math.max(best, Math.min(p.length, q.length) >= 3 ? 76 : 0);
      }
      var pTokens = tokens(phrase);
      var overlap = qTokens.filter(function (token) {
        return pTokens.indexOf(token) !== -1;
      }).length;
      if (overlap) {
        best = Math.max(best, overlap * 18 + (overlap === qTokens.length ? 22 : 0));
      }
    });
    return best;
  }

  function related(query, limit) {
    return STATE.aliases
      .map(function (entry) { return { entry: entry, score: scoreEntry(query, entry) }; })
      .filter(function (item) { return item.score > 0; })
      .sort(function (a, b) {
        if (b.score !== a.score) {
          return b.score - a.score;
        }
        return String(a.entry.label).localeCompare(String(b.entry.label));
      })
      .slice(0, limit || 4)
      .map(function (item) { return item.entry; });
  }

  function resolveUrl(url) {
    return new URL(String(url || "").replace(/^\.\//, ""), BASE_URL).href;
  }

  function searchInput() {
    return document.querySelector("[data-md-component='search-query'], .md-search__input, input[name='query']");
  }

  function searchResult() {
    return document.querySelector("[data-md-component='search-result'], .md-search-result");
  }

  function removePanel(container) {
    var current = container && container.querySelector(".fsi-search-helper");
    if (current) {
      current.remove();
    }
  }

  function hasNoResults(container, query) {
    if (!container || normalize(query).length < 2) {
      return false;
    }
    var meta = container.querySelector(".md-search-result__meta");
    var metaText = normalize(meta ? meta.textContent : "");
    if (metaText.indexOf("no matching") !== -1 || metaText.indexOf("no results") !== -1) {
      return true;
    }
    var articles = container.querySelectorAll(".md-search-result__article, .md-search-result__item article");
    var list = container.querySelector(".md-search-result__list, [role='list']");
    return Boolean(list && list.children.length > 0 && articles.length === 0 && metaText);
  }

  function appendLink(parent, entry) {
    var link = document.createElement("a");
    link.className = "fsi-search-helper__link";
    link.href = resolveUrl(entry.url);
    link.textContent = entry.label || entry.term;
    link.setAttribute("data-search-helper-term", entry.term || "");
    parent.appendChild(link);
    return link;
  }

  function renderRelated(container, matches) {
    var panel = document.createElement("aside");
    panel.className = "fsi-search-helper fsi-search-helper--related";
    panel.setAttribute("aria-live", "polite");

    var prefix = document.createElement("span");
    prefix.className = "fsi-search-helper__prefix";
    prefix.textContent = "Related:";
    panel.appendChild(prefix);
    appendLink(panel, matches[0]);

    var arrow = document.createElement("span");
    arrow.className = "fsi-search-helper__arrow";
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "\u2192";
    panel.appendChild(arrow);
    container.prepend(panel);
  }

  function renderEmpty(container, matches) {
    var panel = document.createElement("section");
    panel.className = "fsi-search-helper fsi-search-helper--empty";
    panel.setAttribute("role", "status");
    panel.setAttribute("aria-live", "polite");

    var title = document.createElement("strong");
    title.className = "fsi-search-helper__title";
    title.textContent = "No matches";
    panel.appendChild(title);

    var text = document.createElement("span");
    text.className = "fsi-search-helper__text";
    text.textContent = matches.length ? " Try:" : " Try a control ID, acronym, product name, or regulation citation.";
    panel.appendChild(text);

    if (matches.length) {
      var list = document.createElement("ul");
      list.className = "fsi-search-helper__list";
      matches.forEach(function (entry) {
        var item = document.createElement("li");
        appendLink(item, entry);
        list.appendChild(item);
      });
      panel.appendChild(list);
    }
    container.prepend(panel);
  }

  function update() {
    var input = searchInput();
    var container = searchResult();
    if (!input || !container || !STATE.aliasesReady) {
      return;
    }
    var query = input.value || "";
    var nq = normalize(query);
    var matches = nq ? related(query, 4) : [];
    var mode = "none";
    if (nq) {
      if (hasNoResults(container, query)) {
        mode = "empty";
      } else if (matches.length) {
        mode = "related";
      }
    }
    var sig = mode + "|" + nq + "|" + matches.map(function (m) { return m.term; }).join(",");
    var existing = container.querySelector(".fsi-search-helper");
    // Skip when the helper already reflects this exact state. This prevents the
    // panel's own DOM mutations from re-triggering the observers (render loop).
    if (existing && existing.getAttribute("data-fsi-sig") === sig) {
      return;
    }
    if (existing) {
      existing.remove();
    }
    STATE.lastQuery = query;
    if (mode === "empty") {
      renderEmpty(container, matches);
    } else if (mode === "related") {
      renderRelated(container, matches);
    }
    var panel = container.querySelector(".fsi-search-helper");
    if (panel) {
      panel.setAttribute("data-fsi-sig", sig);
    }
  }

  function scheduleUpdate() {
    window.clearTimeout(STATE.updateTimer);
    STATE.updateTimer = window.setTimeout(update, 80);
  }

  function bind() {
    var input = searchInput();
    var container = searchResult();
    if (input && !input.dataset.fsiSearchHelperBound) {
      input.dataset.fsiSearchHelperBound = "true";
      input.addEventListener("input", scheduleUpdate);
      input.addEventListener("keyup", scheduleUpdate);
      input.addEventListener("search", scheduleUpdate);
    }
    if (container && !container.dataset.fsiSearchHelperObserved) {
      container.dataset.fsiSearchHelperObserved = "true";
      var resultObserver = new MutationObserver(scheduleUpdate);
      resultObserver.observe(container, { childList: true, subtree: true, characterData: true });
    }
    scheduleUpdate();
  }

  function observeDom() {
    if (STATE.observer) {
      STATE.observer.disconnect();
    }
    STATE.observer = new MutationObserver(function () {
      window.clearTimeout(STATE.retryTimer);
      STATE.retryTimer = window.setTimeout(bind, 100);
    });
    STATE.observer.observe(document.documentElement, { childList: true, subtree: true });
    bind();
  }

  function loadAliases() {
    if (STATE.aliasesReady) {
      return Promise.resolve();
    }
    return fetch(new URL("search-aliases.json", BASE_URL).href, { credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Unable to load search aliases: " + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        STATE.aliases = Array.isArray(data) ? data : [];
        STATE.aliasesReady = true;
      })
      .catch(function () {
        STATE.aliases = [];
        STATE.aliasesReady = true;
      });
  }

  function start() {
    loadAliases().then(observeDom);
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(start);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
