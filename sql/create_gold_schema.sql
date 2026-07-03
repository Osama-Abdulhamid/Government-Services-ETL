/* =====================================================================
   Gold Layer — Star Schema DDL
   Government Services Performance & Complaints ETL Platform
   Target: Azure SQL Database
   ---------------------------------------------------------------------
   Grain of fact_reviews = ONE ROW PER REVIEW.
   Design note: the original proposal modeled two facts (ratings +
   complaints with resolution_time / reopen_count). After profiling the
   real source (Google Maps reviews), the true grain is "a review",
   which carries an optional star rating and optional free text — there
   is no complaint-resolution lifecycle in the data. The unified
   fact_reviews avoids empty NULL columns and stays a clean star schema.
   A review_type column ('both' / 'rating_only' / 'complaint') preserves
   the ability to analyze text-only complaints separately.
   ===================================================================== */

/* ---------- Dimension: Date ---------- */
CREATE TABLE dim_date (
    date_key     INT          NOT NULL PRIMARY KEY,   -- yyyymmdd
    full_date    DATE         NOT NULL,
    year         INT          NOT NULL,
    quarter      INT          NOT NULL,
    month        INT          NOT NULL,
    month_name   VARCHAR(20)  NOT NULL,
    day          INT          NOT NULL,
    day_of_week  INT          NOT NULL,               -- 0=Mon .. 6=Sun
    day_name     VARCHAR(20)  NOT NULL,
    year_month   CHAR(7)      NOT NULL                 -- yyyy-mm
);

/* ---------- Dimension: Service ---------- */
CREATE TABLE dim_service (
    service_key       INT           NOT NULL PRIMARY KEY,
    service_name_ar   NVARCHAR(100) NOT NULL,          -- NVARCHAR for Arabic
    service_name_en   VARCHAR(100)  NOT NULL,
    service_category  VARCHAR(50)   NOT NULL
);

/* ---------- Dimension: Governorate ---------- */
CREATE TABLE dim_governorate (
    governorate_key      INT           NOT NULL PRIMARY KEY,
    governorate_name_ar  NVARCHAR(100) NOT NULL,
    governorate_name_en  VARCHAR(100)  NOT NULL,
    region               VARCHAR(50)   NOT NULL
);

/* ---------- Fact: Reviews ---------- */
CREATE TABLE fact_reviews (
    review_key       INT           NOT NULL PRIMARY KEY,
    date_key         INT           NULL,               -- FK -> dim_date
    service_key      INT           NOT NULL,           -- FK -> dim_service
    governorate_key  INT           NOT NULL,           -- FK -> dim_governorate
    rating_score     DECIMAL(2,1)  NULL,               -- 2.0..5.0, NULL = no stars
    has_rating       BIT           NOT NULL,
    has_text         BIT           NOT NULL,
    text_length      INT           NOT NULL,
    review_type      VARCHAR(20)   NOT NULL,           -- both / rating_only / complaint
    review_id        VARCHAR(32)   NOT NULL,           -- audit link back to Silver

    CONSTRAINT fk_fact_date    FOREIGN KEY (date_key)        REFERENCES dim_date(date_key),
    CONSTRAINT fk_fact_service FOREIGN KEY (service_key)     REFERENCES dim_service(service_key),
    CONSTRAINT fk_fact_gov     FOREIGN KEY (governorate_key) REFERENCES dim_governorate(governorate_key)
);

/* ---------- Helpful indexes for dashboard queries ---------- */
CREATE INDEX ix_fact_service ON fact_reviews(service_key);
CREATE INDEX ix_fact_gov     ON fact_reviews(governorate_key);
CREATE INDEX ix_fact_date    ON fact_reviews(date_key);
