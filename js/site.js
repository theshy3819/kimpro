/* 김프로 — 모든 쪽 공통: 머리 메뉴, 모바일 메뉴, 나타나기(상세 페이지), 예약 폼 */
(() => {
  "use strict";
  document.documentElement.classList.add("js");
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 데스크톱 메뉴: 올리거나 키보드로 들어가면 판이 열리고(CSS),
                대제목을 누르면 그 묶음의 첫 쪽으로 가요(링크) ---------- */
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    closeMenu();
    const inMenu = document.activeElement?.closest("[data-gnb]");
    if (inMenu) $(".gnb__top", inMenu)?.focus();
  });

  /* ---------- 맨 위로: 한 화면쯤 내려가면 나타나요 ---------- */
  const totop = $("[data-totop]");
  if (totop) {
    let ticking = false;
    const sync = () => { totop.classList.toggle("is-on", window.scrollY > window.innerHeight * 0.8); ticking = false; };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(sync); } }, { passive: true });
    sync();
    totop.addEventListener("click", () => {
      if (window.__lenis) window.__lenis.scrollTo(0, { duration: 1.2 });   // 홈(부드러운 스크롤)
      else window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      $(".hdr__brand")?.focus({ preventScroll: true });
    });
  }

  /* ---------- 모바일 메뉴 ---------- */
  const menuBtn = $("[data-menu]");
  const mnav = $("[data-mnav]");
  function closeMenu() {
    if (!mnav || mnav.hidden) return;
    mnav.hidden = true;
    menuBtn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
  }
  menuBtn?.addEventListener("click", () => {
    const open = mnav.hidden;
    mnav.hidden = !open;
    menuBtn.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  });
  mnav && $$("a", mnav).forEach((a) => a.addEventListener("click", closeMenu));
  window.matchMedia("(min-width: 1024px)").addEventListener("change", (m) => m.matches && closeMenu());

  /* ---------- 나타나기(상세 페이지의 [data-rv]) ---------- */
  const rv = $$("[data-rv]");
  if (rv.length) {
    if ("IntersectionObserver" in window && !reduceMotion) {
      const io = new IntersectionObserver((entries) => entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      }), { rootMargin: "0px 0px -6% 0px" });
      rv.forEach((el) => io.observe(el));
    } else {
      rv.forEach((el) => el.classList.add("is-in"));
    }
  }

  /* ---------- 예약 폼: 문자로 보낼 내용을 만들어요(사이트에 저장 · 전송하지 않음) ---------- */
  const form = $("[data-reserve]");
  if (!form) return;
  const done = $("[data-done]");
  const msgEl = $("[data-msg]");
  const smsEl = $("[data-sms]");
  const SHOP = "01064114123";
  const isIOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const isPhone = window.matchMedia("(pointer: coarse)").matches;

  // 상세 쪽에서 "이 시공 예약하기"로 오면 그 시공을 미리 골라 둬요
  const OLD = { film: "tint" }; // 옮긴 시공 이름(예전 링크)
  let pre = new URLSearchParams(location.search).get("service");
  pre = OLD[pre] || pre;
  if (pre) {
    const box = $(`input[name="service"][value="${CSS.escape(pre)}"]`, form);
    if (box) box.checked = true;
  }
  const today = new Date();
  const dateInput = $('input[name="date"]', form);
  if (dateInput) dateInput.min = today.toISOString().slice(0, 10);

  const showErr = (key, on) => { const e = $(`[data-err="${key}"]`, form); if (e) e.hidden = !on; };

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const services = $$('input[name="service"]:checked', form).map((i) => i.dataset.label);
    let ok = true;
    showErr("service", services.length === 0);
    if (!services.length) ok = false;
    ["car", "name", "phone"].forEach((n) => {
      const input = $(`[name="${n}"]`, form);
      const bad = !String(fd.get(n) || "").trim() || (n === "phone" && String(fd.get(n)).replace(/\D/g, "").length < 9);
      input.closest(".field").classList.toggle("is-bad", bad);
      input.setAttribute("aria-invalid", String(bad));
      if (bad) ok = false;
    });
    if (!ok) {
      const first = $('.is-bad input, [data-err="service"]:not([hidden])', form);
      (first?.tagName === "INPUT" ? first : $('input[name="service"]', form))?.focus();
      return;
    }
    const v = (n) => String(fd.get(n) || "").trim();
    const lines = [
      "[김프로 예약 요청]",
      `시공: ${services.join(", ")}`,
      `차종: ${v("car")}${v("year") ? ` (${v("year")}년식)` : ""}`,
      v("memo") && `상태: ${v("memo")}`,
      (v("date") || v("time")) && `방문 희망: ${[v("date"), v("time")].filter(Boolean).join(" ")}`,
      `이름: ${v("name")}`,
      `연락처: ${v("phone")}`,
    ].filter(Boolean);
    const text = lines.join("\n");
    msgEl.textContent = text;
    smsEl.href = `sms:${SHOP}${isIOS ? "&" : "?"}body=${encodeURIComponent(text)}`;
    form.hidden = true;
    done.hidden = false;
    done.focus();
    window.scrollTo({ top: done.getBoundingClientRect().top + scrollY - 100, behavior: reduceMotion ? "auto" : "smooth" });
    if (isPhone) setTimeout(() => { location.href = smsEl.href; }, 400);
  });

  $("[data-back]")?.addEventListener("click", () => { done.hidden = true; form.hidden = false; $('input[name="service"]', form)?.focus(); });

  $("[data-copy]")?.addEventListener("click", async (e) => {
    const btn = e.currentTarget;
    try {
      await navigator.clipboard.writeText(msgEl.textContent);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = msgEl.textContent; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); } catch {}
      ta.remove();
    }
    const old = btn.textContent; btn.textContent = "복사했어요"; setTimeout(() => (btn.textContent = old), 1600);
  });
})();
