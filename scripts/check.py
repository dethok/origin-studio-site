"""Verify the Origin site in headless Chromium. Run: python scripts/check.py"""
import http.server, os, socket, sys, threading, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = 0
def ok(name, cond, extra=""):
    global fails
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra else ""))
    if not cond: fails += 1

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
with socket.socket() as s:
    s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}/"
os.makedirs(f"{ROOT}/research/screens", exist_ok=True)

def watch(page, errs):
    page.on("console", lambda m: m.type == "error" and errs.append("console: " + m.text))
    page.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
    page.on("requestfailed", lambda r: "favicon" not in r.url and errs.append("failed: " + r.url))
    page.on("response", lambda r: r.status >= 400 and "favicon" not in r.url and errs.append(f"{r.status}: {r.url}"))

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- desktop
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); page = ctx.new_page()
    errs = []; watch(page, errs)
    page.goto(base + "index.html", wait_until="networkidle")
    ok("desktop: zero console errors / failed requests", not errs, "; ".join(errs[:3]))
    nav = lambda: page.evaluate("(()=>{const n=document.querySelector('.nav');const c=getComputedStyle(n);const r=n.getBoundingClientRect();return {pos:c.position,top:r.top,h:r.height,bg:c.backgroundColor}})()")
    n0 = nav(); page.mouse.wheel(0, 2500); page.wait_for_timeout(600); n1 = nav()
    ok("nav sticky top 0, same height/bg after 2500px scroll", n0["pos"] == "sticky" and n1["top"] == 0 and n0["h"] == n1["h"] == 65 and n0["bg"] == n1["bg"], f"{n0} -> {n1}")
    page.evaluate("scrollTo(0,0)")
    ok("H1 opacity reaches 1 within 1s", page.evaluate("new Promise(r=>setTimeout(()=>r(+getComputedStyle(document.querySelector('#h1')).opacity),1000))") == 1)
    page.click(".dd-t:has-text('Services')"); page.wait_for_timeout(400)
    box = page.locator("#p-services").bounding_box()
    ok("Services panel visible, >=280px tall", page.locator("#p-services").is_visible() and box["height"] >= 280, f"h={box['height']:.0f}")
    page.keyboard.press("Escape"); page.wait_for_timeout(400)
    ok("Esc hides panel", not page.locator("#p-services").is_visible())
    ok("ScrollTrigger.getAll().length === 1", page.evaluate("ScrollTrigger.getAll().length") == 1)
    page.mouse.move(5, 500)
    idx = lambda: page.evaluate("document.querySelector('.swiper-slide-active')?.dataset.swiperSlideIndex")
    i0 = idx(); ok("swiper active slide exists", i0 is not None)
    page.wait_for_timeout(5200); i1 = idx()
    ok("swiper autoplay advances within 5s", i1 != i0, f"{i0}->{i1}")
    ok("cookie banner visible", page.locator("#cookie").is_visible())
    page.click("#c-rej"); page.reload(wait_until="networkidle")
    ok("cookie banner hidden after reject + reload", not page.locator("#cookie").is_visible())
    n = page.evaluate("document.querySelectorAll('.ph').length"); ok(".ph count > 0", n > 0, f"{n} .ph elements")
    page.evaluate("localStorage.clear()"); page.reload(wait_until="networkidle")
    page.screenshot(path=f"{ROOT}/research/screens/desktop.png", full_page=True)
    ctx.close()
    # ---- mobile
    ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); page = ctx.new_page()
    errs = []; watch(page, errs)
    page.goto(base + "index.html", wait_until="networkidle")
    ok("mobile: zero console errors / failed requests", not errs, "; ".join(errs[:3]))
    sw = page.evaluate("document.documentElement.scrollWidth"); ok("mobile scrollWidth <= 390", sw <= 390, str(sw))
    page.screenshot(path=f"{ROOT}/research/screens/mobile.png", full_page=True)
    page.click("#cookie-x"); page.click("#burger"); page.wait_for_timeout(400)
    ok("hamburger open: accordion visible + aria-expanded", page.locator("#menu").is_visible() and page.get_attribute("#burger", "aria-expanded") == "true")
    page.screenshot(path=f"{ROOT}/research/screens/mobile-menu.png")
    ctx.close()
    # ---- contact
    ctx = b.new_context(viewport={"width": 1440, "height": 900}); page = ctx.new_page()
    errs = []; watch(page, errs)
    page.goto(base + "contact.html", wait_until="networkidle")
    ok("contact: zero console errors / failed requests", not errs, "; ".join(errs[:3]))
    page.click("#contact-form button[type=submit]")
    first = page.evaluate("document.activeElement.name")
    ok("empty submit blocked, first invalid field focused", first == "name" and page.locator("#form-ok").is_hidden(), f"focused={first}")
    page.fill("[name=name]", "Test"); page.fill("[name=email]", "a@b.co"); page.select_option("[name=need]", "Strategy")
    page.click("#contact-form button[type=submit]"); page.wait_for_timeout(200)
    ok("filled submit shows success state", page.locator("#form-ok").is_visible())
    ctx.close(); b.close()
srv.shutdown()
print("ALL PASS" if not fails else f"{fails} FAILED"); sys.exit(1 if fails else 0)
