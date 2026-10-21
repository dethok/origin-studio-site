# lattice.com homepage inventory (observed 2026-10-22, headless Chromium 1440x900 and 390x844)

Method note: the shared Playwright MCP browser was locked by another instance, so I drove an isolated headless Chromium via Python Playwright (scripts probe*.py in this folder). Screenshots are static; time-based animations were inferred from computed styles, GSAP/Swiper state and frame samples, and flagged where not visually confirmed. A cookie banner overlays every screenshot (see section 7).

## Tech signals (measured)
| Item | Finding |
|---|---|
| Platform | Webflow (html class `w-mod-js w-mod-ix3`, `data-wf-site`, Webflow Interactions 3). Only 1 `[data-w-id]` element - interactions are mostly code-driven, not classic IX2 |
| Animation libs | GSAP 3.15.0 + ScrollTrigger, SplitText, MorphSVGPlugin, TextPlugin, DrawSVGPlugin (loaded from cdn.prod.website-files.com/gsap/3.15.0/). Custom bundle `lattice-main.<hash>.js` |
| Carousel | Swiper 12 (jsdelivr) - testimonials |
| Lottie | One dotlottie file (`ai-agent-v3.lottie`, class `agent-lottie`, `data-loop=0`, autoplay) driven by ScrollTrigger scrub |
| Smooth scroll | None. No Lenis; `scroll-behavior: auto`. Native scroll |
| jQuery | 3.5.1 (Webflow default) |
| Other | Osano consent, Segment, GTM, Heap, Marketo Munchkin, Intellimize (A/B), Qualified (chat docking script loaded; no chat widget visible), Unify, Bizible |
| ScrollTrigger instances | Exactly 1: trigger `.agent-lottie`, scrub true, start `clamp(top 80%)`, end `clamp(bottom 60%)`, no pin. No pinned sections anywhere |
| Font | **Matter** (sans-serif fallback), self-hosted. body 18.05px/400; h1 72.2px/500; h2 46.9px/500; tight line-height (~0.9-1.0) on headlines |
| Colours | text/ink `rgb(0,31,31)` (#001F1F); page bg white `#fff` with off-white `#FAF9F7`-ish cream section bg; primary button bg `rgb(4,102,69)` (#046645) text `rgb(205,250,206)` (#CDFACE); secondary button inverse (mint bg, green text); banner lilac (~#C9A6F5); integrations/outro sections saturated indigo-blue gradient (#5865FF-ish, visual estimate from screenshot) |
| Radii | buttons ~12-13px (nav button 11.5px); cards ~24-32px; section "boxes" ~48px+ large rounded containers inset 14px from viewport edge |

## 1. Announcement bar + Nav
- **Announcement bar** (`section.banner`, 33px): lilac strip, "BREAKING NEWS" pill, "The 2027 State of People Strategy Report is out!", "Read the full report ->", dismiss X at right. Scrolls away with the page (not sticky).
- **Nav** (`.nav.w-nav`, `position: sticky; top: 0`, 65px tall, solid white, 1px bottom border). No shrink, no colour change on scroll (measured: height 64.97px and white bg both at top and at scrollY 2500). Sticks to y=0 once banner has scrolled off.
- Layout: logo left (multi-colour mark + "Lattice" wordmark) | centred links: Platform v, Why Lattice v, Customers, Resources v, Pricing | right: "Log in" text link + green "Request a demo" button (solid #046645).
- **Mega menus: CLICK-to-open** (`data-hover=false`, `data-delay=0`; Webflow dropdown). Hover only gives a pale pill highlight on the toggle. Click opens a full-width panel (measured 1299x319) with 200ms Webflow dropdown fade; click outside closes.
  - Platform panel: columns "Platform overview" (Explore Our Platform, Habits, Analytics, MCP [NEW], Product Roadmap), "Products" (Performance with sub-items Reviews/Talent Reviews/PIPs/Succession/1:1s/Updates/Feedback; Engagement; Goals & OKRs; Grow; Compensation), "Lattice AI" (Overview, AI Agent [NEW]), plus a promo card "Take a tour of Lattice - Check out our free interactive tours". Each item = title + one-line description.
  - Why Lattice panel: "The Lattice Advantage" (Why Lattice, How Lattice Compares, Integrations, ROI Estimator) + "Company" (About, Newsroom, CPO Council, Community, Partner Ecosystem) + "Featured" customer-story card (e.g. "How BARK Scaled...").
  - Resources panel exists (not captured separately).
- **Mobile (390px)**: nav collapses at Webflow `small` breakpoint (<=767px... collapse=small). Row shows logo, compact "Request a demo", and a square hamburger button that becomes X when open. Open state = full-width stacked accordion: Platform v, Why Lattice v, Customers, Resources v, Pricing as rounded cream rows; chevrons expand sub-lists. No horizontal overflow (scrollWidth = 390). Banner reflows to 3 lines. (Screenshot 12-mobile-menu.png)

## 2. Hero (`header.hero.is-home`, ~657px tall) - 01-hero.png
- Two-column grid: left copy, right visual. Background: near-white with a very faint warm tint.
- H1 "People + AI: Succeeding Together" (72px, weight 500, 3 lines). Sub (`body-l`): "Join 5,000+ forward-thinking teams using Lattice's HR and AI tools to manage people and performance - all on one trusted platform."
- CTAs: "Request a demo" (`button is-rainbow` - green button with an animated pastel/cyan-pink gradient glow ring around it) + "Take a tour" (`is-secondary`, mint). Both prefetch their target (`<link rel=prefetch>`).
- Right visual: large (~630x430) rounded rectangle with a mint-to-cyan-to-lime blurred gradient frame; inside, a white device card with a pink panel showing a product UI (goals list: "Increase international revenue 80%", nested sub-goals 90%/40%) and a dark caption strip. Frame-to-frame the UI changes (goal row alone vs. nested rows; captions "Goals that align your teams, feedback that fuels growth," -> "and AI-powered development areas that help employees reach their potential.") and the gradient blob position shifts, so it is an auto-playing, time-based, looping product animation. I could NOT identify the element type (no `<video>`, `<canvas>` or lottie inside the hero per DOM scan; likely an HTML/CSS/GSAP timeline or an embedded component) - unconfirmed.
- Text animation: H1 samples at load show opacity 0 -> 1 within ~250-750ms with `transform: none`, i.e. a quick fade-in, no word-split/typewriter detected (0 child spans/divs in h1). SplitText plugin is loaded but I saw no split in the hero.
- **Logo bar** sits at the hero bottom (`section.is-logobar`, 116px): 8 grey/greyscale logos in one row (greenhouse, Robinhood, Loom, Duolingo, Discord, brooklinen, ..., gusto), ~72-108px wide each, evenly spaced. Inline CSS shows `logobar-item { animation: logobar 60s infinite }` ONLY inside `@media (max-width: 991px)` ("Marquee on tablet") - so it is a static row on desktop and an infinite linear marquee on tablet/mobile.

## 3. Sections in page order
| # | Section (class, y-top, height) | Purpose / layout / content |
|---|---|---|
| 0 | `banner` 0, 33 | see above |
| 1 | Hero + logobar 33-756 | see above |
| 2 | `section` "Platform overview" 755, 1121 (02/03 png) | Mint pill-tag label "Platform overview ->" above H2 "High-performing teams are built here" with a right-aligned paragraph + "Take a tour" button. Then a **bento grid of product cards**: top row 2 large cards (Performance - cyan tint, Goals & OKRs - pale lime tint) with cropped product UI screenshots bleeding off the bottom; bottom row 3 equal cards (Engagement - pink, Grow - cream/yellow, Compensation - green). Each card: line icon + title (28px), circular arrow button top-right (tinted to card colour), 2-line description (first sentence bold/dark, second lighter), then a stylised UI mock (white mini cards with skeleton bars). Whole card is a link |
| 3 | `box is-agent` "AI Agent" 1891, 1162 (04 png) | Huge rounded container inset ~14px from viewport edges, pastel pink-to-cyan radial gradient background. Centred: lilac pill "AI Agent ->", H2 "Unblock work and unlock potential with your personal AI Agent", centred paragraph, then a centred "Ask Lattice" chat-window mock (chat bubbles) - this is the **dotlottie** (`ai-agent-v3.lottie`) scrubbed by scroll |
| 4 | `section` "Habits" 3060, 699 (05 png) | Pill "Habits ->", H2 left ("Build high performance through everyday habits") + paragraph and underlined "Learn more ->" right. **4-column card row** (1:1s, Weekly Updates, Feedback, Q&A Boards): white rounded cards, top 55% a pastel gradient tile with a small UI illustration (checklist, emoji mood picker with a highlighted emoji, "Customer-obsessed" checkmark chips, Q&A answer card), bottom: title + circular arrow + 3-line copy |
| 5 | `section` "Customer stories" 3759, 765 (06 png) | Pill + H2 "Trusted by top performers". **Swiper carousel** of 8 slides, ~610px wide cards peeking left/right (next/prev partially visible), pastel card backgrounds (mint, lilac...). Card: headshot with company logo badge, name, title @ company, quote (left) | big stat (e.g. "27%", "3.5x") + caption + "Read the story ->" pill button (right, divided by a vertical rule). **Pagination = pill dots, active dot elongated green pill** |
| 6 | `box is-integrations` 4539, 541 (07 png) | Saturated indigo/blue gradient rounded box. Pill "Integrations ->", white H2 "Integrate everything. Align everyone.", sub copy, then a single row of ~11 rounded-square app tiles (Salesforce, Outlook, Slack-like, Jira, ADP, Teams, Azure...), edge tiles fade/clip out - an **infinite horizontal marquee** (`icons-marquee` animation, 90s linear infinite, two rows listed in DOM) |
| 7 | `section` "Resources" 5087, 589 | Small green "RESOURCES" tag, H2 "Power your high-performing organization", "Library ->" link; row of cards (Library, Events/tickets etc. with big line icons on pastel gradients). Only partly captured in screenshots |
| 8 | `box is-outro` 5690, 607 | Final CTA band: five star emoji row, "3300+ 5-star G2 reviews", H2 "Your people are your business", copy "Ensure both are successful wi...", presumably Request a demo / Take a free tour buttons (`button` + `button is-secondary`, text "Take a free tour" confirmed in DOM). Rounded box. Screenshot 09 missed it (scroll overshoot) |
| 9 | `footer` ~6300-7044 | see section 6 |

Pattern: every content section opens with a **pill label (tinted, with arrow circle) + large H2**; cream (#FAF9F7-ish) page background alternating with large rounded gradient "boxes" for Agent / Integrations / Outro. Max content width ~1240px (x 99-1341 at 1440). Total page height 7044px at 1440.

## 4. Animations (what I measured vs. what is inferred)
| Where | Effect | Trigger | Timing / easing | Loops | Confidence |
|---|---|---|---|---|---|
| Nav dropdowns | Webflow dropdown open/close fade | click | 200ms (`data-duration=200`) | no | measured |
| Nav toggle / buttons | colour/bg hover; transitions in CSS use `cubic-bezier(0.165,0.84,0.44,1)` (easeOutQuart-like) 0.3s/0.5s, `cubic-bezier(0.23,1,0.32,1)` 0.5s, `cubic-bezier(0.22,0.61,0.36,1)` 0.24s | hover | 0.24-0.5s, snappy ease-out | no | measured via computed styles; exact per-element mapping not verified |
| One overshoot transition | `1s linear(0, .708, .927, 1.067, 1.12 ... 1)` spring-style easing (overshoot ~13%) on some element - likely the emoji/checkmark/arrow micro-interactions | hover/state | 1s | no | easing measured, target element unidentified |
| Hero CTA | `is-rainbow` animated gradient glow ring | time | continuous (appears to shift between screenshots) | yes | observed visually, duration not measured |
| Hero visual | auto-playing UI demo with captions + drifting gradient blob | time | several seconds per scene | yes (assumed) | observed 2 different frames; loop not timed |
| H1 | fade-in on load | load | <0.75s | no | measured opacity 0->1 |
| AI Agent chat | dotlottie played by ScrollTrigger scrub | scroll (section top 80% -> bottom 60% of viewport) | progress-linked, not time-based | no (scrub) | measured config; in screenshot the last chat word is blurred mid-reveal (text blur-in effect inside lottie/chat) |
| Testimonials | Swiper 12 autoplay, `loop: true`, `speed: 500ms`, 8 slides; peeking neighbours; dot pagination | time + click/drag | 500ms slide, autoplay delay not read | yes | measured |
| Integration icons | CSS marquee `icons-marquee` | time | 90s linear | infinite | measured |
| Logo bar | CSS marquee `logobar` 60s infinite, only <=991px | time | 60s | infinite | measured from inline CSS |
| Scroll reveals (fade/slide/stagger) on cards, parallax, counters, cursor effects, page transitions | NOT detected: only 1 ScrollTrigger exists, 1 `data-w-id`, no data-aos/gsap attributes, 3 live gsap tweens (global timeline), no Lenis. I did not see staggered entry in screenshots (cards were fully rendered when scrolled in after 1.8s, so a subtle reveal cannot be ruled out) | - | - | - | negative evidence only |
| Pinned / scrollytelling | none (no pinned ScrollTriggers) | - | - | - | measured |

## 5. Footer (`footer`, white, 524px nav grid) - 09-outro-footer.png
Top hairline, then 4 columns of link lists with small-caps grey headings:
1. PLATFORM OVERVIEW (Explore, Habits, Analytics, MCP [NEW], Roadmap, Interactive Tours, Request a Demo); PRODUCTS (Performance, Engagement, Goals & OKRs, Grow, Compensation); LATTICE AI (AI Overview, AI Agent, Skills library [NEW], Prompt library [NEW])
2. SOLUTIONS - industries (Agencies ... Technology, 11 items), divider, company sizes (Small/Midsize/Enterprise), divider, personas (CEOs, HR Leaders, People Managers, Individual Contributors)
3. THE LATTICE ADVANTAGE (Why Lattice, Customer Stories, Compares, Integrations, ROI Estimator); RESOURCES (Library, Articles, Ebooks, Templates, Events & Webinars, Lattiverse, 2027 State of People Strategy [NEW]); SUPPORT (Help Center, Lattice University, Contact Support)
4. COMPANY (About, Careers [HIRING], Pricing, Newsroom, CPO Council, Community, Partner Ecosystem, Log in); PRIVACY & SECURITY (Privacy Policy, Privacy Request, Cookie Preferences, Do Not Sell My Personal Information with CCPA toggle icon, Status, Security Trust Center)
Bottom bar: "Lattice (c) 2026 - All Rights Reserved." left; 4 grey rounded-square social icons right (Facebook, X, YouTube, LinkedIn). NO newsletter form. Small lilac "NEW" / "HIRING" badges inline on links.

## 6. Overlays
- **Cookie banner**: Osano (`.osano-cm-window`), fixed bottom-centre card (~865px wide, white, rounded, shadow) with copy, "Storage Preferences" link, three toggles (Targeted Advertising / Personalization / Analytics), and green Save / Accept All / Reject Non-Essential buttons; X to dismiss. Full-width stacked on mobile. Appears on first visit (headless, no consent cookie).
- **Chat widget**: none visible; Qualified script (`qualified.js`, `docking.js`) is loaded, so a chat/meeting dock may appear for some visitors/regions - unconfirmed. Two other `position: fixed` elements with GUID ids exist (likely Qualified/Intellimize containers).
- Announcement bar: described above.

## Replication notes
Stack to match: Webflow-style layout, Matter-like geometric grotesque (e.g. use a similar licensed font), 1240px container, huge radii, pastel tinted card system, pill section labels, GSAP+ScrollTrigger only for the lottie scrub, Swiper for testimonials, CSS keyframes for marquees, click-to-open mega menu, sticky non-shrinking nav. The motion language is restrained: most "animation" is looping product-UI demos and marquees, not scroll choreography.

Files: /private/tmp/claude-501/-Users-tedkoh-maximizer/19f8e1f9-c169-4baa-830a-db09765824fc/scratchpad/lattice/ (01-hero.png ... 12-mobile-menu.png, info*.json raw measurements)
