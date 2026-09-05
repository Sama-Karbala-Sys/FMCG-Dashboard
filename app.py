import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import datetime

# ==========================================
# 1. إعدادات الصفحة والثيم (Google Finance)
# ==========================================
st.set_page_config(page_title="SamaKarbala Finance", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        /* ثيم Google Finance */
        .stApp { background-color: #202124; color: #e8eaed; direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        /* الكروت الإحصائية */
        div[data-testid="metric-container"] {
            background-color: #292a2d; border: 1px solid #3c4043; padding: 15px; border-radius: 8px;
        }
        div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; font-weight: 500 !important; }
        div[data-testid="stMetricLabel"] { color: #9aa0a6 !important; font-size: 1rem !important; }
        
        /* إخفاء القوائم الافتراضية */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* الجداول (Dataframes) */
        [data-testid="stDataFrame"] { background-color: #292a2d; border-radius: 8px; border: 1px solid #3c4043; }
        
        /* العناوين */
        h1, h2, h3 { color: #e8eaed !important; font-weight: 400; }
        .finance-title { color: #8ab4f8; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ألوان الجارتات بستايل Finance
gf_colors = ['#8ab4f8', '#81c995', '#f28b82', '#fde293', '#c58af9', '#f48fb1', '#78d9ec']
gf_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#9aa0a6'),
    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#3c4043')
)

# ==========================================
# 2. الهيدر والروابط السحابية
# ==========================================
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("<h1><span class='finance-title'>Finance</span> SamaKarbala</h1>", unsafe_allow_html=True)
    st.caption(f"السوق متصل 🟢 • التحديث الأخير: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
with c2:
    if st.button("تحديث البيانات 🔄", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# لوحة الروابط (يمكنك إخفاؤها لاحقاً بوضعها داخل st.expander)
with st.expander("⚙️ إعدادات الروابط السحابية (للمدير)", expanded=False):
    sales_url = st.text_input("رابط المبيعات:", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv")
    pur_url = st.text_input("رابط مشتريات المجزر:", "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv")

# ==========================================
# 3. دوال السحب وتحليل البيانات
# ==========================================
@st.cache_data(ttl=300)
def fetch_data(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # كسر الكاش (Cache-Busting)
        final_url = url + ('&' if '?' in url else '?') + str(time.time())
        res = requests.get(final_url, headers=headers, timeout=15)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            df = pd.read_csv(io.StringIO(res.text), on_bad_lines='skip')
            df.columns = [str(c).replace('\ufeff', '').strip() for c in df.columns]
            return df
    except Exception as e:
        pass
    return pd.DataFrame()

# ==========================================
# 4. التبويبات الرئيسية (Tabs)
# ==========================================
tab_sales, tab_pur = st.tabs(["📊 المبيعات والمحافظات", "🛒 مشتريات المجزر"])

# ----------------------------------------------------
# التبويب الأول: المبيعات والمحافظات
# ----------------------------------------------------
with tab_sales:
    df_sales = fetch_data(sales_url)
    if not df_sales.empty:
        # البحث عن الأعمدة
        c_ton = next((c for c in df_sales.columns if 'طن' in str(c)), None)
        c_qty = next((c for c in df_sales.columns if 'عدد' in str(c) or 'كمية' in str(c)), None)
        c_gov = next((c for c in df_sales.columns if 'محافظ' in str(c) or 'Gov' in str(c)), None)
        c_agent = next((c for c in df_sales.columns if 'زبون' in str(c) or 'وكيل' in str(c)), None)
        c_item = next((c for c in df_sales.columns if 'مادة' in str(c) or 'Product' in str(c)), None)
        c_cat = next((c for c in df_sales.columns if 'تصنيف' in str(c) or 'Cat' in str(c)), None)

        if c_ton and c_qty:
            df_sales[c_ton] = pd.to_numeric(df_sales[c_ton].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            df_sales[c_qty] = pd.to_numeric(df_sales[c_qty].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)

        # الكروت الإحصائية
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("إجمالي المبيعات (طن)", f"{df_sales[c_ton].sum():,.2f}" if c_ton else "0")
        k2.metric("إجمالي المبيعات (صندوق)", f"{df_sales[c_qty].sum():,.0f}" if c_qty else "0")
        k3.metric("عدد الوكلاء النشطين", f"{df_sales[c_agent].nunique()}" if c_agent else "0")
        k4.metric("إجمالي الحركات", f"{len(df_sales):,.0f}")
        
        st.markdown("---")

        # الجارتات
        if c_gov and c_ton and c_cat:
            r1c1, r1c2 = st.columns(2)
            
            with r1c1:
                st.markdown("### التوزيع الجغرافي (أطنان)")
                gov_data = df_sales.groupby(c_gov)[c_ton].sum().reset_index().sort_values(by=c_ton, ascending=True)
                fig_gov = px.bar(gov_data, x=c_ton, y=c_gov, orientation='h', color_discrete_sequence=['#8ab4f8'])
                fig_gov.update_layout(**gf_layout, showlegend=False, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_gov, use_container_width=True)
                
            with r1c2:
                st.markdown("### توزيع التصنيفات")
                cat_data = df_sales.groupby(c_cat)[c_ton].sum().reset_index()
                fig_cat = px.pie(cat_data, values=c_ton, names=c_cat, hole=0.6, color_discrete_sequence=gf_colors)
                fig_cat.update_layout(**gf_layout, showlegend=True)
                st.plotly_chart(fig_cat, use_container_width=True)
                
        st.markdown("### سجل المبيعات الشامل")
        st.dataframe(df_sales.head(100), use_container_width=True)
    else:
        st.warning("⚠️ جاري سحب بيانات المبيعات، يرجى الانتظار...")

# ----------------------------------------------------
# التبويب الثاني: مشتريات المجزر
# ----------------------------------------------------
with tab_pur:
    df_pur = fetch_data(pur_url)
    if not df_pur.empty:
        # البحث عن الأعمدة بناءً على الصورة
        p_code = df_pur.columns[0] if len(df_pur.columns) > 0 else None
        p_item = df_pur.columns[1] if len(df_pur.columns) > 1 else None
        p_cat = df_pur.columns[2] if len(df_pur.columns) > 2 else None
        p_cur = next((c for c in df_pur.columns if 'الرصيد' in str(c)), None)
        p_req = next((c for c in df_pur.columns if 'المطلوب' in str(c)), None)
        p_comp = next((c for c in df_pur.columns if 'شركة' in str(c) or 'الشركة' in str(c)), None)
        p_status = df_pur.columns[9] if len(df_pur.columns) > 9 else None

        if p_cur and p_req:
            df_pur[p_cur] = pd.to_numeric(df_pur[p_cur].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
            df_pur[p_req] = pd.to_numeric(df_pur[p_req].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)

        # الكروت الإحصائية للمشتريات
        pk1, pk2, pk3, pk4 = st.columns(4)
        pk1.metric("إجمالي المطلوب سيستم", f"{df_pur[p_req].sum():,.0f}" if p_req else "0")
        pk2.metric("إجمالي الرصيد الحالي", f"{df_pur[p_cur].sum():,.0f}" if p_cur else "0")
        pk3.metric("عدد الشركات الموردة", f"{df_pur[p_comp].nunique()}" if p_comp else "0")
        pk4.metric("عدد المواد المسجلة", f"{df_pur[p_item].nunique()}" if p_item else "0")

        st.markdown("---")

        # الجارتات
        if p_item and p_cur and p_req and p_comp:
            pr1, pr2 = st.columns(2)
            
            with pr1:
                st.markdown("### حجم الطلبات حسب الشركة")
                comp_data = df_pur.groupby(p_comp)[p_req].sum().reset_index()
                fig_comp = px.pie(comp_data, values=p_req, names=p_comp, hole=0.6, color_discrete_sequence=gf_colors)
                fig_comp.update_layout(**gf_layout, showlegend=True)
                st.plotly_chart(fig_comp, use_container_width=True)
                
            with pr2:
                st.markdown("### أعلى 10 مواد: المطلوب مقابل الرصيد")
                top_items = df_pur.groupby(p_item)[[p_req, p_cur]].sum().nlargest(10, p_req).reset_index()
                top_melted = top_items.melt(id_vars=p_item, value_vars=[p_req, p_cur], var_name='النوع', value_name='الكمية')
                
                # استخدام ألوان محددة: المطلوب (أحمر) ، الرصيد (أخضر/أزرق)
                fig_compare = px.bar(top_melted, x=p_item, y='الكمية', color='النوع', barmode='group', color_discrete_map={p_req: '#f28b82', p_cur: '#81c995'})
                fig_compare.update_layout(**gf_layout, legend_title_text='', xaxis_title="", yaxis_title="")
                # قص أسماء المواد الطويلة
                fig_compare.update_xaxes(tickformat="~s", tickangle=-45)
                st.plotly_chart(fig_compare, use_container_width=True)

        st.markdown("### سجل مشتريات المجزر")
        st.dataframe(df_pur, use_container_width=True)
    else:
        st.warning("⚠️ جاري سحب بيانات المشتريات، يرجى الانتظار...")
