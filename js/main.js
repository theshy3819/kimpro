/* 김프로 — 스크롤로 움직이는 장면
 * 영상을 프레임 WebP로 쪼개 두고(assets/<이름>/manifest.json), 스크롤 진행도에 맞는 프레임을 캔버스에 그려요.
 *   polish    : 첫 장 광택 장면(정면 → 보닛 확대 → 패드가 지나간 자리부터 깨끗해짐 → 줌아웃)
 *   turntable : 턴테이블 위에서 도는 차(서비스 칸 왼쪽)
 * 프레임이 아직 없으면 정지 사진을 천천히 움직여 대신해요.
 */
(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- 프레임 묶음 ---------- */
  class Sequence {
    constructor(name, stillUrl) {
      this.name = name;
      this.stillUrl = stillUrl;
      this.mode = "loading"; // "frames" | "still"
      this.frames = [];
      this.still = null;
      this.count = 0;
      this.listeners = [];
    }

    ready() { this.listeners.forEach((fn) => fn()); }

    async load() {
      try {
        const res = await fetch(`assets/${this.name}/manifest.json`, { cache: "no-cache" });
        if (!res.ok) throw new Error("no manifest");
        const m = await res.json();
        const small = window.matchMedia("(max-width: 767px)").matches;
        const set = (small && m.mobile) || m.desktop;
        if (!set || !m.count) throw new Error("empty manifest");
        this.count = m.count;
        this.frames = new Array(m.count).fill(null);
        const url = (i) => `${set.dir}/${set.prefix}${String(i).padStart(m.pad || 3, "0")}.${m.ext || "webp"}`;
        // 성긴 프레임부터 받아 빨리 움직이게 하고, 사이를 채워요.
        const order = [];
        const seen = new Set();
        const push = (i) => { if (!seen.has(i)) { seen.add(i); order.push(i); } };
        push(0); push(m.count - 1);
        for (const step of [16, 8, 4, 2, 1]) for (let i = 0; i < m.count; i += step) push(i);
        await this.loadOne(0, url(0));
        this.mode = "frames";
        this.ready();
        let next = 1;
        const worker = async () => {
          while (next < order.length) {
            const i = order[next++];
            if (!this.frames[i]) await this.loadOne(i, url(i));
          }
        };
        await Promise.all([worker(), worker(), worker(), worker()]);
      } catch {
        await this.loadStill();
      }
    }

    loadOne(i, src) {
      return new Promise((resolve) => {
        const img = new Image();
        img.decoding = "async";
        img.onload = () => { this.frames[i] = img; resolve(); };
        img.onerror = () => resolve();
        img.src = src;
      });
    }

    loadStill() {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => { this.still = img; this.mode = "still"; this.ready(); resolve(); };
        img.onerror = () => resolve();
        img.src = this.stillUrl;
      });
    }

    // t(0~1)에 가장 가까운, 이미 받은 프레임
    frameAt(t) {
      const want = Math.round(clamp(t) * (this.count - 1));
      for (let d = 0; d < this.count; d++) {
        if (this.frames[want - d]) return this.frames[want - d];
        if (this.frames[want + d]) return this.frames[want + d];
      }
      return null;
    }
  }

  /* ---------- 캔버스 하나 ---------- */
  class SeqView {
    /**
     * opts.zoomCap   세로 화면에서 너비 기준 최대 확대(Infinity면 화면 가득 채움)
     * opts.centerY   그림의 세로 위치(0~1)
     * opts.wideShift 가로로 넓은 화면에서 오른쪽으로 비키는 정도(너비 비율)
     * opts.still     정지 사진 모드 움직임: { zoom, fx, fy } — (fx,fy) 쪽으로 zoom배까지 다가감
     */
    constructor(canvas, seq, opts) {
      this.c = canvas;
      this.ctx = canvas.getContext("2d", { alpha: false });
      this.seq = seq;
      this.o = Object.assign({ zoomCap: Infinity, centerY: 0.5, wideShift: 0, still: { zoom: 1.16, fx: 0.5, fy: 0.5, pan: 0.05 } }, opts);
      this.t = 0;
      this.target = 0;
      this.drawn = -1;
      seq.listeners.push(() => (this.drawn = -1));
      this.resize();
    }

    resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const r = this.c.getBoundingClientRect();
      this.w = Math.max(1, Math.round(r.width * dpr));
      this.h = Math.max(1, Math.round(r.height * dpr));
      this.c.width = this.w;
      this.c.height = this.h;
      this.drawn = -1;
    }

    tick() {
      this.t = reduceMotion ? this.target : lerp(this.t, this.target, 0.14);
      if (Math.abs(this.t - this.target) < 0.0005) this.t = this.target;
      const key = Math.round(this.t * 2000);
      if (key === this.drawn) return;
      this.drawn = key;
      this.draw();
    }

    draw() {
      const { ctx, w, h, seq, o } = this;
      ctx.fillStyle = "#0a0a0a";
      ctx.fillRect(0, 0, w, h);
      const img = seq.mode === "frames" ? seq.frameAt(this.t) : seq.mode === "still" ? seq.still : null;
      if (!img) { this.drawn = -1; return; }
      const iw = img.naturalWidth, ih = img.naturalHeight;
      const cover = Math.max(w / iw, h / ih);
      const s = Math.min(cover, (w / iw) * o.zoomCap);
      let dw = iw * s, dh = ih * s;
      const shift = w / h > 1.25 ? o.wideShift * (1 - 0.55 * this.t) : 0;
      let dx = (w - dw) / 2 + shift * w;
      let dy = h * o.centerY - dh / 2;
      if (seq.mode === "still") {
        // 정지 사진: 초점 (fx, fy)로 천천히 다가가며, 초점을 화면 가운데 쪽으로 끌어와요
        const z = 1 + (o.still.zoom - 1) * this.t;
        const px = dx + o.still.fx * dw, py = dy + o.still.fy * dh;
        const tx = lerp(px, w / 2, this.t * 0.7) + (o.still.pan || 0) * w * (0.5 - this.t);
        const ty = lerp(py, h * 0.45, this.t * 0.7);
        dw *= z; dh *= z;
        dx = tx - o.still.fx * dw;
        dy = ty - o.still.fy * dh;
      }
      ctx.drawImage(img, dx, dy, dw, dh);
      // 세로 화면에서 위아래가 비면, 그림 경계를 바탕색으로 녹여요
      if (dy > 1) {
        const f = Math.min(dh * 0.18, dy * 2);
        let g = ctx.createLinearGradient(0, dy, 0, dy + f);
        g.addColorStop(0, "#0a0a0a"); g.addColorStop(1, "rgba(10,10,10,0)");
        ctx.fillStyle = g; ctx.fillRect(0, dy - 1, w, f + 1);
        g = ctx.createLinearGradient(0, dy + dh - f, 0, dy + dh);
        g.addColorStop(0, "rgba(10,10,10,0)"); g.addColorStop(1, "#0a0a0a");
        ctx.fillStyle = g; ctx.fillRect(0, dy + dh - f, w, f + 1);
      }
    }
  }

  /* ---------- 준비 ---------- */
  const turntable = new Sequence("turntable", "assets/img/car-base.webp");
  const polish = new Sequence("polish", "assets/img/polish-front.webp");
  turntable.load();
  polish.load();

  const svcView = new SeqView($('[data-car-canvas="services"]'), turntable, { zoomCap: 1.75, centerY: 0.44 });
  // 세로 화면에서는 왼쪽의 패드까지 보이게 너비 기준으로 1.8배까지만 키워요
  const sceneView = new SeqView($('[data-seq-canvas="polish"]'), polish, { zoomCap: 1.8, centerY: 0.42, still: { zoom: 2.2, fx: 0.5, fy: 0.46, pan: 0 } });
  const views = [svcView, sceneView];

  const beatsIn = (root) => $$("[data-beat]", root).map((el) => {
    const [a, b] = el.dataset.beat.split(",").map(Number);
    return { el, a, b };
  });
  const HOLD_AT = 0.78; // 첫 장 스크롤의 이 지점에서 영상이 끝나고, 남은 구간은 마지막 장면(깨끗한 차)을 보여 줘요
  const sceneEl = $("[data-scene]");
  const sceneBeats = beatsIn(sceneEl);
  const sceneBar = $("[data-scene-bar]");
  const hdr = $("[data-hdr]");
  const fab = $(".fab");
  const cards = $$(".svc");
  const idxEl = $("[data-svc-idx]");
  const partEl = $("[data-svc-part]");
  let activeCard = -1;

  const progressOf = (el, vh) => {
    const r = el.getBoundingClientRect();
    return { p: clamp(-r.top / (r.height - vh)), r };
  };

  /* ---------- 스크롤 상태 계산 ---------- */
  function update() {
    const vh = window.innerHeight;

    // 1) 첫 장: 보닛으로 다가가 → 패드가 지나간 자리부터 깨끗해짐 → 줌아웃
    //    영상은 스크롤 0~HOLD_AT 동안 재생하고, 그 뒤로는 깨끗해진 차에 머물러요.
    const { p: s, r } = progressOf(sceneEl, vh);
    const vt = clamp(s / HOLD_AT);
    sceneView.target = vt;
    sceneBeats.forEach(({ el, a, b }) => el.classList.toggle("is-on", s >= a && s < b));
    if (sceneBar) sceneBar.style.transform = `scaleX(${vt})`;
    hdr.classList.toggle("is-solid", r.bottom < vh * 0.98);
    if (fab) fab.classList.toggle("is-on", r.bottom < vh * 0.6);

    // 2) 서비스: 화면 가운데에 있는 카드들 사이를 이어서 차 각도를 정해요
    const mid = window.innerWidth >= 1024 ? vh * 0.55 : vh * 0.72;
    const centers = cards.map((c) => { const b = c.getBoundingClientRect(); return b.top + b.height / 2; });
    let t = Number(cards[0].dataset.frame), cur = 0;
    for (let i = 0; i < cards.length; i++) {
      if (centers[i] <= mid) { cur = i; t = Number(cards[i].dataset.frame); }
    }
    if (cur < cards.length - 1 && centers[cur] <= mid) {
      const f0 = Number(cards[cur].dataset.frame), f1 = Number(cards[cur + 1].dataset.frame);
      const k = clamp((mid - centers[cur]) / (centers[cur + 1] - centers[cur]));
      t = lerp(f0, f1, k);
      if (k > 0.5) cur += 1;
    }
    svcView.target = t;
    if (cur !== activeCard) {
      activeCard = cur;
      cards.forEach((c, i) => c.classList.toggle("is-active", i === cur));
      if (idxEl) idxEl.textContent = String(cur + 1).padStart(2, "0");
      if (partEl) partEl.textContent = cards[cur].dataset.part || "";
    }
  }

  /* ---------- 부드러운 스크롤(Lenis) ---------- */
  let lenis = null;
  if (!reduceMotion && window.Lenis) {
    lenis = new window.Lenis({ lerp: 0.1, wheelMultiplier: 0.9 });
    window.__lenis = lenis; // site.js의 맨 위로 단추가 같이 써요
  }
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      const target = id === "#top" ? document.body : $(id);
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: id === "#top" ? 0 : -8 });
      else target.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
    });
  });

  function loop(time) {
    if (lenis) lenis.raf(time);
    update();
    views.forEach((v) => v.tick());
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  let rz;
  window.addEventListener("resize", () => {
    clearTimeout(rz);
    rz = setTimeout(() => views.forEach((v) => v.resize()), 120);
  });

  /* ---------- 나타나기 ---------- */
  const revealTargets = [
    ".services__head > *", ".record > .h2", ".stat", ".process > .h2", ".step",
    ".compare figure", ".equip__txt > *", ".visit__card > *", ".ftr__cols > *",
  ];
  const rvEls = $$(revealTargets.join(","));
  $$(".bars li").forEach((li, i) => li.style.setProperty("--i", i));
  const grows = $$(".bars");
  if ("IntersectionObserver" in window && !reduceMotion) {
    rvEls.forEach((el) => el.classList.add("rv"));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        en.target.classList.add("is-in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    rvEls.forEach((el) => io.observe(el));
    grows.forEach((el) => io.observe(el));
  } else {
    grows.forEach((el) => el.classList.add("is-in"));
  }

  /* ---------- 숫자 세기 ---------- */
  const nums = $$("[data-count]");
  const fmt = (n) => n.toLocaleString("ko-KR");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io2 = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        io2.unobserve(en.target);
        const el = en.target, end = Number(el.dataset.count), t0 = performance.now(), dur = 1400;
        const step = (now) => {
          const k = clamp((now - t0) / dur);
          el.textContent = fmt(Math.round(end * (1 - Math.pow(1 - k, 3))));
          if (k < 1) requestAnimationFrame(step);
        };
        el.textContent = "0";
        requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    nums.forEach((n) => io2.observe(n));
  }
})();
