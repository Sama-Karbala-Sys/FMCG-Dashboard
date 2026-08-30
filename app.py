import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# ==========================================
# 1. إعدادات الصفحة واللغة
# ==========================================
st.set_page_config(page_title="FMCG Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp { direction: rtl; }
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] { text-align: right; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px; background-color: #0f172a; padding: 10px;
            border-radius: 16px; border: 1px solid #1e293b; display: flex; justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px; font-size: 16px !important; font-weight: 600;
            background-color: transparent; border-radius: 10px !important;
            padding: 10px 30px; color: #94a3b8; border: none; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stTabs [data-baseweb="tab"]:hover { background-color: #1e293b; color: #e2e8f0; }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. رأس الصفحة وزر التحديث اللحظي
# ==========================================
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("📊 نظام إدارة المبيعات والمخازن | FMCG")
with col_btn:
    st.write("") 
    if st.button("🔄 تحديث البيانات الآن", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

tab_gov, tab_frz, tab_slh, tab_mat = st.tabs([
    "📍 توزيع المحافظات", "🧊 أرصدة الثلاجات", "❄️ مخازن المجزر", "📦 المواد الأولية"
])

# ==========================================
# 3. دوال سحب البيانات السحابية
# ==========================================

@st.cache_data(ttl=300)
def load_gov_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv"
    try:
        response = requests.get(url, timeout=15)
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = df.columns.str.replace('\ufeff', '').str.replace('\n', '').str.replace('\r', '').str.strip()
        
        col_date = next((c for c in df.columns if 'تاريخ' in c or 'date' in c.lower()), None)
        col_gov = next((c for c in df.columns if 'محافظ' in c), None)
        col_agent = next((c for c in df.columns if 'زبون' in c or 'وكيل' in c), None)
        col_item = next((c for c in df.columns if 'مادة' in c or 'product' in c.lower()), None)
        col_cat = 'Category' if 'Category' in df.columns else next((c for c in df.columns if 'تصنيف' in c), None)
        col_ff = next((c for c in df.columns if 'item type' in c.lower() or 'طازج' in c or 'fresh' in c.lower()), None)
        col_label = next((c for c in df.columns if 'own' in c.lower() or 'label' in c.lower()), None)
        col_ton = next((c for c in df.columns if 'طن' in c), None)
        col_qty = next((c for c in df.columns if 'عدد' in c), None)

        if col_date:
            def fix_date(val):
                if pd.isna(val): return pd.NaT
                val_str = str(val).strip()
                if val_str.replace('.', '', 1).isdigit():
                    num = float(val_str)
                    if num > 20000: return pd.to_datetime(num, unit='D', origin='1899-12-30')
                try: return pd.to_datetime(val_str)
                except: return pd.NaT
            df[col_date] = df[col_date].apply(fix_date)

        for c in [col_ton, col_qty]:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)
                
        for c in [col_gov, col_agent, col_item, col_cat, col_ff, col_label]:
            if c and c in df.columns: df[c] = df[c].fillna('غير مصنف')
                
        return df, col_date, col_gov, col_agent, col_item, col_cat, col_ff, col_label, col_ton, col_qty
    except Exception:
        return pd.DataFrame(), *([None]*9)

@st.cache_data(ttl=300)
def load_freezer_data():
    url_freezer = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDphmbL58bqGdSFFFpU7NfVtAefvztGcjf5zPX8FBl5Rj3tW6H8vySo3T8CXGzyQ/pub?output=csv"
    try:
        response = requests.get(url_freezer, timeout=15)
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = df.columns.str.replace('\ufeff', '').str.replace('\n', '').str.replace('\r', '').str.strip()

        col_item = next((c for c in df.columns if 'ماد' in c), None)
        col_frz = next((c for c in df.columns if 'ثلاج' in c), None)
        col_start = next((c for c in df.columns if 'رصيد' in c), None)
        col_prod = next((c for c in df.columns if 'نتاج' in c), None)
        col_sold = next((c for c in df.columns if 'مباع' in c or 'صادر' in c), None)
        col_short = next((c for c in df.columns if 'نقص' in c), None)
        col_final = next((c for c in df.columns if 'نهائي' in c), None)
        
        num_cols = [col_start, col_prod, col_sold, col_short, col_final]
        for c in num_cols:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)

        if col_item and col_item in df.columns: df[col_item] = df[col_item].fillna('غير مصنف')
        if col_frz and col_frz in df.columns: df[col_frz] = df[col_frz].fillna('غير مصنف')
        
        return df, col_item, col_frz, col_start, col_prod, col_sold, col_short, col_final
    except Exception:
        return pd.DataFrame(), *([None]*7)

