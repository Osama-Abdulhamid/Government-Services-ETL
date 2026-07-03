"""
تصنيف أنواع الشكاوى: نكتشف الناس بتشتكي من إيه بالظبط.
"""
import pandas as pd

df = pd.read_csv("nlp_with_sentiment.csv")

# نركّز على المراجعات السلبية بس
neg = df[df['sentiment'] == 'negative'].copy()
print(f"عدد المراجعات السلبية: {len(neg)}")

# نعرّف فئات الشكاوى بكلماتها المفتاحية (عامية + فصحى)
topics = {
    'البطء والتأخير':      ['بطيء', 'بطء', 'تأخير', 'يطول', 'طويل', 'انتظار', 'ساعات', 'مستني', 'بطيئة', 'تاخير'],
    'سوء المعاملة':        ['معامله', 'معاملة', 'احترام', 'اخلاق', 'وقاحة', 'عصبي', 'يزعق', 'سوء', 'محترم'],
    'الزحام':              ['زحمة', 'زحام', 'زحمه', 'مزدحم', 'كتير', 'طابور', 'زحمه'],
    'قلة الموظفين':        ['موظف', 'شباك', 'شبابيك', 'عدد', 'ناقص', 'مفيش حد'],
    'الرشوة والفساد':      ['رشوة', 'رشوه', 'فلوس', 'بقشيش', 'فساد', 'واسطة', 'كسب'],
    'سوء التنظيم':         ['تنظيم', 'فوضى', 'عشوائي', 'نظام', 'ارشادات', 'مش عارف'],
    'سوء النظافة/المكان':  ['نظافة', 'وسخ', 'مكان', 'ضيق', 'قذر', 'حمام'],
}

# نعدّ كل فئة
print("\n" + "="*55)
print("  أكثر الشكاوى تكراراً (في المراجعات السلبية)")
print("="*55)

results = {}
for topic, keywords in topics.items():
    # نبحث عن أي كلمة مفتاحية في النص المنظّف
    pattern = '|'.join(keywords)
    count = neg['review_text_norm'].astype(str).str.contains(pattern, case=False, na=False).sum()
    results[topic] = count

# نرتّب ونعرض
for topic, count in sorted(results.items(), key=lambda x: -x[1]):
    pct = count / len(neg) * 100
    bar = '█' * int(pct / 2)
    print(f"{topic:20} {count:4} ({pct:4.1f}%) {bar}")

# نحفظ
pd.DataFrame(list(results.items()), columns=['topic', 'count']).to_csv(
    "complaint_topics.csv", index=False, encoding='utf-8-sig')
print("\n✅ اتحفظ complaint_topics.csv")