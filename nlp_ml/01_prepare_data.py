"""
تجهيز الداتا للـ NLP: ناخد المراجعات اللي فيها نص عربي.
"""
import pandas as pd

# اقرا الـ Silver (المسار الصح)
df = pd.read_csv("../data/2-silver/gov_reviews_silver.csv")
print(f"إجمالي الصفوف: {len(df)}")

# ناخد بس اللي فيها نص عربي (text_len > 0)
df_text = df[df['text_len'].fillna(0) > 0].copy()
print(f"المراجعات اللي فيها نص: {len(df_text)}")

# نشيل أي نص قصير جداً (أقل من 3 حروف - مش مفيد للتحليل)
df_text = df_text[df_text['review_text_norm'].astype(str).str.len() >= 3].copy()
print(f"بعد شيل النصوص القصيرة جداً: {len(df_text)}")

# review_type: نحسبه (both / complaint / rating_only)
df_text['review_type'] = df_text.apply(
    lambda r: 'both' if (r['has_rating'] and r['text_len'] > 0)
    else ('complaint' if r['text_len'] > 0 else 'rating_only'), axis=1)

# نحفظ ملف مخصّص للـ NLP
cols = ['review_id', 'governorate', 'service', 'rating', 'has_rating',
        'review_text', 'review_text_norm', 'review_type', 'review_date_approx']
df_text[[c for c in cols if c in df_text.columns]].to_csv(
    "nlp_input.csv", index=False, encoding='utf-8-sig')

print(f"\n✅ اتحفظ nlp_input.csv بـ {len(df_text)} مراجعة")

# عينة من النصوص للتأكد
print("\n--- عينة من النصوص ---")
for i, txt in enumerate(df_text['review_text'].head(3), 1):
    print(f"{i}. {str(txt)[:80]}")

# توزيع النوع
print("\n--- توزيع review_type ---")
print(df_text['review_type'].value_counts().to_string())