@st.cache_data(ttl=300)
def load_slaughterhouse_data():
    url_slh = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQHSv4SF_rudpU2753hjWpkwyuiQ59RHr3zfiZZb43IOmdf1PZvytibN_Dc5Oxwxg/pub?output=csv"
    try:
        response = requests.get(url_slh, timeout=15)
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = df.columns.str.replace('\ufeff', '').str.replace('\n', '').str.replace('\r', '').str.strip()

        col_item = next((c for c in df.columns if 'Column13' in c or 'Item Name' in c), None)
        col_qty = next((c for c in df.columns if 'Qty in Kg' in c or 'Qty' in c), None)
        col_birds = next((c for c in df.columns if 'Num Of Birds' in c or 'Birds' in c), None)
        col_prev = next((c for c in df.columns if 'Previous balance' in c), None)
        col_ff = next((c for c in df.columns if 'Fresh/Frozen' in c), None)
        col_brand = next((c for c in df.columns if 'Brand' in c), None)
        col_group = next((c for c in df.columns if 'Product Group' in c), None)
        col_label = next((c for c in df.columns if 'Own/Private' in c), None)
        col_pieces = next((c for c in df.columns if 'Pieces' in c), None)
        
        num_cols = [col_qty, col_birds, col_prev, col_pieces]
        for c in num_cols:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True), errors='coerce').fillna(0)

        cat_cols = [col_item, col_ff, col_brand, col_group, col_label]
        for c in cat_cols:
            if c and c in df.columns:
                df[c] = df[c].fillna('غير مصنف | N/A')
        
        return df, col_item, col_qty, col_birds, col_prev, col_ff, col_brand, col_group, col_label, col_pieces
    except Exception:
        return pd.DataFrame(), *([None]*9)

@st.cache_data(ttl=300)
def load_raw_materials_data():
    url_mat = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTyT8AIVzoC083IILST_hw5Q4j29tMBoYpdA568JyzSuJuOnX0BKq0MwOa9GE0aBQ/pub?output=csv"
    try:
        response = requests.get(url_mat, timeout=15)
        response.encoding = 'utf-8' 
        
        # قراءة الملف بشكل طبيعي أولاً
        df = pd.read_csv(io.StringIO(response.text))
        
        # الرادار الذكي: إذا كانت الأعمدة بدون اسم (Unnamed)، راح يبحث عن العناوين الحقيقية
        cols_str = ' '.join(df.columns.astype(str))
        if 'المادة' not in cols_str and 'الكمية' not in cols_str:
            header_idx = None
            # يبحث في أول 15 سطر عن الكلمات المفتاحية
            for idx, row in df.head(15).iterrows():
                row_str = ' '.join(str(val) for val in row.values)
                if 'المادة' in row_str or 'الكمية' in row_str or 'تاريخ' in row_str:
                    header_idx = idx
                    break
            
            # إذا لگه السطر، يرفعه يسويه هو العناوين ويمسح الفراغات الفوگ
            if header_idx is not None:
                df.columns = df.iloc[header_idx]
                df = df.iloc[header_idx + 1:].reset_index(drop=True)

        # تنظيف أسماء الأعمدة بعد ما لكيناها
        df.columns = df.columns.astype(str).str.replace('\ufeff', '').str.replace('\n', '').str.replace('\r', '').str.strip()

        col_date = next((c for c in df.columns if 'تاريخ' in c), None)
        col_type = next((c for c in df.columns if 'نوع الاذن' in c or 'نوع' in c), None)
        col_dept = next((c for c in df.columns if 'قسم' in c), None)
        col_item = next((c for c in df.columns if 'مادة' in c and 'كود' not in c), None)
        col_qty = next((c for c in df.columns if 'كمية' in c), None)
        col_bal = next((c for c in df.columns if 'رصيد' in c and 'حالي' in c), None)
        col_cat = next((c for c in df.columns if 'تصنيف' in c), None)
        
        num_cols = [col_qty, col_bal]
        for c in num_cols:
            if c and c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(r'[^\d\.-]', '', regex=True).replace('-', '0'), errors='coerce').fillna(0)

        if col_date and col_date in df.columns:
            def fix_date(val):
                if pd.isna(val): return pd.NaT
                val_str = str(val).strip()
                if val_str.replace('.', '', 1).isdigit():
                    num = float(val_str)
                    if num > 20000: return pd.to_datetime(num, unit='D', origin='1899-12-30')
                try: return pd.to_datetime(val_str)
                except: return pd.NaT
            df[col_date] = df[col_date].apply(fix_date)

        cat_cols = [col_type, col_dept, col_item, col_cat]
        for c in cat_cols:
            if c and c in df.columns:
                df[c] = df[c].fillna('غير مصنف')
        
        return df, col_date, col_type, col_dept, col_item, col_qty, col_bal, col_cat
    except Exception as e:
        st.error(f"⚠️ خطأ في قراءة المواد الأولية: {e}")
        return pd.DataFrame(), *([None]*7)


