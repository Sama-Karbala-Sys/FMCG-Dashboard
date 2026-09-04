import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import datetime
import time
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
            background-color: #202124 !important; /* لون خلفية Google Finance الداكن */
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
        /* تعديل سهم الصعود والنزول في الكروت */
        div[data-testid="stMetricDelta"] svg {
            display: none;
        }
        div[data-testid="stMetricDelta"] > div {
             font-size: 0.9rem !important;
        }

        /* =========================================
           1. التابات (الأقسام العلوية) - ستايل Google Finance
           ========================================= */
        div.row-widget.stRadio > div {
            display: flex; flex-direction: row; justify-content: flex-start; gap: 20px;
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
            border-bottom: 2px solid #8ab4f8 !important; /* خط أزرق تحت القسم النشط */
        }
        div.stRadio > div[role="radiogroup"] > label[data-checked="true"] p { color: #8ab4f8 !important; font-weight: bold !important; }
        div.stRadio > div[role="radiogroup"] > label p { color: #e8eaed !important; font-size: 1rem !important; margin: 0; }


        /* =========================================
           2. الكروت الإحصائية (Metrics / Cards)
           ========================================= */
        div[data-testid="metric-container"] {
            background-color: #292a2d !important; /* لون الكروت */
            border: 1px solid #3c4043;
            padding: 20px;
            border-radius: 8px;
            box-shadow: none;
        }

        /* =========================================
           3. الرسوم البيانية (Charts)
           ========================================= */
        .stPlotlyChart {
            background-color: #292a2d !important;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #3c4043;
        }

        /* =========================================
           4. الفلاتر والقوائم المنسدلة (Selectboxes)
           ========================================= */
        div[data-baseweb="select"] > div, input {
            border-radius: 4px !important;
            background-color: #303134 !important; /* خلفية الحقول */
            border: 1px solid #5f6368 !important;
            color: #e8eaed !important;
        }
        div[data-baseweb="select"] > div:hover, input:hover {
            border-color: #8ab4f8 !important;
        }

        /* =========================================
           5. القوائم المطوية (Expanders) وزر التطبيق
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
            border: none; border-radius: 4px !important; font-weight: 500;
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #aecbfa !important;
        }
        
        /* =========================================
           6. الجداول (Dataframes)
           ========================================= */
        /* محاولة تحسين مظهر الجداول لتلائم الثيم الداكن */
        [data-testid="stDataFrame"] {
            background-color: #292a2d;
            border: 1px solid #3c4043;
            border-radius: 8px;
        }
        
        /* خط فاصل رمادي */
        hr {
            border-top: 1px solid #3c4043 !important;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        
        h1, h2, h3 {
            color: #e8eaed !important;
            font-weight: 400 !important;
        }
        h1 { font-size: 1.5rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .success-text { color: #81c995 !important; } /* لون أخضر Google Finance */
        .danger-text { color: #f28b82 !important; } /* لون أحمر Google Finance */
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. رأس الصفحة، حالة النظام، وزر التحديث
# ==========================================
col_title, col_btn = st.columns([5, 1])
with col_title:
    st.markdown("<h1><span style='color: #8ab4f8;'>Finance</span> FMCG</h1>", unsafe_allow_html=True)
    current_time = datetime.datetime.now().strftime("%d %B, %H:%M UTC")
    st.markdown(f"<p style='color: #9aa0a6; font-size: 0.85rem; margin-top: -10px;'>الأسواق مفتوحة • {current_time}</p>", unsafe_allow_html=True)
with col_btn:
    st.write("") 
    if st.button("تحديث", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 3. شريط التابات
# ==========================================
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'mat_new' # جعل التاب الجديد هو الافتراضي

tabs_dict = {
    "المواد (الجديد)": "mat_new", # التاب الجديد بناء على صورتك
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

# 🔴 دالة سحب البيانات للقسم الجديد (من صورتك) 🔴
@st.cache_data(ttl=600)
def load_new_materials_data():
    # 🔴🔴🔴 يجب وضع الرابط الفعلي لملف الـ CSV الخاص بالصورة الثانية هنا 🔴🔴🔴
    # سأضع لك رابطاً وهمياً لكي يعمل الكود، يرجى تغييره برابط Google Sheet (Pub -> CSV) الحقيقي
    url = "ضع_الرابط_هنا" 
    
    # ------------------ جزء محاكاة البيانات لغرض العرض ------------------
    # إذا لم تضع رابطاً، سيقوم هذا الجزء بتوليد بيانات تشبه صورتك حتى ترى التصميم يعمل
    if url == "ضع_الرابط_هنا":
        data = {
            'التاريخ': ['8/1/2026']*20,
            'نوع الاذن': ['افتتاحي']*20,
            'القسم': ['الاحشاء']*20,
            'كود المادة': ['51529', '51530', '51531', '51532', '51533', '51534', '51523', '51524', '51525', '51526', '51527', '51528', '51421', '51422', '51423', '65035', '65034', '65033', '65073', '67306'],
            'المادة': ['توب فلم / كبد دجاج طازج الريان 450 غرام', 'توب فلم / حواصل دجاج طازج الريان 450 غرام', 'توب فلم / قلب دجاج طازج الريان 450 غرام', 'توب فلم / كبد دجاج طازج الريان 900 غرام', 'توب فلم / حواصل دجاج طازج الريان 900 غرام', 'توب فلم / قلب دجاج طازج الريان 900 غرام', 'توب فلم / كبد دجاج طازج البوادي 450 غرام', 'توب فلم / حواصل دجاج طازج البوادي 450 غرام', 'توب فلم / قلب دجاج طازج البوادي 450 غرام', 'توب فلم / كبد دجاج طازج البوادي 900 غرام', 'توب فلم / حواصل دجاج طازج البوادي 900 غرام', 'توب فلم / قلب دجاج طازج البوادي 900 غرام', 'Sealed Air 450 غرام', 'Sealed Air 450 غرام', 'Sealed Air 450 غرام', 'Sealed Air 450 غرام', 'Sealed Air 450 غرام', 'Sealed Air 450 غرام', 'Sealed Air 900 غرام', 'توب فلم / كبد دجاج طازج الريان 450 غرام نايكو'],
            'الوحدة': ['Mtr']*20,
            'الكمية': [0, 0, 0, 0, 0, 0, 0, 0, 0, 21000, 28000, 0, 0, 0, 0, 44000, 23000, 48960, 47000, 183100],
            'فلتر الارصدة': ['الكل']*20,
            'الرصيد الحالي': [0, 0, 0, 0, 0, 0, 0, 0, 0, 21000, 28000, 0, 0, 0, 0, 44000, 23000, 48960, 47000, 183100],
            'التصنيف': ['كبد 450 غرام ريان', 'حواصل 450 غرام ريان', 'قلوب 450 غرام ريان', 'كبد 900 غرام ريان', 'حواصل 900 غرام ريان', 'قلوب 900 غرام ريان', 'كبد 450 غرام بوادي', 'حواصل 450 غرام بوادي', 'قلوب 450 غرام بوادي', 'كبد 900 غرام بوادي', 'حواصل 900 غرام بوادي', 'قلوب 900 غرام بوادي', 'كبد 450 غرام ريان', 'حواصل 450 غرام ريان', 'قلوب 450 غرام ريان', 'توب فلم / حواصل دجاج محمد الكفيل 450 غرام', 'توب فلم / قلب دجاج محمد الكفيل 450 غرام', 'توب فلم / كبد دجاج محمد الكفيل 450 غرام', 'توب فلم / كبد دجاج محمد الكفيل 900 غرام', 'حواصل 450 غرام ريان']
        }
        df = pd.DataFrame(data)
        return df, 'التاريخ', 'القسم', 'المادة', 'الوحدة', 'الكمية', 'الرصيد الحالي', 'التصنيف'
    # -------------------------------------------------------------------------
    
    try:
        df = fetch_sheet_csv(url)
        if df.empty: return pd.DataFrame(), None, None, None, None, None, None, None
        df = clean_columns(df)
        
        c_date = next((c for c in df.columns if 'تاريخ' in c), None)
        c_dept = next((c for c in df.columns if 'قسم' in c), None)
        c_item = next((c for c in df.columns if 'مادة' in c and 'كود' not in c), None)
        c_unit = next((c for c in df.columns if 'وحدة' in c), None)
        c_qty = next((c for c in df.columns if 'كمية' in c), None)
        c_bal = next((c for c in df.columns if 'رصيد' in c), None)
        c_cat = next((c for c in df.columns if 'تصنيف' in c), None)
        
        for c in [c_qty, c_bal]:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('-', '0'), errors='coerce').fillna(0)
                
        return df, c_date, c_dept, c_item, c_unit, c_qty, c_bal, c_cat
    except Exception:
        return pd.DataFrame(), None, None, None, None, None, None, None


# =========================================================================
# دوال الأقسام السابقة (مختصرة لعدم الإطالة، يجب إبقاء دوالك كما هي)
# =========================================================================
# ... (ضع دوال load_slh_general_data, load_gov_data, load_freezer_data, 
# load_slaughterhouse_data, load_raw_materials_data, load_pur_cat_data, load_pur_slh_data هنا) ...

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
        return df, c_cat, c_item, c_unit, c_bal, c_confirmed, c_total_bal, c_req, c_forecast, c_coverage
    except Exception: return pd.DataFrame(), None, None, None, None, None, None, None, None, None

@st.cache_data(ttl=600)
def load_gov_data(): return pd.DataFrame(), None, None, None, None, None, None, None, None, None
@st.cache_data(ttl=600)
def load_freezer_data(): return pd.DataFrame(), None, None, None, None, None, None, None
@st.cache_data(ttl=600)
def load_slaughterhouse_data(): return pd.DataFrame(), None, None, None, None, None, None, None
@st.cache_data(ttl=600)
def load_raw_materials_data(): return pd.DataFrame(), None, None, None, None, None, None, None
@st.cache_data(ttl=600)
def load_pur_cat_data(): return pd.DataFrame(), None, None, None, None, None, None, None, None
@st.cache_data(ttl=600)
def load_pur_slh_data(): return pd.DataFrame(), None, None, None, None, None, None, None, None, None

# ==========================================
# 5. منطق عرض الأقسام 
# ==========================================
try:
    # ------------------ 📊 القسم الجديد (بناء على صورتك) ------------------
    if st.session_state.active_tab == 'mat_new':
        df_new, c_date, c_dept, c_item, c_unit, c_qty, c_bal, c_cat = load_new_materials_data()
        
        if not df_new.empty:
            # تخطيط يشبه Google Finance
            st.markdown("<h3>نظرة عامة على الأرصدة</h3>", unsafe_allow_html=True)
            
            # --- 1. الكروت العلوية (Metrics) ---
            k1, k2, k3, k4 = st.columns(4)
            total_bal = df_new[c_bal].sum() if c_bal and c_bal in df_new.columns else 0
            total_qty = df_new[c_qty].sum() if c_qty and c_qty in df_new.columns else 0
            items_count = df_new[c_item].nunique() if c_item and c_item in df_new.columns else 0
            
            # محاكاة شكل التغير في السهم
            k1.metric("إجمالي الرصيد الحالي", f"{total_bal:,.0f}", "+0.0% منذ الافتتاح")
            k2.metric("الكمية المدخلة (الكمية)", f"{total_qty:,.0f}")
            k3.metric("عدد المواد الفريدة", f"{items_count}")
            k4.metric("السجلات", str(len(df_new)))
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- 2. الرسوم البيانية (Line Charts) بستايل Finance ---
            st.markdown("<h3>الأداء والتوزيع</h3>", unsafe_allow_html=True)
            row_c1, row_c2 = st.columns([2, 1])
            
            with row_c1:
                # رسم بياني للرصيد لأعلى 10 مواد (محاكاة حركة السهم)
                if c_item and c_bal and c_item in df_new.columns:
                    top_bal = df_new[df_new[c_bal] > 0].sort_values(by=c_bal, ascending=False).head(10)
                    if not top_bal.empty:
                        # رسم خطي (Area) باللون الأخضر المميز لـ Google Finance
                        fig_line = px.area(top_bal, x=c_item, y=c_bal, title="أعلى أرصدة المواد (الرئيسية)")
                        fig_line.update_traces(line_color='#81c995', fillcolor='rgba(129, 201, 149, 0.2)')
                        fig_line.update_layout(
                            paper_bgcolor='#292a2d', plot_bgcolor='#292a2d', font=dict(color='#e8eaed'),
                            xaxis=dict(showgrid=False, color='#e8eaed'), yaxis=dict(showgrid=True, gridcolor='#3c4043', color='#e8eaed')
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
            
            with row_c2:
                # قائمة أسهم/مواد مصغرة (تشبه قائمة "قائمة الأسهم" يمين Google Finance)
                st.markdown("<h4 style='color:#e8eaed; margin-bottom: 10px;'>أعلى أرصدة التصنيفات</h4>", unsafe_allow_html=True)
                if c_cat and c_bal and c_cat in df_new.columns:
                    top_cats = df_new.groupby(c_cat)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=False).head(6)
                    for index, row in top_cats.iterrows():
                        val = row[c_bal]
                        cat_name = row[c_cat]
                        if val > 0:
                            # تصميم صف يشبه سهم منفصل
                            st.markdown(f"""
                            <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #3c4043; padding: 10px 0;'>
                                <div>
                                    <div style='font-weight: 500; font-size: 0.95rem;'>{val:,.0f}</div>
                                    <div style='color: #81c995; font-size: 0.8rem;'>+1.2% ↑</div>
                                </div>
                                <div style='text-align: left;'>
                                    <div style='font-weight: 500;'>{cat_name[:15]}..</div>
                                    <div style='color: #9aa0a6; font-size: 0.8rem;'>تصنيف</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            
            # --- 3. الفلاتر والجدول بستايل داكن ---
            st.markdown("<h3>تفاصيل البيانات (أصول ذات صلة)</h3>", unsafe_allow_html=True)
            with st.expander("تصفية البيانات", expanded=False):
                with st.form("new_mat_form"):
                    f1, f2 = st.columns(2)
                    sel_dept = f1.multiselect("القسم", df_new[c_dept].unique() if c_dept in df_new.columns else [])
                    sel_cat = f2.multiselect("التصنيف", df_new[c_cat].unique() if c_cat in df_new.columns else [])
                    submitted = st.form_submit_button("تطبيق")
            
            if sel_dept: df_new = df_new[df_new[c_dept].isin(sel_dept)]
            if sel_cat: df_new = df_new[df_new[c_cat].isin(sel_cat)]
            
            st.dataframe(df_new, use_container_width=True)

        else:
            st.warning("⚠️ لا توجد بيانات. تأكد من رابط الـ CSV.")


    # ------------------ الأقسام القديمة (باختصار) ------------------
    # يمكنك نسخ الأقسام القديمة من الكود السابق ولصقها هنا
    # مع العلم أن تصميمها سيتأثر بستايل الـ CSS الداكن الجديد (مما يجعلها تبدو كـ Google Finance تلقائياً)
    elif st.session_state.active_tab == 'slh_gen':
        st.write("قسم عام المجزر")
    # ... إلخ


except Exception as e:
    st.error("حدث خطأ")
