import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io
import datetime
import time
import traceback

# ==========================================
# 1. إعدادات الصفحة (نظام الحماية من الانهيار)
# ==========================================
try:
    st.set_page_config(page_title="FMCG Enterprise Dashboard", layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass

try:
    st.markdown("""
        <style>
            .stApp { direction: rtl; }
            div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] { text-align: right; }
            div[data-testid="stSidebar"] { background-color: #0f172a; border-left: 1px solid #1e293b; }
            .kpi-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; }
            .kpi-title { color: #94a3b8; font-size: 16px; margin-bottom: 10px; }
            .kpi-value { color: #38bdf8; font-size: 28px; font-weight: bold; }
            .alert-card { padding: 15px; border-radius: 8px; margin-bottom: 10px; border-right: 5px solid; }
            .alert-red { background-color: rgba(239, 68, 68, 0.1); border-color: #ef4444; color: #fca5a5; }
            .alert-orange { background-color: rgba(245, 158, 11, 0.1); border-color: #f59e0b; color: #fcd34d; }
            div[data-testid="stFormSubmitButton"] > button {
                height: 50px; font-size: 18px !important; font-weight: bold !important;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important; color: #ffffff !important;
                border: none; border-radius: 8px !important; width: 100%; transition: all 0.3s;
            }
            div[data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. دوال السحب العنيدة (نظام المحاولات المتعددة)
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
        res = {'df': pd.DataFrame(), 'c_item': None, 'c_prod': None, 'c_sold': None, 'c_short': None, 'c_final': None}
        if df_raw.empty: return res
        df = clean_columns(df_raw.copy())
        
        res['c_item'] = next((c for c in df.columns if 'ماد' in c), None)
        res['c_prod'] = next((c for c in df.columns if 'نتاج' in c), None)
        res['c_sold'] = next((c for c in df.columns if 'مباع' in c or 'صادر' in c), None)
        res['c_short'] = next((c for c in df.columns if 'نقص' in c), None)
        res['c_final'] = next((c for c in df.columns if 'نهائي' in c), None)
        
        for c in [res['c_prod'], res['c_sold'], res['c_short'], res['c_final']]:
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
                row_str = ' '.join(str(val) for val in row.values)
                if 'المادة' in row_str or 'الكمية' in row_str or 'تاريخ' in row_str:
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
    def load_pur_data():
        df_cat_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5lFKwIUSMCyYxRvpRMUl3PDlO6JY-x07zi0FgH9O2Atbryh4TjEpH7UGxtQ_Cw/pub?output=csv")
        df_slh_raw = fetch_sheet_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv")
        
        res = {'df_cat': pd.DataFrame(), 'df_slh': pd.DataFrame(), 'c_ord_date_c': None, 'c_comp_c': None, 'c_emp': None, 'c_req_c': None, 'c_cur_c': None, 'c_unit_c': None, 'c_item_c': None, 
               'c_ord_date_s': None, 'c_comp_s': None, 'c_arr_s': None, 'c_req_s': None, 'c_cur_s': None, 'c_item_s': None, 'c_cat_s': None}
        
        if not df_cat_raw.empty:
            df_cat = clean_columns(df_cat_raw.copy())
            res['c_ord_date_c'] = next((c for c in df_cat.columns if 'تاريخ' in c), None)
            res['c_comp_c'] = next((c for c in df_cat.columns if 'الشركة' in c), None)
            res['c_emp'] = next((c for c in df_cat.columns if 'الموظف' in c), None)
            res['c_req_c'] = next((c for c in df_cat.columns if 'المطلوب' in c), None)
            res['c_cur_c'] = next((c for c in df_cat.columns if 'الرصيد' in c), None)
            res['c_unit_c'] = next((c for c in df_cat.columns if 'الوحدة' in c), None)
            res['c_item_c'] = next((c for c in df_cat.columns if 'اسم المادة' in c or 'المادة' in c), None)
            for c in [res['c_req_c'], res['c_cur_c']]:
                if c and c in df_cat.columns: df_cat[c] = pd.to_numeric(df_cat[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
            res['df_cat'] = df_cat
            
        if not df_slh_raw.empty:
            df_slh = clean_columns(df_slh_raw.copy())
            res['c_ord_date_s'] = next((c for c in df_slh.columns if 'تاريخ' in c), None)
            res['c_comp_s'] = next((c for c in df_slh.columns if 'شركة' in c or 'الشركة' in c), None)
            res['c_arr_s'] = next((c for c in df_slh.columns if 'وصول' in c), None)
            res['c_req_s'] = next((c for c in df_slh.columns if 'المطلوب' in c), None)
            res['c_cur_s'] = next((c for c in df_slh.columns if 'الرصيد' in c), None)
            res['c_cat_s'] = next((c for c in df_slh.columns if 'تصنيف' in c), None)
            res['c_item_s'] = next((c for c in df_slh.columns if 'اسم المادة' in c or ('المادة' in c and 'تصنيف' not in c)), None)
            for c in [res['c_req_s'], res['c_cur_s']]:
                if c and c in df_slh.columns: df_slh[c] = pd.to_numeric(df_slh[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('', '0'), errors='coerce').fillna(0)
            res['df_slh'] = df_slh
            
        return res

    # ==========================================
    # 4. القائمة الجانبية (Sidebar)
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=80)
        st.title("القائمة الرئيسية")
        st.markdown("---")
        
        menu_options = [
            "🏠 لوحة القيادة (الرئيسية)", 
            "🚨 التنبيهات الذكية",
            "🔎 تفاصيل المادة (360°)",
            "📍 مبيعات المحافظات", 
            "🧊 مخازن الثلاجات", 
            "❄️ مخازن المجزر", 
            "📦 المواد الأولية",
            "🛒 مشتريات المصنفات", 
            "🔪 مشتريات المجزر"
        ]
        
        choice = st.radio("انتقل إلى:", menu_options)
        st.markdown("---")
        if st.button("🔄 مزامنة السحابة (مسح الذاكرة)", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.caption(f"آخر تحديث: {datetime.datetime.now().strftime('%H:%M')}")

    # ==========================================
    # 5. جلب كل البيانات
    # ==========================================
    data_gov = load_gov_data()
    data_frz = load_freezer_data()
    data_slh = load_slh_data()
    data_mat = load_mat_data()
    data_pur = load_pur_data()

    def check_empty(df, section_name):
        if df.empty:
            st.warning(f"⚠️ لا توجد بيانات مسحوبة لقسم ({section_name}). حاول عمل تحديث.")
            return True
        return False

    # ----------------- 🏠 الرئيسية -----------------
    if choice == "🏠 لوحة القيادة (الرئيسية)":
        st.title("🏠 لوحة القيادة الشاملة (Enterprise Overview)")
        
        total_sales_qty = data_gov['df'][data_gov['c_qty']].sum() if not data_gov['df'].empty and data_gov['c_qty'] in data_gov['df'].columns else 0
        total_stock_frz = data_frz['df'][data_frz['c_final']].sum() if not data_frz['df'].empty and data_frz['c_final'] in data_frz['df'].columns else 0
        total_stock_slh = data_slh['df'][data_slh['c_qty']].sum() if not data_slh['df'].empty and data_slh['c_qty'] in data_slh['df'].columns else 0
        total_stock = total_stock_frz + total_stock_slh
        total_req_cat = data_pur['df_cat'][data_pur['c_req_c']].sum() if not data_pur['df_cat'].empty and data_pur['c_req_c'] in data_pur['df_cat'].columns else 0
        total_req_slh = data_pur['df_slh'][data_pur['c_req_s']].sum() if not data_pur['df_slh'].empty and data_pur['c_req_s'] in data_pur['df_slh'].columns else 0
        total_purchases = total_req_cat + total_req_slh
        total_short_frz = data_frz['df'][data_frz['c_short']].sum() if not data_frz['df'].empty and data_frz['c_short'] in data_frz['df'].columns else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi-card"><div class="kpi-title">🛒 إجمالي المبيعات (عدد)</div><div class="kpi-value">{total_sales_qty:,.0f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi-card"><div class="kpi-title">📦 إجمالي المخزون الفعلي</div><div class="kpi-value">{total_stock:,.0f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi-card"><div class="kpi-title">📥 إجمالي الطلبات (مشتريات)</div><div class="kpi-value">{total_purchases:,.0f}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi-card"><div class="kpi-title">⚠️ إجمالي النقص/التالف</div><div class="kpi-value text-red-500">{total_short_frz:,.0f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        row1, row2 = st.columns(2)
        with row1:
            if not data_gov['df'].empty and data_gov['c_gov'] in data_gov['df'].columns and data_gov['c_ton'] in data_gov['df'].columns:
                fig_gov = px.bar(data_gov['df'].groupby(data_gov['c_gov'])[data_gov['c_ton']].sum().reset_index().nlargest(7, data_gov['c_ton']), 
                                 x=data_gov['c_ton'], y=data_gov['c_gov'], orientation='h', title="🏆 أعلى المحافظات سحباً (طن)", color=data_gov['c_ton'], color_continuous_scale='Blues')
                st.plotly_chart(fig_gov, use_container_width=True)
        with row2:
            if not data_pur['df_cat'].empty and data_pur['c_item_c'] in data_pur['df_cat'].columns and data_pur['c_req_c'] in data_pur['df_cat'].columns:
                fig_pur = px.pie(data_pur['df_cat'].groupby(data_pur['c_item_c'])[data_pur['c_req_c']].sum().reset_index().nlargest(5, data_pur['c_req_c']), 
                                 values=data_pur['c_req_c'], names=data_pur['c_item_c'], hole=0.5, title="🔥 أكثر 5 مواد مطلوبة للتوريد", color_discrete_sequence=px.colors.sequential.Oranges_r)
                st.plotly_chart(fig_pur, use_container_width=True)

    # ----------------- 🚨 التنبيهات -----------------
    elif choice == "🚨 التنبيهات الذكية":
        st.title("🚨 مركز التنبيهات والمراقبة الذكية")
        st.markdown("---")
        alerts_found = False
        if not data_frz['df'].empty and data_frz['c_item'] in data_frz['df'].columns and data_frz['c_short'] in data_frz['df'].columns:
            short_items = data_frz['df'][data_frz['df'][data_frz['c_short']] > 0]
            if not short_items.empty:
                alerts_found = True
                st.subheader("🔴 مواد بها نقص أو تالف (تتطلب مراجعة)")
                for _, row in short_items.nlargest(5, data_frz['c_short']).iterrows():
                    st.markdown(f'<div class="alert-card alert-red"><b>المادة:</b> {row[data_frz["c_item"]]} | <b>كمية النقص:</b> {row[data_frz["c_short"]]:,.0f}</div>', unsafe_allow_html=True)
                    
        if not data_pur['df_cat'].empty and data_pur['c_item_c'] in data_pur['df_cat'].columns and data_pur['c_req_c'] in data_pur['df_cat'].columns and data_pur['c_cur_c'] in data_pur['df_cat'].columns:
            df_cat = data_pur['df_cat']
            critical_orders = df_cat[df_cat[data_pur['c_req_c']] > (df_cat[data_pur['c_cur_c']] * 3)]
            if not critical_orders.empty:
                alerts_found = True
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🟠 فجوة توريد (المطلوب يتجاوز الرصيد بكثير)")
                for _, row in critical_orders.nlargest(5, data_pur['c_req_c']).iterrows():
                    st.markdown(f'<div class="alert-card alert-orange"><b>المادة:</b> {row[data_pur["c_item_c"]]} | <b>المطلوب:</b> {row[data_pur["c_req_c"]]:,.0f} | <b>الرصيد:</b> {row[data_pur["c_cur_c"]]:,.0f}</div>', unsafe_allow_html=True)

        if not alerts_found:
            st.success("✅ وضع النظام مستقر، لا توجد تنبيهات حرجة حالياً.")

    # ----------------- 🔎 تفاصيل المادة -----------------
    elif choice == "🔎 تفاصيل المادة (360°)":
        st.title("🔎 البحث الشامل عن مادة (360-View)")
        all_items = set()
        if not data_gov['df'].empty and data_gov['c_item'] in data_gov['df'].columns: all_items.update(data_gov['df'][data_gov['c_item']].dropna().unique())
        if not data_frz['df'].empty and data_frz['c_item'] in data_frz['df'].columns: all_items.update(data_frz['df'][data_frz['c_item']].dropna().unique())
        if not data_slh['df'].empty and data_slh['c_item'] in data_slh['df'].columns: all_items.update(data_slh['df'][data_slh['c_item']].dropna().unique())
        all_items = [i for i in list(all_items) if str(i).strip() != '']
        
        if all_items:
            selected_item = st.selectbox("ابحث عن المادة (اكتب للبحث):", sorted(all_items))
            if selected_item:
                c1, c2, c3 = st.columns(3)
                sales_qty = data_gov['df'][data_gov['df'][data_gov['c_item']] == selected_item][data_gov['c_qty']].sum() if not data_gov['df'].empty and data_gov['c_item'] in data_gov['df'].columns else 0
                stock_frz = data_frz['df'][data_frz['df'][data_frz['c_item']] == selected_item][data_frz['c_final']].sum() if not data_frz['df'].empty and data_frz['c_item'] in data_frz['df'].columns else 0
                stock_slh = data_slh['df'][data_slh['df'][data_slh['c_item']] == selected_item][data_slh['c_qty']].sum() if not data_slh['df'].empty and data_slh['c_item'] in data_slh['df'].columns else 0
                
                c1.metric("🛒 إجمالي المبيعات (عدد)", f"{sales_qty:,.0f}")
                c2.metric("🧊 المخزون في الثلاجات", f"{stock_frz:,.0f}")
                c3.metric("❄️ المخزون في المجزر", f"{stock_slh:,.0f}")
                st.markdown("---")
                if not data_gov['df'].empty and data_gov['c_item'] in data_gov['df'].columns and data_gov['c_gov'] in data_gov['df'].columns:
                    item_gov_df = data_gov['df'][data_gov['df'][data_gov['c_item']] == selected_item]
                    if not item_gov_df.empty:
                        st.markdown("#### 📍 المحافظات التي تستهلك هذه المادة:")
                        fig = px.pie(item_gov_df.groupby(data_gov['c_gov'])[data_gov['c_qty']].sum().reset_index(), values=data_gov['c_qty'], names=data_gov['c_gov'], hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)

    # ----------------- 📍 مبيعات المحافظات (بالفلاتر والرسومات الكاملة) -----------------
    elif choice == "📍 مبيعات المحافظات":
        st.title("📍 مبيعات المحافظات")
        df = data_gov['df'].copy()
        if not check_empty(df, "المحافظات"):
            c_date, c_gov, c_agent, c_item, c_cat, c_ff, c_label, c_ton, c_qty = data_gov['c_date'], data_gov['c_gov'], data_gov['c_agent'], data_gov['c_item'], data_gov['c_cat'], data_gov['c_ff'], data_gov['c_label'], data_gov['c_ton'], data_gov['c_qty']
            
            with st.expander("🔍 فلاتر قسم المحافظات", expanded=True):
                with st.form("gov_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("اختر الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_gov = f2.multiselect("📍 المحافظة", df[c_gov].unique() if c_gov and c_gov in df.columns else [])
                    sel_ff = f3.multiselect("❄️ طازج أو مجمد", df[c_ff].unique() if c_ff and c_ff in df.columns else [])
                    sel_label = f4.multiselect("🏷️ العلامة التجارية", df[c_label].unique() if c_label and c_label in df.columns else [])
                    submitted_gov = st.form_submit_button("🚀 تطبيق الفلاتر")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_gov: df = df[df[c_gov].isin(sel_gov)]
            if sel_ff: df = df[df[c_ff].isin(sel_ff)]
            if sel_label: df = df[df[c_label].isin(sel_label)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 إجمالي المبيعات (طن)", f"{df[c_ton].sum():,.2f}" if c_ton and c_ton in df.columns else "0")
            k2.metric("🔢 إجمالي المبيعات (عدد)", f"{df[c_qty].sum():,.0f}" if c_qty and c_qty in df.columns else "0")
            k3.metric("👥 الزبائن والوكلاء", f"{df[c_agent].nunique()}" if c_agent and c_agent in df.columns else "0")
            k4.metric("📄 المستندات المسجلة", f"{len(df)}")
            st.markdown("---")

            try:
                pie1, pie2, pie3 = st.columns(3)
                with pie1:
                    if c_cat and c_ton and c_cat in df.columns and c_ton in df.columns:
                        fig_cat = px.pie(df.groupby(c_cat)[c_ton].sum().reset_index(), values=c_ton, names=c_cat, hole=0.4, title="🛒 التصنيف (Category)")
                        fig_cat.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_cat, use_container_width=True)
                with pie2:
                    if c_ff and c_ton and c_ff in df.columns and c_ton in df.columns:
                        fig_ff = px.pie(df.groupby(c_ff)[c_ton].sum().reset_index(), values=c_ton, names=c_ff, color_discrete_sequence=['#3b82f6', '#06b6d4'], title="❄️ طازج ومجمد")
                        fig_ff.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_ff, use_container_width=True)
                with pie3:
                    if c_label and c_ton and c_label in df.columns and c_ton in df.columns:
                        fig_label = px.pie(df.groupby(c_label)[c_ton].sum().reset_index(), values=c_ton, names=c_label, color_discrete_sequence=['#f59e0b', '#ec4899'], title="🏷️ العلامة التجارية")
                        fig_label.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_label, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            try:
                if c_gov and c_ton and c_gov in df.columns and c_ton in df.columns:
                    fig_gov = px.bar(df.groupby(c_gov)[c_ton].sum().reset_index().sort_values(by=c_ton, ascending=True), x=c_ton, y=c_gov, orientation='h', color=c_gov, text_auto='.2s', title="📍 التوزيع حسب المحافظات")
                    fig_gov.update_layout(showlegend=False, height=450)
                    st.plotly_chart(fig_gov, use_container_width=True)

                bar1, bar2 = st.columns(2)
                with bar1:
                    if c_agent and c_ton and c_agent in df.columns and c_ton in df.columns:
                        fig_agent = px.bar(df.groupby(c_agent)[c_ton].sum().reset_index().sort_values(by=c_ton, ascending=False).head(10), x=c_agent, y=c_ton, color=c_ton, color_continuous_scale='Purples', text_auto='.2s', title="🏆 أفضل 10 زبائن (طن)")
                        st.plotly_chart(fig_agent, use_container_width=True)
                with bar2:
                    if c_item and c_qty and c_item in df.columns and c_qty in df.columns:
                        fig_item = px.bar(df.groupby(c_item)[c_qty].sum().reset_index().sort_values(by=c_qty, ascending=False).head(10), x=c_item, y=c_qty, color=c_qty, color_continuous_scale='Reds', text_auto='.2s', title="📦 أفضل 10 مواد مبيعاً (عدد)")
                        st.plotly_chart(fig_item, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            with st.expander("📋 عرض جدول تفاصيل المحافظات"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="gov.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

    # ----------------- 🧊 مخازن الثلاجات -----------------
    elif choice == "🧊 مخازن الثلاجات":
        st.title("🧊 مخازن الثلاجات")
        df = data_frz['df'].copy()
        if not check_empty(df, "الثلاجات"):
            c_item, c_frz, c_start, c_prod, c_sold, c_short, c_final = data_frz['c_item'], data_frz['c_frz'], data_frz['c_start'], data_frz['c_prod'], data_frz['c_sold'], data_frz['c_short'], data_frz['c_final']
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 المخزون الحالي", f"{df[c_final].sum():,.0f}" if c_final and c_final in df.columns else "0")
            k2.metric("🏭 إجمالي الإنتاج الداخلي", f"{df[c_prod].sum():,.0f}" if c_prod and c_prod in df.columns else "0")
            k3.metric("🛒 إجمالي المباع الصادر", f"{df[c_sold].sum():,.0f}" if c_sold and c_sold in df.columns else "0")
            k4.metric("⚠️ إجمالي النقص أو التالف", f"{df[c_short].sum():,.0f}" if c_short and c_short in df.columns else "0", delta="- هدر", delta_color="inverse")
            st.markdown("---")

            try:
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    if c_frz and c_final and c_frz in df.columns and c_final in df.columns:
                        fig_stock = px.bar(df.groupby(c_frz)[c_final].sum().reset_index().sort_values(by=c_final, ascending=False), x=c_frz, y=c_final, color=c_frz, text_auto='.2s', title="🧊 المخزون الحالي في كل ثلاجة")
                        st.plotly_chart(fig_stock, use_container_width=True)
                with row1_col2:
                    if c_frz and c_short and c_frz in df.columns and c_short in df.columns:
                        frz_short = df.groupby(c_frz)[c_short].sum().reset_index()
                        if frz_short[c_short].sum() > 0:
                            fig_short = px.pie(frz_short, values=c_short, names=c_frz, hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r, title="⚠️ توزيع النقص حسب الثلاجة")
                            st.plotly_chart(fig_short, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            try:
                if c_frz and c_prod and c_sold and c_frz in df.columns:
                    flow_melted = df.groupby(c_frz)[[c_prod, c_sold]].sum().reset_index().melt(id_vars=c_frz, value_vars=[c_prod, c_sold], var_name='العملية', value_name='الكمية')
                    fig_flow = px.bar(flow_melted, x=c_frz, y='الكمية', color='العملية', barmode='group', color_discrete_map={c_prod: '#10b981', c_sold: '#f43f5e'}, text_auto='.2s', title="🔄 مقارنة الإنتاج مقابل المباع")
                    st.plotly_chart(fig_flow, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول الثلاجات"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="frz.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

    # ----------------- ❄️ مخازن المجزر -----------------
    elif choice == "❄️ مخازن المجزر":
        st.title("❄️ مخازن المجزر")
        df = data_slh['df'].copy()
        if not check_empty(df, "المجزر"):
            c_date, c_qty, c_prev, c_prod, c_sold, c_item, c_code = data_slh['c_date'], data_slh['c_qty'], data_slh['c_prev'], data_slh['c_prod'], data_slh['c_sold'], data_slh['c_item'], data_slh['c_code']
            
            with st.expander("🔍 فلاتر مخازن المجزر", expanded=True):
                with st.form("slh_form"):
                    f1, f2 = st.columns(2)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("تحديد فترة المجزر", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_item = f2.multiselect("اختر المادة", df[c_item].unique() if c_item and c_item in df.columns else [])
                    submitted_slh = st.form_submit_button("🚀 تطبيق الفلاتر")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_item: df = df[df[c_item].isin(sel_item)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 إجمالي الكمية", f"{df[c_qty].sum():,.2f}" if c_qty and c_qty in df.columns else "0")
            k2.metric("🏭 إجمالي الإنتاج", f"{df[c_prod].sum():,.0f}" if c_prod and c_prod in df.columns else "0")
            k3.metric("🛒 إجمالي المباع", f"{df[c_sold].sum():,.0f}" if c_sold and c_sold in df.columns else "0")
            k4.metric("🔙 الرصيد السابق", f"{df[c_prev].sum():,.0f}" if c_prev and c_prev in df.columns else "0")
            st.markdown("---")

            try:
                pie1, pie2 = st.columns(2)
                with pie1:
                    t_prod, t_sold = df[c_prod].sum() if c_prod in df.columns else 0, df[c_sold].sum() if c_sold in df.columns else 0
                    if t_prod > 0 or t_sold > 0:
                        fig_pie1 = px.pie(pd.DataFrame({'العملية': ['الإنتاج', 'المباع'], 'الكمية': [t_prod, t_sold]}), values='الكمية', names='العملية', hole=0.4, title="🔄 نسبة الإنتاج مقابل المبيعات", color_discrete_sequence=['#10b981', '#f43f5e'])
                        fig_pie1.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_pie1, use_container_width=True)
                with pie2:
                    if c_item and c_qty and c_item in df.columns and c_qty in df.columns:
                        fig_pie2 = px.pie(df.groupby(c_item)[c_qty].sum().nlargest(5).reset_index(), values=c_qty, names=c_item, hole=0.4, title="📦 أعلى 5 مواد متوفرة", color_discrete_sequence=px.colors.sequential.Blues_r)
                        fig_pie2.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_pie2, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_item and c_prod and c_item in df.columns and c_prod in df.columns:
                        fig_prod = px.bar(df.groupby(c_item)[c_prod].sum().reset_index().sort_values(by=c_prod, ascending=True).tail(10), x=c_prod, y=c_item, orientation='h', color=c_prod, color_continuous_scale='Greens', text_auto='.2s', title="🏆 أعلى 10 مواد حسب الإنتاج")
                        st.plotly_chart(fig_prod, use_container_width=True)
                with row1_c2:
                    if c_item and c_qty and c_item in df.columns and c_qty in df.columns:
                        fig_qty = px.bar(df.groupby(c_item)[c_qty].sum().reset_index().sort_values(by=c_qty, ascending=True).tail(10), x=c_qty, y=c_item, orientation='h', color=c_qty, color_continuous_scale='Blues', text_auto='.2s', title="📦 أعلى 10 مواد حسب الكمية")
                        st.plotly_chart(fig_qty, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            with st.expander("📋 عرض جدول المجزر"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="slh.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

    # ----------------- 📦 المواد الأولية -----------------
    elif choice == "📦 المواد الأولية":
        st.title("📦 المواد الأولية")
        df = data_mat['df'].copy()
        if not check_empty(df, "المواد الأولية"):
            c_date, c_type, c_dept, c_item, c_qty, c_bal, c_cat = data_mat['c_date'], data_mat['c_type'], data_mat['c_dept'], data_mat['c_item'], data_mat['c_qty'], data_mat['c_bal'], data_mat['c_cat']
            
            with st.expander("🔍 فلاتر المواد الأولية", expanded=True):
                with st.form("mat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_date and c_date in df.columns:
                        df[c_date] = pd.to_datetime(df[c_date], errors='coerce')
                        valid_dates = df[c_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("اختر الفترة", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_dept = f2.multiselect("اختر القسم", df[c_dept].unique() if c_dept and c_dept in df.columns else [])
                    sel_type = f3.multiselect("نوع الإذن", df[c_type].unique() if c_type and c_type in df.columns else [])
                    sel_cat = f4.multiselect("التصنيف", df[c_cat].unique() if c_cat and c_cat in df.columns else [])
                    submitted_mat = st.form_submit_button("🚀 تطبيق الفلاتر")

            if len(date_range) == 2 and c_date: df = df[(df[c_date].dt.date >= date_range[0]) & (df[c_date].dt.date <= date_range[1])]
            if sel_dept: df = df[df[c_dept].isin(sel_dept)]
            if sel_type: df = df[df[c_type].isin(sel_type)]
            if sel_cat: df = df[df[c_cat].isin(sel_cat)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("📦 إجمالي الرصيد الحالي", f"{df[c_bal].sum():,.0f}" if c_bal and c_bal in df.columns else "0")
            k2.metric("🔄 إجمالي الكميات للحركة", f"{df[c_qty].sum():,.0f}" if c_qty and c_qty in df.columns else "0")
            k3.metric("🏷️ عدد المواد المختلفة", f"{df[c_item].nunique()}" if c_item and c_item in df.columns else "0")
            k4.metric("📄 إجمالي السجلات", f"{len(df)}")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_dept and c_bal and c_dept in df.columns and c_bal in df.columns:
                        fig_dept = px.bar(df.groupby(c_dept)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True), x=c_bal, y=c_dept, orientation='h', color=c_dept, text_auto='.2s', title="🏢 الأرصدة الحالية حسب القسم")
                        st.plotly_chart(fig_dept, use_container_width=True)
                with row1_c2:
                    if c_cat and c_bal and c_cat in df.columns and c_bal in df.columns:
                        fig_cat_mat = px.pie(df.groupby(c_cat)[c_bal].sum().reset_index(), values=c_bal, names=c_cat, hole=0.4, title="🏷️ توزيع الأرصدة حسب التصنيف")
                        fig_cat_mat.update_traces(textposition='inside', textinfo='percent')
                        st.plotly_chart(fig_cat_mat, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            try:
                if c_item and c_bal and c_item in df.columns and c_bal in df.columns:
                    fig_top_mat = px.bar(df.groupby(c_item)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True).tail(10), x=c_bal, y=c_item, orientation='h', color=c_bal, color_continuous_scale='Blues', text_auto='.2s', title="🏆 أعلى 10 مواد متوفرة بالمخزن")
                    st.plotly_chart(fig_top_mat, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول المواد الأولية"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="mat.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

    # ----------------- 🛒 مشتريات المصنفات -----------------
    elif choice == "🛒 مشتريات المصنفات":
        st.title("🛒 مشتريات المصنفات")
        df = data_pur['df_cat'].copy()
        if not check_empty(df, "مشتريات المصنفات"):
            c_ord_date, c_comp, c_emp, c_req, c_cur, c_unit, c_item = data_pur['c_ord_date_c'], data_pur['c_comp_c'], data_pur['c_emp'], data_pur['c_req_c'], data_pur['c_cur_c'], data_pur['c_unit_c'], data_pur['c_item_c']
            
            with st.expander("🔍 فلاتر مشتريات المصنفات", expanded=True):
                with st.form("pur_cat_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in df.columns:
                        df[c_ord_date] = pd.to_datetime(df[c_ord_date], errors='coerce')
                        valid_dates = df[c_ord_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("اختر فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_comp = f2.multiselect("🏢 الشركة الموردة", df[c_comp].unique() if c_comp and c_comp in df.columns else [])
                    sel_emp = f3.multiselect("👤 الموظف المتابع", df[c_emp].unique() if c_emp and c_emp in df.columns else [])
                    sel_unit = f4.multiselect("⚖️ الوحدة", df[c_unit].unique() if c_unit and c_unit in df.columns else [])
                    submitted_pur_cat = st.form_submit_button("🚀 تطبيق الفلاتر")

            if len(date_range) == 2 and c_ord_date: df = df[(df[c_ord_date].dt.date >= date_range[0]) & (df[c_ord_date].dt.date <= date_range[1])]
            if sel_comp: df = df[df[c_comp].isin(sel_comp)]
            if sel_emp: df = df[df[c_emp].isin(sel_emp)]
            if sel_unit: df = df[df[c_unit].isin(sel_unit)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🛒 إجمالي المطلوب", f"{df[c_req].sum():,.0f}" if c_req and c_req in df.columns else "0")
            k2.metric("📦 إجمالي الرصيد الحالي للمواد", f"{df[c_cur].sum():,.0f}" if c_cur and c_cur in df.columns else "0")
            k3.metric("🏢 عدد الشركات الموردة", f"{df[c_comp].nunique()}" if c_comp and c_comp in df.columns else "0")
            k4.metric("👤 عدد الموظفين المتابعين", f"{df[c_emp].nunique()}" if c_emp and c_emp in df.columns else "0")
            st.markdown("---")

            try:
                row1_c1, row1_c2 = st.columns(2)
                with row1_c1:
                    if c_comp and c_req and c_comp in df.columns and c_req in df.columns:
                        fig_comp = px.pie(df.groupby(c_comp)[c_req].sum().reset_index(), values=c_req, names=c_comp, hole=0.5, title="🏢 توزيع الطلبات حسب الشركة", color_discrete_sequence=px.colors.qualitative.Prism)
                        fig_comp.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_comp, use_container_width=True)
                with row1_c2:
                    if c_emp and c_req and c_emp in df.columns and c_req in df.columns:
                        fig_emp = px.bar(df.groupby(c_emp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=True), x=c_req, y=c_emp, orientation='h', title="👤 حجم متابعة الطلبات لكل موظف", text_auto='.2s', color=c_req, color_continuous_scale='Teal')
                        st.plotly_chart(fig_emp, use_container_width=True)
            except Exception: pass
            
            st.markdown("---")
            try:
                if c_item and c_req and c_cur and c_item in df.columns and c_req in df.columns and c_cur in df.columns:
                    melted_items = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index().melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                    fig_compare = px.bar(melted_items, x=c_item, y='الكمية', color='النوع', barmode='group', title="⚖️ مقارنة: المطلوب مقابل الرصيد لأعلى 10 مواد", color_discrete_map={c_req: '#f59e0b', c_cur: '#3b82f6'}, text_auto='.2s')
                    fig_compare.update_layout(legend_title_text='', xaxis_title="")
                    st.plotly_chart(fig_compare, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول المشتريات"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="pur_cat.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

    # ----------------- 🔪 مشتريات المجزر -----------------
    elif choice == "🔪 مشتريات المجزر":
        st.title("🔪 مشتريات المجزر")
        df = data_pur['df_slh'].copy()
        if not check_empty(df, "مشتريات المجزر"):
            c_ord_date, c_comp, c_arr, c_req, c_cur, c_cat, c_item = data_pur['c_ord_date_s'], data_pur['c_comp_s'], data_pur['c_arr_s'], data_pur['c_req_s'], data_pur['c_cur_s'], data_pur['c_cat_s'], data_pur['c_item_s']
            
            with st.expander("🔍 فلاتر مشتريات المجزر", expanded=True):
                with st.form("pur_slh_form"):
                    f1, f2, f3, f4 = st.columns(4)
                    if c_ord_date and c_ord_date in df.columns:
                        df[c_ord_date] = pd.to_datetime(df[c_ord_date], errors='coerce')
                        valid_dates = df[c_ord_date].dropna()
                        min_d, max_d = valid_dates.min().date(), valid_dates.max().date() if not valid_dates.empty else (datetime.date.today(), datetime.date.today())
                        date_range = f1.date_input("اختر فترة الطلب", [min_d, max_d], min_value=min_d, max_value=max_d)
                    else: date_range = []

                    sel_comp = f2.multiselect("🏢 الشركة الموردة", df[c_comp].unique() if c_comp and c_comp in df.columns else [])
                    sel_cat = f3.multiselect("🏷️ تصنيف المادة", df[c_cat].unique() if c_cat and c_cat in df.columns else [])
                    sel_arr = f4.multiselect("⏳ حالة التوريد", df[c_arr].unique() if c_arr and c_arr in df.columns else [])
                    submitted_pur_slh = st.form_submit_button("🚀 تطبيق الفلاتر")

            if len(date_range) == 2 and c_ord_date: df = df[(df[c_ord_date].dt.date >= date_range[0]) & (df[c_ord_date].dt.date <= date_range[1])]
            if sel_comp: df = df[df[c_comp].isin(sel_comp)]
            if sel_cat: df = df[df[c_cat].isin(sel_cat)]
            if sel_arr: df = df[df[c_arr].isin(sel_arr)]

            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🛒 إجمالي المطلوب سيستم", f"{df[c_req].sum():,.0f}" if c_req and c_req in df.columns else "0")
            k2.metric("📦 إجمالي الرصيد الحالي", f"{df[c_cur].sum():,.0f}" if c_cur and c_cur in df.columns else "0")
            k3.metric("🏢 عدد الشركات", f"{df[c_comp].nunique()}" if c_comp and c_comp in df.columns else "0")
            k4.metric("🏷️ عدد التصنيفات", f"{df[c_cat].nunique()}" if c_cat and c_cat in df.columns else "0")
            st.markdown("---")

            try:
                if c_cat and c_item and c_req and c_cat in df.columns and c_item in df.columns and c_req in df.columns:
                    tree_data = df[df[c_req] > 0].dropna(subset=[c_cat, c_item])
                    tree_data[c_cat], tree_data[c_item] = tree_data[c_cat].astype(str), tree_data[c_item].astype(str)
                    if not tree_data.empty:
                        fig_tree = px.treemap(tree_data, path=[px.Constant("مشتريات المجزر"), c_cat, c_item], values=c_req, title="🗺️ الخريطة الهيكلية للطلبات", color=c_req, color_continuous_scale='Blues')
                        fig_tree.update_traces(root_color="#1e293b", textinfo="label+value", textfont=dict(size=15))
                        fig_tree.update_layout(margin=dict(t=50, l=10, r=10, b=10), height=650)
                        st.plotly_chart(fig_tree, use_container_width=True)
            except Exception: pass
                    
            st.markdown("---")
            try:
                row2_c1, row2_c2 = st.columns(2)
                with row2_c1:
                    if c_item and c_req and c_cur and c_item in df.columns and c_req in df.columns and c_cur in df.columns:
                        melted_slh = df.groupby(c_item)[[c_req, c_cur]].sum().nlargest(10, c_req).reset_index().melt(id_vars=c_item, value_vars=[c_req, c_cur], var_name='النوع', value_name='الكمية')
                        fig_comp_slh = px.bar(melted_slh, x='الكمية', y=c_item, color='النوع', orientation='h', barmode='group', title="⚖️ أعلى 10 مواد: (المطلوب) مقابل (الرصيد)", color_discrete_map={c_req: '#8b5cf6', c_cur: '#10b981'}, text_auto='.2s')
                        fig_comp_slh.update_layout(legend_title_text='', yaxis_title="")
                        st.plotly_chart(fig_comp_slh, use_container_width=True)
                with row2_c2:
                    if c_comp and c_req and c_comp in df.columns and c_req in df.columns:
                        fig_comp_bar = px.bar(df.groupby(c_comp)[c_req].sum().reset_index().sort_values(by=c_req, ascending=False).head(10), x=c_comp, y=c_req, title="🏢 أعلى 10 شركات موردة", color=c_req, color_continuous_scale='Sunset', text_auto='.2s')
                        fig_comp_bar.update_layout(xaxis_title="")
                        st.plotly_chart(fig_comp_bar, use_container_width=True)
            except Exception: pass

            st.markdown("---")
            with st.expander("📋 عرض جدول مشتريات المجزر"):
                st.download_button(label="📥 تحميل (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name="pur_slh.csv", mime="text/csv")
                st.dataframe(df.head(100), use_container_width=True)

except Exception as e:
    st.error("🚨 النظام اكتشف خطأ مخفي! اضغط على زر مسح الذاكرة أدناه لترسيت النظام:")
    st.code(traceback.format_exc())
    if st.button("🔄 مسح الذاكرة وإعادة التشغيل (Reboot)", key="emergency_reset"):
        st.cache_data.clear()
        st.rerun()
