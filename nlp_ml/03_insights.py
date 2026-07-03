"""
استخراج Insights من نتايج المشاعر: ربط المشاعر بالخدمات والمحافظات.
"""
import pandas as pd

df = pd.read_csv("nlp_with_sentiment.csv")

# دالة تحسب نسبة السلبي لأي تجميعة
def sentiment_breakdown(group_col, title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)
    # نعمل جدول: كل فئة × نسبة كل شعور
    pct = pd.crosstab(df[group_col], df['sentiment'], normalize='index') * 100
    pct = pct.round(1)
    # نرتّب حسب نسبة السلبي (الأعلى أول)
    if 'negative' in pct.columns:
        pct = pct.sort_values('negative', ascending=False)
    # نضيف العدد الكلي
    pct['total_reviews'] = df.groupby(group_col).size()
    print(pct.to_string())

# 1. المشاعر حسب الخدمة
sentiment_breakdown('service', 'المشاعر حسب الخدمة (٪) — مرتبة بالأكثر سلبية')

# 2. المشاعر حسب المحافظة
sentiment_breakdown('governorate', 'المشاعر حسب المحافظة (٪) — مرتبة بالأكثر سلبية')

# 3. الأهم: التناقض بين النجوم والمشاعر
print("\n" + "="*60)
print("  🔴 التناقض: مراجعات نجوم عالية بس مشاعر سلبية")
print("="*60)
# ناخد اللي ليها rating >= 4 بس الـ sentiment سلبي
contradiction = df[(df['rating'] >= 4) & (df['sentiment'] == 'negative')]
print(f"مراجعات بـ 4-5 نجوم لكن مشاعرها سلبية: {len(contradiction)}")
print(f"دي {len(contradiction)/len(df[df['rating']>=4])*100:.1f}% من المراجعات عالية التقييم")
print("\nأمثلة:")
for _, r in contradiction.head(3).iterrows():
    print(f"  ⭐{r['rating']:.0f} بس سلبي: {str(r['review_text'])[:70]}")

# 4. حفظ ملخص للـ dashboard
summary = pd.crosstab(df['service'], df['sentiment'])
summary.to_csv("sentiment_by_service.csv", encoding='utf-8-sig')
print("\n✅ اتحفظ sentiment_by_service.csv")