"""
مقارنة التصنيف اليدوي بتصنيف الموديل → الدقّة الحقيقية + تحليل الأخطاء.
"""
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

manual = pd.read_csv("validation_manual.csv")
hidden = pd.read_csv("validation_hidden.csv")

manual['my_label'] = manual['my_label'].astype(str).str.strip().str.lower()
valid_labels = ['positive', 'negative', 'neutral']

# نتأكد إن كل الصفوف اتصنّفت
unlabeled = manual[~manual['my_label'].isin(valid_labels)]
if len(unlabeled) > 0:
    print(f"⚠️ فيه {len(unlabeled)} صف مش متصنّف صح:")
    print(unlabeled[['id', 'my_label']].to_string(index=False))

merged = manual.merge(hidden, on='id')
merged = merged[merged['my_label'].isin(valid_labels)]

y_true = merged['my_label']
y_pred = merged['model_label']

# 1) الدقّة الكلية
acc = accuracy_score(y_true, y_pred)
print("="*55)
print(f"  🎯 دقّة الموديل مقابل التقييم البشري: {acc*100:.1f}%")
print(f"  (على {len(merged)} مراجعة)")
print("="*55)

# 2) تقرير مفصّل
print("\n--- الدقّة لكل فئة ---")
print(classification_report(y_true, y_pred, digits=2, zero_division=0))

# 3) Confusion Matrix
print("--- Confusion Matrix ---")
print("(الصفوف = تصنيفك، الأعمدة = الموديل)\n")
labels = ['negative', 'neutral', 'positive']
cm = confusion_matrix(y_true, y_pred, labels=labels)
cm_df = pd.DataFrame(cm, index=[f'انت:{l}' for l in labels],
                     columns=[f'موديل:{l}' for l in labels])
print(cm_df.to_string())

# 4) تحليل الأخطاء - بطريقة آمنة (نستخدم النص من الملف لو موجود)
print("\n" + "="*55)
print("  🔍 أمثلة على أخطاء الموديل (اختلف عن تقييمك)")
print("="*55)
errors = merged[merged['my_label'] != merged['model_label']].copy()
print(f"عدد الاختلافات: {len(errors)} من {len(merged)}\n")

# نجيب النص من nlp_with_sentiment.csv بدل الاعتماد على العمود
text_lookup = None
for col in ['review_text']:
    if col in manual.columns:
        text_lookup = manual.set_index('id')[col].to_dict()
        break

if text_lookup:
    for _, r in errors.head(10).iterrows():
        txt = str(text_lookup.get(r['id'], ''))[:55]
        print(f"[انت: {r['my_label']:8} | موديل: {r['model_label']:8}] {txt}")
else:
    # لو مفيش نص، نعرض الـ id بس
    print("(النص مش متاح في الملف — عرض الـ IDs بس)")
    for _, r in errors.head(10).iterrows():
        print(f"  id {r['id']:3}: انت={r['my_label']:8} | موديل={r['model_label']}")

merged.to_csv("validation_results.csv", index=False, encoding='utf-8-sig')
print(f"\n✅ اتحفظ validation_results.csv")
print(f"\n📊 الخلاصة: الموديل اتّفق مع التقييم البشري في {acc*100:.1f}% من الحالات")