import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import datetime
import time
import traceback

# ==========================================
# 1. إعدادات الصفحة والثيم (Google Finance)
# ==========================================
try:
    st.set_page_config(page_title="SamaKarbala Finance", layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass

# حقن CSS لتحويل Streamlit إلى مظهر Google Finance
st.markdown("""
    <style>
        /* الخلفية الرئيسية */
        .stApp { 
            background-color: #202124; 
            direction: rtl; 
        }
        
        /* القائمة الجانبية (Sidebar) */
        [data-testid="stSidebar"] {
            background-color: #1a1b1e !important;
            border-left: 1px solid #3c4043;
        }
        
        /* الكروت الإحصائية (Metrics) */
        div[data-testid="metric-container"] {
            background-color: #292a2d; 
            border: 1px solid #3c4043; 
            padding: 15px; 
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: 500 !important; }
        div[data-testid="stMetricLabel"] { color: #9aa0a6 !important; font-size: 0.95rem !important; }
        
        /* الجداول (DataFrames) */
        [data-testid="stDataFrame"] > div {
            background-color: #292a2d;
            border: 1px solid #3c4043;
            border-radius: 8px;
        }
        
        /* الفلاتر (Expander) */
        div[data-testid="stExpander"] {
            background-color: #292a2d !important;
            border-radius: 8px;
            border: 1px solid #3c4043;
        }
        div[data-testid="stExpander"] summary p {
            color: #e8eaed !important;
            font-weight: 500 !important;
        }
        
        /* العناوين والنصوص */
        h1, h2, h3, h4, h5, p, span {
            color: #e8eaed !important;
        }
        .finance-title { color: #8ab4f8 !important; font-weight: bold; }
        
        /* أزرار التطبيق */
        div[data-testid="stFormSubmitButton"] > button, .stButton > button {
            background-color: #8ab4f8 !important; 
            color: #202124 !important; 
            border: none; 
            border-radius: 4px !important; 
            font-weight: bold; 
            height: 45px;
        }
        div[data-testid="stFormSubmitButton"] > button:hover, .stButton > button:hover {
            background-color: #aecbfa !important;
        }
        
        hr { border-top: 1px solid #3c4043 !important; }
    </style>
""", unsafe_allow_html=True)

# إعدادات Plotly لتطابق Google Finance
gf_colors = ['#8ab4f8', '#81c995', '#f28b82', '#fde293', '#c58af9', '#f48fb1', '#78d9ec']
gf_layout = dict(
    paper_bgcolor='#292a2d',
    plot_bgcolor='#292a2d',
    font=dict(color='#e8eaed'),
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#3c4043', zeroline=False),
    margin=dict(t=40, b=10, l=10, r=10)
)

# ==========================================
# 2. دوال السحب المضادة للتعليق
# ==========================================
def fetch_sheet_csv(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for _ in range(3):
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                df = pd.read_csv(io.StringIO(res.text), on_bad_lines='skip')
                if not df.empty: return df
        except Exception: pass
        time.sleep(1)
    try: return pd.read_csv(url, on_bad_lines='skip')
    except Exception: return pd.DataFrame()

def clean_columns(df):
    df.columns = [str(c).replace('\ufeff', '').replace('\n', '').replace('\r', '').strip() for c in df.columns]
    return df

# --- دوال تحميل الأقسام الـ 7 ---
@st.cache_data(ttl=600)
def load_gov_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_date': None, 'c_gov': None, 'c_agent': None, 'c_item': None, 'c_cat': None, 'c_ff': None, 'c_label': None, 'c_ton': None, 'c_qty': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_date'] = next((c for c in df.columns if 'تاريخ' in c or 'date' in c.lower()), None)
    res['c_gov'] = next((c for c in df.columns if 'محافظ' in c), None)
    res['c_agent'] = next((c for c in df.columns if 'زبون' in c or 'وكيل' in c), None)
    res['c_item'] = next((c for c in df.columns if 'مادة' in c or 'product' in c.lower()), None)
    res['c_cat'] = 'Category' if 'Category' in df.columns else next((c for c in df.columns if 'تصنيف' in c), None)
    res['c_ff'] = next((c for c in df.columns if 'item type' in c.lower() or 'طازج' in c or 'fresh' in c.lower()), None)
    res['c_label'] = next((c for c in df.columns if 'own' in c.lower() or 'label' in c.lower()), None)
    res['c_ton'] = next((c for c in df.columns if 'طن' in c), None)
    res['c_qty'] = next((c for c in df.columns if 'عدد' in c), None)
    for c in [res['c_ton'], res['c_qty']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_freezer_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQDphmbL58bqGdSFFFpU7NfVtAefvztGcjf5zPX8FBl5Rj3tW6H8vySo3T8CXGzyQ/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_item': None, 'c_frz': None, 'c_start': None, 'c_prod': None, 'c_sold': None, 'c_short': None, 'c_final': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_item'] = next((c for c in df.columns if 'ماد' in c), None)
    res['c_frz'] = next((c for c in df.columns if 'ثلاج' in c), None)
    res['c_start'] = next((c for c in df.columns if 'رصيد' in c), None)
    res['c_prod'] = next((c for c in df.columns if 'نتاج' in c), None)
    res['c_sold'] = next((c for c in df.columns if 'مباع' in c or 'صادر' in c), None)
    res['c_short'] = next((c for c in df.columns if 'نقص' in c), None)
    res['c_final'] = next((c for c in df.columns if 'نهائي' in c), None)
    for c in [res['c_start'], res['c_prod'], res['c_sold'], res['c_short'], res['c_final']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_slh_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQHSv4SF_rudpU2753hjWpkwyuiQ59RHr3zfiZZb43IOmdf1PZvytibN_Dc5Oxwxg/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_date': None, 'c_qty': None, 'c_prev': None, 'c_prod': None, 'c_sold': None, 'c_item': None, 'c_code': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_date'] = next((c for c in df.columns if 'Date' in str(c) or 'تاريخ' in str(c)), None)
    res['c_qty'] = next((c for c in df.columns if 'Qty' in str(c) or 'كمية' in str(c)), None)
    res['c_prev'] = next((c for c in df.columns if 'Previous' in str(c) or 'رصيد' in str(c)), None)
    res['c_prod'] = next((c for c in df.columns if 'Production' in str(c) or 'إنتاج' in str(c)), None)
    res['c_sold'] = next((c for c in df.columns if 'Sold' in str(c) or 'مباع' in str(c)), None)
    res['c_item'] = next((c for c in df.columns if 'Item Name' in str(c) or 'المادة' in str(c)), None)
    res['c_code'] = next((c for c in df.columns if 'Code' in str(c) or 'كود' in str(c)), None)
    for c in [res['c_qty'], res['c_prev'], res['c_prod'], res['c_sold']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_mat_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vTyT8AIVzoC083IILST_hw5Q4j29tMBoYpdA568JyzSuJuOnX0BKq0MwOa9GE0aBQ/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_date': None, 'c_type': None, 'c_dept': None, 'c_item': None, 'c_qty': None, 'c_bal': None, 'c_cat': None}
    if df_raw.empty: return res
    cols_str = ' '.join(df_raw.columns.astype(str))
    if 'المادة' not in cols_str and 'الكمية' not in cols_str:
        header_idx = None
        for idx, row in df_raw.head(15).iterrows():
            if 'المادة' in ' '.join(str(val) for val in row.values):
                header_idx = idx
                break
        if header_idx is not None:
            df_raw.columns = df_raw.iloc[header_idx]
            df_raw = df_raw.iloc[header_idx + 1:].reset_index(drop=True)
    df = clean_columns(df_raw.copy())
    res['c_date'] = next((c for c in df.columns if 'تاريخ' in c), None)
    res['c_type'] = next((c for c in df.columns if 'نوع' in c), None)
    res['c_dept'] = next((c for c in df.columns if 'قسم' in c), None)
    res['c_item'] = next((c for c in df.columns if 'مادة' in c and 'كود' not in c), None)
    res['c_qty'] = next((c for c in df.columns if 'كمية' in c), None)
    res['c_bal'] = next((c for c in df.columns if 'رصيد' in c and 'حالي' in c), None)
    res['c_cat'] = next((c for c in df.columns if 'تصنيف' in c), None)
    for c in [res['c_qty'], res['c_bal']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('-', '0'), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_pur_cat_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5lFKwIUSMCyYxRvpRMUl3PDlO6JY-x07zi0FgH9O2Atbryh4TjEpH7UGxtQ_Cw/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_ord_date': None, 'c_comp': None, 'c_emp': None, 'c_req': None, 'c_cur': None, 'c_unit': None, 'c_item': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_ord_date'] = next((c for c in df.columns if 'تاريخ' in c), None)
    res['c_comp'] = next((c for c in df.columns if 'الشركة' in c), None)
    res['c_emp'] = next((c for c in df.columns if 'الموظف' in c), None)
    res['c_req'] = next((c for c in df.columns if 'المطلوب' in c), None)
    res['c_cur'] = next((c for c in df.columns if 'الرصيد' in c), None)
    res['c_unit'] = next((c for c in df.columns if 'الوحدة' in c), None)
    res['c_item'] = next((c for c in df.columns if 'اسم المادة' in c or 'المادة' in c), None)
    for c in [res['c_req'], res['c_cur']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_pur_slh_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_ord_date': None, 'c_comp': None, 'c_arr': None, 'c_req': None, 'c_cur': None, 'c_item': None, 'c_cat': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_ord_date'] = next((c for c in df.columns if 'تاريخ' in c), None)
    res['c_comp'] = next((c for c in df.columns if 'شركة' in c or 'الشركة' in c), None)
    res['c_arr'] = next((c for c in df.columns if 'وصول' in c or 'حالة' in c), None)
    res['c_req'] = next((c for c in df.columns if 'المطلوب' in c), None)
    res['c_cur'] = next((c for c in df.columns if 'الرصيد' in c), None)
    res['c_cat'] = next((c for c in df.columns if 'تصنيف' in c), None)
    res['c_item'] = next((c for c in df.columns if 'اسم المادة' in c or ('المادة' in c and 'تصنيف' not in c)), None)
    for c in [res['c_req'], res['c_cur']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
    res['df'] = df
    return res

@st.cache_data(ttl=600)
def load_slh_gen_data():
    df_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM4ycja48KN-96D91Ppv0CHRkIzyOBGgpAszLcOEID09N5CYspJSSsU98wvIFyQ/pub?output=csv")
    res = {'df': pd.DataFrame(), 'c_cat': None, 'c_item': None, 'c_bal': None, 'c_conf': None, 'c_req': None, 'c_cov': None}
    if df_raw.empty: return res
    df = clean_columns(df_raw.copy())
    res['c_cat'] = next((c for c in df.columns if 'تصنيف' in c), None)
    res['c_item'] = next((c for c in df.columns if 'مادة' in c), None)
    res['c_bal'] = next((c for c in df.columns if 'الرصيد' in c and '/' not in c and '+' not in c), None)
    res['c_conf'] = next((c for c in df.columns if 'المثبت' in c and '/' not in c and '+' not in c and 'مطلوب' not in c), None)
    res['c_req'] = next((c for c in df.columns if 'مطلوب' in c), None)
    res['c_cov'] = next((c for c in df.columns if 'يكفي' in c and '+' not in c), None)
    for c in [res['c_bal'], res['c_conf'], res['c_req'], res['c_cov']]:
        if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
    res['df'] = df
    return res

# دالة مختبر التحليلات المخصص لإعادة الاستخدام
def custom_analysis_lab(df, cat_cols, num_cols, key_prefix):
    st.markdown("### 🛠️ مختبر التحليلات المخصص")
    with st.form(f"form_{key_prefix}"):
        ca1, ca2 = st.columns(2)
        x_axis = ca1.selectbox("اختر حقل المقارنة (X):", cat_cols) if cat_cols else None
        y_axis = ca2.selectbox("اختر القيمة (Y):", num_cols) if num_cols else None
        submitted = st.form_submit_button("📊 رسم التحليل")
    if submitted and x_axis and y_axis:
        try:
            custom_df = df.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(15)
            fig = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis} حسب {x_axis}")
            fig.update_traces(marker_color='#8ab4f8')
            fig.update_layout(**gf_layout)
            st.plotly_chart(fig, use_container_width=True)
        except Exception: pass


# ==========================================
# 3. القائمة الجانبية (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'><span class='finance-title'>Finance</span> Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu_options = [
        "📍 مبيعات المحافظات", 
        "🧊 مخازن الثلاجات", 
        "❄️ مخازن المجزر", 
        "📊 عام المجزر",
        "📦 المواد الأولية", 
        "🛒 مشتريات المصنفات", 
        "🔪 مشتريات المجزر"
    ]
    choice = st.radio("القوائم", menu_options, label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 تحديث السحابة", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"آخر تحديث: {datetime.datetime.now().strftime('%H:%M')}")

# ==========================================
# 4. محتوى الأقسام (الصفحات)
# ==========================================
st.markdown(f"<h2>{choice}</h2>", unsafe_allow_html=True)

try:
    # ----------------- 1. مبيعات المحافظات -----------------
    if choice == "📍 مبيعات المحافظات":
        data = load_gov_data()
        df = data['df']
        if not df.empty:
            c_date, c_gov, c_agent, c_item, c_cat, c_ff, c_label, c_ton, c_qty = data['c_date'], data['c_gov'], data['c_agent'], data['c_item'], data['c_cat'], data['c_ff'], data['c_label'], data['c_ton'], data['c_qty']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("gov_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("التاريخ", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []
                    sel_gov = f2.multiselect("المحافظة", df[c_gov].unique() if c_gov and c_gov in df.columns else [])
                    sel_ff = f3.multiselect("طازج أو مجمد", df[c_ff].unique() if c_ff and c_ff in df.columns else [])
                    sel_label = f4.multiselect("العلامة التجارية", df[c_label].unique() if c_label and c_label in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_gov: df = df[df[c_gov].isin(sel_gov)]
            if sel_ff: df = df[df[c_ff].isin(sel_ff)]
            if sel_label: df = df[df[c_label].isin(sel_label)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المبيعات (طن)", f"{df[c_ton].sum():,.2f}" if c_ton and c_ton in df.columns else "0", "+0.0%")
            k2.metric("إجمالي المبيعات (عدد)", f"{df[c_qty].sum():,.0f}" if c_qty and c_qty in df.columns else "0")
            k3.metric("الزبائن والوكلاء", f"{df[c_agent].nunique()}" if c_agent and c_agent in df.columns else "0")
            k4.metric("المستندات", f"{len(df)}")
            st.markdown("---")

            try:
                pie1, pie2, pie3 = st.columns(3)
                with pie1:
                    if c_cat and c_ton and c_cat in df.columns and c_ton in df.columns:
                        fig_cat = px.pie(df.groupby(c_cat)[c_ton].sum().reset_index(), values=c_ton, names=c_cat, hole=0.5, title="التصنيف", color_discrete_sequence=gf_colors)
                        fig_cat.update_layout(**gf_layout, showlegend=False)
                        fig_cat.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_cat, use_container_width=True)
                with pie2:
                    if c_ff and c_ton and c_ff in df.columns and c_ton in df.columns:
                        fig_ff = px.pie(df.groupby(c_ff)[c_ton].sum().reset_index(), values=c_ton, names=c_ff, hole=0.5, title="طازج / مجمد", color_discrete_sequence=['#8ab4f8', '#81c995'])
                        fig_ff.update_layout(**gf_layout, showlegend=False)
                        fig_ff.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_ff, use_container_width=True)
                with pie3:
                    if c_label and c_ton and c_label in df.columns and c_ton in df.columns:
                        fig_label = px.pie(df.groupby(c_label)[c_ton].sum().reset_index(), values=c_ton, names=c_label, hole=0.5, title="العلامة التجارية", color_discrete_sequence=['#fde293', '#f28b82'])
                        fig_label.update_layout(**gf_layout, showlegend=False)
                        fig_label.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_label, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            try:
                if c_gov and c_ton and c_gov in df.columns and c_ton in df.columns:
                    fig_gov = px.bar(df.groupby(c_gov)[c_ton].sum().reset_index().sort_values(by=c_ton, ascending=True), x=c_ton, y=c_gov, orientation='h', title="توزيع المحافظات")
                    fig_gov.update_traces(marker_color='#8ab4f8')
                    fig_gov.update_layout(**gf_layout, height=450)
                    st.plotly_chart(fig_gov, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "gov")
            
            st.markdown("---")
            with st.expander("📋 عرض جدول تفاصيل المحافظات (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار أو الضغط على تحديث السحابة.")

    # ----------------- 2. مخازن الثلاجات -----------------
    elif choice == "🧊 مخازن الثلاجات":
        data = load_freezer_data()
        df = data['df']
        if not df.empty:
            c_item, c_frz, c_start, c_prod, c_sold, c_short, c_final = data['c_item'], data['c_frz'], data['c_start'], data['c_prod'], data['c_sold'], data['c_short'], data['c_final']
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("المخزون الحالي", f"{df[c_final].sum():,.0f}" if c_final and c_final in df.columns else "0")
            k2.metric("الإنتاج الداخلي", f"{df[c_prod].sum():,.0f}" if c_prod and c_prod in df.columns else "0")
            k3.metric("المباع الصادر", f"{df[c_sold].sum():,.0f}" if c_sold and c_sold in df.columns else "0")
            k4.metric("النقص أو التالف", f"{df[c_short].sum():,.0f}" if c_short and c_short in df.columns else "0")
            st.markdown("---")

            try:
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    if c_frz and c_final and c_frz in df.columns and c_final in df.columns:
                        fig_stock = px.bar(df.groupby(c_frz)[c_final].sum().reset_index().sort_values(by=c_final, ascending=False), x=c_frz, y=c_final, title="المخزون الحالي في كل ثلاجة")
                        fig_stock.update_traces(marker_color='#8ab4f8')
                        fig_stock.update_layout(**gf_layout)
                        st.plotly_chart(fig_stock, use_container_width=True)
                with row1_col2:
                    if c_frz and c_short and c_frz in df.columns and c_short in df.columns:
                        frz_short = df.groupby(c_frz)[c_short].sum().reset_index()
                        if frz_short[c_short].sum() > 0:
                            fig_short = px.pie(frz_short, values=c_short, names=c_frz, hole=0.5, title="توزيع النقص حسب الثلاجة", color_discrete_sequence=['#f28b82', '#f48fb1'])
                            fig_short.update_layout(**gf_layout, showlegend=False)
                            st.plotly_chart(fig_short, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "frz")
            st.markdown("---")
            with st.expander("📋 عرض جدول الثلاجات (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

    # ----------------- 3. مخازن المجزر -----------------
    elif choice == "❄️ مخازن المجزر":
        data = load_slh_data()
        df = data['df']
        if not df.empty:
            c_date, c_qty, c_prev, c_prod, c_sold, c_item, c_code = data['c_date'], data['c_qty'], data['c_prev'], data['c_prod'], data['c_sold'], data['c_item'], data['c_code']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("slh_form"):
                    f1, f2 = st.columns(2)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("فترة المجزر", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []
                    sel_item = f2.multiselect("المادة", df[c_item].unique() if c_item and c_item in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_item: df = df[df[c_item].isin(sel_item)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الكمية", f"{df[c_qty].sum():,.2f}" if c_qty and c_qty in df.columns else "0")
            k2.metric("إجمالي الإنتاج", f"{df[c_prod].sum():,.0f}" if c_prod and c_prod in df.columns else "0")
            k3.metric("إجمالي المباع", f"{df[c_sold].sum():,.0f}" if c_sold and c_sold in df.columns else "0")
            k4.metric("الرصيد السابق", f"{df[c_prev].sum():,.0f}" if c_prev and c_prev in df.columns else "0")
            st.markdown("---")

            try:
                pie1, pie2 = st.columns(2)
                with pie1:
                    t_prod = df[c_prod].sum() if c_prod in df.columns else 0
                    t_sold = df[c_sold].sum() if c_sold in df.columns else 0
                    if t_prod > 0 or t_sold > 0:
                        fig_pie1 = px.pie(pd.DataFrame({'العملية': ['الإنتاج', 'المباع'], 'الكمية': [t_prod, t_sold]}), values='الكمية', names='العملية', hole=0.5, title="الإنتاج مقابل المبيعات", color_discrete_sequence=['#8ab4f8', '#f28b82'])
                        fig_pie1.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_pie1, use_container_width=True)
                with pie2:
                    if c_item and c_qty and c_item in df.columns and c_qty in df.columns:
                        fig_pie2 = px.pie(df.groupby(c_item)[c_qty].sum().nlargest(5).reset_index(), values=c_qty, names=c_item, hole=0.5, title="أعلى 5 مواد متوفرة", color_discrete_sequence=gf_colors)
                        fig_pie2.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_pie2, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "slh")
            st.markdown("---")
            with st.expander("📋 عرض جدول المجزر (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

    # ----------------- 4. عام المجزر -----------------
    elif choice == "📊 عام المجزر":
        data = load_slh_gen_data()
        df = data['df']
        if not df.empty:
            c_cat, c_item, c_unit, c_bal, c_conf, c_tot, c_req, c_for, c_cov = data['c_cat'], data['c_item'], data['c_unit'], data['c_bal'], data['c_conf'], data['c_total_bal'], data['c_req'], data['c_forecast'], data['c_coverage']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("slh_gen_form"):
                    f1, f2 = st.columns(2)
                    sel_cat = f1.multiselect("التصنيف", df[c_cat].unique() if c_cat and c_cat in df.columns else [])
                    sel_item = f2.multiselect("المادة", df[c_item].unique() if c_item and c_item in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")
                    
            if sel_cat: df = df[df[c_cat].isin(sel_cat)]
            if sel_item: df = df[df[c_item].isin(sel_item)]
            
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الرصيد الفعلي", f"{df[c_bal].sum():,.0f}" if c_bal and c_bal in df.columns else "0")
            k2.metric("المثبت (قيد الوصول)", f"{df[c_conf].sum():,.0f}" if c_conf and c_conf in df.columns else "0")
            k3.metric("المطلوب تثبيته", f"{df[c_req].sum():,.0f}" if c_req and c_req in df.columns else "0")
            crit = len(df[(df[c_cov] < 7) & (df[c_cov] > 0)]) if c_cov and c_cov in df.columns else 0
            k4.metric("مواد حرجة (< 7 أيام)", str(crit))
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_cat and c_bal and c_cat in df.columns and c_bal in df.columns:
                        fig_cat = px.pie(df.groupby(c_cat)[c_bal].sum().reset_index(), values=c_bal, names=c_cat, hole=0.5, title="توزيع الرصيد حسب التصنيف", color_discrete_sequence=gf_colors)
                        fig_cat.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_cat, use_container_width=True)
                with row1_c2:
                    if c_item and c_cov and c_item in df.columns and c_cov in df.columns:
                        crit_df = df[df[c_cov] > 0].sort_values(by=c_cov, ascending=True).head(10)
                        fig_crit = px.bar(crit_df, x=c_cov, y=c_item, orientation='h', title="المواد الأكثر حرجاً (أيام)")
                        fig_crit.update_traces(marker_color='#f28b82')
                        fig_crit.update_layout(**gf_layout)
                        st.plotly_chart(fig_crit, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            try:
                if c_item and c_bal and c_conf and c_item in df.columns:
                    top_items = df.sort_values(by=c_bal, ascending=False).head(15)
                    melted = top_items.melt(id_vars=c_item, value_vars=[c_bal, c_conf], var_name='النوع', value_name='الكمية')
                    fig_comp = px.bar(melted, x=c_item, y='الكمية', color='النوع', barmode='group', title="الرصيد الفعلي مقابل المثبت", color_discrete_map={c_bal: '#8ab4f8', c_conf: '#81c995'})
                    fig_comp.update_layout(**gf_layout, legend_title_text='')
                    st.plotly_chart(fig_comp, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "slh_gen")
            st.markdown("---")
            with st.expander("📋 عرض جدول عام المجزر الشامل (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

    # ----------------- 5. المواد الأولية -----------------
    elif choice == "📦 المواد الأولية":
        data = load_mat_data()
        df = data['df']
        if not df.empty:
            c_date, c_type, c_dept, c_item, c_qty, c_bal, c_cat = data['c_date'], data['c_type'], data['c_dept'], data['c_item'], data['c_qty'], data['c_bal'], data['c_cat']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("mat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []
                    sel_dept = f2.multiselect("القسم", df[c_dept].unique() if c_dept and c_dept in df.columns else [])
                    sel_type = f3.multiselect("نوع الإذن", df[c_type].unique() if c_type and c_type in df.columns else [])
                    sel_cat = f4.multiselect("التصنيف", df[c_cat].unique() if c_cat and c_cat in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_dept: df = df[df[c_dept].isin(sel_dept)]
            if sel_type: df = df[df[c_type].isin(sel_type)]
            if sel_cat: df = df[df[c_cat].isin(sel_cat)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الرصيد الحالي", f"{df[c_bal].sum():,.0f}" if c_bal and c_bal in df.columns else "0")
            k2.metric("إجمالي الكميات للحركة", f"{df[c_qty].sum():,.0f}" if c_qty and c_qty in df.columns else "0")
            k3.metric("عدد المواد المختلفة", f"{df[c_item].nunique()}" if c_item and c_item in df.columns else "0")
            k4.metric("إجمالي السجلات", f"{len(df)}")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_dept and c_bal and c_dept in df.columns and c_bal in df.columns:
                        fig_dept = px.bar(df.groupby(c_dept)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True), x=c_bal, y=c_dept, orientation='h', title="الأرصدة الحالية حسب القسم")
                        fig_dept.update_traces(marker_color='#8ab4f8')
                        fig_dept.update_layout(**gf_layout)
                        st.plotly_chart(fig_dept, use_container_width=True)
                with row1_c2:
                    if c_cat and c_bal and c_cat in df.columns and c_bal in df.columns:
                        fig_cat_mat = px.pie(df.groupby(c_cat)[c_bal].sum().reset_index(), values=c_bal, names=c_cat, hole=0.5, title="توزيع الأرصدة حسب التصنيف", color_discrete_sequence=gf_colors)
                        fig_cat_mat.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_cat_mat, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "mat")
            st.markdown("---")
            with st.expander("📋 عرض جدول المواد الأولية (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

    # ----------------- 6. مشتريات المصنفات -----------------
    elif choice == "🛒 مشتريات المصنفات":
        data = load_pur_cat_data()
        df = data['df']
        if not df.empty:
            c_ord_date, c_comp, c_emp, c_req, c_cur, c_unit, c_item = data['c_ord_date'], data['c_comp'], data['c_emp'], data['c_req'], data['c_cur'], data['c_unit'], data['c_item']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("pur_cat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in df.columns:
                        df[c_ord_date] = pd.to_datetime(df[c_ord_date], errors='coerce')
                        valid_dates = df[c_ord_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_comp = f2.multiselect("الشركة الموردة", df[c_comp].unique() if c_comp and c_comp in df.columns else [])
                    sel_emp = f3.multiselect("الموظف المتابع", df[c_emp].unique() if c_emp and c_emp in df.columns else [])
                    sel_unit = f4.multiselect("الوحدة", df[c_unit].unique() if c_unit and c_unit in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")

            if len(date_range) == 2 and c_ord_date: df = df[(df[c_ord_date].dt.date >= date_range[0]) & (df[c_ord_date].dt.date <= date_range[1])]
            if sel_comp: df = df[df[c_comp].isin(sel_comp)]
            if sel_emp: df = df[df[c_emp].isin(sel_emp)]
            if sel_unit: df = df[df[c_unit].isin(sel_unit)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المطلوب", f"{df[c_req].sum():,.0f}" if c_req and c_req in df.columns else "0")
            k2.metric("إجمالي الرصيد الحالي", f"{df[c_cur].sum():,.0f}" if c_cur and c_cur in df.columns else "0")
            k3.metric("عدد الشركات الموردة", f"{df[c_comp].nunique()}" if c_comp and c_comp in df.columns else "0")
            k4.metric("الموظفين المتابعين", f"{df[c_emp].nunique()}" if c_emp and c_emp in df.columns else "0")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_comp and c_req and c_comp in df.columns and c_req in df.columns:
                        fig_comp = px.pie(df.groupby(c_comp)[c_req].sum().reset_index(), values=c_req, names=c_comp, hole=0.5, title="توزيع الطلبات حسب الشركة", color_discrete_sequence=gf_colors)
                        fig_comp.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_comp, use_container_width=True)
                with row1_c2:
                    if c_emp and c_req and c_emp in df.columns and c_req in df.columns:
                        fig_emp = px.bar(df.groupby(c_emp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=True), x=c_req, y=c_emp, orientation='h', title="حجم متابعة الطلبات لكل موظف")
                        fig_emp.update_traces(marker_color='#8ab4f8')
                        fig_emp.update_layout(**gf_layout)
                        st.plotly_chart(fig_emp, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            try:
                if c_item and c_req and c_cur and c_item in df.columns:
                    melted_items = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index().melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                    fig_compare = px.bar(melted_items, x=c_item, y='الكمية', color='النوع', barmode='group', title="مقارنة: المطلوب مقابل الرصيد لأعلى 10 مواد", color_discrete_map={c_req: '#f28b82', c_cur: '#8ab4f8'})
                    fig_compare.update_layout(**gf_layout, legend_title_text='')
                    st.plotly_chart(fig_compare, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "pur_cat")
            st.markdown("---")
            with st.expander("📋 عرض السجل الكامل لمشتريات المصنفات (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

    # ----------------- 7. مشتريات المجزر -----------------
    elif choice == "🔪 مشتريات المجزر":
        data = load_pur_slh_data()
        df = data['df']
        if not df.empty:
            c_ord_date, c_comp, c_arr, c_req, c_cur, c_cat, c_item = data['c_ord_date'], data['c_comp'], data['c_arr'], data['c_req'], data['c_cur'], data['c_cat'], data['c_item']
            
            with st.expander("🔍 الفلاتر", expanded=True):
                with st.form("pur_slh_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in df.columns:
                        df[c_ord_date] = pd.to_datetime(df[c_ord_date], errors='coerce')
                        valid_dates = df[c_ord_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_comp = f2.multiselect("الشركة الموردة", df[c_comp].unique() if c_comp and c_comp in df.columns else [])
                    sel_cat = f3.multiselect("تصنيف المادة", df[c_cat].unique() if c_cat and c_cat in df.columns else [])
                    sel_arr = f4.multiselect("حالة التوريد", df[c_arr].unique() if c_arr and c_arr in df.columns else [])
                    st.form_submit_button("تطبيق 🚀")

            if len(date_range) == 2 and c_ord_date: df = df[(df[c_ord_date].dt.date >= date_range[0]) & (df[c_ord_date].dt.date <= date_range[1])]
            if sel_comp: df = df[df[c_comp].isin(sel_comp)]
            if sel_cat: df = df[df[c_cat].isin(sel_cat)]
            if sel_arr: df = df[df[c_arr].isin(sel_arr)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المطلوب سيستم", f"{df[c_req].sum():,.0f}" if c_req and c_req in df.columns else "0")
            k2.metric("إجمالي الرصيد الحالي", f"{df[c_cur].sum():,.0f}" if c_cur and c_cur in df.columns else "0")
            k3.metric("عدد الشركات", f"{df[c_comp].nunique()}" if c_comp and c_comp in df.columns else "0")
            k4.metric("عدد التصنيفات", f"{df[c_cat].nunique()}" if c_cat and c_cat in df.columns else "0")
            st.markdown("---")
                    
            try:
                row2_c1, row2_c2 = st.columns(2)
                with row2_c1:
                    if c_item and c_req and c_cur and c_item in df.columns:
                        top_slh_items = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
                        melted_slh = top_slh_items.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                        fig_comp_slh = px.bar(melted_slh, x='الكمية', y=c_item, color='النوع', orientation='h', barmode='group', title="أعلى 10 مواد: (المطلوب) مقابل (الرصيد)", color_discrete_map={c_req: '#f28b82', c_cur: '#81c995'})
                        fig_comp_slh.update_layout(**gf_layout, legend_title_text='')
                        st.plotly_chart(fig_comp_slh, use_container_width=True)

                with row2_c2:
                    if c_comp and c_req and c_comp in df.columns:
                        comp_perf = df.groupby(c_comp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=False).head(10)
                        fig_comp_bar = px.bar(comp_perf, x=c_comp, y=c_req, title="أعلى 10 شركات موردة")
                        fig_comp_bar.update_traces(marker_color='#8ab4f8')
                        fig_comp_bar.update_layout(**gf_layout)
                        st.plotly_chart(fig_comp_bar, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            custom_analysis_lab(df, [c for c in df.columns if df[c].dtype == 'object'], [c for c in df.columns if df[c].dtype != 'object'], "pur_slh")
            st.markdown("---")
            with st.expander("📋 عرض السجل الكامل لمشتريات المجزر (Raw)"):
                st.dataframe(df.head(150), use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار.")

except Exception as e:
    st.error("🚨 النظام اكتشف خطأ غير متوقع. يرجى مسح الذاكرة من القائمة الجانبية.")
    st.code(traceback.format_exc())
