# Origin Social Studio — website

Static site (no build step): a Lattice.com homepage replica with Origin's brand skin, plus a discovery-call page.

- `index.html`, `contact.html`, `css/styles.css`, `js/main.js`
- Everything unknown is a placeholder: `<span class="ph">` (dashed outline) or an `<a data-ph="...">` link.
- Run locally: `python3 -m http.server 8000` in this folder, then open http://localhost:8000/
- Check: `python scripts/check.py` (needs Python Playwright + Chromium; writes screenshots to `research/screens/`)
- Libraries load from CDN (GSAP 3.13, Swiper 12, Inter), so it needs internet.
- All paths are relative, so it can be hosted under a sub-path.

Deploy: `./deploy.sh` (pushes main, enables GitHub Pages once, polls the live URL until the served index.html hash matches local).
