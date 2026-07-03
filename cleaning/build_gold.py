"""
Silver -> Gold builder for the Government Services ETL Platform.
Builds a star schema (fact_reviews + dim_service + dim_governorate + dim_date)
from the cleaned Silver CSV. Unifies duplicate service names and derives review_type.

    pip install pandas
    python build_gold.py
"""
import pandas as pd

SRC = "gov_reviews_silver.csv"
OUT = "."   # writes CSVs to current folder

df = pd.read_csv(SRC)

# ---------------------------------------------------------------
# 1) Unify service names (different terms for the same service)
# ---------------------------------------------------------------
service_map = {
    "إدارة المرور": "وحدة مرور",
    "مكتب توثيق الشهر العقاري": "مكتب الشهر العقاري",
    "الأحوال المدنية": "مكتب السجل المدني",
}
df["service_unified"] = df["service"].replace(service_map)
df["rev_date"] = pd.to_datetime(df["review_date_approx"], errors="coerce")

# ---------------------------------------------------------------
# 2) dim_service
# ---------------------------------------------------------------
service_info = {
    "مكتب السجل المدني":  ("Civil Registry Office",     "Civil Status"),
    "وحدة مرور":          ("Traffic Unit",              "Traffic"),
    "مكتب الشهر العقاري": ("Real Estate Notary Office", "Notarization"),
    "مكتب بريد":          ("Post Office",               "Postal"),
}
services = sorted(df["service_unified"].unique())
dim_service = pd.DataFrame({
    "service_key":      range(1, len(services) + 1),
    "service_name_ar":  services,
    "service_name_en":  [service_info[s][0] for s in services],
    "service_category": [service_info[s][1] for s in services],
})
dim_service.to_csv(f"{OUT}/dim_service.csv", index=False, encoding="utf-8-sig")
svc_lookup = dict(zip(dim_service["service_name_ar"], dim_service["service_key"]))

# ---------------------------------------------------------------
# 3) dim_governorate
# ---------------------------------------------------------------
gov_region = {
    "القاهرة":"Greater Cairo","الجيزة":"Greater Cairo","القليوبية":"Greater Cairo",
    "الإسكندرية":"Delta/Coast","البحيرة":"Delta/Coast","الدقهلية":"Delta/Coast",
    "الشرقية":"Delta/Coast","الغربية":"Delta/Coast","المنوفية":"Delta/Coast",
    "بورسعيد":"Canal","الإسماعيلية":"Canal",
    "أسيوط":"Upper Egypt","المنيا":"Upper Egypt","سوهاج":"Upper Egypt",
    "بني سويف":"Upper Egypt","الفيوم":"Upper Egypt","قنا":"Upper Egypt","أسوان":"Upper Egypt",
}
gov_en = {
    "القاهرة":"Cairo","الجيزة":"Giza","القليوبية":"Qalyubia","الإسكندرية":"Alexandria",
    "البحيرة":"Beheira","الدقهلية":"Dakahlia","الشرقية":"Sharqia","الغربية":"Gharbia",
    "المنوفية":"Monufia","بورسعيد":"Port Said","الإسماعيلية":"Ismailia",
    "أسيوط":"Asyut","المنيا":"Minya","سوهاج":"Sohag","بني سويف":"Beni Suef",
    "الفيوم":"Faiyum","قنا":"Qena","أسوان":"Aswan",
}
govs = sorted(df["governorate"].unique())
dim_gov = pd.DataFrame({
    "governorate_key":     range(1, len(govs) + 1),
    "governorate_name_ar": govs,
    "governorate_name_en": [gov_en.get(g, g) for g in govs],
    "region":              [gov_region.get(g, "Other") for g in govs],
})
dim_gov.to_csv(f"{OUT}/dim_governorate.csv", index=False, encoding="utf-8-sig")
gov_lookup = dict(zip(dim_gov["governorate_name_ar"], dim_gov["governorate_key"]))

# ---------------------------------------------------------------
# 4) dim_date (built from the actual date range in the data)
# ---------------------------------------------------------------
valid = df["rev_date"].dropna()
rng = pd.date_range(valid.min().normalize(), valid.max().normalize(), freq="D")
dim_date = pd.DataFrame({"full_date": rng})
dim_date["date_key"]    = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"]        = dim_date["full_date"].dt.year
dim_date["quarter"]     = dim_date["full_date"].dt.quarter
dim_date["month"]       = dim_date["full_date"].dt.month
dim_date["month_name"]  = dim_date["full_date"].dt.strftime("%B")
dim_date["day"]         = dim_date["full_date"].dt.day
dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek
dim_date["day_name"]    = dim_date["full_date"].dt.strftime("%A")
dim_date["year_month"]  = dim_date["full_date"].dt.strftime("%Y-%m")
dim_date = dim_date[["date_key","full_date","year","quarter","month","month_name",
                     "day","day_of_week","day_name","year_month"]]
dim_date.to_csv(f"{OUT}/dim_date.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 5) fact_reviews (grain = one row per review)
# ---------------------------------------------------------------
fact = pd.DataFrame()
fact["review_key"]      = range(1, len(df) + 1)
fact["date_key"]        = pd.to_numeric(df["rev_date"].dt.strftime("%Y%m%d"), errors="coerce").astype("Int64")
fact["service_key"]     = df["service_unified"].map(svc_lookup)
fact["governorate_key"] = df["governorate"].map(gov_lookup)
fact["rating_score"]    = df["rating"]
fact["has_rating"]      = df["has_rating"].astype(int)
fact["has_text"]        = (df["text_len"].fillna(0) > 0).astype(int)
fact["text_length"]     = df["text_len"].fillna(0).astype(int)

def rtype(has_r, has_t):
    if has_r and has_t: return "both"
    if has_r:           return "rating_only"
    return "complaint"
fact["review_type"] = [rtype(r, t) for r, t in
                       zip(df["has_rating"], df["text_len"].fillna(0) > 0)]
fact["review_id"] = df["review_id"]
fact.to_csv(f"{OUT}/fact_reviews.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("GOLD LAYER BUILT")
print(f"  dim_service ....... {len(dim_service)} rows")
print(f"  dim_governorate ... {len(dim_gov)} rows")
print(f"  dim_date .......... {len(dim_date)} rows")
print(f"  fact_reviews ...... {len(fact)} rows")
print(f"  FK nulls: date={fact['date_key'].isna().sum()} "
      f"service={fact['service_key'].isna().sum()} gov={fact['governorate_key'].isna().sum()}")
print("  review_type:")
print(fact["review_type"].value_counts().to_string())
