// Screenshot the local site at fixed scroll fractions, for desktop or mobile, and log console errors.
//   node shoot.mjs <url> <outDir> <width> <height> <fractions comma list>
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
const [url, outDir, W, H, fr, preEval] = process.argv.slice(2); // preEval: 찍기 전에 실행할 JS(선택)
// 각 값은 페이지 전체 비율(0.2) 또는 "#섹션id:비율"(그 섹션의 스크롤 구간 안 비율)
const fracs = (fr || "0,0.1,0.2").split(",");
mkdirSync(outDir, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const port = 14000 + Math.floor(Math.random() * 5000), prof = mkdtempSync(join(tmpdir(), "sh-"));
const br = spawn("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
try {
  let page; for (let i = 0; i < 50 && !page; i++) { await sleep(200); try { page = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json(); } catch {} }
  const ws = new WebSocket(page.webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = new Map(); const logs = [];
  ws.onmessage = (e) => { const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
    if (m.method === "Runtime.exceptionThrown") logs.push("EXC " + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
    if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type)) logs.push(m.params.type + " " + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 300));
    if (m.method === "Network.loadingFailed") logs.push("NETFAIL " + m.params.errorText + " " + (m.params.requestId));
  };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  const ev = async (x) => (await send("Runtime.evaluate", { expression: x, awaitPromise: true, returnByValue: true }))?.result?.value;
  await send("Page.enable"); await send("Runtime.enable"); await send("Network.enable");
  const mobile = +W < 600;
  await send("Emulation.setDeviceMetricsOverride", { width: +W, height: +H, deviceScaleFactor: mobile ? 2 : 1, mobile });
  if (mobile) await send("Emulation.setTouchEmulationEnabled", { enabled: true });
  await send("Page.navigate", { url }); await sleep(3500);
  const SH = await ev("document.documentElement.scrollHeight");
  for (const [i, f] of fracs.entries()) {
    if (f.startsWith("#")) {
      const [sel, k] = f.split(":");
      await ev(`(()=>{const e=document.querySelector('${sel}');const top=e.getBoundingClientRect().top+scrollY;window.scrollTo(0, Math.round(top + ${+k} * (e.offsetHeight - innerHeight)));})()`);
    } else {
      await ev(`window.scrollTo(0, ${Math.round(+f * (SH - +H))})`);
    }
    await sleep(2200);
    if (preEval) { await ev(preEval); await sleep(700); }
    const shot = await send("Page.captureScreenshot", { format: "jpeg", quality: 70 });
    writeFileSync(join(outDir, `p${String(i).padStart(2, "0")}_${f.replace(/[#:]/g, "-")}.jpg`), Buffer.from(shot.data, "base64"));
  }
  const overflow = await ev("document.documentElement.scrollWidth > window.innerWidth");
  console.log(JSON.stringify({ SH, overflow, logs }, null, 1));
  ws.close();
} finally { br.kill(); await sleep(300); try { rmSync(prof, { recursive: true, force: true }); } catch {} }
