"""
Scrape status — what FINISHED, what you HAVE, what's MISSING.
Run it in the same folder as gov_reviews_bronze.csv and scrape_done_queries.txt
    python scrape_status.py
"""
import os
import pandas as pd

# ---- EDIT these two lists to match what you actually ran in the scraper ----
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
TARGETS = [f"{s} {g}" for s in SERVICES for g in GOVERNORATES]

CSV        = "gov_reviews_bronze.csv"
CHECKPOINT = "scrape_done_queries.txt"

# 1) WHAT FINISHED
done = set()
if os.path.exists(CHECKPOINT):
    done = {l.strip() for l in open(CHECKPOINT, encoding="utf-8") if l.strip()}
remaining = [t for t in TARGETS if t not in done]

print("=" * 56)
print("  PROGRESS  (الخطوات اللي خلصت)")
print("=" * 56)
print(f"  Targets total ..... {len(TARGETS)}")
print(f"  Finished .......... {len(done)}  ({len(done)/max(len(TARGETS),1)*100:.0f}%)")
print(f"  Remaining ......... {len(remaining)}")

# 2) WHAT YOU HAVE
if os.path.exists(CSV):
    df = pd.read_csv(CSV)
    print("\n" + "=" * 56)
    print("  DATA YOU HAVE  (الداتا اللي معاك)")
    print("=" * 56)
    print(f"  Total reviews ......... {len(df)}")
    print(f"  With rating ........... {df['rating'].notna().sum()}  ({df['rating'].notna().mean()*100:.0f}%)")
    print(f"  Governorates covered .. {df['governorate'].nunique()} / {len(GOVERNORATES)}")
    print("\n  Reviews per governorate:")
    print(df['governorate'].value_counts().to_string().replace("\n", "\n    "))
    print("\n  Reviews per service-query (top 15):")
    print(df['service_query'].value_counts().head(15).to_string().replace("\n", "\n    "))
    counts = df['service_query'].value_counts().to_dict()
    thin = [q for q in done if counts.get(q, 0) < 5]
    print(f"\n  Finished but <5 reviews (thin spots): {len(thin)}")
else:
    df = None
    print("\n  (gov_reviews_bronze.csv not found in this folder)")

# 3) WHAT'S MISSING
print("\n" + "=" * 56)
print("  MISSING  (لسه ماتكشطش)")
print("=" * 56)
for t in remaining[:40]:
    print("   -", t)
if len(remaining) > 40:
    print(f"   ... and {len(remaining) - 40} more")

# 4) VERDICT
if df is not None:
    n, g, s = len(df), df['governorate'].nunique(), df['service_query'].nunique()
    enough = (n >= 2500 and g >= 4 and s >= 6)
    print("\n" + "=" * 56)
    print("  VERDICT:", "ENOUGH to proceed ✅" if enough else "scrape a bit more first ⏳")
    print(f"  (reviews={n}, governorates={g}, service-queries={s})")
    print("=" * 56)