# ==========================================
# 4. بناء محتوى قسم المحافظات
# ==========================================
with tab_gov:
    df_gov, col_date, col_gov, col_agent, col_item, col_cat, col_ff, col_label, col_ton, col_qty = load_gov_data()
    if not df_gov.empty:
        filtered_df = df_gov.copy()
        
        st.sidebar.header("🔍 فلاتر المحافظات")
        if col_date:
            valid_dates = filtered_df[col_date].dropna()
            if not valid_dates.empty:
                min_d, max_d = valid_dates.min().date(), valid_dates.max().date()
                if min_d != max_d:
                    date_range = st.sidebar.date_input("📅 التاريخ", [min_d, max_d], min_value=min_d, max_value=max_d)
                    if len(date_range) == 2:
                        filtered_df = filtered_df[(filtered_df[col_date].dt.date >= date_range[0]) & (filtered_df[col_date].dt.date <= date_range[1])]

        if col_gov:
            sel_gov = st.sidebar.multiselect("📍 اختر المحافظة", filtered_df[col_gov].unique())
            if sel_gov: filtered_df = filtered_df[filtered_df[col_gov].isin(sel_gov)]
        if col_ff:
            sel_ff = st.sidebar.multiselect("❄️ طازج أو مجمد", filtered_df[col_ff].unique())
            if sel_ff: filtered_df = filtered_df[filtered_df[col_ff].isin(sel_ff)]
        if col_label:
            sel_label = st.sidebar.multiselect("🏷️ العلامة التجارية", filtered_df[col_label].unique())
            if sel_label: filtered_df = filtered_df[filtered_df[col_label].isin(sel_label)]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📦 إجمالي المبيعات (طن)", f"{filtered_df[col_ton].sum():,.2f}" if col_ton else "0")
        c2.metric("🔢 إجمالي المبيعات (عدد)", f"{filtered_df[col_qty].sum():,.0f}" if col_qty else "0")
        c3.metric("👥 الزبائن والوكلاء", f"{filtered_df[col_agent].nunique()}" if col_agent else "0")
        c4.metric("📄 المستندات المسجلة", f"{len(filtered_df)}")
        st.markdown("---")

        pie1, pie2, pie3 = st.columns(3)
        with pie1:
            if col_cat and col_ton:
                cat_data = filtered_df.groupby(col_cat)[col_ton].sum().reset_index()
                fig_cat = px.pie(cat_data, values=col_ton, names=col_cat, hole=0.4, title="🛒 التصنيف (Category)")
                fig_cat.update_traces(textposition='inside', textinfo='percent')
                fig_cat.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_cat, use_container_width=True)
        with pie2:
            if col_ff and col_ton:
                ff_data = filtered_df.groupby(col_ff)[col_ton].sum().reset_index()
                fig_ff = px.pie(ff_data, values=col_ton, names=col_ff, color_discrete_sequence=['#3b82f6', '#06b6d4'], title="❄️ طازج ومجمد")
                fig_ff.update_traces(textposition='inside', textinfo='percent')
                fig_ff.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_ff, use_container_width=True)
        with pie3:
            if col_label and col_ton:
                label_data = filtered_df.groupby(col_label)[col_ton].sum().reset_index()
                fig_label = px.pie(label_data, values=col_ton, names=col_label, color_discrete_sequence=['#f59e0b', '#ec4899'], title="🏷️ العلامة التجارية")
                fig_label.update_traces(textposition='inside', textinfo='percent')
                fig_label.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_label, use_container_width=True)

        st.markdown("---")
        if col_gov and col_ton:
            gov_data = filtered_df.groupby(col_gov)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=True)
            fig_gov = px.bar(gov_data, x=col_ton, y=col_gov, orientation='h', color=col_gov, text_auto='.2s', title="📍 التوزيع حسب المحافظات")
            fig_gov.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig_gov, use_container_width=True)

        bar1, bar2 = st.columns(2)
        with bar1:
            if col_agent and col_ton:
                agent_data = filtered_df.groupby(col_agent)[col_ton].sum().reset_index().sort_values(by=col_ton, ascending=False).head(10)
                fig_agent = px.bar(agent_data, x=col_agent, y=col_ton, color=col_ton, color_continuous_scale='Purples', text_auto='.2s', title="🏆 أفضل 10 زبائن (طن)")
                st.plotly_chart(fig_agent, use_container_width=True)
        with bar2:
            if col_item and col_qty:
                item_data = filtered_df.groupby(col_item)[col_qty].sum().reset_index().sort_values(by=col_qty, ascending=False).head(10)
                fig_item = px.bar(item_data, x=col_item, y=col_qty, color=col_qty, color_continuous_scale='Reds', text_auto='.2s', title="📦 أفضل 10 مواد مبيعاً (عدد)")
                st.plotly_chart(fig_item, use_container_width=True)
        
        st.markdown("---")
        with st.expander("📋 عرض جدول تفاصيل المحافظات (اضغط للفتح)"):
            st.dataframe(filtered_df, use_container_width=True)

