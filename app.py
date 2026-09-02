import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import datetime
import time
import traceback

# ==========================================
# 1. إعدادات الصفحة واللغة
# ==========================================
try:
    st.set_page_config(page_title="FMCG Dashboard - PS Edition", layout="wide")
except Exception:
    pass

st.markdown("""
    <style>
        /* =========================================
           🎮 خلفية البلي ستيشن الهادئة والعميقة (PS Vibe)
           ========================================= */
        .stApp { 
            background: radial-gradient(circle at 50% 120%, #0f4c81 0%, #03142e 50%, #01060e 100%) !important;
            background-attachment: fixed !important;
            color: #e2e8f0; 
            direction: rtl; 
        }
        
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] { 
            text-align: right; 
        }

        /* =========================================
           🚀 1. التابات (الأقسام العلوية)
           ========================================= */
        div.row-widget.stRadio > div {
            display: flex; flex-direction: row; justify-content: center; gap: 15px;
            background-color: transparent; padding: 20px 10px; flex-wrap: wrap;
        }
        div.stRadio > div[role="radiogroup"] > label {
            background-color: rgba(30, 41, 59, 0.8) !important; border: 1px solid #334155 !important;
            padding: 12px 20px !important; border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            cursor: pointer !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }
        div.stRadio > div[role="radiogroup"] > label > div:first-child { display: none !important; }
        
        div.stRadio > div[role="radiogroup"] > label:hover {
            transform: scale(1.15) translateY(-5px) !important;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            border-color: #93c5fd !important;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.5) !important; z-index: 10 !important;
        }
        div.stRadio > div[role="radiogroup"] > label:hover p { color: #ffffff !important; font-weight: 900 !important; }
        
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            transform: scale(1.05) !important; border-color: #34d399 !important;
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4) !important;
        }
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] p { color: #ffffff !important; font-weight: bold !important; }

        /* =========================================
           🚀 2. الكروت الإحصائية (Metrics)
           ========================================= */
        div[data-testid="metric-container"] {
            background-color: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid #334155;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-8px) scale(1.05);
            background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.9)) !important;
            box-shadow: 0 15px 30px rgba(56, 189, 248, 0.4);
            border-color: #38bdf8;
            z-index: 5;
        }

        /* =========================================
           🚀 3. الرسوم البيانية (Charts)
           ========================================= */
        .stPlotlyChart {
            background-color: rgba(30, 41, 59, 0.4) !important;
            border-radius: 16px;
            padding: 15px;
            border: 1px solid #334155;
            transition: all 0.4s ease;
        }
        .stPlotlyChart:hover {
            transform: scale(1.03) translateY(-5px);
            background-color: rgba(30, 41, 59, 0.8) !important;
            box-shadow: 0 15px 30px rgba(139, 92, 246, 0.3);
            border-color: #a78bfa;
            z-index: 5;
        }

        /* =========================================
           🚀 4. الفلاتر والقوائم المنسدلة (Selectboxes)
           ========================================= */
        div[data-baseweb="select"] > div, input {
            transition: all 0.3s ease;
            border-radius: 10px !important;
            background-color: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid #475569 !important;
        }
        div[data-baseweb="select"] > div:hover, input:hover {
            transform: scale(1.03);
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4) !important;
            border-color: #34d399 !important;
        }

        /* =========================================
           🚀 5. القوائم المطوية (Expanders)
           ========================================= */
        div[data-testid="stExpander"] {
            background-color: rgba(30, 41, 59, 0.5) !important;
            border-radius: 12px;
            border: 1px solid #334155;
            transition: all 0.3s ease;
        }
        div[data-testid="stExpander"]:hover {
            transform: translateY(-3px) scale(1.01);
            background-color: rgba(30, 41, 59, 0.8) !important;
            box-shadow: 0 10px 20px rgba(245, 158, 11, 0.2);
            border-color: #fbbf24;
        }

        /* =========================================
           🚀 6. الجداول (Dataframes)
           ========================================= */
        div[data-testid="stDataFrame"] {
            transition: all 0.3s ease;
        }
        div[data-testid="stDataFrame"]:hover {
            transform: scale(1.01);
            box-shadow: 0 10px 25px rgba(255, 255, 255, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. رأس الصفحة، حالة النظام، وزر التحديث
# ==========================================
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("🎮 نظام إدارة المبيعات والمخازن | FMCG")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🔵 حالة النظام: PS Interactive Mode | النسخة الكلاسيكية | آخر تحديث: {current_time}")
with col_btn:
    st.write("") 
    if st.button("🔄 تحديث البيانات (Sync)", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ==========================================
# 3. شريط التابات (نظام البلي ستيشن)
# ==========================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'gov'

tabs_dict = {
    "📍 المحافظات": "gov",
    "🧊 الثلاجات": "frz",
    "❄️ مخازن المجزر": "slh",
    "📊 عام المجزر": "slh_gen",
    "📦 المواد الأولية": "mat",
    "🛒 مشتريات المصنفات": "pur_cat",
    "🔪 مشتريات المجزر": "pur_slh"
}

selected_tab_name = st.radio(
    "اختر القسم:",
    list(tabs_dict.keys()),
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.active_tab = tabs_dict[selected_tab_name]

st.markdown("---")

# ==========================================
# 4. دوال سحب البيانات (المحرك المضمون الأصلي)
# ==========================================
def fetch_sheet_csv(url):
    try:
        return pd.read_csv(url, on_bad_lines='skip')
    except Exception:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                return pd.read_csv(io.StringIO(res.text), on_bad_lines='skip')
            else:
                return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

@st.cache_data(ttl=600)
def load_slh_general_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM4ycja48KN-96D91Ppv0CHRkIzyOBGgpAszLcOEID09N5CYspJSSsU98wvIFyQ/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame()
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_gov_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None, None, None
        
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        col_date = next((c for c in df.columns if 'تاريخ' in c or 'date' in c.lower()), None)
        col_gov = next((c for c in df.columns if 'محافظ' in c), None)
        col_agent = next((c for c in df.columns if 'زبون' in c or 'وكيل' in c), None)
        col_item = next((c for c in df.columns if 'مادة' in c or 'product' in c.lower()), None)
        col_cat = 'Category' if 'Category' in df.columns else next((c for c in df.columns if 'تصنيف' in c), None)
        col_ff = next((c for c in df.columns if 'item type' in c.lower() or 'طازج' in c or 'fresh' in c.lower()), None)
        col_label = next((c for c in df.columns if 'own' in c.lower() or 'label' in c.lower()), None)
        col_ton = next((c for c in df.columns if 'طن' in c), None)
        col_qty = next((c for c in df.columns if 'عدد' in c), None)

        if col_date: df[col_date] = pd.to_datetime(df[col_date], errors='coerce')
        for c in [col_ton, col_qty]:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
        for c in [col_gov, col_agent, col_item, col_cat, col_ff, col_label]:
            if c and c in df.columns: df[c] = df[c].fillna('غير مصنف')
                
        return df, col_date, col_gov, col_agent, col_item, col_cat, col_ff, col_label, col_ton, col_qty
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_freezer_data():
    url_freezer = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDphmbL58bqGdSFFFpU7NfVtAefvztGcjf5zPX8FBl5Rj3tW6H8vySo3T8CXGzyQ/pub?output=csv"
    try:
        df = fetch_sheet_csv(url_freezer)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None
        
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        col_item = next((c for c in df.columns if 'ماد' in c), None)
        col_frz = next((c for c in df.columns if 'ثلاج' in c), None)
        col_start = next((c for c in df.columns if 'رصيد' in c), None)
        col_prod = next((c for c in df.columns if 'نتاج' in c), None)
        col_sold = next((c for c in df.columns if 'مباع' in c or 'صادر' in c), None)
        col_short = next((c for c in df.columns if 'نقص' in c), None)
        col_final = next((c for c in df.columns if 'نهائي' in c), None)
        
        num_cols = [col_start, col_prod, col_sold, col_short, col_final]
        for c in num_cols:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
        if col_item and col_item in df.columns: df[col_item] = df[col_item].fillna('غير مصنف')
        if col_frz and col_frz in df.columns: df[col_frz] = df[col_frz].fillna('غير مصنف')
        
        return df, col_item, col_frz, col_start, col_prod, col_sold, col_short, col_final
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_slaughterhouse_data():
    url_slh = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQHSv4SF_rudpU2753hjWpkwyuiQ59RHr3zfiZZb43IOmdf1PZvytibN_Dc5Oxwxg/pub?output=csv"
    try:
        df = fetch_sheet_csv(url_slh)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None
        
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        col_date = next((c for c in df.columns if 'Date' in str(c) or 'تاريخ' in str(c)), None)
        col_qty = next((c for c in df.columns if 'Qty' in str(c) or 'كمية' in str(c)), None)
        col_prev = next((c for c in df.columns if 'Previous' in str(c) or 'رصيد' in str(c)), None)
        col_prod = next((c for c in df.columns if 'Production' in str(c) or 'إنتاج' in str(c)), None)
        col_sold = next((c for c in df.columns if 'Sold' in str(c) or 'مباع' in str(c)), None)
        col_item = next((c for c in df.columns if 'Item Name' in str(c) or 'المادة' in str(c)), None)
        col_code = next((c for c in df.columns if 'Code' in str(c) or 'كود' in str(c)), None)
        
        if col_date: df[col_date] = pd.to_datetime(df[col_date], errors='coerce')
        for c in [col_qty, col_prev, col_prod, col_sold]:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
        if col_item and col_item in df.columns: df[col_item] = df[col_item].fillna('غير مصنف')
        
        return df, col_date, col_qty, col_prev, col_prod, col_sold, col_item, col_code
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_raw_materials_data():
    url_mat = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTyT8AIVzoC083IILST_hw5Q4j29tMBoYpdA568JyzSuJuOnX0BKq0MwOa9GE0aBQ/pub?output=csv"
    try:
        df = fetch_sheet_csv(url_mat)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None
        
        cols_str = ' '.join(df.columns.astype(str))
        if 'المادة' not in cols_str and 'الكمية' not in cols_str:
            header_idx = None
            for idx, row in df.head(15).iterrows():
                row_str = ' '.join(str(val) for val in row.values)
                if 'المادة' in row_str or 'الكمية' in row_str or 'تاريخ' in row_str:
                    header_idx = idx
                    break
            if header_idx is not None:
                df.columns = df.iloc[header_idx]
                df = df.iloc[header_idx + 1:].reset_index(drop=True)

        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        col_date = next((c for c in df.columns if 'تاريخ' in c), None)
        col_type = next((c for c in df.columns if 'نوع' in c), None)
        col_dept = next((c for c in df.columns if 'قسم' in c), None)
        col_item = next((c for c in df.columns if 'مادة' in c and 'كود' not in c), None)
        col_qty = next((c for c in df.columns if 'كمية' in c), None)
        col_bal = next((c for c in df.columns if 'رصيد' in c and 'حالي' in c), None)
        col_cat = next((c for c in df.columns if 'تصنيف' in c), None)
        
        for c in [col_qty, col_bal]:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('-', '0'), errors='coerce').fillna(0)
        if col_date and col_date in df.columns: df[col_date] = pd.to_datetime(df[col_date], errors='coerce')

        return df, col_date, col_type, col_dept, col_item, col_qty, col_bal, col_cat
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_pur_cat_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5lFKwIUSMCyYxRvpRMUl3PDlO6JY-x07zi0FgH9O2Atbryh4TjEpH7UGxtQ_Cw/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None, None
        
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        col_emp = next((c for c in df.columns if 'الموظف' in c), None)
        col_arrival = next((c for c in df.columns if 'وصول' in c), None)
        col_ord_date = next((c for c in df.columns if 'تاريخ الطلب' in c), None)
        col_comp = next((c for c in df.columns if 'الشركة' in c), None)
        col_req = next((c for c in df.columns if 'المطلوب' in c), None)
        col_cur = next((c for c in df.columns if 'الرصيد' in c), None)
        col_unit = next((c for c in df.columns if 'الوحدة' in c), None)
        col_item = next((c for c in df.columns if 'اسم المادة' in c or 'المادة' in c), None)
        
        for c in [col_req, col_cur]:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
        if col_ord_date and col_ord_date in df.columns: df[col_ord_date] = pd.to_datetime(df[col_ord_date], errors='coerce', dayfirst=True)
        for c in [col_emp, col_comp, col_unit, col_item, col_arrival]:
            if c and c in df.columns: df[c] = df[c].fillna('غير محدد')
                
        return df, col_emp, col_arrival, col_ord_date, col_comp, col_req, col_cur, col_unit, col_item
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_pur_slh_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None, None, None
        
        df.columns = df.columns.astype(str).str.replace(r'[\ufeff\n\r]', '', regex=True).str.strip()
        c_arr = next((c for c in df.columns if 'وصول' in c), None)
        c_ord_date = next((c for c in df.columns if 'تاريخ' in c), None)
        c_comp = next((c for c in df.columns if 'الشركة' in c or 'شركة' in c), None)
        c_req = next((c for c in df.columns if 'المطلوب' in c), None)
        c_cur = next((c for c in df.columns if 'الرصيد' in c), None)
        c_unit = next((c for c in df.columns if 'الوحدة' in c), None)
        c_dept = next((c for c in df.columns if 'القسم' in c or 'قسم' in c), None)
        c_cat = next((c for c in df.columns if 'تصنيف' in c), None)
        c_item = next((c for c in df.columns if 'اسم المادة' in c or ('المادة' in c and 'تصنيف' not in c)), None)

        for c in [c_req, c_cur]:
            if c and c in df.columns: df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
        if c_ord_date and c_ord_date in df.columns: df[c_ord_date] = pd.to_datetime(df[c_ord_date], errors='coerce', dayfirst=True)
        for c in [c_arr, c_comp, c_unit, c_dept, c_cat, c_item]:
            if c and c in df.columns: df[c] = df[c].fillna('غير محدد')

        return df, c_arr, c_ord_date, c_comp, c_req, c_cur, c_unit, c_dept, c_cat, c_item
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None, None, None

# ==========================================
# 5. منطق عرض الأقسام (الكود الأصلي الكلاسيكي)
# ==========================================
try:
    # ------------------ 📊 قسم عام المجزر (الجديد) ------------------
    if st.session_state.active_tab == 'slh_gen':
        st.title("📊 عام المجزر (التقرير الشامل)")
        
        df_slh_gen = load_slh_general_data()
        
        if df_slh_gen.empty:
            st.info("⚠️ تعذر سحب البيانات، يرجى الانتظار والمحاولة مرة أخرى.")
        else:
            st.success("✅ تم سحب البيانات بنجاح.")
            st.markdown("""
            **ملاحظة:** يعرض هذا القسم البيانات كما هي موجودة في التقرير المعقد. يمكنك تصفح وتحميل التقرير بالكامل من هنا.
            """)
            with st.expander("📋 عرض بيانات عام المجزر", expanded=True):
                st.download_button(label="📥 تحميل التقرير (CSV)", data=df_slh_gen.to_csv(index=False).encode('utf-8'), file_name="slh_general_data.csv", mime="text/csv")
                st.dataframe(df_slh_gen, use_container_width=True)

    # ------------------ قسم المحافظات ------------------
    elif st.session_state.active_tab == 'gov':
        df_gov, col_date, col_gov, col_agent, col_item, col_cat, col_ff, col_label, col_ton, col_qty = load_gov_data()
        
        if not df_gov.empty:
            filtered_df = df_gov.copy()
            with st.expander("🔍 فلاتر قسم المحافظات", expanded=True):
                with st.form("gov_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if col_date and col_date in filtered_df.columns:
                        valid_dates = filtered_df[col_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date = f1.checkbox("☑️ تفعيل فلتر التاريخ", value=False, key="gov_chk")
                            if use_date:
                                date_range = f1.date_input("اختر الفترة", [min_d, max_d], min_value=min_d, max_value=max_d, key="gov_date")
                                if len(date_range) == 2:
                                    filtered_df = filtered_df[(filtered_df[col_date].dt.date >= date_range[0]) & (filtered_df[col_date].dt.date <= date_range[1])]

                    if col_gov and col_gov in filtered_df.columns:
                        sel_gov = f2.multiselect("📍 المحافظة", filtered_df[col_gov].unique(), key="gov_gov")
                        if sel_gov: filtered_df = filtered_df[filtered_df[col_gov].isin(sel_gov)]
                    if col_ff and col_ff in filtered_df.columns:
                        sel_ff = f3.multiselect("❄️ طازج أو مجمد", filtered_df[col_ff].unique(), key="gov_ff")
                        if sel_ff: filtered_df = filtered_df[filtered_df[col_ff].isin(sel_ff)]
                    if col_label and col_label in filtered_df.columns:
                        sel_label = f4.multiselect("🏷️ العلامة التجارية", filtered_df[col_label].unique(), key="gov_lbl")
                        if sel_label: filtered_df = filtered_df[filtered_df[col_label].isin(sel_label)]

                    submitted_gov = st.form_submit_button("🚀 تطبيق الفلاتر")

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📦 إجمالي المبيعات (طن)", f"{filtered_df[col_ton].sum():,.2f}" if col_ton and col_ton in filtered_df.columns else "0")
            c2.metric("🔢 إجمالي المبيعات (عدد)", f"{filtered_df[col_qty].sum():,.0f}" if col_qty and col_qty in filtered_df.columns else "0")
            c3.metric("👥 الزبائن والوكلاء", f"{filtered_df[col_agent].nunique()}" if col_agent and col_agent in filtered_df.columns else "0")
            c4.metric("📄 المستندات المسجلة", f"{len(filtered_df)}")
            st.markdown("---")

            try:
                pie1, pie2, pie3 = st.columns(3)
                with pie1:
                    if col_cat and col_ton and col_cat in filtered_df.columns and col_ton in filtered_df.columns:
                        cat_data = filtered_df.groupby(col_cat)[col_ton].sum().reset_index()
                        fig_cat = px.pie(cat_data, values=col_ton, names=col_cat, hole=0.4, title="🛒 التصنيف (Category)")
                        fig_cat.update_traces(textposition='inside', textinfo='percent')
                        fig_cat.update_layout(legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_cat, use_container_width=True)
                with pie2:
                    if col_ff and col_ton and col_ff in filtered_df.columns and col_ton in filtered_df.columns:
                        ff_data = filtered_df.groupby(col_ff)[col_ton].sum().reset_index()
                        fig_ff = px.pie(ff_data, values=col_ton, names=col_ff, color_discrete_sequence=['#3b82f6', '#06b6d4'], title="❄️ طازج ومجمد")
                        fig_ff.update_traces(textposition='inside', textinfo='percent')
                        fig_ff.update_layout(legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_ff, use_container_width=True)
                with pie3:
                    if col_label and col_ton and col_label in filtered_df.columns and col_ton in filtered_df.columns:
                        label_data = filtered_df.groupby(col_label)[col_ton].sum().reset_index()
                        fig_label = px.pie(label_data, values=col_ton, names=col_label, color_discrete_sequence=['#f59e0b', '#ec4899'], title="🏷️ العلامة التجارية")
                        fig_label.update_traces(textposition='inside', textinfo='percent')
                        fig_label.update_layout(legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_label, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            try:
                if col_gov and col_ton and col_gov in filtered_df.columns and col_ton in filtered_df.columns:
                    gov_data = filtered_df.groupby(col_gov)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=True)
                    fig_gov = px.bar(gov_data, x=col_ton, y=col_gov, orientation='h', color=col_gov, text_auto='.2s', title="📍 التوزيع حسب المحافظات")
                    fig_gov.update_layout(showlegend=False, height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_gov, use_container_width=True)

                bar1, bar2 = st.columns(2)
                with bar1:
                    if col_agent and col_ton and col_agent in filtered_df.columns and col_ton in filtered_df.columns:
                        agent_data = filtered_df.groupby(col_agent)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=False).head(10)
                        fig_agent = px.bar(agent_data, x=col_agent, y=col_ton, color=col_ton, color_continuous_scale='Purples', text_auto='.2s', title="🏆 أفضل 10 زبائن (طن)")
                        fig_agent.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_agent, use_container_width=True)
                with bar2:
                    if col_item and col_qty and col_item in filtered_df.columns and col_qty in filtered_df.columns:
                        item_data = filtered_df.groupby(col_item)[col_qty].sum().reset_index().sort_values(by=col_qty, ascending=False).head(10)
                        fig_item = px.bar(item_data, x=col_item, y=col_qty, color=col_qty, color_continuous_scale='Reds', text_auto='.2s', title="📦 أفضل 10 مواد مبيعاً (عدد)")
                        fig_item.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_item, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_gov_form"):
                ca1, ca2 = st.columns(2)
                gov_cat_cols = [c for c in [col_gov, col_agent, col_item, col_cat, col_ff, col_label] if c and c in filtered_df.columns]
                gov_num_cols = [c for c in [col_ton, col_qty] if c and c in filtered_df.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", gov_cat_cols) if gov_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", gov_num_cols) if gov_num_cols else None
                submitted_ca = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca and x_axis and y_axis:
                try:
                    custom_df = filtered_df.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول تفاصيل المحافظات"):
                csv_gov = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول المحافظات (CSV)", data=csv_gov, file_name="gov_data.csv", mime="text/csv")
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

    # ------------------ قسم الثلاجات ------------------
    elif st.session_state.active_tab == 'frz':
        df_frz, c_item, c_frz, c_start, c_prod, c_sold, c_short, c_final = load_freezer_data()
        
        if not df_frz.empty:
            filtered_frz = df_frz.copy()
            st.subheader("📊 ملخص حركة المخزون | Inventory Movement")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 المخزون الحالي", f"{filtered_frz[c_final].sum():,.0f}" if c_final and c_final in filtered_frz.columns else "0")
            k2.metric("🏭 إجمالي الإنتاج الداخلي", f"{filtered_frz[c_prod].sum():,.0f}" if c_prod and c_prod in filtered_frz.columns else "0")
            k3.metric("🛒 إجمالي المباع الصادر", f"{filtered_frz[c_sold].sum():,.0f}" if c_sold and c_sold in filtered_frz.columns else "0")
            k4.metric("⚠️ إجمالي النقص أو التالف", f"{filtered_frz[c_short].sum():,.0f}" if c_short and c_short in filtered_frz.columns else "0", delta="- هدر", delta_color="inverse")
            st.markdown("---")

            try:
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    if c_frz and c_final and c_frz in filtered_frz.columns and c_final in filtered_frz.columns:
                        frz_stock = filtered_frz.groupby(c_frz)[c_final].sum().reset_index().sort_values(by=c_final, ascending=False)
                        fig_stock = px.bar(frz_stock, x=c_frz, y=c_final, color=c_frz, text_auto='.2s', title="🧊 المخزون الحالي في كل ثلاجة")
                        fig_stock.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_stock, use_container_width=True)
                with row1_col2:
                    if c_frz and c_short and c_frz in filtered_frz.columns and c_short in filtered_frz.columns:
                        frz_short = filtered_frz.groupby(c_frz)[c_short].sum().reset_index()
                        if frz_short[c_short].sum() > 0:
                            fig_short = px.pie(frz_short, values=c_short, names=c_frz, hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r, title="⚠️ توزيع النقص حسب الثلاجة")
                            fig_short.update_traces(textposition='inside', textinfo='percent')
                            fig_short.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                            st.plotly_chart(fig_short, use_container_width=True)
                        else:
                            st.success("✅ لا يوجد أي نقص في الثلاجات!")
            except Exception: pass

            st.markdown("---")
            try:
                if c_frz and c_prod and c_sold and c_frz in filtered_frz.columns:
                    flow_data = filtered_frz.groupby(c_frz)[[c_prod, c_sold]].sum().reset_index()
                    flow_melted = flow_data.melt(id_vars=c_frz, value_vars=[c_prod, c_sold], var_name='العملية', value_name='الكمية')
                    fig_flow = px.bar(flow_melted, x=c_frz, y='الكمية', color='العملية', barmode='group', color_discrete_map={c_prod: '#10b981', c_sold: '#f43f5e'}, text_auto='.2s', title="🔄 مقارنة الإنتاج مقابل المباع")
                    fig_flow.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_flow, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_frz_form"):
                ca1, ca2 = st.columns(2)
                frz_cat_cols = [c for c in [c_item, c_frz] if c and c in filtered_frz.columns]
                frz_num_cols = [c for c in [c_start, c_prod, c_sold, c_short, c_final] if c and c in filtered_frz.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", frz_cat_cols) if frz_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", frz_num_cols) if frz_num_cols else None
                submitted_ca_frz = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca_frz and x_axis and y_axis:
                try:
                    custom_df = filtered_frz.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول أرصدة الثلاجات"):
                csv_frz = filtered_frz.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول الثلاجات (CSV)", data=csv_frz, file_name="freezer_data.csv", mime="text/csv")
                st.dataframe(filtered_frz, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

    # ------------------ قسم المجزر ------------------
    elif st.session_state.active_tab == 'slh':
        df_slh, c_date, c_qty, c_prev, c_prod, c_sold, c_item, c_code = load_slaughterhouse_data()
        
        if not df_slh.empty:
            filtered_slh = df_slh.copy()
            with st.expander("🔍 فلاتر مخازن المجزر", expanded=True):
                with st.form("slh_form"):
                    f1, f2 = st.columns(2)
                    if c_date and c_date in filtered_slh.columns:
                        valid_dates = filtered_slh[c_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_slh = f1.checkbox("☑️ تفعيل فلتر التاريخ", value=False, key="slh_chk")
                            if use_date_slh:
                                date_range = f1.date_input("تحديد فترة المجزر", [min_d, max_d], min_value=min_d, max_value=max_d, key="slh_date")
                                if len(date_range) == 2:
                                    filtered_slh = filtered_slh[(filtered_slh[c_date].dt.date >= date_range[0]) & (filtered_slh[c_date].dt.date <= date_range[1])]

                    if c_item and c_item in filtered_slh.columns:
                        sel_item = f2.multiselect("اختر المادة", filtered_slh[c_item].unique(), key="slh_item_sel")
                        if sel_item: filtered_slh = filtered_slh[filtered_slh[c_item].isin(sel_item)]

                    submitted_slh = st.form_submit_button("🚀 تطبيق الفلاتر")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 إجمالي الكمية", f"{filtered_slh[c_qty].sum():,.2f}" if c_qty and c_qty in filtered_slh.columns else "0")
            k2.metric("🏭 إجمالي الإنتاج", f"{filtered_slh[c_prod].sum():,.0f}" if c_prod and c_prod in filtered_slh.columns else "0")
            k3.metric("🛒 إجمالي المباع", f"{filtered_slh[c_sold].sum():,.0f}" if c_sold and c_sold in filtered_slh.columns else "0")
            k4.metric("🔙 الرصيد السابق", f"{filtered_slh[c_prev].sum():,.0f}" if c_prev and c_prev in filtered_slh.columns else "0")
            st.markdown("---")

            try:
                pie1, pie2 = st.columns(2)
                with pie1:
                    total_prod = filtered_slh[c_prod].sum() if c_prod and c_prod in filtered_slh.columns else 0
                    total_sold = filtered_slh[c_sold].sum() if c_sold and c_sold in filtered_slh.columns else 0
                    if total_prod > 0 or total_sold > 0:
                        pie_df = pd.DataFrame({'العملية': ['الإنتاج', 'المباع'], 'الكمية': [total_prod, total_sold]})
                        fig_pie1 = px.pie(pie_df, values='الكمية', names='العملية', hole=0.4, title="🔄 نسبة الإنتاج مقابل المبيعات", color_discrete_sequence=['#10b981', '#f43f5e'])
                        fig_pie1.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie1.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_pie1, use_container_width=True)
                with pie2:
                    if c_item and c_qty and c_item in filtered_slh.columns and c_qty in filtered_slh.columns:
                        top5 = filtered_slh.groupby(c_item)[c_qty].sum().nlargest(5).reset_index()
                        fig_pie2 = px.pie(top5, values=c_qty, names=c_item, hole=0.4, title="📦 أعلى 5 مواد متوفرة", color_discrete_sequence=px.colors.sequential.Blues_r)
                        fig_pie2.update_traces(textposition='inside', textinfo='percent')
                        fig_pie2.update_layout(legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_pie2, use_container_width=True)
            except Exception: pass
                
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_item and c_prod and c_item in filtered_slh.columns and c_prod in filtered_slh.columns:
                        prod_data = filtered_slh.groupby(c_item)[c_prod].sum().reset_index().sort_values(by=c_prod, ascending=True).tail(10)
                        fig_prod = px.bar(prod_data, x=c_prod, y=c_item, orientation='h', color=c_prod, color_continuous_scale='Greens', text_auto='.2s', title="🏆 أعلى 10 مواد حسب الإنتاج")
                        fig_prod.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_prod, use_container_width=True)
                with row1_c2:
                    if c_item and c_qty and c_item in filtered_slh.columns and c_qty in filtered_slh.columns:
                        qty_data = filtered_slh.groupby(c_item)[c_qty].sum().reset_index().sort_values(by=c_qty, ascending=True).tail(10)
                        fig_qty = px.bar(qty_data, x=c_qty, y=c_item, orientation='h', color=c_qty, color_continuous_scale='Blues', text_auto='.2s', title="📦 أعلى 10 مواد حسب الكمية")
                        fig_qty.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_qty, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_slh_form"):
                ca1, ca2 = st.columns(2)
                slh_cat_cols = [c for c in [c_item, c_code] if c and c in filtered_slh.columns]
                slh_num_cols = [c for c in [c_qty, c_prev, c_prod, c_sold] if c and c in filtered_slh.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", slh_cat_cols) if slh_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", slh_num_cols) if slh_num_cols else None
                submitted_ca_slh = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca_slh and x_axis and y_axis:
                try:
                    custom_df = filtered_slh.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول بيانات المجزر"):
                csv_slh = filtered_slh.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول المجزر (CSV)", data=csv_slh, file_name="slaughterhouse_data.csv", mime="text/csv")
                if c_date and c_date in filtered_slh.columns:
                    filtered_slh[c_date] = filtered_slh[c_date].dt.strftime('%Y-%m-%d')
                st.dataframe(filtered_slh, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

    # ------------------ قسم المواد الأولية ------------------
    elif st.session_state.active_tab == 'mat':
        df_mat, c_date, c_type, c_dept, c_item, c_qty, c_bal, c_cat = load_raw_materials_data()
        
        if not df_mat.empty:
            filtered_mat = df_mat.copy()
            with st.expander("📦 فلاتر المواد الأولية", expanded=True):
                with st.form("mat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in filtered_mat.columns:
                        valid_dates = filtered_mat[c_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_mat = f1.checkbox("☑️ تفعيل فلتر التاريخ", value=False, key="mat_chk")
                            if use_date_mat:
                                date_range = f1.date_input("اختر الفترة", [min_d, max_d], min_value=min_d, max_value=max_d, key="mat_date")
                                if len(date_range) == 2:
                                    filtered_mat = filtered_mat[(filtered_mat[c_date].dt.date >= date_range[0]) & (filtered_mat[c_date].dt.date <= date_range[1])]

                    if c_dept and c_dept in filtered_mat.columns:
                        sel_dept = f2.multiselect("اختر القسم", filtered_mat[c_dept].unique(), key="mat_dept")
                        if sel_dept: filtered_mat = filtered_mat[filtered_mat[c_dept].isin(sel_dept)]
                    if c_type and c_type in filtered_mat.columns:
                        sel_type = f3.multiselect("نوع الإذن", filtered_mat[c_type].unique(), key="mat_type")
                        if sel_type: filtered_mat = filtered_mat[filtered_mat[c_type].isin(sel_type)]
                    if c_cat and c_cat in filtered_mat.columns:
                        sel_cat = f4.multiselect("التصنيف", filtered_mat[c_cat].unique(), key="mat_cat")
                        if sel_cat: filtered_mat = filtered_mat[filtered_mat[c_cat].isin(sel_cat)]
                        
                    submitted_mat = st.form_submit_button("🚀 تطبيق الفلاتر")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 إجمالي الرصيد الحالي", f"{filtered_mat[c_bal].sum():,.0f}" if c_bal and c_bal in filtered_mat.columns else "0")
            k2.metric("🔄 إجمالي الكميات للحركة", f"{filtered_mat[c_qty].sum():,.0f}" if c_qty and c_qty in filtered_mat.columns else "0")
            k3.metric("🏷️ عدد المواد المختلفة", f"{filtered_mat[c_item].nunique()}" if c_item and c_item in filtered_mat.columns else "0")
            k4.metric("📄 إجمالي السجلات", f"{len(filtered_mat)}")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_dept and c_bal and c_dept in filtered_mat.columns and c_bal in filtered_mat.columns:
                        dept_data = filtered_mat.groupby(c_dept)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True)
                        fig_dept = px.bar(dept_data, x=c_bal, y=c_dept, orientation='h', color=c_dept, text_auto='.2s', title="🏢 الأرصدة الحالية حسب القسم")
                        fig_dept.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_dept, use_container_width=True)
                with row1_c2:
                    if c_cat and c_bal and c_cat in filtered_mat.columns and c_bal in filtered_mat.columns:
                        cat_data = filtered_mat.groupby(c_cat)[c_bal].sum().reset_index()
                        fig_cat_mat = px.pie(cat_data, values=c_bal, names=c_cat, hole=0.4, title="🏷️ توزيع الأرصدة حسب التصنيف")
                        fig_cat_mat.update_traces(textposition='inside', textinfo='percent')
                        fig_cat_mat.update_layout(legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_cat_mat, use_container_width=True)
            except Exception: pass
                
            st.markdown("---")
            try:
                if c_item and c_bal and c_item in filtered_mat.columns and c_bal in filtered_mat.columns:
                    item_data = filtered_mat.groupby(c_item)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True).tail(10)
                    fig_top_mat = px.bar(item_data, x=c_bal, y=c_item, orientation='h', color=c_bal, color_continuous_scale='Blues', text_auto='.2s', title="🏆 أعلى 10 مواد متوفرة بالمخزن")
                    fig_top_mat.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_top_mat, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_mat_form"):
                ca1, ca2 = st.columns(2)
                mat_cat_cols = [c for c in [c_dept, c_type, c_cat, c_item] if c and c in filtered_mat.columns]
                mat_num_cols = [c for c in [c_qty, c_bal] if c and c in filtered_mat.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", mat_cat_cols) if mat_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", mat_num_cols) if mat_num_cols else None
                submitted_ca_mat = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca_mat and x_axis and y_axis:
                try:
                    custom_df = filtered_mat.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول بيانات المواد الأولية"):
                csv_mat = filtered_mat.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول المواد الأولية (CSV)", data=csv_mat, file_name="raw_materials_data.csv", mime="text/csv")
                if c_date and c_date in filtered_mat.columns: 
                    filtered_mat[c_date] = filtered_mat[c_date].dt.strftime('%Y-%m-%d')
                st.dataframe(filtered_mat, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

    # ------------------ قسم مشتريات المصنفات ------------------
    elif st.session_state.active_tab == 'pur_cat':
        df_pur, c_emp, c_arr, c_ord_date, c_comp, c_req, c_cur, c_unit, c_item = load_pur_cat_data()
        
        if not df_pur.empty:
            filtered_pur = df_pur.copy()
            with st.expander("🔍 فلاتر مشتريات المصنفات", expanded=True):
                with st.form("pur_cat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in filtered_pur.columns:
                        valid_dates = filtered_pur[c_ord_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_pur = f1.checkbox("☑️ تفعيل فلتر تاريخ الطلب", value=False, key="pur_chk")
                            if use_date_pur:
                                date_range = f1.date_input("اختر فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d, key="pur_date")
                                if len(date_range) == 2:
                                    filtered_pur = filtered_pur[(filtered_pur[c_ord_date].dt.date >= date_range[0]) & (filtered_pur[c_ord_date].dt.date <= date_range[1])]

                    if c_comp and c_comp in filtered_pur.columns:
                        sel_comp = f2.multiselect("🏢 الشركة الموردة", filtered_pur[c_comp].unique(), key="pur_comp")
                        if sel_comp: filtered_pur = filtered_pur[filtered_pur[c_comp].isin(sel_comp)]
                    if c_emp and c_emp in filtered_pur.columns:
                        sel_emp = f3.multiselect("👤 الموظف المتابع", filtered_pur[c_emp].unique(), key="pur_emp")
                        if sel_emp: filtered_pur = filtered_pur[filtered_pur[c_emp].isin(sel_emp)]
                    if c_unit and c_unit in filtered_pur.columns:
                        sel_unit = f4.multiselect("⚖️ الوحدة", filtered_pur[c_unit].unique(), key="pur_unit")
                        if sel_unit: filtered_pur = filtered_pur[filtered_pur[c_unit].isin(sel_unit)]
                        
                    submitted_pur_cat = st.form_submit_button("🚀 تطبيق الفلاتر")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🛒 إجمالي المطلوب", f"{filtered_pur[c_req].sum():,.0f}" if c_req and c_req in filtered_pur.columns else "0")
            k2.metric("📦 إجمالي الرصيد الحالي للمواد", f"{filtered_pur[c_cur].sum():,.0f}" if c_cur and c_cur in filtered_pur.columns else "0")
            k3.metric("🏢 عدد الشركات الموردة", f"{filtered_pur[c_comp].nunique()}" if c_comp and c_comp in filtered_pur.columns else "0")
            k4.metric("👤 عدد الموظفين المتابعين", f"{filtered_pur[c_emp].nunique()}" if c_emp and c_emp in filtered_pur.columns else "0")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_comp and c_req and c_comp in filtered_pur.columns and c_req in filtered_pur.columns:
                        comp_data = filtered_pur.groupby(c_comp)[c_req].sum().reset_index()
                        fig_comp = px.pie(comp_data, values=c_req, names=c_comp, hole=0.5, title="🏢 توزيع الطلبات حسب الشركة", color_discrete_sequence=px.colors.qualitative.Prism)
                        fig_comp.update_traces(textposition='inside', textinfo='percent+label')
                        fig_comp.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_comp, use_container_width=True)
                with row1_c2:
                    if c_emp and c_req and c_emp in filtered_pur.columns and c_req in filtered_pur.columns:
                        emp_data = filtered_pur.groupby(c_emp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=True)
                        fig_emp = px.bar(emp_data, x=c_req, y=c_emp, orientation='h', title="👤 حجم متابعة الطلبات لكل موظف", text_auto='.2s', color=c_req, color_continuous_scale='Teal')
                        fig_emp.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_emp, use_container_width=True)
            except Exception: pass
                
            st.markdown("---")

            try:
                if c_item and c_req and c_cur and c_item in filtered_pur.columns and c_req in filtered_pur.columns and c_cur in filtered_pur.columns:
                    top_items = filtered_pur.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
                    melted_items = top_items.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                    fig_compare = px.bar(melted_items, x=c_item, y='الكمية', color='النوع', barmode='group', title="⚖️ مقارنة: المطلوب مقابل الرصيد لأعلى 10 مواد", color_discrete_map={c_req: '#f59e0b', c_cur: '#3b82f6'}, text_auto='.2s')
                    fig_compare.update_layout(legend_title_text='', xaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_compare, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_pur_cat_form"):
                ca1, ca2 = st.columns(2)
                pur_cat_cols = [c for c in [c_emp, c_comp, c_unit, c_item, c_arr] if c and c in filtered_pur.columns]
                pur_num_cols = [c for c in [c_req, c_cur] if c and c in filtered_pur.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", pur_cat_cols) if pur_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", pur_num_cols) if pur_num_cols else None
                submitted_ca_pur_cat = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca_pur_cat and x_axis and y_axis:
                try:
                    custom_df = filtered_pur.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض السجل الكامل لمشتريات المصنفات"):
                csv_pur = filtered_pur.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول مشتريات المصنفات (CSV)", data=csv_pur, file_name="pur_cat_data.csv", mime="text/csv")
                if c_ord_date and c_ord_date in filtered_pur.columns:
                    filtered_pur[c_ord_date] = filtered_pur[c_ord_date].dt.strftime('%Y-%m-%d')
                st.dataframe(filtered_pur, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

    # ------------------ قسم مشتريات المجزر ------------------
    elif st.session_state.active_tab == 'pur_slh':
        df_pur_slh, c_arr, c_ord_date, c_comp, c_req, c_cur, c_unit, c_dept, c_cat, c_item = load_pur_slh_data()
        
        if not df_pur_slh.empty:
            filtered_slh = df_pur_slh.copy()

            with st.expander("🔍 فلاتر مشتريات المجزر", expanded=True):
                with st.form("pur_slh_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in filtered_slh.columns:
                        valid_dates = filtered_slh[c_ord_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_pur = f1.checkbox("☑️ تفعيل فلتر تاريخ الطلب", value=False, key="pur_slh_chk")
                            if use_date_pur:
                                date_range = f1.date_input("اختر فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d, key="pur_slh_date")
                                if len(date_range) == 2:
                                    filtered_slh = filtered_slh[(filtered_slh[c_ord_date].dt.date >= date_range[0]) & (filtered_slh[c_ord_date].dt.date <= date_range[1])]

                    if c_comp and c_comp in filtered_slh.columns:
                        sel_comp = f2.multiselect("🏢 الشركة الموردة", filtered_slh[c_comp].unique(), key="pur_slh_comp")
                        if sel_comp: filtered_slh = filtered_slh[filtered_slh[c_comp].isin(sel_comp)]

                    if c_cat and c_cat in filtered_slh.columns:
                        sel_cat = f3.multiselect("🏷️ تصنيف المادة", filtered_slh[c_cat].unique(), key="pur_slh_cat")
                        if sel_cat: filtered_slh = filtered_slh[filtered_slh[c_cat].isin(sel_cat)]

                    if c_arr and c_arr in filtered_slh.columns:
                        sel_arr = f4.multiselect("⏳ حالة التوريد", filtered_slh[c_arr].unique(), key="pur_slh_arr")
                        if sel_arr: filtered_slh = filtered_slh[filtered_slh[c_arr].isin(sel_arr)]
                        
                    submitted_pur_slh = st.form_submit_button("🚀 تطبيق الفلاتر")

            if use_date_pur and len(date_range) == 2 and c_ord_date:
                filtered_slh = filtered_slh[(filtered_slh[c_ord_date].dt.date >= date_range[0]) & (filtered_slh[c_ord_date].dt.date <= date_range[1])]
            if sel_comp: filtered_slh = filtered_slh[filtered_slh[c_comp].isin(sel_comp)]
            if sel_cat: filtered_slh = filtered_slh[filtered_slh[c_cat].isin(sel_cat)]
            if sel_arr: filtered_slh = filtered_slh[filtered_slh[c_arr].isin(sel_arr)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🛒 إجمالي المطلوب سيستم", f"{filtered_slh[c_req].sum():,.0f}" if c_req and c_req in filtered_slh.columns else "0")
            k2.metric("📦 إجمالي الرصيد الحالي", f"{filtered_slh[c_cur].sum():,.0f}" if c_cur and c_cur in filtered_slh.columns else "0")
            k3.metric("🏢 عدد الشركات", f"{filtered_slh[c_comp].nunique()}" if c_comp and c_comp in filtered_slh.columns else "0")
            k4.metric("🏷️ عدد التصنيفات", f"{filtered_slh[c_cat].nunique()}" if c_cat and c_cat in filtered_slh.columns else "0")
            st.markdown("---")

            try:
                if c_cat and c_item and c_req and c_cat in filtered_slh.columns and c_item in filtered_slh.columns and c_req in filtered_slh.columns:
                    tree_data = filtered_slh[filtered_slh[c_req] > 0].dropna(subset=[c_cat, c_item])
                    tree_data[c_cat] = tree_data[c_cat].astype(str)
                    tree_data[c_item] = tree_data[c_item].astype(str)
                    
                    if not tree_data.empty:
                        fig_tree = px.treemap(tree_data, path=[px.Constant("مشتريات المجزر"), c_cat, c_item], values=c_req,
                                              title="🗺️ الخريطة الهيكلية للطلبات",
                                              color=c_req, color_continuous_scale='Blues')
                        
                        fig_tree.update_traces(root_color="#1e293b", textinfo="label+value", textfont=dict(size=15))
                        fig_tree.update_layout(margin=dict(t=50, l=10, r=10, b=10), height=650, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_tree, use_container_width=True)
            except Exception: pass
                    
            st.markdown("---")

            try:
                row2_c1, row2_c2 = st.columns(2)
                with row2_c1:
                    if c_item and c_req and c_cur and c_item in filtered_slh.columns and c_req in filtered_slh.columns and c_cur in filtered_slh.columns:
                        top_slh_items = filtered_slh.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
                        melted_slh = top_slh_items.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                        fig_comp_slh = px.bar(melted_slh, x='الكمية', y=c_item, color='النوع', orientation='h', barmode='group',
                                             title="⚖️ أعلى 10 مواد: (المطلوب) مقابل (الرصيد)",
                                             color_discrete_map={c_req: '#8b5cf6', c_cur: '#10b981'}, text_auto='.2s')
                        fig_comp_slh.update_layout(legend_title_text='', yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_comp_slh, use_container_width=True)

                with row2_c2:
                    if c_comp and c_req and c_comp in filtered_slh.columns and c_req in filtered_slh.columns:
                        comp_perf = filtered_slh.groupby(c_comp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=False).head(10)
                        fig_comp_bar = px.bar(comp_perf, x=c_comp, y=c_req, title="🏢 أعلى 10 شركات موردة",
                                              color=c_req, color_continuous_scale='Sunset', text_auto='.2s')
                        fig_comp_bar.update_layout(xaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                        st.plotly_chart(fig_comp_bar, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            st.markdown("### 🛠️ مختبر التحليلات المخصص")
            with st.form("custom_pur_slh_form"):
                ca1, ca2 = st.columns(2)
                pur_slh_cat_cols = [c for c in [c_arr, c_comp, c_dept, c_cat, c_unit, c_item] if c and c in filtered_slh.columns]
                pur_slh_num_cols = [c for c in [c_req, c_cur] if c and c in filtered_slh.columns]
                x_axis = ca1.selectbox("اختر حقل المقارنة:", pur_slh_cat_cols) if pur_slh_cat_cols else None
                y_axis = ca2.selectbox("اختر القيمة المراد حسابها:", pur_slh_num_cols) if pur_slh_num_cols else None
                submitted_ca_pur_slh = st.form_submit_button("📊 رسم التحليل")

            if submitted_ca_pur_slh and x_axis and y_axis:
                try:
                    custom_df = filtered_slh.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, color=y_axis, color_continuous_scale='Magma', text_auto='.2s', title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_layout(xaxis_title="", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#cbd5e1'))
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض السجل الكامل لمشتريات المجزر"):
                csv_pur_slh = filtered_slh.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 تحميل جدول مشتريات المجزر (CSV)", data=csv_pur_slh, file_name="pur_slh_data.csv", mime="text/csv")
                if c_ord_date and c_ord_date in filtered_slh.columns:
                    filtered_slh[c_ord_date] = filtered_slh[c_ord_date].dt.strftime('%Y-%m-%d')
                st.dataframe(filtered_slh, use_container_width=True)
        else:
            st.warning("⚠️ جاري سحب البيانات... يرجى الانتظار ثواني.")

except Exception as e:
    pass
