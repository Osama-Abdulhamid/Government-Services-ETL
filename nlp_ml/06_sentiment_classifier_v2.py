"""
موديل تصنيف المشاعر - نسخة محسّنة (v2).
تحسينات: class_weight balanced + TF-IDF أوسع + cross-validation.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
import joblib

# --- 1. الداتا ---
df = pd.read_csv("nlp_with_sentiment.csv")
df = df.dropna(subset=['review_text_norm', 'sentiment'])
df = df[df['review_text_norm'].astype(str).str.len() >= 3]
print(f"عدد المراجعات: {len(df)}")

X = df['review_text_norm'].astype(str)
y = df['sentiment']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# --- 2. TF-IDF محسّن ---
print("\nبنحوّل لـ TF-IDF (محسّن)...")
tfidf = TfidfVectorizer(
    max_features=8000,      # زودنا من 5000 لـ 8000
    ngram_range=(1, 3),     # كلمات مفردة + أزواج + ثلاثيات
    min_df=2,
    sublinear_tf=True,      # تحسين لتوزيع الترددات
)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)
print(f"عدد الـ features: {X_train_vec.shape[1]}")

# --- 3. موديلين محسّنين (بـ class_weight balanced) ---
models = {
    'Logistic (balanced)': LogisticRegression(
        max_iter=2000, C=2.0, class_weight='balanced'),
    'Linear SVM (balanced)': LinearSVC(
        C=1.0, class_weight='balanced', max_iter=3000),
}

best_model, best_acc, best_name = None, 0, ""
for name, model in models.items():
    print("\n" + "="*55)
    print(f"  موديل: {name}")
    print("="*55)
    model.fit(X_train_vec, y_train)
    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f"الدقّة: {acc*100:.1f}%")
    print(classification_report(y_test, preds, digits=2))
    if acc > best_acc:
        best_model, best_acc, best_name = model, acc, name

# --- 4. Cross-validation للأفضل (نتأكد الدقّة مستقرة) ---
print("\n" + "="*55)
print(f"  Cross-Validation لأفضل موديل ({best_name})")
print("="*55)
X_all_vec = tfidf.transform(X)
cv_scores = cross_val_score(best_model, X_all_vec, y, cv=5, scoring='accuracy')
print(f"دقّة الـ 5-folds: {[f'{s*100:.1f}%' for s in cv_scores]}")
print(f"المتوسط: {cv_scores.mean()*100:.1f}% (±{cv_scores.std()*100:.1f}%)")

# --- 5. نحفظ ---
joblib.dump(best_model, "sentiment_model_v2.pkl")
joblib.dump(tfidf, "tfidf_vectorizer_v2.pkl")
print(f"\n🏆 أفضل موديل: {best_name} بدقّة {best_acc*100:.1f}%")
print("✅ اتحفظ sentiment_model_v2.pkl")

# --- 6. مقارنة قبل وبعد ---
print("\n" + "="*55)
print("  📊 المقارنة:")
print("="*55)
print(f"  v1 (الأصلي):  78.7%")
print(f"  v2 (محسّن):   {best_acc*100:.1f}%")
diff = best_acc*100 - 78.7
print(f"  الفرق:        {'+' if diff>=0 else ''}{diff:.1f}%")