# ==========================================
# 5. بناء محتوى قسم أرصدة الثلاجات
# ==========================================
with tab_frz:
    df_frz, c_item, c_frz, c_start, c_prod, c_sold, c_short, c_final = load_freezer_data()
    
    if not df_frz.empty:
        filtered_frz = df_frz.copy()
        
        st.subheader("📊 ملخص حركة المخزون | Inventory Movement")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📦 المخزون الحالي (الكمية النهائية)", f"{filtered_frz[c_final].sum():,.0f}" if c_final else "0")
        k2.metric("🏭 إجمالي الإنتاج الداخلي", f"{filtered_frz[c_prod].sum():,.0f}" if c_prod else "0")
        k3.metric("🛒 إجمالي المباع الصادر", f"{filtered_frz[c_sold].sum():,.0f}" if c_sold else "0")
        k4.metric("⚠️ إجمالي النقص أو التالف", f"{filtered_frz[c_short].sum():,.0f}" if c_short else "0", delta="- هدر", delta_color="inverse")
        st.markdown("---")

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            if c_frz and c_final:
                frz_stock = filtered_frz.groupby(c_frz)[c_final].sum().reset_index().sort_values(by=c_final, ascending=False)
                fig_stock = px.bar(frz_stock, x=c_frz, y=c_final, color=c_frz, text_auto='.2s', title="🧊 المخزون الحالي في كل ثلاجة")
                st.plotly_chart(fig_stock, use_container_width=True)
                
        with row1_col2:
            if c_frz and c_short:
                frz_short = filtered_frz.groupby(c_frz)[c_short].sum().reset_index()
                if frz_short[c_short].sum() > 0:
                    fig_short = px.pie(frz_short, values=c_short, names=c_frz, hole=0.4, color_discrete_sequence=px.colors.sequential.Reds_r, title="⚠️ توزيع النقص حسب الثلاجة")
                    fig_short.update_traces(textposition='inside', textinfo='percent')
                    fig_short.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
                    st.plotly_chart(fig_short, use_container_width=True)
                else:
                    st.success("✅ لا يوجد أي نقص في الثلاجات!")

        st.markdown("---")
        if c_frz and c_prod and c_sold:
            flow_data = filtered_frz.groupby(c_frz)[[c_prod, c_sold]].sum().reset_index()
            flow_melted = flow_data.melt(id_vars=c_frz, value_vars=[c_prod, c_sold], var_name='العملية', value_name='الكمية')
            fig_flow = px.bar(flow_melted, x=c_frz, y='الكمية', color='العملية', barmode='group', 
                              color_discrete_map={c_prod: '#10b981', c_sold: '#f43f5e'}, text_auto='.2s', title="🔄 مقارنة (الإنتاج الداخلي) مقابل (المباع)")
            st.plotly_chart(fig_flow, use_container_width=True)

        st.markdown("---")
        with st.expander("📋 عرض جدول أرصدة الثلاجات (اضغط للفتح)"):
            st.dataframe(filtered_frz, use_container_width=True)

