"""
تجهيز عيّنة للـ validation اليدوي.
بياخد 100 مراجعة عشوائية، ويحطها في ملف للتصنيف اليدوي (بدون إظهار تقييم الموديل).
"""
import pandas as pd

# اقرا نتايج الموديل
df = pd.read_csv("nlp_with_sentiment.csv")

# ناخد عيّنة عشوائية 100 مراجعة (نص واضح، مش قصير جداً)
df_valid = df[df['review_text'].astype(str).str.len() >= 15].copy()
sample = df_valid.sample(n=100, random_state=42).reset_index(drop=True)

# نحفظ نسختين:
# 1) نسخة للتصنيف اليدوي (بدون تقييم الموديل - عشان الحياد)
manual = pd.DataFrame({
    'id': range(1, 101),
    'review_text': sample['review_text'],
    'my_label': '',   # هتملأها إنت: positive / negative / neutral
})
manual.to_csv("validation_manual.csv", index=False, encoding='utf-8-sig')

# 2) نسخة مخفية فيها تقييم الموديل (للمقارنة بعدين)
hidden = pd.DataFrame({
    'id': range(1, 101),
    'model_label': sample['sentiment'],
    'model_score': sample['sentiment_score'],
})
hidden.to_csv("validation_hidden.csv", index=False, encoding='utf-8-sig')

print("✅ اتعمل ملفين:")
print("   - validation_manual.csv  (اللي هتصنّف فيه بإيدك)")
print("   - validation_hidden.csv  (تقييم الموديل - متفتحوش دلوقتي!)")
print(f"\nعدد المراجعات: {len(sample)}")
print("\n📝 دلوقتي: افتح validation_manual.csv واملأ عمود my_label")
print("   بـ positive / negative / neutral لكل مراجعة")