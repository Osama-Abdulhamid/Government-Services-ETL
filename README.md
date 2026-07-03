# 🏛️ Government Services Performance & Complaints ETL Platform

> An end-to-end cloud data platform that scrapes, processes, and analyzes real Google Maps reviews of Egyptian government offices using AI/NLP — turning thousands of scattered citizen opinions into actionable government insights.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4)
![AraBERT](https://img.shields.io/badge/NLP-AraBERT-purple)
![Streamlit](https://img.shields.io/badge/App-Streamlit-FF4B4B)
![License](https://img.shields.io/badge/License-Academic-green)

---

## 📖 Overview

Egyptian government services receive thousands of citizen reviews on Google Maps every day — but this valuable feedback is **untapped**: scattered across offices, written in Egyptian dialect, and never systematically analyzed.

This project builds a **complete ETL pipeline** that:
1. **Scrapes** 12,000+ real reviews (Playwright)
2. **Cleans & unifies** the data (Pandas, Medallion architecture)
3. **Stores** it in a cloud data warehouse (Azure SQL, star schema)
4. **Analyzes** sentiment & complaints with AI (AraBERT + ML models)
5. **Presents** insights via interactive dashboards (Streamlit + Power BI)

**Result:** Data-driven insights that tell government which services are worst, which governorates need intervention, and what citizens actually complain about.

---

## 🎯 Key Findings

| Finding | Insight |
|---------|---------|
| 🔴 **Rating Paradox** | Avg 4.2★ rating but **44.8% negative** text sentiment — ratings alone mislead |
| 🗺️ **Geographic Gap** | Upper Egypt worst (Sohag 62.9%, Qena 61.4%) vs Asyut (24.9%) |
| 👥 **#1 Complaint** | Staff shortage across **all** services (28-36%) — a structural crisis |
| 📈 **Trend** | Slowly improving: 47.6% (2018) → 40.9% (2026) |
| ✅ **Validation** | **85% agreement** with human labeling (100-review sample) |

---

## 🏗️ Architecture

```
Google Maps → Playwright → Bronze (raw CSV)
                              ↓ clean + normalize
                           Silver (cleaned)
                              ↓ star schema
                           Gold (fact + dims)
                              ↓ ADF pipeline
                        Azure SQL Warehouse
                          ↓              ↓
                    Power BI      NLP/ML Layer (AraBERT)
                    (dashboard)         ↓
                              Streamlit App (bilingual)
```

**Medallion Architecture** (Bronze → Silver → Gold) on Azure Data Lake Storage Gen2, feeding a **star schema** warehouse in Azure SQL Database, orchestrated by **Azure Data Factory**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Ingestion** | Playwright (browser automation) |
| **Data Lake** | Azure Data Lake Storage Gen2 |
| **Processing** | Pandas |
| **Warehouse** | Azure SQL Database (star schema) |
| **ETL** | Azure Data Factory |
| **NLP** | AraBERT (CAMeL-Lab) |
| **ML** | scikit-learn (TF-IDF + Logistic Regression, Isolation Forest) |
| **BI** | Power BI |
| **Web App** | Streamlit + Plotly (bilingual EN/AR) |

---

## 📊 The Data

- **12,093** reviews scraped → **10,953** after cleaning → **8,425** with Arabic text for NLP
- **18** governorates, **4** government services
- **Privacy by Design:** author names never stored, review IDs hashed, aggregated analysis only

---

## 🤖 Machine Learning

**1. Sentiment Classifier** (Knowledge Distillation from AraBERT labels)
- TF-IDF (8000 features, 1-3 grams) + Logistic Regression
- **78.9%** accuracy · 5-fold CV: 78.1% (±1.1%)

**2. Anomaly Detection** (Isolation Forest)
- Detects both **struggling** offices (need intervention) and **exemplary** ones (success models)

**3. Human Validation**
- 85% agreement with manual labeling on a random 100-review sample

---

## 📁 Project Structure

```
Government-Services-ETL/
├── scraping/          # Playwright scraper
├── data/              # Bronze / Silver / Gold layers
├── cleaning/          # Data cleaning & modeling scripts
├── sql/               # SQL DDL & queries
├── nlp_ml/            # NLP & ML scripts (01-09)
├── streamlit_app/     # Interactive bilingual dashboard
├── powerbi/           # Power BI dashboard
├── docs/              # Documentation & guides
└── diagrams/          # Architecture diagrams
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Azure account (for cloud services)

### Installation

```bash
# Clone the repository
git clone https://github.com/Osama-Abdulhamid/Government-Services-ETL.git
cd Government-Services-ETL

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the Streamlit App

```bash
cd streamlit_app
streamlit run app.py
```

The app opens at `http://localhost:8501` with 5 pages: Overview, Sentiment, Complaints, Priority & Anomaly, and Live Predict.

---

## 📈 Results & Recommendations

Based on the analysis, three actionable recommendations for government:

1. **Structural staffing crisis** → national hiring plan (staff shortage is #1 across all services)
2. **Geographic inequality** → targeted resources for Upper Egypt governorates
3. **Priority intervention list** → phased action starting with highest-priority offices

---

## ⚠️ Limitations

- Sentiment model (MSA-trained) occasionally misclassifies Egyptian dialect & negation
- Complaint categorization uses keyword matching (approximate; topic modeling planned)
- Review dates are approximate (relative dates converted)
- Single data source (Google Maps)

See full documentation in `/docs` for detailed limitations & future work.

---

## 🔮 Future Work

- **EgyBERT** for better Egyptian dialect handling
- **Apache Airflow** for pipeline orchestration
- **Azure Event Hubs** for real-time streaming
- **Docker** for containerized deployment
- **Azure OpenAI** for Arabic text-to-SQL

---

## 👤 Author

**Osama Abdulhamid**
Data Science Student, Helwan University
DEPI — Big Data Engineering (Huawei Track)

---

## 📄 License

This project is for academic purposes (graduation project).

---

*Built with ❤️ to help improve public services through data.*