# ==========================================
# 6. بناء محتوى قسم مخازن المجزر (Slaughterhouse)
# ==========================================
with tab_slh:
    df_slh, c_item, c_qty, c_birds, c_prev, c_ff, c_brand, c_group, c_label, c_pieces = load_slaughterhouse_data()
    
    if not df_slh.empty:
        filtered_slh = df_slh.copy()
        
        st.subheader("🏭 ملخص أرصدة المجزر | Slaughterhouse Balances")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("⚖️ إجمالي الوزن (Kg)", f"{filtered_slh[c_qty].sum():,.2f}" if c_qty else "0")
        k2.metric("🐔 إجمالي الطيور (Birds)", f"{filtered_slh[c_birds].sum():,.0f}" if c_birds else "0")
        k3.metric("📦 إجمالي القطع (Pieces)", f"{filtered_slh[c_pieces].sum():,.0f}" if c_pieces else "0")
        k4.metric("🔙 الرصيد السابق", f"{filtered_slh[c_prev].sum():,.0f}" if c_prev else "0")
        st.markdown("---")

        row1_c1, row1_c2, row1_c3 = st.columns(3)
        with row1_c1:
            if c_group and c_qty:
                group_data = filtered_slh.groupby(c_group)[c_qty].sum().reset_index()
                fig_grp = px.pie(group_data, values=c_qty, names=c_group, hole=0.4, title="📦 الوزن حسب (Product Group)")
                fig_grp.update_traces(textposition='inside', textinfo='percent')
                fig_grp.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_grp, use_container_width=True)
                
        with row1_c2:
            if c_ff and c_qty:
                ff_data = filtered_slh.groupby(c_ff)[c_qty].sum().reset_index()
                fig_ff = px.pie(ff_data, values=c_qty, names=c_ff, color_discrete_sequence=['#3b82f6', '#06b6d4'], title="❄️ طازج ومجمد (Kg)")
                fig_ff.update_traces(textposition='inside', textinfo='percent')
                fig_ff.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_ff, use_container_width=True)

        with row1_c3:
            if c_brand and c_qty:
                brand_data = filtered_slh.groupby(c_brand)[c_qty].sum().reset_index()
                fig_brnd = px.pie(brand_data, values=c_qty, names=c_brand, color_discrete_sequence=['#8b5cf6', '#d946ef'], title="🏷️ العلامة التجارية (Brand)")
                fig_brnd.update_traces(textposition='inside', textinfo='percent')
                fig_brnd.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_brnd, use_container_width=True)

        st.markdown("---")
        
        row2_c1, row2_c2 = st.columns(2)
        with row2_c1:
            if c_item and c_qty:
                item_data = filtered_slh.groupby(c_item)[c_qty].sum().reset_index().sort_values(by=c_qty, ascending=True).tail(10)
                fig_item = px.bar(item_data, x=c_qty, y=c_item, orientation='h', color=c_qty, color_continuous_scale='Greens', text_auto='.2s', title="🏆 أعلى 10 مواد حسب الوزن (Kg)")
                fig_item.update_layout(showlegend=False)
                st.plotly_chart(fig_item, use_container_width=True)

        with row2_c2:
            if c_item and c_birds:
                bird_data = filtered_slh.groupby(c_item)[c_birds].sum().reset_index().sort_values(by=c_birds, ascending=True).tail(10)
                fig_bird = px.bar(bird_data, x=c_birds, y=c_item, orientation='h', color=c_birds, color_continuous_scale='Oranges', text_auto='.2s', title="🐔 أعلى 10 مواد حسب عدد الطيور")
                fig_bird.update_layout(showlegend=False)
                st.plotly_chart(fig_bird, use_container_width=True)

        st.markdown("---")
        with st.expander("📋 عرض جدول بيانات المجزر (اضغط للفتح)"):
            st.dataframe(filtered_slh, use_container_width=True)

