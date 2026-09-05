import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import time
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة وتصميم سما كربلاء (الكحلي والذهبي)
# ==========================================
st.set_page_config(page_title="SamaKarbala Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        /* الخلفية الرئيسية للبرنامج */
        .stApp { background-color: #0f172a; direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* القائمة الجانبية (السايدبار) */
        [data-testid="stSidebar"] { background-color: #111827 !important; border-left: 1px solid #334155; }
        
        /* الكروت الإحصائية (Metrics) */
        div[data-testid="metric-container"] {
            background-color: #1e293b; 
            border: 1px solid #334155; 
            padding: 15px; 
            border-radius: 12px;
            border-top: 4px solid #cca344; /* الخط الذهبي المميز */
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: bold !important; }
        div[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 1rem !important; }
        
        /* الجداول (DataFrames) */
        [data-testid="stDataFrame"] > div { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
        
        /* الفلاتر (Expander) */
        div[data-testid="stExpander"] { background-color: #1e293b !important; border-radius: 12px; border: 1px solid #334155; }
        div[data-testid="stExpander"] summary p { color: #f8fafc !important; font-weight: bold !important; }
        
        /* أزرار التطبيق */
        div[data-testid="stFormSubmitButton"] > button, .stButton > button {
            background-color: #cca344 !important; 
            color: #ffffff !important; 
            border: none; 
            border-radius: 8px !important; 
            font-weight: bold; 
            height: 45px;
            width: 100%;
        }
        div[data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover { background-color: #b38b34 !important; }
        
        /* العناوين */
        h1, h2, h3 { color: #f8fafc !important; }
        hr { border-top: 1px solid #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# ألوان الجارتات تتناسب وية التصميم
theme_colors = ['#cca344', '#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#0ea5e9']
chart_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#334155', zeroline=False),
    margin=dict(t=40, b=10, l=10, r=10)
)

# ==========================================
# 2. الهيدر والقائمة الجانبية
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#cca344 !important;'>Sama Karbala</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = ["📍 مبيعات المحافظات", "🧊 الثلاجات", "❄️ مخازن المجزر", "📊 عام المجزر", "📦 المواد الأولية", "🛒 مشتريات المصنفات", "🔪 مشتريات المجزر"]
    choice = st.radio("الأقسام:", menu, label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 تحديث البيانات"):
        st.cache_data.clear()
        st.rerun()

st.markdown(f"<h1>{choice}</h1>", unsafe_allow_html=True)

# ==========================================
# 3. دالة السحب الذكية (بدون تعليق)
# ==========================================
@st.cache_data(ttl=300)
def fetch_data(url, skip_rows=0, find_header=False):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for _ in range(3):
        try:
            res = requests.get(url + ('&' if '?' in url else '?') + f't={time.time()}', headers=headers, timeout=12)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                df = pd.read_csv(io.StringIO(res.text), on_bad_lines='skip')
                
                # معالجة الشيتات اللي هيدرها مو بأول سطر (مثل المواد الأولية)
                if find_header:
                    cols_str = ' '.join(df.columns.astype(str))
                    if 'المادة' not in cols_str and 'الكمية' not in cols_str:
                        for idx, row in df.head(15).iterrows():
                            if 'المادة' in ' '.join(str(val) for val in row.values):
                                df.columns = df.iloc[idx]
                                df = df.iloc[idx + 1:].reset_index(drop=True)
                                break
                
                df.columns = [str(c).replace('\ufeff', '').replace('\n', '').strip() for c in df.columns]
                return df
        except Exception:
            time.sleep(1)
    return pd.DataFrame()

# ==========================================
# 4. محتوى الأقسام (الـ 7 أقسام)
# ==========================================

# ----------------- 1. مبيعات المحافظات -----------------
if choice == "📍 مبيعات المحافظات":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv")
    if not df.empty:
        c_date = next((c for c in df.columns if 'تاريخ' in c or 'date' in c.lower()), None)
        c_gov = next((c for c in df.columns if 'محافظ' in c), None)
        c_agent = next((c for c in df.columns if 'زبون' in c or 'وكيل' in c), None)
        c_ton = next((c for c in df.columns if 'طن' in c), None)
        c_qty = next((c for c in df.columns if 'عدد' in c), None)
        
        for c in [c_ton, c_qty]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("إجمالي المبيعات (طن)", f"{df[c_ton].sum():,.2f}" if c_ton else "0")
        k2.metric("إجمالي المبيعات (عدد)", f"{df[c_qty].sum():,.0f}" if c_qty else "0")
        k3.metric("الزبائن", f"{df[c_agent].nunique()}" if c_agent else "0")
        k4.metric("السجلات", f"{len(df)}")
        
        if c_gov and c_ton:
            st.markdown("---")
            fig = px.bar(df.groupby(c_gov)[c_ton].sum().reset_index().sort_values(by=c_ton), x=c_ton, y=c_gov, orientation='h', title="توزيع المحافظات")
            fig.update_traces(marker_color='#3b82f6')
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 2. الثلاجات -----------------
elif choice == "🧊 الثلاجات":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vQDphmbL58bqGdSFFFpU7NfVtAefvztGcjf5zPX8FBl5Rj3tW6H8vySo3T8CXGzyQ/pub?output=csv")
    if not df.empty:
        c_frz = next((c for c in df.columns if 'ثلاج' in c), None)
        c_prod = next((c for c in df.columns if 'نتاج' in c), None)
        c_sold = next((c for c in df.columns if 'مباع' in c or 'صادر' in c), None)
        c_short = next((c for c in df.columns if 'نقص' in c), None)
        c_final = next((c for c in df.columns if 'نهائي' in c), None)
        
        for c in [c_prod, c_sold, c_short, c_final]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("المخزون الحالي", f"{df[c_final].sum():,.0f}" if c_final else "0")
        k2.metric("الإنتاج", f"{df[c_prod].sum():,.0f}" if c_prod else "0")
        k3.metric("المباع", f"{df[c_sold].sum():,.0f}" if c_sold else "0")
        k4.metric("النقص", f"{df[c_short].sum():,.0f}" if c_short else "0")
        
        if c_frz and c_final:
            st.markdown("---")
            fig = px.bar(df.groupby(c_frz)[c_final].sum().reset_index(), x=c_frz, y=c_final, title="الأرصدة في الثلاجات")
            fig.update_traces(marker_color='#cca344')
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 3. مخازن المجزر -----------------
elif choice == "❄️ مخازن المجزر":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vQHSv4SF_rudpU2753hjWpkwyuiQ59RHr3zfiZZb43IOmdf1PZvytibN_Dc5Oxwxg/pub?output=csv")
    if not df.empty:
        c_qty = next((c for c in df.columns if 'Qty' in str(c) or 'كمية' in str(c)), None)
        c_prod = next((c for c in df.columns if 'Production' in str(c) or 'إنتاج' in str(c)), None)
        c_sold = next((c for c in df.columns if 'Sold' in str(c) or 'مباع' in str(c)), None)
        c_item = next((c for c in df.columns if 'Item Name' in str(c) or 'المادة' in str(c)), None)
        
        for c in [c_qty, c_prod, c_sold]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3 = st.columns(3)
        k1.metric("الكمية المتوفرة", f"{df[c_qty].sum():,.0f}" if c_qty else "0")
        k2.metric("الإنتاج", f"{df[c_prod].sum():,.0f}" if c_prod else "0")
        k3.metric("المباع", f"{df[c_sold].sum():,.0f}" if c_sold else "0")
        
        if c_item and c_qty:
            st.markdown("---")
            fig = px.bar(df.groupby(c_item)[c_qty].sum().reset_index().nlargest(10, c_qty), x=c_qty, y=c_item, orientation='h', title="أعلى المواد توفراً")
            fig.update_traces(marker_color='#10b981')
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 4. عام المجزر -----------------
elif choice == "📊 عام المجزر":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM4ycja48KN-96D91Ppv0CHRkIzyOBGgpAszLcOEID09N5CYspJSSsU98wvIFyQ/pub?output=csv")
    if not df.empty:
        c_item = next((c for c in df.columns if 'مادة' in c), None)
        c_bal = next((c for c in df.columns if 'الرصيد' in c and '/' not in c and '+' not in c), None)
        c_conf = next((c for c in df.columns if 'المثبت' in c and '/' not in c and '+' not in c and 'مطلوب' not in c), None)
        c_req = next((c for c in df.columns if 'مطلوب' in c), None)
        
        for c in [c_bal, c_conf, c_req]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3 = st.columns(3)
        k1.metric("إجمالي الرصيد", f"{df[c_bal].sum():,.0f}" if c_bal else "0")
        k2.metric("المثبت (قيد الوصول)", f"{df[c_conf].sum():,.0f}" if c_conf else "0")
        k3.metric("المطلوب", f"{df[c_req].sum():,.0f}" if c_req else "0")
        
        if c_item and c_bal and c_conf:
            st.markdown("---")
            top = df.nlargest(10, c_bal)
            melted = top.melt(id_vars=c_item, value_vars=[c_bal, c_conf], var_name='النوع', value_name='الكمية')
            fig = px.bar(melted, x=c_item, y='الكمية', color='النوع', barmode='group', title="الرصيد مقابل المثبت", color_discrete_map={c_bal: '#cca344', c_conf: '#3b82f6'})
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 5. المواد الأولية -----------------
elif choice == "📦 المواد الأولية":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vTyT8AIVzoC083IILST_hw5Q4j29tMBoYpdA568JyzSuJuOnX0BKq0MwOa9GE0aBQ/pub?output=csv", find_header=True)
    if not df.empty:
        c_dept = next((c for c in df.columns if 'قسم' in c), None)
        c_item = next((c for c in df.columns if 'مادة' in c and 'كود' not in c), None)
        c_qty = next((c for c in df.columns if 'كمية' in c), None)
        c_bal = next((c for c in df.columns if 'رصيد' in c and 'حالي' in c), None)
        
        for c in [c_qty, c_bal]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('-', '0'), errors='coerce').fillna(0)
            
        k1, k2, k3 = st.columns(3)
        k1.metric("إجمالي الرصيد", f"{df[c_bal].sum():,.0f}" if c_bal else "0")
        k2.metric("حركة الكميات", f"{df[c_qty].sum():,.0f}" if c_qty else "0")
        k3.metric("عدد المواد", f"{df[c_item].nunique()}" if c_item else "0")
        
        if c_dept and c_bal:
            st.markdown("---")
            fig = px.bar(df.groupby(c_dept)[c_bal].sum().reset_index(), x=c_dept, y=c_bal, title="الأرصدة حسب القسم")
            fig.update_traces(marker_color='#f59e0b')
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 6. مشتريات المصنفات -----------------
elif choice == "🛒 مشتريات المصنفات":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5lFKwIUSMCyYxRvpRMUl3PDlO6JY-x07zi0FgH9O2Atbryh4TjEpH7UGxtQ_Cw/pub?output=csv")
    if not df.empty:
        c_comp = next((c for c in df.columns if 'الشركة' in c), None)
        c_req = next((c for c in df.columns if 'المطلوب' in c), None)
        c_cur = next((c for c in df.columns if 'الرصيد' in c), None)
        c_item = next((c for c in df.columns if 'المادة' in c), None)
        
        for c in [c_req, c_cur]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3 = st.columns(3)
        k1.metric("إجمالي المطلوب", f"{df[c_req].sum():,.0f}" if c_req else "0")
        k2.metric("الرصيد الحالي", f"{df[c_cur].sum():,.0f}" if c_cur else "0")
        k3.metric("عدد الشركات", f"{df[c_comp].nunique()}" if c_comp else "0")
        
        if c_item and c_req and c_cur:
            st.markdown("---")
            top = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
            melted = top.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
            fig = px.bar(melted, x=c_item, y='الكمية', color='النوع', barmode='group', title="المطلوب مقابل الرصيد", color_discrete_map={c_req: '#ef4444', c_cur: '#10b981'})
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")

# ----------------- 7. مشتريات المجزر -----------------
elif choice == "🔪 مشتريات المجزر":
    df = fetch_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv")
    if not df.empty:
        c_comp = next((c for c in df.columns if 'شركة' in c or 'الشركة' in c), None)
        c_req = next((c for c in df.columns if 'المطلوب' in c), None)
        c_cur = next((c for c in df.columns if 'الرصيد' in c), None)
        c_item = next((c for c in df.columns if 'المادة' in c and 'تصنيف' not in c), None)
        
        for c in [c_req, c_cur]:
            if c: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            
        k1, k2, k3 = st.columns(3)
        k1.metric("المطلوب سيستم", f"{df[c_req].sum():,.0f}" if c_req else "0")
        k2.metric("الرصيد الحالي", f"{df[c_cur].sum():,.0f}" if c_cur else "0")
        k3.metric("الشركات", f"{df[c_comp].nunique()}" if c_comp else "0")
        
        if c_item and c_req and c_cur:
            st.markdown("---")
            top = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
            melted = top.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
            fig = px.bar(melted, x=c_item, y='الكمية', color='النوع', barmode='group', title="أعلى 10 مواد مطلوبة", color_discrete_map={c_req: '#ef4444', c_cur: '#10b981'})
            fig.update_layout(**chart_layout)
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("البيانات الكاملة"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("جاري سحب البيانات...")
