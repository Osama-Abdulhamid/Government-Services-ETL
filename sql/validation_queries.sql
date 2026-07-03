-- ========== dim_date ==========
CREATE TABLE dim_date (
    date_key     INT          NOT NULL PRIMARY KEY,
    full_date    DATE         NOT NULL,
    year         INT          NOT NULL,
    quarter      INT          NOT NULL,
    month        INT          NOT NULL,
    month_name   VARCHAR(20)  NOT NULL,
    day          INT          NOT NULL,
    day_of_week  INT          NOT NULL,
    day_name     VARCHAR(20)  NOT NULL,
    year_month   CHAR(7)      NOT NULL
);

-- ========== dim_service ==========
CREATE TABLE dim_service (
    service_key       INT           NOT NULL PRIMARY KEY,
    service_name_ar   NVARCHAR(100) NOT NULL,
    service_name_en   VARCHAR(100)  NOT NULL,
    service_category  VARCHAR(50)   NOT NULL
);

-- ========== dim_governorate ==========
CREATE TABLE dim_governorate (
    governorate_key      INT           NOT NULL PRIMARY KEY,
    governorate_name_ar  NVARCHAR(100) NOT NULL,
    governorate_name_en  VARCHAR(100)  NOT NULL,
    region               VARCHAR(50)   NOT NULL
);

-- ========== fact_reviews ==========
CREATE TABLE fact_reviews (
    review_key       INT           NOT NULL PRIMARY KEY,
    date_key         INT           NULL,
    service_key      INT           NOT NULL,
    governorate_key  INT           NOT NULL,
    rating_score     DECIMAL(2,1)  NULL,
    has_rating       BIT           NOT NULL,
    has_text         BIT           NOT NULL,
    text_length      INT           NOT NULL,
    review_type      VARCHAR(20)   NOT NULL,
    review_id        VARCHAR(32)   NOT NULL,
    CONSTRAINT fk_fact_date    FOREIGN KEY (date_key)        REFERENCES dim_date(date_key),
    CONSTRAINT fk_fact_service FOREIGN KEY (service_key)     REFERENCES dim_service(service_key),
    CONSTRAINT fk_fact_gov     FOREIGN KEY (governorate_key) REFERENCES dim_governorate(governorate_key)
);

-- ========== indexes ==========
CREATE INDEX ix_fact_service ON fact_reviews(service_key);
CREATE INDEX ix_fact_gov     ON fact_reviews(governorate_key);
CREATE INDEX ix_fact_date    ON fact_reviews(date_key);