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
    # client markup 2026-11-17: removed items stay gone, logo is the real file, chat block centred
    gone = page.evaluate("""['#banner','.logobar','#stories','#platforms','#resources','.stars','.card .arr','.c4 .arr','#p-why',
      'a[href=\"#stories\"]','a[data-ph=\"youtube-url\"]'].filter(q=>document.querySelector(q))""")
    ok("client-removed elements absent", not gone, str(gone))
    navt = page.evaluate("[...document.querySelectorAll('#menu > a, #menu .dd-t')].map(e=>e.textContent.trim())")
    ok("nav = Services + Why Origin only", navt == ["Services", "Why Origin"], str(navt))
    ok("Why Origin links to How it feels", page.get_attribute("#menu > a", "href") == "index.html#how-it-feels")
    ok("logo is the client PNG and loaded", page.evaluate("(()=>{const i=document.querySelector('.logo img');return !!i&&i.src.endsWith('origin-logo.png')&&i.naturalWidth>0})()"))
    foot = page.evaluate("document.querySelector('.foot').innerText")
    ok("footer trimmed", not any(w in foot for w in ["Who we help", "ORIGIN ADVANTAGE", "Origin Advantage", "Resources", "Building Origin", "Careers", "Pricing"]), "")
    ok("services copy updated", "Put together the content support that fits your business." in page.inner_text("#services"))
    cx = page.evaluate("(()=>{const w=document.querySelector('#how-it-feels .wrap').getBoundingClientRect(),c=document.querySelector('#chat').getBoundingClientRect(),h=document.querySelector('#how-it-feels h2').getBoundingClientRect();return [w.left+w.width/2,c.left+c.width/2,h.left+h.width/2]})()")
    ok("How it feels centred (chat + h2 within 2px of centre)", abs(cx[0]-cx[1]) < 2 and abs(cx[0]-cx[2]) < 2, str([round(x) for x in cx]))
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
    ok("contact: Pick a time removed", page.locator("[data-ph=calendly-url]").count() == 0)
    ok("contact: footer identical to home", page.evaluate("document.querySelector('.foot').innerText") == foot)
    ctx.close(); b.close()
srv.shutdown()
print("ALL PASS" if not fails else f"{fails} FAILED"); sys.exit(1 if fails else 0)
