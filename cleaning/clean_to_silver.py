"""
Bronze -> Silver cleaning for the scraped government-services reviews.
Cleans text, normalizes Arabic, de-duplicates, parses relative Arabic dates
into approximate absolute dates, and writes a Silver-layer CSV.
    pip install pandas
    python clean_to_silver.py
"""
import pandas as pd, re
from datetime import datetime, timedelta

SRC = "gov_reviews_bronze.csv"
OUT = "gov_reviews_silver.csv"

df = pd.read_csv(SRC)
n0 = len(df)

# --- clean text ---
df['review_text'] = df['review_text'].fillna('').astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
df['text_len'] = df['review_text'].str.len()
df['has_rating'] = df['rating'].notna()

# drop rows with no usable signal (no rating AND no/too-short text)
df = df[~((~df['has_rating']) & (df['text_len'] < 5))].copy()
after_signal = len(df)

# --- Arabic normalization (for NLP) ---
HARAKAT = re.compile(r'[\u064B-\u0652\u0670]')
def normalize_ar(t):
    t = HARAKAT.sub('', t)            # remove diacritics
    t = t.replace('\u0640', '')       # remove tatweel  ـ
    t = re.sub('[إأآ]', 'ا', t)       # normalize alef
    t = t.replace('ى', 'ي')           # alef maqsura -> yaa
    t = re.sub(r'https?://\S+', '', t) # strip URLs
    return re.sub(r'\s+', ' ', t).strip()
df['review_text_norm'] = df['review_text'].map(normalize_ar)

# --- de-duplicate on normalized text ---
mask = df['review_text_norm'].str.len() > 0
dups = df[mask].duplicated(subset='review_text_norm', keep='first')
df = df.drop(index=df[mask].index[dups]).copy()
after_dedupe = len(df)

# --- service name (strip governorate suffix from the search query) ---
df['service'] = df.apply(lambda r: r['service_query'].replace(str(r['governorate']), '').strip(), axis=1)

# --- parse relative Arabic dates -> approximate absolute date ---
def parse_rel(s, ref):
    s = str(s); m = re.search(r'(\d+)', s)
    if   re.search(r'سنة|سنوات|سنتين|عام|أعوام', s): unit, dflt = 'years',  (2 if 'سنتين' in s else 1)
    elif re.search(r'شهر|أشهر|شهور', s):             unit, dflt = 'months', (2 if 'شهرين' in s else 1)
    elif re.search(r'أسبوع|أسابيع|اسبوع', s):        unit, dflt = 'weeks',  (2 if ('أسبوعين' in s or 'اسبوعين' in s) else 1)
    elif re.search(r'يوم|أيام|ايام', s):             unit, dflt = 'days',   (2 if 'يومين' in s else 1)
    elif re.search(r'ساعة|ساعات', s):                unit, dflt = 'hours',  1
    elif 'أمس' in s or 'امس' in s:                   unit, dflt, m = 'days', 1, None
    elif 'اليوم' in s or 'الآن' in s:                unit, dflt, m = 'days', 0, None
    else: return pd.NA, pd.NA
    n = int(m.group(1)) if m else dflt
    if unit == 'hours':
        d = ref - timedelta(hours=n)
    else:
        d = ref - timedelta(days={'years':365,'months':30,'weeks':7,'days':1}[unit] * n)
    return d.date().isoformat(), unit

def ref_of(row):
    try: return datetime.fromisoformat(str(row['scraped_at']))
    except Exception: return datetime(2026, 6, 29)

res = df.apply(lambda r: parse_rel(r['review_date'], ref_of(r)), axis=1, result_type='expand')
df['review_date_approx'] = res[0]; df['date_unit'] = res[1]
df = df.rename(columns={'review_date': 'review_date_raw'})

# --- final Silver schema ---
cols = ['review_id','governorate','service','service_query','rating','has_rating',
        'review_text','review_text_norm','text_len','review_date_raw','review_date_approx','date_unit','scraped_at']
silver = df[cols]
silver.to_csv(OUT, index=False, encoding='utf-8-sig')

# --- summary ---
print(f"Bronze rows ............ {n0}")
print(f"Dropped (no signal) .... {n0 - after_signal}")
print(f"Dropped (duplicates) ... {after_signal - after_dedupe}")
print(f"Silver rows ............ {len(silver)}")
print(f"Rating coverage ........ {silver['rating'].notna().sum()} ({silver['rating'].notna().mean()*100:.0f}%)")
print(f"Date parsed ............ {silver['review_date_approx'].notna().sum()} ({silver['review_date_approx'].notna().mean()*100:.0f}%)")
pdd = pd.to_datetime(silver['review_date_approx'], errors='coerce')
print(f"Date range ............. {pdd.min().date()}  ->  {pdd.max().date()}")
print("Per service:")
print(silver['service'].value_counts().to_string())