# Gold Layer — Star Schema

**Project:** Government Services Performance & Complaints ETL Platform
**Layer:** Gold (curated, dashboard-ready)
**Built from:** `gov_reviews_silver.csv` (10,953 rows)

---

## Files in this package

| File | Rows | Purpose |
|------|------|---------|
| `fact_reviews.csv` | 10,953 | Fact table — one row per review |
| `dim_service.csv` | 4 | Service dimension (Arabic + English + category) |
| `dim_governorate.csv` | 18 | Governorate dimension (+ region grouping) |
| `dim_date.csv` | 5,111 | Date dimension (2012-07-03 → 2026-06-30) |
| `create_gold_schema.sql` | — | DDL for Azure SQL Database |
| `build_gold.py` | — | The script that builds all tables from Silver |

---

## The grain (most important design decision)

**`fact_reviews` grain = ONE ROW PER REVIEW.**

Each Google Maps review carries an *optional* star rating and *optional*
free text. So a single fact row holds both signals.

### Why one fact, not two (a change from the proposal)

The original proposal modeled two fact tables:
- `fact_service_ratings` (rating_score, wait_time)
- `fact_complaints` (resolution_time, is_resolved, reopen_count)

After profiling the **real** source data, the complaint-lifecycle measures
(`resolution_time`, `is_resolved`, `reopen_count`) **do not exist** in
Google Maps reviews — a review is a citizen's opinion, not a tracked
support ticket. Modeling them would produce a fact table with permanently
empty columns.

**Decision:** unify into a single `fact_reviews`. This:
- matches the true grain of the data (a review),
- avoids empty NULL measure columns,
- remains a clean, valid Kimball star schema,
- is simpler to query in Power BI.

A `review_type` column (`both` / `rating_only` / `complaint`) preserves the
ability to slice text-only complaints separately — keeping the spirit of the
proposal's two-fact split without the empty columns.

> **For the defense:** "The proposal assumed formal complaint data with a
> resolution lifecycle. After data profiling the actual source, I found the
> real grain is a *review*, so I evolved the design to reflect the data
> honestly. This is standard practice — the model follows the data."

---

## Service unification

Seven scraped service labels were merged into 4 real services in `dim_service`:

| Unified service | Merged from |
|-----------------|-------------|
| مكتب السجل المدني (Civil Registry) | + الأحوال المدنية |
| وحدة مرور (Traffic Unit) | + إدارة المرور |
| مكتب الشهر العقاري (Real Estate Notary) | + مكتب توثيق الشهر العقاري |
| مكتب بريد (Post Office) | — |

---

## Known data characteristics (be ready to explain these)

- **Rating coverage = 75%.** 2,777 reviews are text-only (no stars). These
  are flagged `review_type = 'complaint'` and `has_rating = 0`.
- **No 1-star ratings exist** in the source. Ratings range 2.0–5.0. Angry
  feedback tends to appear as text-only reviews (the nulls), not 1-star.
  This is a real property of the data, not a bug — worth stating openly.
- **Dates are approximate.** Google Maps shows relative dates ("منذ سنتين")
  which were converted to absolute dates in the Silver layer. Treat the
  day/month as approximate; year-level analysis is reliable.
- **place_name is empty.** The scraper grain is `service_query`, so
  individual office names were not captured. Analysis is at the
  service × governorate level.

---

## review_type breakdown

| review_type | count | meaning |
|-------------|-------|---------|
| both | 5,662 | has a rating AND text |
| complaint | 2,777 | text only, no stars |
| rating_only | 2,514 | stars only, no text |

---

## Next steps

1. ✅ Gold layer built (you are here)
2. ⬜ Create Azure resources (Resource Group, ADLS Gen2, Azure SQL)
3. ⬜ Upload these CSVs to ADLS Gen2 Gold zone
4. ⬜ Run `create_gold_schema.sql` in Azure SQL, load the CSVs
5. ⬜ Connect Power BI, build the star schema model + first KPI
