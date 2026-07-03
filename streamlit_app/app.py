"""
GovInsight — Bilingual AI Analytics Dashboard
AI-Powered Citizen Feedback Intelligence Platform
"""
import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
from translations import t

# ============ PAGE CONFIG ============
st.set_page_config(page_title="GovInsight | AI Analytics", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="expanded")

if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ============ CUSTOM CSS ============
def load_css(lang):
    direction = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Cairo:wght@300;400;700&display=swap');
        html, body, [class*="css"] {{ font-family: {'Cairo' if lang=='ar' else 'Inter'}, sans-serif; }}
        .main .block-container {{ direction: {direction}; text-align: {align}; padding-top: 2rem; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .hero-title {{
            font-size: 3.2rem; font-weight: 800;
            background: linear-gradient(120deg, #6366f1, #a855f7, #ec4899, #6366f1);
            background-size: 300% 300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: shimmer 8s ease infinite; margin-bottom: 0.2rem; line-height: 1.15;
        }}
        @keyframes shimmer {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
        .hero-sub {{ color: #7d8590; font-size: 1.1rem; font-weight: 300; margin-bottom: 2rem; }}
        .kpi-card {{
            background: rgba(99,102,241,0.06); backdrop-filter: blur(12px);
            border: 1px solid rgba(99,102,241,0.2); border-radius: 20px; padding: 1.6rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4); transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
            position: relative; overflow: hidden;
        }}
        .kpi-card::before {{ content:''; position:absolute; top:0; {align}:0; width:100%; height:3px;
            background: linear-gradient(90deg, #6366f1, #ec4899); }}
        .kpi-card:hover {{ transform: translateY(-6px); border-color: rgba(99,102,241,0.6);
            box-shadow: 0 12px 40px rgba(99,102,241,0.25); }}
        .kpi-value {{ font-size: 2.3rem; font-weight: 800; color: #fff; margin: 0.3rem 0; }}
        .kpi-label {{ color: #7d8590; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; }}
        .kpi-icon {{ font-size: 1.6rem; }}
        .section-h {{ font-size: 1.4rem; font-weight: 600; color: #e6edf3;
            border-{align}: 3px solid #6366f1; padding-{align}: 0.8rem; margin: 1.5rem 0 1rem 0; }}
        .insight-box {{ background: linear-gradient(145deg, rgba(168,85,247,0.1), rgba(99,102,241,0.05));
            border: 1px solid rgba(168,85,247,0.3); border-radius: 16px;
            padding: 1.3rem 1.6rem; margin: 1.2rem 0; color: #c9d1d9; line-height: 1.7; }}
        .insight-box b {{ color: #a855f7; }}
        .caveat-box {{ background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3);
            border-radius: 12px; padding: 1rem 1.3rem; margin: 1rem 0; color: #d0d6dd; font-size: 0.9rem; }}
        section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0d1117 0%, #12161f 100%);
            border-{align}: 1px solid rgba(99,102,241,0.15); }}
    </style>""", unsafe_allow_html=True)

load_css(st.session_state.lang)
lang = st.session_state.lang

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    df = pd.read_csv("data/nlp_with_sentiment.csv")
    topics = pd.read_csv("data/complaint_topics.csv")
    priority = pd.read_csv("data/priority_scores.csv")
    anomaly = pd.read_csv("data/anomaly_results.csv")
    over_time = pd.read_csv("data/sentiment_over_time.csv")
    return df, topics, priority, anomaly, over_time

df, topics, priority, anomaly, over_time = load_data()

service_map = {"إدارة المرور": "وحدة مرور", "مكتب توثيق الشهر العقاري": "مكتب الشهر العقاري",
               "الأحوال المدنية": "مكتب السجل المدني"}
df['service_u'] = df['service'].replace(service_map)
SVC_KEY = {"مكتب السجل المدني": "svc_civil", "وحدة مرور": "svc_traffic",
           "مكتب الشهر العقاري": "svc_notary", "مكتب بريد": "svc_post"}

def svc_name(s):
    return t(SVC_KEY.get(s, ""), lang) if s in SVC_KEY else s

df['svc_label'] = df['service_u'].map(svc_name)

# Governorate english names
GOV_EN = {"القاهرة":"Cairo","الجيزة":"Giza","القليوبية":"Qalyubia","الإسكندرية":"Alexandria",
          "البحيرة":"Beheira","الدقهلية":"Dakahlia","الشرقية":"Sharqia","الغربية":"Gharbia",
          "المنوفية":"Monufia","بورسعيد":"Port Said","الإسماعيلية":"Ismailia","أسيوط":"Asyut",
          "المنيا":"Minya","سوهاج":"Sohag","بني سويف":"Beni Suef","الفيوم":"Faiyum","قنا":"Qena","أسوان":"Aswan"}
def gov_name(g):
    return GOV_EN.get(g, g) if lang == "en" else g

C_NEG, C_POS, C_NEU = '#ff4d6d', '#00e5a0', '#6c7a92'
SENT_LABEL = {'negative': t('negative', lang), 'positive': t('positive', lang), 'neutral': t('neutral', lang)}

# ============ SIDEBAR ============
st.sidebar.markdown(f"### 🏛️ **{t('app_name', lang)}**")
st.sidebar.caption(t('app_tagline', lang))

col_en, col_ar = st.sidebar.columns(2)
if col_en.button("🇬🇧 English", use_container_width=True, type="primary" if lang=="en" else "secondary"):
    st.session_state.lang = "en"; st.rerun()
if col_ar.button("🇪🇬 العربية", use_container_width=True, type="primary" if lang=="ar" else "secondary"):
    st.session_state.lang = "ar"; st.rerun()

st.sidebar.markdown("---")
pages = {"nav_overview": "◆ "+t("nav_overview", lang), "nav_sentiment": "◆ "+t("nav_sentiment", lang),
         "nav_complaints": "◆ "+t("nav_complaints", lang), "nav_priority": "◆ "+t("nav_priority", lang),
         "nav_predict": "◆ "+t("nav_predict", lang)}
page_key = st.sidebar.radio("NAV", list(pages.keys()), format_func=lambda k: pages[k], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(f"""<div style='color:#7d8590; font-size:0.85rem; line-height:2;'>
📊 <b style='color:#6366f1'>{len(df):,}</b> {t('reviews_analyzed', lang)}<br>
🏢 <b style='color:#6366f1'>{df['service_u'].nunique()}</b> {t('services', lang)}<br>
🗺️ <b style='color:#6366f1'>{df['governorate'].nunique()}</b> {t('governorates', lang)}<br>
🤖 {t('model', lang)}: <b style='color:#6366f1'>AraBERT</b></div>""", unsafe_allow_html=True)

def kpi(col, icon, value, label):
    col.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>{icon}</div>
        <p class='kpi-value'>{value}</p><p class='kpi-label'>{label}</p></div>""", unsafe_allow_html=True)

def styled_fig(fig, height=350):
    fig.update_layout(height=height, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'), margin=dict(t=20, b=20, l=20, r=40))
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    return fig

# ============ PAGE: OVERVIEW ============
if page_key == "nav_overview":
    st.markdown(f"<div class='hero-title'>{t('hero_title', lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>{t('hero_sub', lang)}</div>", unsafe_allow_html=True)

    neg_pct = (df['sentiment']=='negative').mean()*100
    pos_pct = (df['sentiment']=='positive').mean()*100
    avg_rating = df['rating'].mean()

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"📝",f"{len(df):,}",t("kpi_reviews",lang))
    kpi(c2,"😞",f"{neg_pct:.1f}%",t("kpi_negative",lang))
    kpi(c3,"😊",f"{pos_pct:.1f}%",t("kpi_positive",lang))
    kpi(c4,"⭐",f"{avg_rating:.2f}",t("kpi_rating",lang))

    st.markdown(f"<div class='insight-box'>🔍 <b>{t('key_finding',lang)}</b> {t('paradox_text',lang,r=f'{avg_rating:.2f}',n=f'{neg_pct:.0f}')}</div>", unsafe_allow_html=True)

    col1,col2 = st.columns([1,1.3])
    with col1:
        st.markdown(f"<div class='section-h'>{t('sent_dist',lang)}</div>", unsafe_allow_html=True)
        sc = df['sentiment'].value_counts()
        fig = go.Figure(go.Pie(values=sc.values, labels=[SENT_LABEL[s] for s in sc.index], hole=0.55,
            marker=dict(colors=[{'negative':C_NEG,'positive':C_POS,'neutral':C_NEU}[s] for s in sc.index]),
            textinfo='percent', textfont=dict(size=14,color='white')))
        fig.update_layout(legend=dict(orientation='h', y=-0.1))
        st.plotly_chart(styled_fig(fig), use_container_width=True)
    with col2:
        st.markdown(f"<div class='section-h'>{t('neg_by_service',lang)}</div>", unsafe_allow_html=True)
        svc = df.groupby('svc_label')['sentiment'].apply(lambda x:(x=='negative').mean()*100).sort_values()
        fig = go.Figure(go.Bar(x=svc.values, y=svc.index, orientation='h',
            marker=dict(color=svc.values, colorscale=[[0,C_POS],[1,C_NEG]]),
            text=[f'{v:.0f}%' for v in svc.values], textposition='outside', textfont=dict(color='#e6edf3')))
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    st.markdown(f"<div class='caveat-box'>⚠️ {t('overview_caveat',lang)}</div>", unsafe_allow_html=True)

# ============ PAGE: SENTIMENT ============
elif page_key == "nav_sentiment":
    st.markdown(f"<div class='hero-title'>{t('nav_sentiment',lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>{t('sent_deep_sub',lang)}</div>", unsafe_allow_html=True)

    svc_options = ["__all__"] + sorted(df['service_u'].unique().tolist())
    chosen = st.selectbox(t('filter_service',lang), svc_options,
        format_func=lambda s: t('all_services',lang) if s=="__all__" else svc_name(s))
    fdf = df if chosen=="__all__" else df[df['service_u']==chosen]

    col1,col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='section-h'>{t('sent_by_gov',lang)}</div>", unsafe_allow_html=True)
        gov = fdf.groupby('governorate')['sentiment'].apply(lambda x:(x=='negative').mean()*100).sort_values(ascending=False).head(12)
        fig = go.Figure(go.Bar(x=gov.values, y=[gov_name(g) for g in gov.index], orientation='h',
            marker=dict(color=gov.values, colorscale=[[0,C_POS],[1,C_NEG]]),
            text=[f'{v:.0f}%' for v in gov.values], textposition='outside', textfont=dict(color='#e6edf3')))
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(styled_fig(fig,420), use_container_width=True)
    with col2:
        st.markdown(f"<div class='section-h'>{t('sent_over_time',lang)}</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Scatter(x=over_time['year'], y=over_time['pct_negative'], mode='lines+markers',
            line=dict(color=C_NEG,width=3), marker=dict(size=8,color=C_NEG), fill='tozeroy',
            fillcolor='rgba(255,77,109,0.1)'))
        fig.update_xaxes(title=t('year',lang)); fig.update_yaxes(title='Negative %')
        st.plotly_chart(styled_fig(fig,420), use_container_width=True)

    first_n,last_n = over_time['pct_negative'].iloc[0], over_time['pct_negative'].iloc[-1]
    tk = 'trend_improve' if last_n<first_n else 'trend_worsen'
    st.markdown(f"<div class='insight-box'>📈 {t(tk,lang,a=f'{first_n:.0f}',b=f'{last_n:.0f}')}</div>", unsafe_allow_html=True)

# ============ PAGE: COMPLAINTS ============
elif page_key == "nav_complaints":
    st.markdown(f"<div class='hero-title'>{t('nav_complaints',lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>{t('complaints_sub',lang)}</div>", unsafe_allow_html=True)

    # ترجمة أسماء الشكاوى
    TOPIC_EN = {"قلة الموظفين":"Staff Shortage","سوء النظافة/المكان":"Poor Facilities","الزحام":"Overcrowding",
                "سوء المعاملة":"Poor Treatment","سوء التنظيم":"Disorganization","البطء والتأخير":"Delays",
                "الرشوة والفساد":"Corruption"}
    tp = topics.sort_values('count', ascending=True).copy()
    tp['label'] = tp['topic'].map(lambda x: TOPIC_EN.get(x,x)) if lang=="en" else tp['topic']

    st.markdown(f"<div class='section-h'>{t('top_complaints',lang)}</div>", unsafe_allow_html=True)
    fig = go.Figure(go.Bar(x=tp['count'], y=tp['label'], orientation='h',
        marker=dict(color=tp['count'], colorscale='Purples'),
        text=tp['count'], textposition='outside', textfont=dict(color='#e6edf3')))
    st.plotly_chart(styled_fig(fig,450), use_container_width=True)

    top_c = topics.sort_values('count',ascending=False).iloc[0]['topic']
    top_c_label = TOPIC_EN.get(top_c,top_c) if lang=="en" else top_c
    st.markdown(f"<div class='insight-box'>🔍 {t('complaint_insight',lang,c=top_c_label)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='caveat-box'>⚠️ {t('complaint_caveat',lang)}</div>", unsafe_allow_html=True)

# ============ PAGE: PRIORITY & ANOMALY ============
elif page_key == "nav_priority":
    st.markdown(f"<div class='hero-title'>{t('nav_priority',lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>{t('priority_sub',lang)}</div>", unsafe_allow_html=True)

    # toggle: أسوأ ولا أفضل
    view = st.radio(t('view_mode',lang), ["worst","best"],
        format_func=lambda v: t('view_worst',lang) if v=="worst" else t('view_best',lang),
        horizontal=True)

    if view == "worst":
        st.markdown(f"<div class='section-h'>{t('worst_list',lang)}</div>", unsafe_allow_html=True)
        pr = priority.sort_values('priority_score', ascending=False).head(10).copy()
        pr['label'] = pr.apply(lambda r: f"{svc_name(r['service_u'])} — {gov_name(r['governorate'])}", axis=1)
        fig = go.Figure(go.Bar(x=pr['priority_score'], y=pr['label'], orientation='h',
            marker=dict(color=pr['pct_neg'], colorscale=[[0,'#f59e0b'],[1,C_NEG]], showscale=True, colorbar=dict(title='Neg%')),
            text=[f"{v:.0f}%" for v in pr['pct_neg']], textposition='inside', textfont=dict(color='white')))
        fig.update_yaxes(autorange='reversed'); fig.update_xaxes(title=t('priority_score',lang))
        st.plotly_chart(styled_fig(fig,450), use_container_width=True)
    else:
        st.markdown(f"<div class='section-h'>{t('best_list',lang)}</div>", unsafe_allow_html=True)
        # درجة التميّز: نسبة الإيجابي × لوغاريتم عدد المراجعات
        import numpy as np
        pr = priority.copy()
        pr['pct_pos'] = 100 - pr['pct_neg']  # تقريب: الإيجابي مكمّل السلبي (مبسّط)
        # لو عندنا عمود pct_positive حقيقي نستخدمه، وإلا نحسب من الداتا
        pos_by = df.groupby(['service_u','governorate'])['sentiment'].apply(lambda x:(x=='positive').mean()*100).reset_index()
        pos_by.columns = ['service_u','governorate','pct_pos_real']
        pr = pr.merge(pos_by, on=['service_u','governorate'], how='left')
        pr['excellence'] = (pr['pct_pos_real'] * np.log1p(pr['reviews'])).round(0)
        pr = pr.sort_values('excellence', ascending=False).head(10)
        pr['label'] = pr.apply(lambda r: f"{svc_name(r['service_u'])} — {gov_name(r['governorate'])}", axis=1)
        fig = go.Figure(go.Bar(x=pr['excellence'], y=pr['label'], orientation='h',
            marker=dict(color=pr['pct_pos_real'], colorscale=[[0,'#84cc16'],[1,C_POS]], showscale=True, colorbar=dict(title='Pos%')),
            text=[f"{v:.0f}%" for v in pr['pct_pos_real']], textposition='inside', textfont=dict(color='#0d1117')))
        fig.update_yaxes(autorange='reversed'); fig.update_xaxes(title=t('pos_score',lang))
        st.plotly_chart(styled_fig(fig,450), use_container_width=True)
        st.markdown(f"<div class='insight-box'>🏆 {t('best_insight',lang)}</div>", unsafe_allow_html=True)

    # الشذوذ (زي ما هو)
    st.markdown(f"<div class='section-h'>{t('anomaly_title',lang)}</div>", unsafe_allow_html=True)
    an = anomaly[anomaly['anomaly']==-1].copy()
    an['svc'] = an['service_u'].map(svc_name)
    an['gov'] = an['governorate'].map(gov_name)
    an['type'] = an['pct_negative'].map(lambda x: t('anom_bad',lang) if x>=45 else t('anom_good',lang))
    show = an[['svc','gov','pct_negative','avg_rating','reviews','type']].copy()
    show['pct_negative'] = show['pct_negative'].round(1)
    show['avg_rating'] = show['avg_rating'].round(2)
    show.columns = [t('col_service',lang),t('col_gov',lang),t('col_neg',lang),t('col_rating',lang),t('col_reviews',lang),t('col_type',lang)]
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.markdown(f"<div class='insight-box'>🎯 {t('anomaly_insight',lang)}</div>", unsafe_allow_html=True)

# ============ PAGE: LIVE PREDICT ============
elif page_key == "nav_predict":
    import joblib

    @st.cache_resource
    def load_light_model():
        return joblib.load("models/sentiment_model_v2.pkl"), joblib.load("models/tfidf_vectorizer_v2.pkl")
        
    @st.cache_resource
    def load_marbert():
        try:
            from transformers import pipeline
            import torch

            device = 0 if torch.cuda.is_available() else -1

            return pipeline(
                "text-classification",
                model="Ammar-alhaj-ali/arabic-MARBERT-sentiment",
                device=device,
                truncation=True,
                max_length=256
            )

        except Exception:
            # transformers مش متثبّت في نسخة النشر
            return None
    model, vec = load_light_model()

    st.markdown(f"<div class='hero-title'>{t('predict_title',lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-sub'>{t('predict_sub',lang)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight-box'>🤖 {t('model_info',lang)}</div>", unsafe_allow_html=True)

    if "predict_text" not in st.session_state:
        st.session_state.predict_text = ""

    examples = ["الموظفين محترمين والخدمة سريعة جدا","زحمة رهيبة وانتظرت ساعتين مفيش تنظيم","المكان كويس بس محتاج موظفين اكتر"]
    st.markdown(f"**{t('try_examples',lang)}**")
    ex_cols = st.columns(3)
    for i,ex in enumerate(examples):
        if ex_cols[i].button(ex, use_container_width=True, key=f"ex{i}"):
            st.session_state.predict_text = ex; st.rerun()

    text = st.text_area(t('predict_input',lang), value=st.session_state.predict_text, height=120, placeholder="اكتب هنا...")

    if st.button("🔍 "+t('predict_btn',lang), type="primary", use_container_width=True):
        # فحص: النص عربي؟
        has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
        if not text.strip():
            st.warning(t('empty_warn',lang))
        elif not has_arabic:
            st.error(t('arabic_only',lang))
        else:
            colors = {'negative':C_NEG,'positive':C_POS,'neutral':C_NEU}
            emojis = {'negative':'😞','positive':'😊','neutral':'😐'}
            labels = {'negative':t('negative',lang),'positive':t('positive',lang),'neutral':t('neutral',lang)}
            def norm(lbl):
                l=str(lbl).lower()
                return 'negative' if 'neg' in l else ('positive' if 'pos' in l else 'neutral')

            def card(pred, conf):
                return f"""<div style='background: linear-gradient(145deg, {colors[pred]}22, {colors[pred]}11);
                    border: 2px solid {colors[pred]}; border-radius: 16px; padding: 1.5rem; text-align: center;'>
                    <div style='font-size: 3rem;'>{emojis[pred]}</div>
                    <div style='font-size: 1.5rem; font-weight: 800; color: {colors[pred]};'>{labels[pred]}</div>
                    {f"<div style='color:#7d8590;'>{t('confidence',lang)}: <b style='color:#fff'>{conf:.1f}%</b></div>" if conf else ""}
                    </div>"""

            col_a,col_b = st.columns(2)
            with col_a:
                st.markdown(f"<div class='section-h'>⚡ {t('model_light',lang)}</div>", unsafe_allow_html=True)
                st.caption(t('light_desc',lang))
                X = vec.transform([text]); pred = model.predict(X)[0]
                try: conf = max(model.predict_proba(X)[0])*100
                except Exception: conf = None
                st.markdown(card(pred,conf), unsafe_allow_html=True)
            with col_b:
                st.markdown(f"<div class='section-h'>🧠 {t('model_advanced',lang)}</div>", unsafe_allow_html=True)
                st.caption(t('advanced_desc',lang))
                try:
                    with st.spinner(t('loading_marbert',lang)):
                        marbert = load_marbert(); result = marbert(text)[0]
                    m_pred = norm(result['label']); m_conf = result['score']*100
                    st.markdown(card(m_pred,m_conf), unsafe_allow_html=True)
                    st.markdown("---")
                    if pred==m_pred: st.success(t('agree',lang))
                    else: st.warning(t('disagree',lang))
                except Exception as e:
                    st.error(t('marbert_error',lang))
                    st.caption(str(e)[:150])