# ==========================================
# 7. قسم المواد الأولية 
# ==========================================
with tab_mat:
    df_mat, c_date, c_type, c_dept, c_item, c_qty, c_bal, c_cat = load_raw_materials_data()
    
    if not df_mat.empty:
        filtered_mat = df_mat.copy()
        
        st.sidebar.markdown("---")
        st.sidebar.header("📦 فلاتر المواد الأولية")
        if c_dept:
            sel_dept = st.sidebar.multiselect("اختر القسم", filtered_mat[c_dept].unique())
            if sel_dept: filtered_mat = filtered_mat[filtered_mat[c_dept].isin(sel_dept)]
        
        if c_type:
            sel_type = st.sidebar.multiselect("نوع الإذن", filtered_mat[c_type].unique())
            if sel_type: filtered_mat = filtered_mat[filtered_mat[c_type].isin(sel_type)]
            
        if c_cat:
            sel_cat = st.sidebar.multiselect("التصنيف", filtered_mat[c_cat].unique())
            if sel_cat: filtered_mat = filtered_mat[filtered_mat[c_cat].isin(sel_cat)]

        st.subheader("📊 ملخص أرصدة المواد الأولية | Raw Materials Summary")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📦 إجمالي الرصيد الحالي", f"{filtered_mat[c_bal].sum():,.0f}" if c_bal else "0")
        k2.metric("🔄 إجمالي الكميات للحركة", f"{filtered_mat[c_qty].sum():,.0f}" if c_qty else "0")
        k3.metric("🏷️ عدد المواد المختلفة", f"{filtered_mat[c_item].nunique()}" if c_item else "0")
        k4.metric("📄 إجمالي السجلات", f"{len(filtered_mat)}")
        st.markdown("---")

        row1_c1, row1_c2 = st.columns(2)
        with row1_c1:
            if c_dept and c_bal:
                dept_data = filtered_mat.groupby(c_dept)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True)
                fig_dept = px.bar(dept_data, x=c_bal, y=c_dept, orientation='h', color=c_dept, text_auto='.2s', title="🏢 الأرصدة الحالية حسب القسم")
                fig_dept.update_layout(showlegend=False)
                st.plotly_chart(fig_dept, use_container_width=True)
                
        with row1_c2:
            if c_cat and c_bal:
                cat_data = filtered_mat.groupby(c_cat)[c_bal].sum().reset_index()
                fig_cat_mat = px.pie(cat_data, values=c_bal, names=c_cat, hole=0.4, title="🏷️ توزيع الأرصدة حسب التصنيف")
                fig_cat_mat.update_traces(textposition='inside', textinfo='percent')
                fig_cat_mat.update_layout(legend=dict(orientation="h", y=-0.2), uniformtext_minsize=10, uniformtext_mode='hide')
                st.plotly_chart(fig_cat_mat, use_container_width=True)

        st.markdown("---")
        
        if c_item and c_bal:
            item_data = filtered_mat.groupby(c_item)[c_bal].sum().reset_index().sort_values(by=c_bal, ascending=True).tail(10)
            fig_top_mat = px.bar(item_data, x=c_bal, y=c_item, orientation='h', color=c_bal, color_continuous_scale='Blues', text_auto='.2s', title="🏆 أعلى 10 مواد متوفرة بالمخزن (الرصيد الحالي)")
            fig_top_mat.update_layout(showlegend=False)
            st.plotly_chart(fig_top_mat, use_container_width=True)

        st.markdown("---")
        with st.expander("📋 عرض جدول بيانات المواد الأولية (اضغط للفتح)"):
            if c_date and c_date in filtered_mat.columns: 
                filtered_mat[c_date] = filtered_mat[c_date].dt.strftime('%Y-%m-%d')
            st.dataframe(filtered_mat, use_container_width=True)