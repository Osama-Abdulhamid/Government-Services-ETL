"""
تحليل المشاعر (Sentiment Analysis) للمراجعات العربية باستخدام AraBERT.
الموديل: CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment
"""
import pandas as pd
import torch
from transformers import pipeline
import time

# --- 1. نتأكد من الـ GPU ---
device = 0 if torch.cuda.is_available() else -1
print(f"الجهاز: {'GPU ✅ ' + torch.cuda.get_device_name(0) if device == 0 else 'CPU'}")

# --- 2. نحمّل الموديل (بصيغة safetensors الآمنة) ---
print("\nبنحمّل موديل الـ sentiment...")
sentiment = pipeline(
    "text-classification",
    model="CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment",
    device=device,
    truncation=True,
    max_length=256,
    model_kwargs={"use_safetensors": True},
)
print("✅ الموديل جاهز")

# --- 3. نقرا الداتا ---
df = pd.read_csv("nlp_input.csv")
texts = df['review_text'].astype(str).tolist()
print(f"\nعدد المراجعات: {len(texts)}")

# --- 4. نشغّل التحليل (batch عشان السرعة) ---
print("بنحلّل... (الـ GPU هيشتغل دلوقتي)")
t0 = time.time()

results = sentiment(texts, batch_size=32)

elapsed = time.time() - t0
print(f"✅ خلص في {elapsed:.1f} ثانية ({len(texts)/elapsed:.0f} مراجعة/ثانية)")

# --- 5. نضيف النتايج للداتا ---
df['sentiment'] = [r['label'] for r in results]
df['sentiment_score'] = [round(r['score'], 3) for r in results]

# --- 6. نحفظ ---
df.to_csv("nlp_with_sentiment.csv", index=False, encoding='utf-8-sig')
print(f"\n✅ اتحفظ nlp_with_sentiment.csv")

# --- 7. نتايج سريعة ---
print("\n" + "="*50)
print("توزيع المشاعر العام:")
print("="*50)
print(df['sentiment'].value_counts().to_string())
print(f"\nكنسبة مئوية:")
print((df['sentiment'].value_counts(normalize=True)*100).round(1).to_string())

# عينة
print("\n--- عينة من النتايج ---")
for _, row in df.head(5).iterrows():
    print(f"[{row['sentiment']:8}] {str(row['review_text'])[:60]}")