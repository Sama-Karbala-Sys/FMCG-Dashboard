import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import datetime
import traceback

# ==========================================
# 1. إعدادات الصفحة واللغة
# ==========================================
try:
    st.set_page_config(page_title="FMCG Finance Dashboard", layout="wide")
except Exception:
    pass

st.markdown("""
    <style>
        /* =========================================
           ثيم Google Finance (أسود داكن / رمادي)
           ========================================= */
        .stApp { 
            background-color: #202124 !important; 
            color: #e8eaed !important; 
            direction: rtl; 
            font-family: Roboto, Arial, sans-serif !important;
        }
        
        /* إخفاء عناصر Streamlit الافتراضية المزعجة */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* نصوص وأرقام الكروت */
        div[data-testid="stMetricValue"] { 
            text-align: right; 
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 500 !important;
        }
        div[data-testid="stMetricLabel"] { 
            text-align: right; 
            color: #9aa0a6 !important;
            font-size: 0.9rem !important;
        }
        div[data-testid="stMetricDelta"] > div {
             font-size: 0.9rem !important;
        }

        /* =========================================
           1. التابات (الأقسام العلوية) - ستايل Google Finance
           ========================================= */
        div.row-widget.stRadio > div {
            display: flex; flex-direction: row; justify-content: center; gap: 20px;
            background-color: #202124; padding: 10px 0; border-bottom: 1px solid #3c4043;
            flex-wrap: wrap; margin-bottom: 20px;
        }
        div.stRadio > div[role="radiogroup"] > label {
            background-color: transparent !important; border: none !important;
            padding: 8px 0 !important; border-radius: 0 !important;
            cursor: pointer !important; box-shadow: none !important;
            border-bottom: 2px solid transparent !important;
        }
        div.stRadio > div[role="radiogroup"] > label > div:first-child { display: none !important; }
        
        div.stRadio > div[role="radiogroup"] > label:hover p { color: #8ab4f8 !important; }
        
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            border-bottom: 2px solid #8ab4f8 !important; 
        }
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] p { color: #8ab4f8 !important; font-weight: bold !important; }
        div.stRadio > div[role="radiogroup"] > label p { color: #e8eaed !important; font-size: 1rem !important; margin: 0; }

        /* =========================================
           2. الكروت الإحصائية
           ========================================= */
        div[data-testid="metric-container"] {
            background-color: #292a2d !important; 
            border: 1px solid #3c4043;
            padding: 20px;
            border-radius: 8px;
            box-shadow: none;
            transition: transform 0.2s;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            border-color: #5f6368;
        }

        /* =========================================
           3. الفلاتر والقوائم المنسدلة 
           ========================================= */
        div[data-baseweb="select"] > div, input {
            border-radius: 4px !important;
            background-color: #303134 !important; 
            border: 1px solid #5f6368 !important;
            color: #e8eaed !important;
        }
        div[data-baseweb="select"] > div:hover, input:hover {
            border-color: #8ab4f8 !important;
        }

        /* =========================================
           4. القوائم المطوية وزر التطبيق
           ========================================= */
        div[data-testid="stExpander"] {
            background-color: #292a2d !important;
            border-radius: 8px; border: 1px solid #3c4043;
        }
        div[data-testid="stExpander"] summary {
            color: #e8eaed !important; font-weight: 500;
        }
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #8ab4f8 !important; color: #202124 !important;
            border: none; border-radius: 4px !important; font-weight: 500; width: 100%; height: 45px;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #aecbfa !important;
        }
        
        /* =========================================
           5. الجداول
           ========================================= */
        [data-testid="stDataFrame"] {
            background-color: #292a2d;
            border: 1px solid #3c4043;
            border-radius: 8px;
        }
        
        hr { border-top: 1px solid #3c4043 !important; margin-top: 1.5rem; margin-bottom: 1.5rem; }
        h1, h2, h3 { color: #e8eaed !important; font-weight: 400 !important; }
        h1 { font-size: 1.8rem !important; }
        h3 { font-size: 1.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# ألوان وتخطيط Plotly ليتوافق مع Google Finance
gf_layout = dict(
    paper_bgcolor='#292a2d',
    plot_bgcolor='#292a2d',
    font=dict(color='#e8eaed'),
    xaxis=dict(showgrid=False, gridcolor='#3c4043', zeroline=False),
    yaxis=dict(showgrid=True, gridcolor='#3c4043', zeroline=False),
    margin=dict(t=40, b=10, l=10, r=10)
)
gf_colors = ['#8ab4f8', '#81c995', '#f28b82', '#fde293', '#c58af9', '#f48fb1', '#78d9ec']

# ==========================================
# 2. رأس الصفحة، حالة النظام، وزر التحديث
# ==========================================
col_title, col_btn = st.columns([5, 1])
with col_title:
    st.markdown("<h1><span style='color: #8ab4f8;'>Finance</span> FMCG Enterprise</h1>", unsafe_allow_html=True)
    current_time = datetime.datetime.now().strftime("%d %B, %H:%M UTC")
    st.markdown(f"<p style='color: #9aa0a6; font-size: 0.85rem; margin-top: -10px;'>السوق متصل • {current_time}</p>", unsafe_allow_html=True)
with col_btn:
    st.write("") 
    if st.button("تحديث السحابة", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 3. شريط التابات
# ==========================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'gov'

tabs_dict = {
    "المحافظات": "gov",
    "الثلاجات": "frz",
    "مخازن المجزر": "slh",
    "عام المجزر": "slh_gen",
    "المواد الأولية": "mat",
    "مشتريات المصنفات": "pur_cat",
    "مشتريات المجزر": "pur_slh"
}

selected_tab_name = st.radio(
    "القوائم",
    list(tabs_dict.keys()),
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.active_tab = tabs_dict[selected_tab_name]

# ==========================================
# 4. دوال السحب 
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

def clean_columns(df):
    df.columns = [str(c).replace('\ufeff', '').replace('\n', '').replace('\r', '').strip() for c in df.columns]
    return df

@st.cache_data(ttl=600)
def load_gov_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None, None, None
        df = clean_columns(df)
        
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
        df = clean_columns(df)
        
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
        df = clean_columns(df)
        
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
def load_slh_general_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM4ycja48KN-96D91Ppv0CHRkIzyOBGgpAszLcOEID09N5CYspJSSsU98wvIFyQ/pub?output=csv"
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None, None, None
        df = clean_columns(df)
        
        c_cat = next((c for c in df.columns if 'تصنيف' in c), None)
        c_item = next((c for c in df.columns if 'مادة' in c), None)
        c_unit = next((c for c in df.columns if 'وحدة' in c), None)
        
        c_bal = next((c for c in df.columns if 'الرصيد' in c and '/' not in c and '+' not in c), None)
        c_confirmed = next((c for c in df.columns if 'المثبت' in c and '/' not in c and '+' not in c and 'مطلوب' not in c), None)
        c_total_bal = next((c for c in df.columns if 'الرصيد' in c and 'المثبت' in c and '/' not in c), None)
        
        c_req = next((c for c in df.columns if 'مطلوب' in c), None)
        c_forecast = next((c for c in df.columns if 'فوركاست' in c), None)
        c_coverage = next((c for c in df.columns if 'يكفي' in c and '+' not in c), None)
        
        num_cols = [c_bal, c_confirmed, c_total_bal, c_req, c_forecast, c_coverage]
        for c in num_cols:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
                
        for c in [c_cat, c_item, c_unit]:
            if c and c in df.columns: df[c] = df[c].fillna('غير محدد')
                
        return df, c_cat, c_item, c_unit, c_bal, c_confirmed, c_total_bal, c_req, c_forecast, c_coverage
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None, None, None

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

        df = clean_columns(df)
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
        df = clean_columns(df)
        
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
        df = clean_columns(df)
        
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
# 5. منطق عرض الأقسام 
# ==========================================
try:
    # ------------------ 📍 قسم المحافظات ------------------
    if st.session_state.active_tab == 'gov':
        df_gov, col_date, col_gov, col_agent, col_item, col_cat, col_ff, col_label, col_ton, col_qty = load_gov_data()
        
        if not df_gov.empty:
            filtered_df = df_gov.copy()
            st.markdown("<h3>نظرة عامة على الأسواق</h3>", unsafe_allow_html=True)
            with st.expander("تصفية بيانات الأسواق", expanded=True):
                with st.form("gov_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if col_date and col_date in filtered_df.columns:
                        valid_dates = filtered_df[col_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date = f1.checkbox("تفعيل فلتر التاريخ", value=False)
                            if use_date:
                                date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                                if len(date_range) == 2:
                                    filtered_df = filtered_df[(filtered_df[col_date].dt.date >= date_range[0]) & (filtered_df[col_date].dt.date <= date_range[1])]

                    if col_gov and col_gov in filtered_df.columns:
                        sel_gov = f2.multiselect("المحافظة", filtered_df[col_gov].unique())
                        if sel_gov: filtered_df = filtered_df[filtered_df[col_gov].isin(sel_gov)]
                    if col_ff and col_ff in filtered_df.columns:
                        sel_ff = f3.multiselect("طازج / مجمد", filtered_df[col_ff].unique())
                        if sel_ff: filtered_df = filtered_df[filtered_df[col_ff].isin(sel_ff)]
                    if col_label and col_label in filtered_df.columns:
                        sel_label = f4.multiselect("العلامة التجارية", filtered_df[col_label].unique())
                        if sel_label: filtered_df = filtered_df[filtered_df[col_label].isin(sel_label)]

                    submitted_gov = st.form_submit_button("تطبيق")

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("إجمالي المبيعات (طن)", f"{filtered_df[col_ton].sum():,.2f}" if col_ton and col_ton in filtered_df.columns else "0", "+0.0% استقرار")
            c2.metric("إجمالي المبيعات (عدد)", f"{filtered_df[col_qty].sum():,.0f}" if col_qty and col_qty in filtered_df.columns else "0")
            c3.metric("الزبائن النشطين", f"{filtered_df[col_agent].nunique()}" if col_agent and col_agent in filtered_df.columns else "0")
            c4.metric("إجمالي السجلات", f"{len(filtered_df)}")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>التوزيع والقطاعات</h3>", unsafe_allow_html=True)
                pie1, pie2, pie3 = st.columns(3)
                with pie1:
                    if col_cat and col_ton and col_cat in filtered_df.columns and col_ton in filtered_df.columns:
                        fig_cat = px.pie(filtered_df.groupby(col_cat)[col_ton].sum().reset_index(), values=col_ton, names=col_cat, hole=0.5, title="التصنيف", color_discrete_sequence=gf_colors)
                        fig_cat.update_traces(textposition='inside', textinfo='percent')
                        fig_cat.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_cat, use_container_width=True)
                with pie2:
                    if col_ff and col_ton and col_ff in filtered_df.columns and col_ton in filtered_df.columns:
                        fig_ff = px.pie(filtered_df.groupby(col_ff)[col_ton].sum().reset_index(), values=col_ton, names=col_ff, hole=0.5, title="طازج مقابل مجمد", color_discrete_sequence=['#8ab4f8', '#81c995'])
                        fig_ff.update_traces(textposition='inside', textinfo='percent')
                        fig_ff.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_ff, use_container_width=True)
                with pie3:
                    if col_label and col_ton and col_label in filtered_df.columns and col_ton in filtered_df.columns:
                        fig_label = px.pie(filtered_df.groupby(col_label)[col_ton].sum().reset_index(), values=col_ton, names=col_label, hole=0.5, title="العلامة التجارية", color_discrete_sequence=['#fde293', '#f28b82'])
                        fig_label.update_traces(textposition='inside', textinfo='percent')
                        fig_label.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_label, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                st.markdown("<h3>أداء الأصول</h3>", unsafe_allow_html=True)
                if col_gov and col_ton and col_gov in filtered_df.columns and col_ton in filtered_df.columns:
                    fig_gov = px.bar(filtered_df.groupby(col_gov)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=True), x=col_ton, y=col_gov, orientation='h', title="توزيع المحافظات")
                    fig_gov.update_traces(marker_color='#8ab4f8')
                    fig_gov.update_layout(**gf_layout, showlegend=False, height=350)
                    st.plotly_chart(fig_gov, use_container_width=True)

                bar1, bar2 = st.columns(2)
                with bar1:
                    if col_agent and col_ton and col_agent in filtered_df.columns and col_ton in filtered_df.columns:
                        fig_agent = px.bar(filtered_df.groupby(col_agent)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=False).head(10), x=col_agent, y=col_ton, title="أعلى الزبائن")
                        fig_agent.update_traces(marker_color='#8ab4f8')
                        fig_agent.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_agent, use_container_width=True)
                with bar2:
                    if col_item and col_qty and col_item in filtered_df.columns and col_qty in filtered_df.columns:
                        fig_item = px.bar(filtered_df.groupby(col_item)[col_qty].sum().reset_index().sort_values(by=col_qty, ascending=False).head(10), x=col_item, y=col_qty, title="أعلى المواد المبيعة")
                        fig_item.update_traces(marker_color='#81c995')
                        fig_item.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_item, use_container_width=True)
            except Exception: pass
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>التحليلات المتقدمة</h3>", unsafe_allow_html=True)
            with st.form("custom_gov_form"):
                ca1, ca2 = st.columns(2)
                gov_cat_cols = [c for c in [col_gov, col_agent, col_item, col_cat, col_ff, col_label] if c and c in filtered_df.columns]
                gov_num_cols = [c for c in [col_ton, col_qty] if c and c in filtered_df.columns]
                x_axis = ca1.selectbox("محور المقارنة:", gov_cat_cols) if gov_cat_cols else None
                y_axis = ca2.selectbox("القيم:", gov_num_cols) if gov_num_cols else None
                submitted_ca = st.form_submit_button("رسم")

            if submitted_ca and x_axis and y_axis:
                try:
                    custom_df = filtered_df.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"مقارنة {y_axis} حسب {x_axis}")
                    fig_custom.update_traces(marker_color='#c58af9')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("بيانات المحافظات الشاملة (Raw Data)"):
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات. يرجى الانتظار...")

    # ------------------ 🧊 قسم الثلاجات ------------------
    elif st.session_state.active_tab == 'frz':
        df_frz, c_item, c_frz, c_start, c_prod, c_sold, c_short, c_final = load_freezer_data()
        
        if not df_frz.empty:
            filtered_frz = df_frz.copy()
            st.markdown("<h3>مؤشرات المخزون وحركة الثلاجات</h3>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المخزون الحالي", f"{filtered_frz[c_final].sum():,.0f}" if c_final and c_final in filtered_frz.columns else "0")
            k2.metric("حجم الإنتاج الداخلي", f"{filtered_frz[c_prod].sum():,.0f}" if c_prod and c_prod in filtered_frz.columns else "0")
            k3.metric("الصادر (مباع)", f"{filtered_frz[c_sold].sum():,.0f}" if c_sold and c_sold in filtered_frz.columns else "0")
            k4.metric("النقص / التالف", f"{filtered_frz[c_short].sum():,.0f}" if c_short and c_short in filtered_frz.columns else "0", "- خسارة" if filtered_frz[c_short].sum() > 0 else "")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    if c_frz and c_final and c_frz in filtered_frz.columns and c_final in filtered_frz.columns:
                        frz_stock = filtered_frz.groupby(c_frz)[c_final].sum().reset_index().sort_values(by=c_final, ascending=False)
                        fig_stock = px.bar(frz_stock, x=c_frz, y=c_final, title="الأرصدة الحالية في الثلاجات")
                        fig_stock.update_traces(marker_color='#8ab4f8')
                        fig_stock.update_layout(**gf_layout)
                        st.plotly_chart(fig_stock, use_container_width=True)
                with row1_col2:
                    if c_frz and c_short and c_frz in filtered_frz.columns and c_short in filtered_frz.columns:
                        frz_short = filtered_frz.groupby(c_frz)[c_short].sum().reset_index()
                        if frz_short[c_short].sum() > 0:
                            fig_short = px.pie(frz_short, values=c_short, names=c_frz, hole=0.5, title="توزيع التالف والنقص", color_discrete_sequence=['#f28b82'])
                            fig_short.update_traces(textposition='inside', textinfo='percent')
                            fig_short.update_layout(**gf_layout, showlegend=False)
                            st.plotly_chart(fig_short, use_container_width=True)
                        else:
                            st.success("الوضع آمن: لا يوجد نقص")
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                if c_frz and c_prod and c_sold and c_frz in filtered_frz.columns:
                    flow_data = filtered_frz.groupby(c_frz)[[c_prod, c_sold]].sum().reset_index()
                    flow_melted = flow_data.melt(id_vars=c_frz, value_vars=[c_prod, c_sold], var_name='العملية', value_name='الكمية')
                    fig_flow = px.bar(flow_melted, x=c_frz, y='الكمية', color='العملية', barmode='group', color_discrete_map={c_prod: '#81c995', c_sold: '#f28b82'}, title="تدفق الإنتاج والمبيعات")
                    fig_flow.update_layout(**gf_layout, legend_title_text='')
                    st.plotly_chart(fig_flow, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات المخصص</h3>", unsafe_allow_html=True)
            with st.form("custom_frz_form"):
                ca1, ca2 = st.columns(2)
                frz_cat_cols = [c for c in [c_item, c_frz] if c and c in filtered_frz.columns]
                frz_num_cols = [c for c in [c_start, c_prod, c_sold, c_short, c_final] if c and c in filtered_frz.columns]
                x_axis = ca1.selectbox("المحور:", frz_cat_cols) if frz_cat_cols else None
                y_axis = ca2.selectbox("القيم:", frz_num_cols) if frz_num_cols else None
                submitted_ca_frz = st.form_submit_button("رسم")

            if submitted_ca_frz and x_axis and y_axis:
                try:
                    custom_df = filtered_frz.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#fde293')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("قاعدة بيانات الثلاجات (Raw)"):
                st.dataframe(filtered_frz, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات...")

    # ------------------ ❄️ مخازن المجزر ------------------
    elif st.session_state.active_tab == 'slh':
        df_slh, c_date, c_qty, c_prev, c_prod, c_sold, c_item, c_code = load_slaughterhouse_data()
        
        if not df_slh.empty:
            filtered_slh = df_slh.copy()
            st.markdown("<h3>نظرة عامة على المجزر</h3>", unsafe_allow_html=True)
            with st.expander("تصفية البيانات", expanded=True):
                with st.form("slh_form"):
                    f1, f2 = st.columns(2)
                    if c_date and c_date in filtered_slh.columns:
                        valid_dates = filtered_slh[c_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_slh = f1.checkbox("تفعيل الفلتر الزمني", value=False)
                            if use_date_slh:
                                date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                                if len(date_range) == 2:
                                    filtered_slh = filtered_slh[(filtered_slh[c_date].dt.date >= date_range[0]) & (filtered_slh[c_date].dt.date <= date_range[1])]

                    if c_item and c_item in filtered_slh.columns:
                        sel_item = f2.multiselect("تحديد المادة", filtered_slh[c_item].unique())
                        if sel_item: filtered_slh = filtered_slh[filtered_slh[c_item].isin(sel_item)]

                    submitted_slh = st.form_submit_button("تطبيق")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الكمية المتوفرة", f"{filtered_slh[c_qty].sum():,.2f}" if c_qty and c_qty in filtered_slh.columns else "0")
            k2.metric("حجم الإنتاج", f"{filtered_slh[c_prod].sum():,.0f}" if c_prod and c_prod in filtered_slh.columns else "0")
            k3.metric("المباع الصادر", f"{filtered_slh[c_sold].sum():,.0f}" if c_sold and c_sold in filtered_slh.columns else "0")
            k4.metric("الأرصدة السابقة", f"{filtered_slh[c_prev].sum():,.0f}" if c_prev and c_prev in filtered_slh.columns else "0")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>مؤشرات العمليات</h3>", unsafe_allow_html=True)
                pie1, pie2 = st.columns(2)
                with pie1:
                    total_prod = filtered_slh[c_prod].sum() if c_prod and c_prod in filtered_slh.columns else 0
                    total_sold = filtered_slh[c_sold].sum() if c_sold and c_sold in filtered_slh.columns else 0
                    if total_prod > 0 or total_sold > 0:
                        pie_df = pd.DataFrame({'العملية': ['الإنتاج', 'المباع'], 'الكمية': [total_prod, total_sold]})
                        fig_pie1 = px.pie(pie_df, values='الكمية', names='العملية', hole=0.5, title="نسبة الإنتاج مقابل المبيعات", color_discrete_sequence=['#8ab4f8', '#f28b82'])
                        fig_pie1.update_traces(textposition='inside', textinfo='percent')
                        fig_pie1.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_pie1, use_container_width=True)
                with pie2:
                    if c_item and c_qty and c_item in filtered_slh.columns and c_qty in filtered_slh.columns:
                        top5 = filtered_slh.groupby(c_item)[c_qty].sum().nlargest(5).reset_index()
                        fig_pie2 = px.pie(top5, values=c_qty, names=c_item, hole=0.5, title="أعلى 5 مواد متوفرة", color_discrete_sequence=gf_colors)
                        fig_pie2.update_traces(textposition='inside', textinfo='percent')
                        fig_pie2.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_pie2, use_container_width=True)
            except Exception: pass
                
            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                st.markdown("<h3>الأصول المادية</h3>", unsafe_allow_html=True)
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_item and c_prod and c_item in filtered_slh.columns and c_prod in filtered_slh.columns:
                        prod_data = filtered_slh.groupby(c_item)[c_prod].sum().reset_index().sort_values(by=c_prod, ascending=True).tail(10)
                        fig_prod = px.bar(prod_data, x=c_prod, y=c_item, orientation='h', title="أعلى المواد إنتاجاً")
                        fig_prod.update_traces(marker_color='#8ab4f8')
                        fig_prod.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_prod, use_container_width=True)
                with row1_c2:
                    if c_item and c_qty and c_item in filtered_slh.columns and c_qty in filtered_slh.columns:
                        qty_data = filtered_slh.groupby(c_item)[c_qty].sum().reset_index().sort_values(by=c_qty, ascending=True).tail(10)
                        fig_qty = px.bar(qty_data, x=c_qty, y=c_item, orientation='h', title="أعلى المواد مخزوناً")
                        fig_qty.update_traces(marker_color='#81c995')
                        fig_qty.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_qty, use_container_width=True)
            except Exception: pass
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات</h3>", unsafe_allow_html=True)
            with st.form("custom_slh_form"):
                ca1, ca2 = st.columns(2)
                slh_cat_cols = [c for c in [c_item, c_code] if c and c in filtered_slh.columns]
                slh_num_cols = [c for c in [c_qty, c_prev, c_prod, c_sold] if c and c in filtered_slh.columns]
                x_axis = ca1.selectbox("محور التقييم:", slh_cat_cols) if slh_cat_cols else None
                y_axis = ca2.selectbox("المؤشر:", slh_num_cols) if slh_num_cols else None
                submitted_ca_slh = st.form_submit_button("عرض")

            if submitted_ca_slh and x_axis and y_axis:
                try:
                    custom_df = filtered_slh.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#c58af9')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("سجل بيانات المجزر الكامل"):
                st.dataframe(filtered_slh, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات...")

    # ------------------ 📊 عام المجزر (القسم الجديد) ------------------
    elif st.session_state.active_tab == 'slh_gen':
        df_slh_gen, c_cat, c_item, c_unit, c_bal, c_confirmed, c_total_bal, c_req, c_forecast, c_coverage = load_slh_general_data()
        
        if not df_slh_gen.empty:
            filtered_slh_gen = df_slh_gen.copy()
            st.markdown("<h3>التقرير الشامل (Forecasting)</h3>", unsafe_allow_html=True)
            with st.expander("تصفية بيانات المجزر العام", expanded=True):
                with st.form("slh_gen_form"):
                    f1, f2 = st.columns(2)
                    sel_cat = f1.multiselect("التصنيف", filtered_slh_gen[c_cat].unique() if c_cat and c_cat in filtered_slh_gen.columns else [])
                    sel_item = f2.multiselect("المادة", filtered_slh_gen[c_item].unique() if c_item and c_item in filtered_slh_gen.columns else [])
                    submitted_slh_gen = st.form_submit_button("تطبيق")
                    
            if sel_cat: filtered_slh_gen = filtered_slh_gen[filtered_slh_gen[c_cat].isin(sel_cat)]
            if sel_item: filtered_slh_gen = filtered_slh_gen[filtered_slh_gen[c_item].isin(sel_item)]
            
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الرصيد الفعلي", f"{filtered_slh_gen[c_bal].sum():,.0f}" if c_bal and c_bal in filtered_slh_gen.columns else "0")
            k2.metric("إجمالي المثبت (قيد الوصول)", f"{filtered_slh_gen[c_confirmed].sum():,.0f}" if c_confirmed and c_confirmed in filtered_slh_gen.columns else "0")
            k3.metric("المطلوب تثبيته (الاحتياج)", f"{filtered_slh_gen[c_req].sum():,.0f}" if c_req and c_req in filtered_slh_gen.columns else "0")
            
            critical_items = 0
            if c_coverage and c_coverage in filtered_slh_gen.columns:
                critical_items = len(filtered_slh_gen[(filtered_slh_gen[c_coverage] < 7) & (filtered_slh_gen[c_coverage] > 0)])
            k4.metric("مواد حرجة (< 7 أيام)", str(critical_items), "- خطر النفاد" if critical_items > 0 else "")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>التوزيع والخطر</h3>", unsafe_allow_html=True)
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_cat and c_bal and c_cat in filtered_slh_gen.columns and c_bal in filtered_slh_gen.columns:
                        fig_cat = px.pie(filtered_slh_gen.groupby(c_cat)[c_bal].sum().reset_index(), values=c_bal, names=c_cat, hole=0.5, title="الرصيد حسب التصنيف", color_discrete_sequence=gf_colors)
                        fig_cat.update_traces(textposition='inside', textinfo='percent')
                        fig_cat.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_cat, use_container_width=True)
                with row1_c2:
                    if c_item and c_coverage and c_item in filtered_slh_gen.columns and c_coverage in filtered_slh_gen.columns:
                        crit_df = filtered_slh_gen[filtered_slh_gen[c_coverage] > 0].sort_values(by=c_coverage, ascending=True).head(10)
                        fig_crit = px.bar(crit_df, x=c_coverage, y=c_item, orientation='h', title="المواد الأكثر حرجاً (أيام)")
                        fig_crit.update_traces(marker_color='#f28b82')
                        fig_crit.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_crit, use_container_width=True)
            except Exception: pass
            
            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                st.markdown("<h3>مقارنة الأصول</h3>", unsafe_allow_html=True)
                if c_item and c_bal and c_confirmed and c_item in filtered_slh_gen.columns:
                    top_items = filtered_slh_gen.sort_values(by=c_bal, ascending=False).head(15)
                    melted = top_items.melt(id_vars=c_item, value_vars=[c_bal, c_confirmed], var_name='النوع', value_name='الكمية')
                    fig_comp = px.bar(melted, x=c_item, y='الكمية', color='النوع', barmode='group', title="الرصيد الفعلي مقابل المثبت (لأعلى 15 مادة)", color_discrete_map={c_bal: '#8ab4f8', c_confirmed: '#81c995'})
                    fig_comp.update_layout(**gf_layout, legend_title_text='')
                    st.plotly_chart(fig_comp, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات المخصص</h3>", unsafe_allow_html=True)
            with st.form("custom_slh_gen_form"):
                ca1, ca2 = st.columns(2)
                cat_cols = [c for c in [c_cat, c_item, c_unit] if c and c in filtered_slh_gen.columns]
                num_cols = [c for c in [c_bal, c_confirmed, c_total_bal, c_req, c_forecast, c_coverage] if c and c in filtered_slh_gen.columns]
                x_axis = ca1.selectbox("محور المقارنة:", cat_cols) if cat_cols else None
                y_axis = ca2.selectbox("القيمة:", num_cols) if num_cols else None
                submitted_ca = st.form_submit_button("عرض النتائج")

            if submitted_ca and x_axis and y_axis:
                try:
                    custom_df = filtered_slh_gen.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#fde293')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("قاعدة البيانات الكاملة"):
                st.dataframe(filtered_slh_gen, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة.")

    # ------------------ 📦 المواد الأولية ------------------
    elif st.session_state.active_tab == 'mat':
        df_mat, c_date, c_type, c_dept, c_item, c_qty, c_bal, c_cat = load_raw_materials_data()
        
        if not df_mat.empty:
            filtered_mat = df_mat.copy()
            st.markdown("<h3>أرصدة المواد الأولية</h3>", unsafe_allow_html=True)
            with st.expander("تصفية المواد", expanded=True):
                with st.form("mat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in filtered_mat.columns:
                        valid_dates = filtered_mat[c_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_mat = f1.checkbox("تفعيل الفلتر", value=False)
                            if use_date_mat:
                                date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                                if len(date_range) == 2:
                                    filtered_mat = filtered_mat[(filtered_mat[c_date].dt.date >= date_range[0]) & (filtered_mat[c_date].dt.date <= date_range[1])]

                    if c_dept and c_dept in filtered_mat.columns:
                        sel_dept = f2.multiselect("القسم", filtered_mat[c_dept].unique())
                        if sel_dept: filtered_mat = filtered_mat[filtered_mat[c_dept].isin(sel_dept)]
                    if c_type and c_type in filtered_mat.columns:
                        sel_type = f3.multiselect("نوع الإذن", filtered_mat[c_type].unique())
                        if sel_type: filtered_mat = filtered_mat[filtered_mat[c_type].isin(sel_type)]
                    if c_cat and c_cat in filtered_mat.columns:
                        sel_cat = f4.multiselect("التصنيف", filtered_mat[c_cat].unique())
                        if sel_cat: filtered_mat = filtered_mat[filtered_mat[c_cat].isin(sel_cat)]
                        
                    submitted_mat = st.form_submit_button("تطبيق")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الرصيد الحالي", f"{filtered_mat[c_bal].sum():,.0f}" if c_bal and c_bal in filtered_mat.columns else "0")
            k2.metric("حركة الكميات", f"{filtered_mat[c_qty].sum():,.0f}" if c_qty and c_qty in filtered_mat.columns else "0")
            k3.metric("أنواع المواد", f"{filtered_mat[c_item].nunique()}" if c_item and c_item in filtered_mat.columns else "0")
            k4.metric("السجلات", f"{len(filtered_mat)}")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>التوزيع على الأقسام</h3>", unsafe_allow_html=True)
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_dept and c_bal and c_dept in filtered_mat.columns and c_bal in filtered_mat.columns:
                        dept_data = filtered_mat.groupby(c_dept)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True)
                        fig_dept = px.bar(dept_data, x=c_bal, y=c_dept, orientation='h', title="أرصدة الأقسام")
                        fig_dept.update_traces(marker_color='#8ab4f8')
                        fig_dept.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_dept, use_container_width=True)
                with row1_c2:
                    if c_cat and c_bal and c_cat in filtered_mat.columns and c_bal in filtered_mat.columns:
                        cat_data = filtered_mat.groupby(c_cat)[c_bal].sum().reset_index()
                        fig_cat_mat = px.pie(cat_data, values=c_bal, names=c_cat, hole=0.5, title="توزيع الأصناف", color_discrete_sequence=gf_colors)
                        fig_cat_mat.update_traces(textposition='inside', textinfo='percent')
                        fig_cat_mat.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_cat_mat, use_container_width=True)
            except Exception: pass
                
            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                st.markdown("<h3>أعلى الأرصدة المتوفرة</h3>", unsafe_allow_html=True)
                if c_item and c_bal and c_item in filtered_mat.columns and c_bal in filtered_mat.columns:
                    item_data = filtered_mat.groupby(c_item)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True).tail(10)
                    fig_top_mat = px.bar(item_data, x=c_bal, y=c_item, orientation='h', title="أعلى 10 مواد")
                    fig_top_mat.update_traces(marker_color='#81c995')
                    fig_top_mat.update_layout(**gf_layout, showlegend=False)
                    st.plotly_chart(fig_top_mat, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات</h3>", unsafe_allow_html=True)
            with st.form("custom_mat_form"):
                ca1, ca2 = st.columns(2)
                mat_cat_cols = [c for c in [c_dept, c_type, c_cat, c_item] if c and c in filtered_mat.columns]
                mat_num_cols = [c for c in [c_qty, c_bal] if c and c in filtered_mat.columns]
                x_axis = ca1.selectbox("المحور:", mat_cat_cols) if mat_cat_cols else None
                y_axis = ca2.selectbox("المؤشر:", mat_num_cols) if mat_num_cols else None
                submitted_ca_mat = st.form_submit_button("عرض")

            if submitted_ca_mat and x_axis and y_axis:
                try:
                    custom_df = filtered_mat.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#c58af9')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("قاعدة بيانات المواد الأولية"):
                st.dataframe(filtered_mat, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات...")

    # ------------------ 🛒 مشتريات المصنفات ------------------
    elif st.session_state.active_tab == 'pur_cat':
        df_pur, c_emp, c_arr, c_ord_date, c_comp, c_req, c_cur, c_unit, c_item = load_pur_cat_data()
        
        if not df_pur.empty:
            filtered_pur = df_pur.copy()
            st.markdown("<h3>مشتريات المصنفات والطلبيات</h3>", unsafe_allow_html=True)
            with st.expander("تصفية الطلبات", expanded=True):
                with st.form("pur_cat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in filtered_pur.columns:
                        valid_dates = filtered_pur[c_ord_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_pur = f1.checkbox("تفعيل الفلتر", value=False)
                            if use_date_pur:
                                date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                                if len(date_range) == 2:
                                    filtered_pur = filtered_pur[(filtered_pur[c_ord_date].dt.date >= date_range[0]) & (filtered_pur[c_ord_date].dt.date <= date_range[1])]

                    if c_comp and c_comp in filtered_pur.columns:
                        sel_comp = f2.multiselect("الشركة", filtered_pur[c_comp].unique())
                        if sel_comp: filtered_pur = filtered_pur[filtered_pur[c_comp].isin(sel_comp)]
                    if c_emp and c_emp in filtered_pur.columns:
                        sel_emp = f3.multiselect("الموظف", filtered_pur[c_emp].unique())
                        if sel_emp: filtered_pur = filtered_pur[filtered_pur[c_emp].isin(sel_emp)]
                    if c_unit and c_unit in filtered_pur.columns:
                        sel_unit = f4.multiselect("الوحدة", filtered_pur[c_unit].unique())
                        if sel_unit: filtered_pur = filtered_pur[filtered_pur[c_unit].isin(sel_unit)]
                        
                    submitted_pur_cat = st.form_submit_button("تطبيق")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المطلوب", f"{filtered_pur[c_req].sum():,.0f}" if c_req and c_req in filtered_pur.columns else "0")
            k2.metric("الرصيد الحالي", f"{filtered_pur[c_cur].sum():,.0f}" if c_cur and c_cur in filtered_pur.columns else "0")
            k3.metric("الشركات الموردة", f"{filtered_pur[c_comp].nunique()}" if c_comp and c_comp in filtered_pur.columns else "0")
            k4.metric("الموظفين", f"{filtered_pur[c_emp].nunique()}" if c_emp and c_emp in filtered_pur.columns else "0")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>مؤشرات الشركات والمتابعة</h3>", unsafe_allow_html=True)
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_comp and c_req and c_comp in filtered_pur.columns and c_req in filtered_pur.columns:
                        comp_data = filtered_pur.groupby(c_comp)[c_req].sum().reset_index()
                        fig_comp = px.pie(comp_data, values=c_req, names=c_comp, hole=0.5, title="توزيع الطلبات للشركات", color_discrete_sequence=gf_colors)
                        fig_comp.update_traces(textposition='inside', textinfo='percent')
                        fig_comp.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_comp, use_container_width=True)
                with row1_c2:
                    if c_emp and c_req and c_emp in filtered_pur.columns and c_req in filtered_pur.columns:
                        emp_data = filtered_pur.groupby(c_emp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=True)
                        fig_emp = px.bar(emp_data, x=c_req, y=c_emp, orientation='h', title="متابعة الموظفين")
                        fig_emp.update_traces(marker_color='#8ab4f8')
                        fig_emp.update_layout(**gf_layout, showlegend=False)
                        st.plotly_chart(fig_emp, use_container_width=True)
            except Exception: pass
                
            st.markdown("<hr>", unsafe_allow_html=True)
            try:
                st.markdown("<h3>المطلوب مقابل الرصيد</h3>", unsafe_allow_html=True)
                if c_item and c_req and c_cur and c_item in filtered_pur.columns and c_req in filtered_pur.columns and c_cur in filtered_pur.columns:
                    top_items = filtered_pur.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
                    melted_items = top_items.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                    fig_compare = px.bar(melted_items, x=c_item, y='الكمية', color='النوع', barmode='group', title="أعلى 10 مواد مطلوبة", color_discrete_map={c_req: '#f28b82', c_cur: '#8ab4f8'})
                    fig_compare.update_layout(**gf_layout, legend_title_text='')
                    st.plotly_chart(fig_compare, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات</h3>", unsafe_allow_html=True)
            with st.form("custom_pur_cat_form"):
                ca1, ca2 = st.columns(2)
                pur_cat_cols = [c for c in [c_emp, c_comp, c_unit, c_item, c_arr] if c and c in filtered_pur.columns]
                pur_num_cols = [c for c in [c_req, c_cur] if c and c in filtered_pur.columns]
                x_axis = ca1.selectbox("المحور:", pur_cat_cols) if pur_cat_cols else None
                y_axis = ca2.selectbox("المؤشر:", pur_num_cols) if pur_num_cols else None
                submitted_ca_pur_cat = st.form_submit_button("عرض")

            if submitted_ca_pur_cat and x_axis and y_axis:
                try:
                    custom_df = filtered_pur.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#fde293')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("قاعدة البيانات الكاملة"):
                st.dataframe(filtered_pur, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات...")

    # ------------------ 🔪 مشتريات المجزر ------------------
    elif st.session_state.active_tab == 'pur_slh':
        df_pur_slh, c_arr, c_ord_date, c_comp, c_req, c_cur, c_unit, c_dept, c_cat, c_item = load_pur_slh_data()
        
        if not df_pur_slh.empty:
            filtered_slh = df_pur_slh.copy()
            st.markdown("<h3>مشتريات المجزر والطلبيات</h3>", unsafe_allow_html=True)
            with st.expander("تصفية الطلبات", expanded=True):
                with st.form("pur_slh_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in filtered_slh.columns:
                        valid_dates = filtered_slh[c_ord_date].dropna()
                        if not valid_dates.empty:
                            min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                            use_date_pur = f1.checkbox("تفعيل الفلتر", value=False)
                            if use_date_pur:
                                date_range = f1.date_input("الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                                if len(date_range) == 2:
                                    filtered_slh = filtered_slh[(filtered_slh[c_ord_date].dt.date >= date_range[0]) & (filtered_slh[c_ord_date].dt.date <= date_range[1])]

                    if c_comp and c_comp in filtered_slh.columns:
                        sel_comp = f2.multiselect("الشركة", filtered_slh[c_comp].unique())
                        if sel_comp: filtered_slh = filtered_slh[filtered_slh[c_comp].isin(sel_comp)]

                    if c_cat and c_cat in filtered_slh.columns:
                        sel_cat = f3.multiselect("التصنيف", filtered_slh[c_cat].unique())
                        if sel_cat: filtered_slh = filtered_slh[filtered_slh[c_cat].isin(sel_cat)]

                    if c_arr and c_arr in filtered_slh.columns:
                        sel_arr = f4.multiselect("الحالة", filtered_slh[c_arr].unique())
                        if sel_arr: filtered_slh = filtered_slh[filtered_slh[c_arr].isin(sel_arr)]
                        
                    submitted_pur_slh = st.form_submit_button("تطبيق")

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي المطلوب", f"{filtered_slh[c_req].sum():,.0f}" if c_req and c_req in filtered_slh.columns else "0")
            k2.metric("إجمالي الرصيد الحالي", f"{filtered_slh[c_cur].sum():,.0f}" if c_cur and c_cur in filtered_slh.columns else "0")
            k3.metric("الشركات", f"{filtered_slh[c_comp].nunique()}" if c_comp and c_comp in filtered_slh.columns else "0")
            k4.metric("التصنيفات", f"{filtered_slh[c_cat].nunique()}" if c_cat and c_cat in filtered_slh.columns else "0")
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>الهيكلية للطلبات</h3>", unsafe_allow_html=True)
                if c_cat and c_item and c_req and c_cat in filtered_slh.columns and c_item in filtered_slh.columns and c_req in filtered_slh.columns:
                    tree_data = filtered_slh[filtered_slh[c_req] > 0].dropna(subset=[c_cat, c_item])
                    tree_data[c_cat] = tree_data[c_cat].astype(str)
                    tree_data[c_item] = tree_data[c_item].astype(str)
                    
                    if not tree_data.empty:
                        fig_tree = px.treemap(tree_data, path=[px.Constant("المشتريات"), c_cat, c_item], values=c_req, color=c_req, color_continuous_scale='Blues')
                        fig_tree.update_traces(root_color="#292a2d", textinfo="label+value")
                        fig_tree.update_layout(**gf_layout, height=500)
                        st.plotly_chart(fig_tree, use_container_width=True)
            except Exception: pass
                    
            st.markdown("<hr>", unsafe_allow_html=True)

            try:
                st.markdown("<h3>مقارنة الأرصدة والشركات</h3>", unsafe_allow_html=True)
                row2_c1, row2_c2 = st.columns(2)
                with row2_c1:
                    if c_item and c_req and c_cur and c_item in filtered_slh.columns and c_req in filtered_slh.columns and c_cur in filtered_slh.columns:
                        top_slh_items = filtered_slh.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index()
                        melted_slh = top_slh_items.melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                        fig_comp_slh = px.bar(melted_slh, x='الكمية', y=c_item, color='النوع', orientation='h', barmode='group', title="المطلوب مقابل الرصيد", color_discrete_map={c_req: '#f28b82', c_cur: '#8ab4f8'})
                        fig_comp_slh.update_layout(**gf_layout, legend_title_text='')
                        st.plotly_chart(fig_comp_slh, use_container_width=True)

                with row2_c2:
                    if c_comp and c_req and c_comp in filtered_slh.columns and c_req in filtered_slh.columns:
                        comp_perf = filtered_slh.groupby(c_comp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=True).head(10)
                        fig_comp_bar = px.bar(comp_perf, x=c_req, y=c_comp, orientation='h', title="أعلى الشركات الموردة")
                        fig_comp_bar.update_traces(marker_color='#81c995')
                        fig_comp_bar.update_layout(**gf_layout)
                        st.plotly_chart(fig_comp_bar, use_container_width=True)
            except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3>مختبر التحليلات</h3>", unsafe_allow_html=True)
            with st.form("custom_pur_slh_form"):
                ca1, ca2 = st.columns(2)
                pur_slh_cat_cols = [c for c in [c_arr, c_comp, c_dept, c_cat, c_unit, c_item] if c and c in filtered_slh.columns]
                pur_slh_num_cols = [c for c in [c_req, c_cur] if c and c in filtered_slh.columns]
                x_axis = ca1.selectbox("المحور:", pur_slh_cat_cols) if pur_slh_cat_cols else None
                y_axis = ca2.selectbox("المؤشر:", pur_slh_num_cols) if pur_slh_num_cols else None
                submitted_ca_pur_slh = st.form_submit_button("عرض")

            if submitted_ca_pur_slh and x_axis and y_axis:
                try:
                    custom_df = filtered_slh.groupby(x_axis)[y_axis].sum().reset_index().sort_values(by=y_axis, ascending=False).head(20)
                    fig_custom = px.bar(custom_df, x=x_axis, y=y_axis, title=f"تحليل {y_axis}")
                    fig_custom.update_traces(marker_color='#fde293')
                    fig_custom.update_layout(**gf_layout)
                    st.plotly_chart(fig_custom, use_container_width=True)
                except Exception: pass

            st.markdown("<hr>", unsafe_allow_html=True)
            with st.expander("قاعدة البيانات الكاملة"):
                st.dataframe(filtered_slh, use_container_width=True)
        else:
            st.warning("⚠️ لا توجد بيانات...")

except Exception as e:
    st.error("جاري إعادة التهيئة...")
    st.code(traceback.format_exc())
