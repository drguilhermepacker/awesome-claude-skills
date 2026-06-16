/* ============================================================
   Dr. Guilherme Packer — marketing site interactions
   Vanilla JS, no build step. Mirrors the Claude Design prototype:
   sticky glass header, smooth-scroll nav, cardiovascular-risk
   calculator, FAQ accordion, WhatsApp toast, entrance reveals.
   ============================================================ */
(function () {
  "use strict";

  /* ---- Lucide icons (CDN). Hydrate once the UMD bundle is ready. ----
     Cap the retries so a failed CDN load (offline, adblock, downtime)
     doesn't poll forever and drain CPU/battery. ~50 × 40ms ≈ 2s. */
  var hydrateRetries = 0;
  function hydrateIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons({ attrs: { "stroke-width": 1.75 } });
    } else if (hydrateRetries < 50) {
      hydrateRetries++;
      setTimeout(hydrateIcons, 40);
    }
  }
  hydrateIcons();

  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Toast ---- */
  var toastEl = document.getElementById("toast");
  var toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2400);
  }

  /* ---- Sticky glass header ---- */
  var header = document.getElementById("siteHeader");
  function onScroll() {
    if (!header) return;
    if (window.scrollY > 24) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- Smooth-scroll nav + active link ---- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll("[data-nav]"));
  navLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      var id = (link.getAttribute("href") || "").replace("#", "");
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: prefersReduced ? "auto" : "smooth", block: "start" });
      }
    });
  });

  /* highlight the section currently in view */
  var sectionIds = ["Sobre", "Especialidade", "Risco", "FAQ", "Contato"];
  var inlineNav = Array.prototype.slice.call(document.querySelectorAll(".site-nav a[href^='#']"));
  var activeTicking = false;
  function setActive() {
    activeTicking = false;
    var pos = window.scrollY + 120;
    var current = "";
    sectionIds.forEach(function (id) {
      var el = document.getElementById(id);
      if (el && el.offsetTop <= pos) current = id;
    });
    inlineNav.forEach(function (a) {
      if (a.classList.contains("btn")) return;
      a.classList.toggle("active", a.getAttribute("href") === "#" + current);
    });
  }
  /* Throttle to one layout read per frame to avoid scroll-time thrashing. */
  window.addEventListener("scroll", function () {
    if (!activeTicking) {
      activeTicking = true;
      window.requestAnimationFrame(setActive);
    }
  }, { passive: true });
  setActive();

  /* ---- Demo links / WhatsApp FAB fire a toast (no real nav) ---- */
  document.querySelectorAll("[data-demo]").forEach(function (el) {
    el.addEventListener("click", function (e) { e.preventDefault(); toast("Abrindo… (demonstração)"); });
  });
  var fab = document.getElementById("waFab");
  if (fab) fab.addEventListener("click", function () { toast("Abrindo o WhatsApp… (demonstração)"); });

  /* ---- Cardiovascular-risk calculator (educational approximation) ---- */
  var age = document.getElementById("riskAge");
  var sys = document.getElementById("riskSys");
  var smoker = document.getElementById("riskSmoker");
  var ageVal = document.getElementById("riskAgeVal");
  var sysVal = document.getElementById("riskSysVal");
  var calcBtn = document.getElementById("riskCalc");
  var resultBox = document.getElementById("riskResult");
  var resultNum = document.getElementById("riskNum");
  var resultBand = document.getElementById("riskBand");

  function hideResult() { if (resultBox) resultBox.classList.add("hidden"); }
  if (age) age.addEventListener("input", function () { ageVal.textContent = age.value; hideResult(); });
  if (sys) sys.addEventListener("input", function () { sysVal.textContent = sys.value; hideResult(); });
  if (smoker) smoker.addEventListener("change", hideResult);

  function band(r) {
    if (r < 5)    return { c: "var(--status-low)",          l: "Baixo risco" };
    if (r < 7.5)  return { c: "var(--status-borderline)",   l: "Risco limítrofe" };
    if (r < 20)   return { c: "var(--status-intermediate)", l: "Risco intermediário" };
    return            { c: "var(--status-high)",            l: "Risco alto" };
  }

  if (calcBtn) {
    calcBtn.addEventListener("click", function () {
      if (!age || !sys || !smoker || !resultNum || !resultBand || !resultBox) return;
      var a = +age.value, s = +sys.value;
      var r = 0.6 * Math.pow(a / 40, 3.0) * Math.pow(Math.max(90, s) / 120, 2.2);
      if (smoker.checked) r *= 1.8;
      r = Math.min(50, Math.max(0.5, Math.round(r * 10) / 10));
      var b = band(r);
      resultNum.textContent = r + "%";
      resultBand.textContent = b.l;
      resultBand.style.color = b.c;
      resultBox.classList.remove("hidden");
    });
  }

  /* ---- FAQ accordion (one open at a time) ---- */
  var faqItems = Array.prototype.slice.call(document.querySelectorAll(".faq__item"));
  faqItems.forEach(function (item) {
    item.querySelector(".faq__q").addEventListener("click", function () {
      var isOpen = item.classList.contains("open");
      faqItems.forEach(function (i) { i.classList.remove("open"); });
      if (!isOpen) item.classList.add("open");
    });
  });

  /* ---- Entrance reveals on scroll ---- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, idx) {
        if (entry.isIntersecting) {
          var el = entry.target;
          setTimeout(function () { el.classList.add("in"); }, idx * 80);
          io.unobserve(el);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
})();
