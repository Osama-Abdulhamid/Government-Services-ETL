"""
Google Maps Reviews Scraper (LARGE SCALE) — Egyptian Government Services
12 services x 18 governorates = 216 targets. Includes RESUME (stop & re-run safely).
Output columns map to the star schema. review_date is RELATIVE Arabic ->
clean_to_silver.py converts it to an absolute date.

Setup:
  pip install playwright pandas
  playwright install chromium
  python gov_reviews_scraper_large.py     # stop anytime with Ctrl+C
  python gov_reviews_scraper_large.py     # run again -> resumes
Note: academic use only; scrape gently; run in batches; the # VERIFY selectors
may need updating against the current Maps DOM (same ones your first run used).
"""

import csv, os, re, time, random, hashlib
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

# ============================ CONFIG ============================
SERVICES = [
    "مكتب السجل المدني", "الأحوال المدنية", "وحدة مرور", "إدارة المرور",
    "مكتب الشهر العقاري", "مكتب توثيق الشهر العقاري", "مكتب بريد", "مكتب التموين",
    "مكتب صحة", "مستشفى حكومي", "مأمورية الضرائب", "مكتب القوى العاملة",
]
GOVERNORATES = [
    "القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "الغربية",
    "القليوبية", "المنوفية", "البحيرة", "أسيوط", "المنيا", "سوهاج",
    "بني سويف", "الفيوم", "قنا", "أسوان", "الإسماعيلية", "بورسعيد",
]
TARGETS = [(s, g) for s in SERVICES for g in GOVERNORATES]   # 216 combinations

MAX_PLACES_PER_QUERY  = 8        # offices to open per search
MAX_REVIEWS_PER_PLACE = 60       # cap reviews per office
HEADLESS              = False     # keep False for the first runs
OUT_FILE              = "gov_reviews_bronze.csv"
CHECKPOINT            = "scrape_done_queries.txt"
# ===============================================================

FIELDS = ["review_id", "governorate", "service_query", "place_name",
          "rating", "review_text", "review_date", "scraped_at"]


def slow(a=1.2, b=3.0):
    time.sleep(random.uniform(a, b))


def make_id(place, author, text):
    return hashlib.md5(f"{place}|{author}|{text[:50]}".encode("utf-8")).hexdigest()[:16]


def parse_rating(aria):
    if not aria:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", aria)
    return float(m.group(1)) if m else None


def load_done():
    if os.path.exists(CHECKPOINT):
        return set(open(CHECKPOINT, encoding="utf-8").read().splitlines())
    return set()


def mark_done(query):
    with open(CHECKPOINT, "a", encoding="utf-8") as f:
        f.write(query + "\n")


def load_seen_ids():
    seen = set()
    if os.path.exists(OUT_FILE):
        try:
            import pandas as pd
            seen = set(pd.read_csv(OUT_FILE)["review_id"].astype(str))
        except Exception:
            pass
    return seen


def dismiss_consent(page):
    try:
        page.get_by_role("button", name=re.compile(r"accept all|قبول الكل|agree|موافق", re.I)).first.click(timeout=3000)
        slow()
    except Exception:
        pass


def open_reviews_tab(page):
    for how in ("tab", "button"):
        try:
            page.get_by_role(how, name=re.compile(r"review|مراجع", re.I)).first.click(timeout=4000)
            return
        except Exception:
            continue


def scroll_reviews(page, rounds=18):
    for _ in range(rounds):
        page.evaluate(
            """() => {
                let best=null, bestH=0;
                document.querySelectorAll('div').forEach(d => {
                    if (d.scrollHeight > d.clientHeight + 200 && d.clientHeight > 300) {
                        if (d.scrollHeight > bestH) { bestH = d.scrollHeight; best = d; }
                    }
                });
                if (best) best.scrollTop = best.scrollHeight; else window.scrollBy(0, 3000);
            }"""
        )
        slow(0.8, 1.6)


def scrape_place(page, gov, query, writer, fh, seen):
    open_reviews_tab(page); slow()
    place_name = ""
    try:
        place_name = page.locator("h1").first.inner_text(timeout=2500).strip()
    except Exception:
        pass
    scroll_reviews(page)
    cards = page.locator("div.jftiEf")                 # VERIFY
    total = min(cards.count(), MAX_REVIEWS_PER_PLACE)
    added = 0
    for i in range(total):
        c = cards.nth(i)
        try:
            more = c.locator('button:has-text("More"), button:has-text("المزيد")')
            if more.count(): more.first.click(timeout=1000)
        except Exception:
            pass
        author = text = date = ""; rating = None
        try: author = c.locator("div.d4r55").first.inner_text(timeout=1000).strip()        # VERIFY
        except Exception: pass
        try: rating = parse_rating(c.locator('span[role="img"]').first.get_attribute("aria-label", timeout=1000))
        except Exception: pass
        try: text = c.locator("span.wiI7pd").first.inner_text(timeout=1000).strip()         # VERIFY
        except Exception: pass
        try: date = c.locator("span.rsqaWe").first.inner_text(timeout=1000).strip()         # VERIFY
        except Exception: pass
        if not text and rating is None:
            continue
        rid = make_id(place_name, author, text)
        if rid in seen:
            continue
        seen.add(rid); added += 1
        writer.writerow({
            "review_id": rid, "governorate": gov, "service_query": query,
            "place_name": place_name, "rating": rating,
            "review_text": re.sub(r"\s+", " ", text).strip(),
            "review_date": date, "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
    fh.flush()
    return added


def run():
    done = load_done()
    seen = load_seen_ids()
    remaining = [(s, g) for (s, g) in TARGETS if f"{s} {g}" not in done]
    print(f"Total targets: {len(TARGETS)} | done: {len(done)} | remaining: {len(remaining)} | reviews so far: {len(seen)}")

    new_file = not os.path.exists(OUT_FILE)
    fh = open(OUT_FILE, "a", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if new_file:
        writer.writeheader(); fh.flush()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(locale="ar-EG", viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        try:
            for idx, (service, gov) in enumerate(remaining, 1):
                query = f"{service} {gov}"
                print(f"\n[{idx}/{len(remaining)}] === {query} ===")
                try:
                    page.goto("https://www.google.com/maps/search/" + query.replace(" ", "+"), timeout=60000)
                    slow(2, 4); dismiss_consent(page)
                    for _ in range(3):
                        page.mouse.wheel(0, 2200); slow(0.6, 1.2)
                    results = page.locator("a.hfpxzc")            # VERIFY
                    links = []
                    for i in range(min(results.count(), MAX_PLACES_PER_QUERY)):
                        try: links.append(results.nth(i).get_attribute("href"))
                        except Exception: pass
                    q_added = 0
                    for url in links:
                        if not url: continue
                        try:
                            page.goto(url, timeout=60000); slow(2, 3.5)
                            q_added += scrape_place(page, gov, query, writer, fh, seen)
                        except Exception as ex:
                            print("    place error:", ex)
                    print(f"    -> +{q_added} reviews (total {len(seen)})")
                    mark_done(query)
                    slow(2, 5)
                except KeyboardInterrupt:
                    raise
                except Exception as ex:
                    print("    query error:", ex)
        except KeyboardInterrupt:
            print("\nStopped by user — progress saved. Re-run to resume.")
        finally:
            browser.close(); fh.close()
    print(f"\nDone for now. Saved {len(seen)} reviews -> {OUT_FILE}")


if __name__ == "__main__":
    run()