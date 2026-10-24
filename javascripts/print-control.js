(function () {
  "use strict";

  var BUTTON_ID = "fsi-print-control-button";
  var WRAPPER_ID = "fsi-print-control";

  function isControlPage() {
    var path = (window.location.pathname || "").toLowerCase();
    return path.indexOf("/controls/pillar-") !== -1;
  }

  function getSiteName() {
    var ogSite = document.querySelector('meta[property="og:site_name"]');
    if (ogSite && ogSite.getAttribute("content")) {
      return ogSite.getAttribute("content").trim();
    }
    var headerTopic = document.querySelector(".md-header__topic .md-ellipsis");
    if (headerTopic && headerTopic.textContent) {
      return headerTopic.textContent.trim();
    }
    return "FSI Agent Governance Framework";
  }

  function getPageTitle() {
    var h1 = document.querySelector(".md-content h1");
    if (h1 && h1.textContent) {
      return h1.textContent.trim();
    }
    var ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle && ogTitle.getAttribute("content")) {
      return ogTitle.getAttribute("content").split(" — ")[0].trim();
    }
    var title = (document.title || "").trim();
    return title.split(" — ")[0].trim() || title;
  }

  function setPrintMetadata() {
    if (!document.body) {
      return;
    }
    document.body.setAttribute("data-print-site", getSiteName());
    var pageTitle = getPageTitle();
    if (pageTitle) {
      document.body.setAttribute("data-print-title", pageTitle);
    }
  }

  function injectPrintButton() {
    if (!isControlPage()) {
      return;
    }

    setPrintMetadata();

    if (document.getElementById(BUTTON_ID)) {
      return;
    }

    var contentInner = document.querySelector(".md-content__inner");
    if (!contentInner) {
      return;
    }

    var wrapper = document.createElement("div");
    wrapper.id = WRAPPER_ID;
    wrapper.className = "print-hide";

    var button = document.createElement("button");
    button.id = BUTTON_ID;
    button.type = "button";
    button.className = "md-button md-button--primary";
    button.setAttribute("aria-label", "Print this control page or save it as a PDF");
    button.textContent = "🖨 Print / Save as PDF";
    button.addEventListener("click", function () {
      window.print();
    });

    wrapper.appendChild(button);

    var firstHeading = contentInner.querySelector("h1");
    if (firstHeading && firstHeading.parentElement === contentInner) {
      firstHeading.insertAdjacentElement("afterend", wrapper);
    } else {
      contentInner.insertAdjacentElement("afterbegin", wrapper);
    }
  }

  function init() {
    injectPrintButton();
  }

  if (
    typeof window.document$ !== "undefined" &&
    window.document$ &&
    typeof window.document$.subscribe === "function"
  ) {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
