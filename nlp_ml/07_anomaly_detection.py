"""
اكتشاف الشذوذ (Anomaly Detection) للمكاتب الحكومية.
بنستخدم Isolation Forest لاكتشاف تركيبات (خدمة×محافظة) شاذة إحصائياً.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --- 1. نقرا الداتا ---
df = pd.read_csv("nlp_with_sentiment.csv")

# نوحّد الخدمات
service_map = {
    "إدارة المرور": "وحدة مرور",
    "مكتب توثيق الشهر العقاري": "مكتب الشهر العقاري",
    "الأحوال المدنية": "مكتب السجل المدني",
}
df['service_u'] = df['service'].replace(service_map)
smap = {'negative': -1, 'neutral': 0, 'positive': 1}
df['sent_num'] = df['sentiment'].map(smap)

# --- 2. نبني features لكل تركيبة خدمة×محافظة ---
grp = df.groupby(['service_u', 'governorate']).agg(
    reviews=('sent_num', 'size'),
    pct_negative=('sentiment', lambda x: (x == 'negative').mean() * 100),
    pct_positive=('sentiment', lambda x: (x == 'positive').mean() * 100),
    avg_sentiment=('sent_num', 'mean'),
    avg_rating=('rating', 'mean'),
    avg_text_len=('review_text', lambda x: x.astype(str).str.len().mean()),
).reset_index()

# نركّز على اللي عندها داتا كفاية
grp = grp[grp['reviews'] >= 20].copy().reset_index(drop=True)
print(f"عدد التركيبات (خدمة×محافظة) للتحليل: {len(grp)}")

# --- 3. نجهّز الـ features للموديل ---
feature_cols = ['pct_negative', 'pct_positive', 'avg_sentiment', 'avg_rating', 'avg_text_len']
X = grp[feature_cols].fillna(grp[feature_cols].mean())

# نعمل scaling (مهم للـ anomaly detection)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- 4. Isolation Forest ---
print("\nبنشغّل Isolation Forest...")
iso = IsolationForest(
    contamination=0.15,   # نتوقّع ~15% شاذين
    random_state=42,
    n_estimators=200,
)
grp['anomaly'] = iso.fit_predict(X_scaled)       # -1 = شاذ, 1 = طبيعي
grp['anomaly_score'] = iso.decision_function(X_scaled)  # كل ما قل = أشذ

# --- 5. النتايج ---
anomalies = grp[grp['anomaly'] == -1].sort_values('anomaly_score')
normal = grp[grp['anomaly'] == 1]

print("\n" + "="*70)
print(f"  🔴 المكاتب الشاذة إحصائياً ({len(anomalies)} من {len(grp)})")
print("="*70)
print(f"  {'الخدمة':<20}{'المحافظة':<12}{'سلبي%':>7}{'تقييم':>7}{'عدد':>6}")
print("  " + "-"*62)
for _, r in anomalies.iterrows():
    print(f"  {r['service_u']:<20}{r['governorate']:<12}{r['pct_negative']:>6.0f}%{r['avg_rating']:>7.1f}{r['reviews']:>6.0f}")

# --- 6. نفهم ليه اتصنّفوا شاذين ---
print("\n" + "="*70)
print("  📊 مقارنة: الشاذين vs الطبيعيين (المتوسطات)")
print("="*70)
comparison = pd.DataFrame({
    'الشاذين': anomalies[feature_cols].mean(),
    'الطبيعيين': normal[feature_cols].mean(),
}).round(1)
print(comparison.to_string())

# --- 7. نحفظ ---
grp.to_csv("anomaly_results.csv", index=False, encoding='utf-8-sig')
print("\n✅ اتحفظ anomaly_results.csv")