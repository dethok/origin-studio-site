"""Behance-style showcase composites: full desktop page stack + phone cutouts per section.
Run: python scripts/showcase.py   ->  showcase/home.png, showcase/contact.png (gitignored).
Preconditions: Playwright chromium (same venv as check.py). Done when both PNGs print their size."""
import http.server, os, socket, threading, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/showcase"; RAW = f"{OUT}/raw"; os.makedirs(RAW, exist_ok=True)
CANVAS, DESK, PHONE = 1600, 1160, 260
PAGES = {
    "home":    {"file": "index.html",   "label": "Home page",
                "phones": [".hero", "#services", "#how-it-feels", "#stories", "#platforms", ".box-violet"]},
    "contact": {"file": "contact.html", "label": "Contact page", "phones": ["main"]},
}
# freeze everything so every capture is the "finished" state: cookie gone, hero on scene 1, chat scrub at end, swiper still
SETTLE = """(async () => {
  document.querySelector('#c-rej')?.click();
  await new Promise(r => setTimeout(r, 400));
  if (window.ScrollTrigger) ScrollTrigger.getAll().forEach(t => { t.disable(false); t.animation && t.animation.progress(1); });
  if (window.gsap) {
    gsap.globalTimeline.getChildren(false, false, true).filter(t => t.repeat() === -1 && t.duration() > 10).forEach(t => t.pause(2));
    gsap.globalTimeline.pause();
  }
  const sw = document.querySelector('#sw'); sw?.swiper?.autoplay?.stop();
})()"""
TOPS = "sels => { const nav = document.querySelector('.nav').getBoundingClientRect().height; return {nav, tops: sels.map(s => document.querySelector(s).getBoundingClientRect().top + scrollY)} }"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
with socket.socket() as s:
    s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}/"

CSS = f"""body{{margin:0;background:#F1F1EF;font-family:-apple-system,BlinkMacSystemFont,Inter,system-ui,sans-serif}}
.canvas{{width:{CANVAS}px;padding:72px 0 140px}}
.top{{display:flex;justify-content:space-between;padding:0 72px 56px;font-size:11px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:#6B6B68}}
.desk{{position:relative;width:{DESK}px;margin:0 auto;outline:1px solid rgba(0,0,0,.08);box-shadow:0 40px 90px -20px rgba(0,0,0,.18)}}
.desk>img{{display:block;width:100%}}
.phone{{position:absolute;width:{PHONE}px;box-sizing:border-box;padding:11px;background:#0D0D0D;border-radius:46px;box-shadow:0 50px 90px -30px rgba(0,0,0,.5),inset 0 0 0 1px rgba(255,255,255,.1)}}
.scr{{position:relative;border-radius:36px;overflow:hidden;aspect-ratio:390/844;background:#fff}}
.scr img{{display:block;width:100%}}
.isl{{position:absolute;top:10px;left:50%;width:78px;height:22px;margin-left:-39px;background:#0D0D0D;border-radius:12px}}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, pg in PAGES.items():
        # desktop: one full-page capture + section tops for phone placement
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2); page = ctx.new_page()
        page.goto(base + pg["file"], wait_until="networkidle"); page.evaluate(SETTLE)
        tops = page.evaluate(TOPS, pg["phones"])["tops"]
        page.screenshot(path=f"{RAW}/{name}-desktop.png", full_page=True); ctx.close()
        # mobile: viewport capture scrolled to each section (nav stays on top)
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True); page = ctx.new_page()
        page.goto(base + pg["file"], wait_until="networkidle"); page.evaluate(SETTLE)
        m = page.evaluate(TOPS, pg["phones"])
        for i, t in enumerate(m["tops"]):
            page.evaluate("y => scrollTo(0, y)", max(0, t - m["nav"])); page.wait_for_timeout(300)
            page.screenshot(path=f"{RAW}/{name}-phone-{i}.png")
        ctx.close()
        # compose: desktop strip centred, phones alternate left/right at their section's y
        scale = DESK / 1440
        phones = "".join(
            f'<div class="phone" style="left:{-(PHONE - 60) if i % 2 == 0 else DESK - 85}px;top:{int(t * scale) + 40}px"><div class="scr"><img src="raw/{name}-phone-{i}.png"><i class="isl"></i></div></div>'
            for i, t in enumerate(tops))
        html = (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="canvas">'
                f'<div class="top"><span>{pg["label"]}</span><span>Origin Social Studio</span><span>Desktop 1440 · Mobile 390</span></div>'
                f'<div class="desk"><img src="raw/{name}-desktop.png">{phones}</div></div>')
        open(f"{OUT}/{name}.html", "w").write(html)
        ctx = b.new_context(viewport={"width": CANVAS, "height": 900}, device_scale_factor=2); page = ctx.new_page()
        page.goto(f"{base}showcase/{name}.html", wait_until="networkidle")
        page.evaluate("Promise.all([...document.images].map(i => i.decode()))")
        page.screenshot(path=f"{OUT}/{name}.png", full_page=True)
        print(f"{OUT}/{name}.png", page.evaluate("[document.body.scrollWidth, document.body.scrollHeight]")); ctx.close()
    b.close()
srv.shutdown()
