"""
Insights عميقة: (1) تطوّر المشاعر عبر الزمن، (2) الشكوى الأولى لكل خدمة،
(3) مؤشر الأولوية المركّب لكل خدمة×محافظة.
"""
import pandas as pd

df = pd.read_csv("nlp_with_sentiment.csv")
df['year'] = pd.to_datetime(df['review_date_approx'], errors='coerce').dt.year

# رقم للمشاعر: سلبي=-1, محايد=0, إيجابي=+1 (عشان نحسب متوسط)
smap = {'negative': -1, 'neutral': 0, 'positive': 1}
df['sent_num'] = df['sentiment'].map(smap)

# ============================================================
# INSIGHT 1: تطوّر المشاعر عبر الزمن
# ============================================================
print("="*60)
print("  1️⃣  تطوّر المشاعر عبر السنين (هل بيتحسّن ولا بيسوء؟)")
print("="*60)

# نركّز على السنين اللي فيها داتا كفاية (>= 50 مراجعة)
by_year = df[df['year'] >= 2018].groupby('year').agg(
    reviews=('sent_num', 'size'),
    avg_sentiment=('sent_num', 'mean'),
    pct_negative=('sentiment', lambda x: (x == 'negative').mean() * 100),
).round(2)
by_year = by_year[by_year['reviews'] >= 30]
print(by_year.to_string())

# اتجاه: مقارنة أول سنة بآخر سنة
if len(by_year) >= 2:
    first_neg = by_year['pct_negative'].iloc[0]
    last_neg = by_year['pct_negative'].iloc[-1]
    trend = "ساءت ⬆️🔴" if last_neg > first_neg else "تحسّنت ⬇️🟢"
    print(f"\n  الاتجاه: نسبة السلبية {trend}")
    print(f"  من {first_neg:.1f}% ({by_year.index[0]}) إلى {last_neg:.1f}% ({by_year.index[-1]})")

# ============================================================
# INSIGHT 2: الشكوى الأولى لكل خدمة
# ============================================================
print("\n" + "="*60)
print("  2️⃣  الشكوى الأولى لكل خدمة (مشكلة كل جهة تحديداً)")
print("="*60)

topics = {
    'البطء والتأخير':      ['بطيء', 'بطء', 'تاخير', 'يطول', 'طويل', 'انتظار', 'ساعات', 'مستني', 'بطيئة'],
    'سوء المعاملة':        ['معامله', 'معاملة', 'احترام', 'اخلاق', 'وقاحة', 'عصبي', 'يزعق'],
    'الزحام':              ['زحمة', 'زحام', 'زحمه', 'مزدحم', 'طابور'],
    'قلة الموظفين':        ['موظف', 'شباك', 'شبابيك', 'عدد', 'ناقص'],
    'الرشوة والفساد':      ['رشوة', 'رشوه', 'فلوس', 'بقشيش', 'فساد', 'واسطة'],
    'سوء التنظيم':         ['تنظيم', 'فوضى', 'عشوائي', 'نظام', 'ارشادات'],
    'سوء النظافة/المكان':  ['نظافة', 'وسخ', 'مكان', 'ضيق', 'قذر', 'حمام'],
}

# نوحّد أسماء الخدمات (زي ما عملنا في الـ Gold)
service_map = {
    "إدارة المرور": "وحدة مرور",
    "مكتب توثيق الشهر العقاري": "مكتب الشهر العقاري",
    "الأحوال المدنية": "مكتب السجل المدني",
}
df['service_u'] = df['service'].replace(service_map)

neg = df[df['sentiment'] == 'negative'].copy()
for service in neg['service_u'].unique():
    sub = neg[neg['service_u'] == service]
    counts = {}
    for topic, kws in topics.items():
        pattern = '|'.join(kws)
        counts[topic] = sub['review_text_norm'].astype(str).str.contains(pattern, na=False).sum()
    top = sorted(counts.items(), key=lambda x: -x[1])[:2]
    print(f"\n  🏢 {service} ({len(sub)} شكوى):")
    for t, c in top:
        print(f"      • {t}: {c} ({c/len(sub)*100:.0f}%)")

# ============================================================
# INSIGHT 3: مؤشر الأولوية المركّب (Priority Score)
# ============================================================
print("\n" + "="*60)
print("  3️⃣  مؤشر الأولوية: المكاتب المحتاجة تدخّل عاجل")
print("="*60)

# لكل تركيبة خدمة×محافظة: نحسب درجة أولوية
grp = df.groupby(['service_u', 'governorate']).agg(
    reviews=('sent_num', 'size'),
    pct_neg=('sentiment', lambda x: (x == 'negative').mean() * 100),
).reset_index()

# نركّز على اللي عندها داتا كفاية (>= 20 مراجعة عشان يبقى ذو دلالة)
grp = grp[grp['reviews'] >= 20].copy()

# Priority Score = نسبة السلبي × لوغاريتم عدد المراجعات (عشان نوازن بين الحدة والحجم)
import numpy as np
grp['priority_score'] = (grp['pct_neg'] * np.log1p(grp['reviews'])).round(0)
grp = grp.sort_values('priority_score', ascending=False)

print("\n  🔴 أعلى 10 مكاتب أولوية للتدخّل:")
print("  " + "-"*56)
print(f"  {'الخدمة':<20}{'المحافظة':<12}{'سلبي%':>7}{'عدد':>6}{'أولوية':>8}")
print("  " + "-"*56)
for _, r in grp.head(10).iterrows():
    print(f"  {r['service_u']:<20}{r['governorate']:<12}{r['pct_neg']:>6.0f}%{r['reviews']:>6.0f}{r['priority_score']:>8.0f}")

# نحفظ كل حاجة
by_year.to_csv("sentiment_over_time.csv", encoding='utf-8-sig')
grp.to_csv("priority_scores.csv", index=False, encoding='utf-8-sig')
print("\n✅ اتحفظ: sentiment_over_time.csv + priority_scores.csv")