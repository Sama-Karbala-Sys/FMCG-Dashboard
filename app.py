<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>شركة سما كربلاء - التقرير التنفيذي</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ================= الستايلات الأساسية (نفس تصميمك الأصلي) ================= */
        body { font-family: 'Cairo', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 0; transition: background-color 0.3s, color 0.3s; }
        ::-webkit-scrollbar { height: 8px; width: 8px; }
        ::-webkit-scrollbar-track { background: #1e293b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        
        .filter-btn { background-color: transparent; border: 1px solid #475569; color: #cbd5e1; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; transition: all 0.2s; }
        .filter-btn:hover { background-color: #334155; border-color: #64748b; }
        .filter-btn.active { background-color: #0f766e; border-color: #14b8a6; color: #ffffff; }
        .metric-btn { background-color: transparent; border: 1px solid #475569; color: #94a3b8; padding: 6px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
        .metric-btn.active { background-color: #334155; border-color: #cca344; color: #cca344; }
        .btn-excel { border: 1px solid #059669; color: #34d399; background-color: transparent; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; display: flex; align-items: center; gap: 4px; transition: all 0.2s; cursor: pointer; }
        .btn-excel:hover { background-color: #059669; color: #ffffff; }
        .report-select { background-color: #0f172a; border: 1px solid #334155; color: #94a3b8; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; outline: none; }
        .report-select:focus { border-color: #cca344; }

        .advanced-table th { background-color: #1e293b; position: sticky; top: 0; z-index: 10; font-size: 0.75rem; border-bottom: 2px solid #334155; padding: 12px 8px;}
        .advanced-table td { padding: 10px 8px; font-size: 0.8rem; border-bottom: 1px solid #1e293b; }
        .advanced-table tr:hover { background-color: #1e293b80; }
        .heatmap-table th { background-color: #1e293b; border: 1px solid #334155; padding: 12px; font-size: 0.85rem; font-weight: 700; }
        .heatmap-table td { border: 1px solid #334155; padding: 8px; font-size: 0.85rem; transition: all 0.2s; }
        .heatmap-table td:hover { filter: brightness(1.2); }
        .badge-A { background: #22c55e30; color: #4ade80; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
        .badge-B { background: #eab30830; color: #fde047; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
        .badge-C { background: #ef444430; color: #f87171; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
        .text-up { color: #4ade80; font-weight: bold; }
        .text-down { color: #f87171; font-weight: bold; }

        #loginOverlay { position: fixed; inset: 0; background-color: #18202f; z-index: 50; display: flex; align-items: center; justify-content: center; background-image: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); transition: background 0.3s; }
        .login-box { background-color: #1b2431; padding: 2.5rem; border: 1px solid #334155; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); width: 100%; max-width: 360px; border-radius: 12px; position: relative; transition: all 0.3s;}
        .login-top-bar { position: absolute; top: 1rem; right: 1rem; display: flex; gap: 8px; }
        .login-icon-btn { background: transparent; border: 1px solid #334155; color: #cbd5e1; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; cursor: pointer; transition: 0.2s;}
        .login-icon-btn:hover { background: #334155; }
        .login-input { width: 100%; padding: 12px 16px; margin-bottom: 14px; background-color: #111827; border: 1px solid #334155; color: white; border-radius: 8px; font-size: 0.9rem; transition: all 0.2s;}
        .login-input:focus { border-color: #cca344; outline: none; }
        .btn-login { width: 100%; background-color: #cca344; color: #ffffff; font-weight: bold; font-size: 1.1rem; padding: 12px; border-radius: 8px; margin-top: 10px; transition: all 0.2s; border: none; cursor: pointer;}
        .btn-login:hover { background-color: #b38b34; }
        .checkbox-custom { width: 1.1rem; height: 1.1rem; accent-color: #cca344; cursor: pointer; }

        body.light-theme { background-color: #f8fafc; color: #0f172a; }
        body.light-theme .bg-slate-800 { background-color: #ffffff; border-color: #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        body.light-theme .bg-\[\#1a2332\], body.light-theme .bg-\[\#111827\] { background-color: #f1f5f9; border-color: #e2e8f0;}
        body.light-theme .text-white { color: #0f172a; }
        body.light-theme .text-slate-400 { color: #64748b; }
        body.light-theme .text-slate-300 { color: #475569; }
        body.light-theme .text-slate-200 { color: #334155; }
        body.light-theme .border-slate-700 { border-color: #e2e8f0; }
        body.light-theme .border-slate-600 { border-color: #cbd5e1; }
        body.light-theme .bg-slate-900 { background-color: #ffffff; color: #0f172a; border-color: #cbd5e1;}
        body.light-theme .advanced-table th { background-color: #e2e8f0; color:#0f172a; border-bottom: 2px solid #cbd5e1; }
        body.light-theme .advanced-table td { border-bottom: 1px solid #e2e8f0; }
        body.light-theme .advanced-table tr:hover { background-color: #f8fafc; }
        body.light-theme .heatmap-table th { background-color: #e2e8f0; color:#0f172a; border-color: #cbd5e1; }
        body.light-theme .heatmap-table td { border-color: #cbd5e1; }
        body.light-theme .report-select { background-color: #ffffff; border-color: #cbd5e1; color: #0f172a; }
        body.light-theme #loginOverlay { background: #f8fafc; }
        body.light-theme .login-box { background-color: #ffffff; border-color: #e2e8f0; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); }
        body.light-theme .login-input { background-color: #f1f5f9; border-color: #cbd5e1; color: #0f172a; }
        body.light-theme .login-icon-btn { color: #0f172a; border-color: #cbd5e1; }
        body.light-theme .login-icon-btn:hover { background: #e2e8f0; }

        /* ستايل التابات (الأقسام) */
        .tab-content { display: none; animation: fadeIn 0.3s ease-in; }
        .tab-content.active { display: block; }
        .tab-btn { background: #1e293b; color: #cbd5e1; border: 1px solid #334155; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
        .tab-btn:hover { background: #334155; }
        .tab-btn.active { background: #cca344; color: #fff; border-color: #cca344; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="w-full min-h-screen">

    <!-- ================= شاشة تسجيل الدخول ================= -->
    <div id="loginOverlay">
        <div class="login-box">
            <div class="login-top-bar" dir="ltr">
                <button onclick="toggleLang()" class="login-icon-btn">EN / ع</button>
                <button onclick="toggleTheme()" id="themeBtnLogin" class="login-icon-btn">☀️</button>
            </div>
            
            <h2 class="text-2xl font-bold text-white text-center mb-1 mt-10" data-ar="تسجيل الدخول" data-en="Login">تسجيل الدخول</h2>
            <p class="text-slate-400 text-[11px] text-center mb-6" data-ar="شركة سما كربلاء — التقرير التنفيذي" data-en="Sama Karbala — Executive Report">شركة سما كربلاء — التقرير التنفيذي</p>
            
            <input type="text" id="usernameInput" data-ar-ph="اسم المستخدم" data-en-ph="Username" placeholder="اسم المستخدم" class="login-input" dir="auto">
            <input type="password" id="passwordInput" data-ar-ph="كلمة المرور" data-en-ph="Password" placeholder="كلمة المرور" class="login-input" dir="auto" onkeypress="if(event.key === 'Enter') checkLogin()">
            
            <div class="flex items-center justify-start gap-2 mb-2 pr-1">
                <input type="checkbox" id="rememberMe" class="checkbox-custom">
                <label for="rememberMe" class="text-sm text-slate-300 cursor-pointer select-none" data-ar="تذكّرني" data-en="Remember Me">تذكّرني</label>
            </div>
            
            <button onclick="checkLogin()" class="btn-login" data-ar="دخول" data-en="Sign In">دخول</button>
            <p id="loginError" class="text-rose-500 text-sm mt-4 text-center hidden" data-ar="البيانات غير صحيحة" data-en="Invalid Credentials">البيانات غير صحيحة</p>
        </div>
    </div>

    <!-- ================= الداشبورد الرئيسي ================= -->
    <div id="mainDashboard" class="w-full max-w-[1800px] mx-auto p-3 md:p-5 hidden">
        
        <!-- الهيدر -->
        <header class="flex flex-col md:flex-row justify-between items-center gap-4 mb-4 bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl">
            <div class="flex items-center gap-4">
                <div>
                    <h1 class="text-2xl font-bold text-[#cca344]" data-ar="لوحة المبيعات والتحليل الشامل" data-en="Sales & Analytics Dashboard">لوحة المبيعات والتحليل الشامل</h1>
                    <p id="welcomeMessage" class="text-sm text-slate-400"></p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <button onclick="toggleLang()" class="login-icon-btn hidden md:block">EN / ع</button>
                <button onclick="toggleTheme()" id="themeBtnMain" class="login-icon-btn hidden md:block">☀️</button>
                <div id="status" class="bg-amber-500/10 text-amber-400 px-3 py-1.5 rounded-full text-xs font-semibold border border-amber-500/20" data-ar="جاري التحقق..." data-en="Checking...">جاري التحقق...</div>
                <button onclick="fetchServerExcel()" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-full text-xs font-bold transition">تحديث السحابة 🔄</button>
                <button onclick="logout()" class="text-slate-400 hover:text-rose-500 text-xs font-bold underline" data-ar="تسجيل خروج" data-en="Logout">تسجيل خروج</button>
            </div>
        </header>

        <!-- ================= شريط الأقسام (Tabs) ================= -->
        <div class="flex gap-2 overflow-x-auto bg-[#1a2332] p-3 rounded-xl border border-slate-700 mb-4 shadow-xl hide-scrollbar">
            <button class="tab-btn active" onclick="switchTab('tab_sales', this)">📊 المبيعات والمحافظات</button>
            <button class="tab-btn" onclick="switchTab('tab_pur_slh', this)">🔪 مشتريات المجزر</button>
            <button class="tab-btn" onclick="switchTab('tab_gen', this)">📊 عام المجزر</button>
            <button class="tab-btn" onclick="switchTab('tab_frz', this)">🧊 الثلاجات</button>
            <button class="tab-btn" onclick="switchTab('tab_slh', this)">❄️ مخازن المجزر</button>
            <button class="tab-btn" onclick="switchTab('tab_mat', this)">📦 المواد الأولية</button>
            <button class="tab-btn" onclick="switchTab('tab_pur_cat', this)">🛒 مشتريات المصنفات</button>
        </div>

        <!-- ================= محتوى الأقسام ================= -->
        
        <!-- 1. المبيعات (التصميم الأصلي بالكامل) -->
        <div id="tab_sales" class="tab-content active">
            <!-- شريط الفلاتر الذكي -->
            <div class="bg-[#1a2332] p-4 rounded-xl border border-slate-700 mb-4 shadow-xl flex flex-col lg:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-2 order-2 lg:order-1">
                    <button id="btnMetricCount" onclick="setMetric('count')" class="metric-btn"><span data-ar="صناديق" data-en="Boxes">صناديق</span> 📦</button>
                    <button id="btnMetricTons" onclick="setMetric('tons')" class="metric-btn active"><span data-ar="طن" data-en="Tons">طن</span> ⚖️</button>
                </div>
                <div class="flex flex-wrap items-center justify-end gap-2 order-1 lg:order-2 flex-row-reverse w-full lg:w-auto">
                    <input type="date" id="dateFrom" onchange="renderSales()" class="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-slate-300 text-xs">
                    <span class="text-slate-400 text-xs" data-ar="إلى" data-en="To">إلى</span>
                    <input type="date" id="dateTo" onchange="renderSales()" class="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-slate-300 text-xs">
                    <button onclick="setDateFilter('last7', this)" class="filter-btn date-btn" data-ar="آخر 7" data-en="Last 7">آخر 7</button>
                    <button onclick="setDateFilter('last30', this)" class="filter-btn date-btn" data-ar="آخر 30" data-en="Last 30">آخر 30</button>
                    <button onclick="setDateFilter('thisMonth', this)" class="filter-btn date-btn" data-ar="هذا الشهر" data-en="This Month">هذا الشهر</button>
                    <button onclick="setDateFilter('all', this)" class="filter-btn date-btn active" data-ar="كل الفترة" data-en="All Time">كل الفترة</button>
                </div>
            </div>

            <!-- البطاقات الإحصائية -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold" data-ar="إجمالي الكمية (طن)" data-en="Total Quantity (Tons)">إجمالي الكمية (طن)</p><h3 id="totalTons" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold" data-ar="إجمالي العدد (صندوق)" data-en="Total Count (Boxes)">إجمالي العدد (صندوق)</p><h3 id="totalCount" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-blue-500 shadow"><p class="text-slate-400 text-xs font-semibold" data-ar="عدد الحركات" data-en="Transactions">عدد الحركات</p><h3 id="totalDocs" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-[#cca344] shadow"><p class="text-slate-400 text-xs font-semibold" data-ar="المعدل اليومي الشامل" data-en="Daily Avg">المعدل اليومي الشامل</p><h3 id="dailyAvgTotal" class="text-2xl font-bold text-white mt-1">0</h3></div>
            </div>

            <!-- المصفوفة الحرارية -->
            <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 mb-4 shadow-xl">
                <div class="flex justify-between items-center mb-3">
                    <h3 id="heatmapTitle" class="text-sm font-bold text-slate-300" data-ar="🔥 المصفوفة الحرارية" data-en="🔥 Heatmap Matrix">🔥 المصفوفة الحرارية</h3>
                    <button onclick="exportTableToExcel('heatmapTableFull', 'المصفوفة_الحرارية')" class="btn-excel" data-ar="إكسل" data-en="Excel">إكسل</button>
                </div>
                <div class="overflow-x-auto max-h-[500px] overflow-y-auto rounded-lg">
                    <table id="heatmapTableFull" class="w-full text-center text-slate-300 whitespace-nowrap text-sm border-collapse heatmap-table"><thead id="heatmapHead" class="sticky top-0 z-10 shadow-md"></thead><tbody id="heatmapBody"></tbody></table>
                </div>
            </div>

            <!-- الجارتات العلوية -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl"><h3 class="text-sm font-bold text-slate-300 mb-2" data-ar="نمو المحافظات" data-en="Growth">نمو المحافظات</h3><div class="w-full h-[300px] relative"><canvas id="growthChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl"><h3 class="text-sm font-bold text-slate-300 mb-2" id="paretoTitle" data-ar="باريتو الوكلاء 80/20" data-en="Pareto 80/20">باريتو الوكلاء 80/20</h3><div class="w-full h-[300px] relative"><canvas id="paretoChart"></canvas></div><p id="paretoSummary" class="text-xs text-slate-400 mt-2 text-center"></p></div>
            </div>
            <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 mb-4 shadow-xl"><h3 class="text-sm font-bold text-slate-300 mb-2" data-ar="اتجاه حصص المحافظات الأسبوعي" data-en="Weekly Share Trend">اتجاه حصص المحافظات الأسبوعي</h3><div class="w-full h-[250px] relative"><canvas id="weeklyShareChart"></canvas></div></div>

            <!-- الجارتات الوسطى -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl"><h3 id="rankingTitle" class="text-sm font-bold text-slate-300 mb-2" data-ar="ترتيب المحافظات" data-en="Gov Ranking">ترتيب المحافظات</h3><div class="w-full h-[250px] relative"><canvas id="rankingChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl"><h3 class="text-sm font-bold text-slate-300 mb-2 text-center" data-ar="حصة المحافظات %" data-en="Gov Share %">حصة المحافظات %</h3><div class="w-full h-[250px] relative flex justify-center"><canvas id="shareChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-xl"><h3 class="text-sm font-bold text-slate-300 mb-2 text-center" data-ar="فريش مقابل مجمد - الإجمالي" data-en="Fresh vs Frozen - Total">فريش مقابل مجمد - الإجمالي</h3><div class="w-full h-[250px] relative flex justify-center"><canvas id="ffTotalChart"></canvas></div></div>
            </div>

            <!-- تقرير المنتجات -->
            <div class="bg-[#111827] rounded-xl border border-slate-700 overflow-hidden shadow-2xl mb-4">
                <div class="p-4 border-b border-slate-700 flex flex-col md:flex-row justify-between items-center gap-4 bg-[#1a2332]">
                    <div class="flex items-center gap-4"><h2 class="text-lg font-bold text-slate-200" data-ar="سحوبات المنتجات" data-en="Products Report">سحوبات المنتجات</h2><button onclick="exportTableToExcel('productReportTableFull', 'تقرير_المنتجات')" class="btn-excel" data-ar="إكسل" data-en="Excel">إكسل</button></div>
                    <div class="flex items-center gap-3 flex-wrap justify-end">
                        <span class="text-xs text-slate-400" data-ar="المحافظة:" data-en="Gov:">المحافظة:</span><select id="reportGovFilter" onchange="updateReportAgentDropdown(); renderSales()" class="report-select w-32"><option value="">الكل</option></select>
                        <span class="text-xs text-slate-400" data-ar="الوكيل:" data-en="Agent:">الوكيل:</span><select id="reportAgentFilter" onchange="renderSales()" class="report-select w-40"><option value="">الكل</option></select>
                    </div>
                </div>
                <div class="overflow-x-auto max-h-[400px] overflow-y-auto">
                    <table id="productReportTableFull" class="w-full text-center advanced-table text-slate-300 whitespace-nowrap"><thead><tr><th class="w-10">#</th><th class="text-right" data-ar="المنتج" data-en="Product">المنتج</th><th data-ar="الفئة" data-en="Category">الفئة</th><th data-ar="صندوق" data-en="Boxes">صندوق</th><th data-ar="طن" data-en="Tons">طن</th></tr></thead><tbody id="productReportTable"><tr><td colspan="5" class="p-4 text-center">بانتظار البيانات...</td></tr></tbody></table>
                </div>
            </div>

            <!-- جدول البيانات الأساسي -->
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700 flex justify-between items-center">
                    <div class="flex flex-col"><span class="font-bold text-sm text-teal-300" data-ar="سجل العمليات الأساسي (المبيعات)" data-en="Main Data Log">سجل العمليات الأساسي</span></div>
                </div>
                <div class="overflow-x-auto w-full max-h-[400px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>التصنيف</th><th>الرقم</th><th>السيارة</th><th>السائق</th><th>الكمية طن</th><th>الكمية عدد</th><th>الفرع</th><th>الوكيل</th><th>المادة</th><th>التاريخ</th><th>المحافظة</th></tr></thead>
                        <tbody id="salesTable"><tr><td colspan="11" class="p-6 text-center text-slate-500">جاري التحميل...</td></tr></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 2. مشتريات المجزر -->
        <div id="tab_pur_slh" class="tab-content">
            <div class="bg-[#1a2332] p-4 rounded-xl border border-slate-700 mb-4 shadow-xl flex gap-3">
                <select id="purSlhComp" onchange="renderPurSlh()" class="report-select w-48"><option value="">🏢 الشركة الموردة (الكل)</option></select>
                <select id="purSlhStat" onchange="renderPurSlh()" class="report-select w-48"><option value="">⏳ حالة التوريد (الكل)</option></select>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-rose-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي المطلوب (سيستم)</p><h3 id="pslhReq" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي الرصيد الحالي</p><h3 id="pslhCur" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-indigo-500 shadow"><p class="text-slate-400 text-xs font-semibold">عدد الشركات الموردة</p><h3 id="pslhComps" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">عدد المواد المطلوبة</p><h3 id="pslhItems" class="text-2xl font-bold text-white mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">توزيع الطلبات حسب الشركة</h3><div class="w-full h-[300px] relative"><canvas id="pslhCompChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">المطلوب مقابل الرصيد (أعلى 10)</h3><div class="w-full h-[300px] relative"><canvas id="pslhCompBarChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-indigo-300">سجل مشتريات المجزر</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>تاريخ الطلب</th><th class="text-indigo-400">الشركة</th><th>الكود</th><th class="text-amber-400">المادة</th><th>التصنيف</th><th>الرصيد الحالي</th><th class="text-rose-400">المطلوب</th><th>حالة التوريد</th></tr></thead>
                        <tbody id="purSlhTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 3. عام المجزر -->
        <div id="tab_gen" class="tab-content">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي الرصيد الفعلي</p><h3 id="genBal" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-indigo-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي المثبت (قيد الوصول)</p><h3 id="genConf" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-rose-500 shadow"><p class="text-slate-400 text-xs font-semibold">المطلوب تثبيته (الاحتياج)</p><h3 id="genReq" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">مواد حرجة (< 7 أيام)</p><h3 id="genCrit" class="text-2xl font-bold text-rose-500 mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">توزيع الرصيد حسب التصنيف</h3><div class="w-full h-[300px] relative"><canvas id="genCatChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">الرصيد الفعلي مقابل المثبت</h3><div class="w-full h-[300px] relative"><canvas id="genCompChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-amber-300">سجل عام المجزر (التقرير الشامل)</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>التصنيف</th><th class="text-amber-400">المادة</th><th>الوحدة</th><th class="text-teal-400">الرصيد</th><th class="text-indigo-400">المثبت</th><th class="text-rose-400">المطلوب</th><th>يكفي أيام</th></tr></thead>
                        <tbody id="genTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 4. الثلاجات -->
        <div id="tab_frz" class="tab-content">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">المخزون الحالي (فعلي)</p><h3 id="frzBal" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-blue-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي الإنتاج الداخلي</p><h3 id="frzProd" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">المباع الصادر</p><h3 id="frzSold" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-rose-500 shadow"><p class="text-slate-400 text-xs font-semibold">النقص أو التالف</p><h3 id="frzShort" class="text-2xl font-bold text-rose-500 mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">المخزون لكل ثلاجة</h3><div class="w-full h-[300px] relative"><canvas id="frzStockChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">الإنتاج مقابل المبيعات</h3><div class="w-full h-[300px] relative"><canvas id="frzFlowChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-teal-300">سجل الثلاجات</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>المادة</th><th>الثلاجة</th><th>رصيد افتتاحي</th><th class="text-blue-400">الإنتاج</th><th class="text-amber-400">المباع</th><th class="text-rose-400">النقص</th><th class="text-teal-400">الرصيد النهائي</th></tr></thead>
                        <tbody id="frzTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 5. مخازن المجزر -->
        <div id="tab_slh" class="tab-content">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">الكمية المتوفرة</p><h3 id="slhBal" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-blue-500 shadow"><p class="text-slate-400 text-xs font-semibold">الإنتاج</p><h3 id="slhProd" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">المباع الصادر</p><h3 id="slhSold" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-indigo-500 shadow"><p class="text-slate-400 text-xs font-semibold">الرصيد السابق</p><h3 id="slhPrev" class="text-2xl font-bold text-white mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">أعلى 10 مواد مخزوناً</h3><div class="w-full h-[300px] relative"><canvas id="slhStockChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">نسبة الإنتاج للمباع</h3><div class="w-full h-[300px] relative"><canvas id="slhPieChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-blue-300">سجل مخازن المجزر</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>التاريخ</th><th>الكود</th><th class="text-amber-400">المادة</th><th>الرصيد السابق</th><th class="text-blue-400">الإنتاج</th><th class="text-rose-400">المباع</th><th class="text-teal-400">الكمية المتوفرة</th></tr></thead>
                        <tbody id="slhTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 6. المواد الأولية -->
        <div id="tab_mat" class="tab-content">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي الرصيد الحالي</p><h3 id="matBal" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-blue-500 shadow"><p class="text-slate-400 text-xs font-semibold">حركة الكميات المتداولة</p><h3 id="matQty" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">عدد الأقسام النشطة</p><h3 id="matDepts" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-indigo-500 shadow"><p class="text-slate-400 text-xs font-semibold">أنواع المواد</p><h3 id="matItems" class="text-2xl font-bold text-white mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">الأرصدة حسب الأقسام</h3><div class="w-full h-[300px] relative"><canvas id="matDeptChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">أعلى 10 مواد توفراً</h3><div class="w-full h-[300px] relative"><canvas id="matTopChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-amber-300">سجل المواد الأولية</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>التاريخ</th><th>نوع الإذن</th><th class="text-indigo-400">القسم</th><th class="text-amber-400">المادة</th><th>التصنيف</th><th class="text-blue-400">الكمية الحركة</th><th class="text-teal-400">الرصيد الحالي</th></tr></thead>
                        <tbody id="matTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 7. مشتريات المصنفات -->
        <div id="tab_pur_cat" class="tab-content">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-rose-500 shadow"><p class="text-slate-400 text-xs font-semibold">إجمالي المطلوب</p><h3 id="pcatReq" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-teal-500 shadow"><p class="text-slate-400 text-xs font-semibold">الرصيد الحالي</p><h3 id="pcatCur" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-indigo-500 shadow"><p class="text-slate-400 text-xs font-semibold">الشركات الموردة</p><h3 id="pcatComps" class="text-2xl font-bold text-white mt-1">0</h3></div>
                <div class="bg-slate-800 p-4 rounded-xl border-t-4 border-t-amber-500 shadow"><p class="text-slate-400 text-xs font-semibold">الموظفين المتابعين</p><h3 id="pcatEmps" class="text-2xl font-bold text-white mt-1">0</h3></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">توزيع الطلبات حسب الشركات</h3><div class="w-full h-[300px] relative"><canvas id="pcatCompChart"></canvas></div></div>
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700"><h3 class="text-sm font-bold text-slate-300 mb-2">المطلوب مقابل الرصيد</h3><div class="w-full h-[300px] relative"><canvas id="pcatCompBarChart"></canvas></div></div>
            </div>
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-2xl pb-2">
                <div class="p-3 bg-slate-850 border-b border-slate-700"><span class="font-bold text-sm text-indigo-300">سجل مشتريات المصنفات</span></div>
                <div class="overflow-x-auto w-full max-h-[450px] overflow-y-auto">
                    <table class="w-full text-center text-xs advanced-table text-slate-300 whitespace-nowrap">
                        <thead><tr><th>تاريخ الطلب</th><th class="text-indigo-400">الشركة</th><th class="text-amber-400">اسم المادة</th><th>الموظف المتابع</th><th>الوحدة</th><th class="text-teal-400">الرصيد الحالي</th><th class="text-rose-400">المطلوب</th></tr></thead>
                        <tbody id="purCatTable"></tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <script>
        // ======================= الروابط السحابية الـ 7 =======================
        const URLS = {
            sales: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRdYYKBv1JCC2q5pcgJAc6QyQGJc9Lsz9EaPD8t2HC5KADIoVzkFCJ-6JaF4tbdfw/pub?output=csv',
            frz: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQDphmbL58bqGdSFFFpU7NfVtAefvztGcjf5zPX8FBl5Rj3tW6H8vySo3T8CXGzyQ/pub?output=csv',
            slh: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQHSv4SF_rudpU2753hjWpkwyuiQ59RHr3zfiZZb43IOmdf1PZvytibN_Dc5Oxwxg/pub?output=csv',
            gen: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTiM4ycja48KN-96D91Ppv0CHRkIzyOBGgpAszLcOEID09N5CYspJSSsU98wvIFyQ/pub?output=csv',
            mat: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTyT8AIVzoC083IILST_hw5Q4j29tMBoYpdA568JyzSuJuOnX0BKq0MwOa9GE0aBQ/pub?output=csv',
            pcat: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ5lFKwIUSMCyYxRvpRMUl3PDlO6JY-x07zi0FgH9O2Atbryh4TjEpH7UGxtQ_Cw/pub?output=csv',
            pslh: 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRfd4_W6y4OJ_Ztbn9d1oJwFz9JOpgyExrOjdnG8Y5ecBDZZctHbo-099vM6-5tdw/pub?output=csv'
        };

        // ======================= المتغيرات الأساسية =======================
        let USERS = { 'admin': { pass: '1234', role: 'admin', name: 'المدير العام' } };
        let currentUser = null;
        let isLightMode = false;
        let currentMetric = 'tons'; 
        let chartInstances = {};
        let ALL_DATA = { sales:[], frz:[], slh:[], gen:[], mat:[], pcat:[], pslh:[] };
        
        const govColors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#0ea5e9'];
        Chart.defaults.color = '#94a3b8'; 
        Chart.defaults.font.family = 'Cairo';

        // ======================= التبديل والتسجيل =======================
        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
            
            if(tabId === 'tab_sales') renderSales();
            if(tabId === 'tab_frz') renderFrz();
            if(tabId === 'tab_slh') renderSlh();
            if(tabId === 'tab_gen') renderGen();
            if(tabId === 'tab_mat') renderMat();
            if(tabId === 'tab_pur_cat') renderPurCat();
            if(tabId === 'tab_pur_slh') renderPurSlh();
        }

        function checkLogin() {
            if(document.getElementById('passwordInput').value === '1234') {
                document.getElementById('loginOverlay').style.display = 'none';
                document.getElementById('mainDashboard').style.display = 'block';
                fetchServerExcel();
            } else { document.getElementById('loginError').style.display = 'block'; }
        }
        function logout() { location.reload(); }
        
        function toggleTheme() {
            isLightMode = !isLightMode;
            document.body.classList.toggle('light-theme', isLightMode);
            document.getElementById('themeBtnLogin').innerText = isLightMode ? '🌙' : '☀️';
            document.getElementById('themeBtnMain').innerText = isLightMode ? '🌙' : '☀️';
            Chart.defaults.color = isLightMode ? '#5f6368' : '#94a3b8';
            switchTab(document.querySelector('.tab-content.active').id, document.querySelector('.tab-btn.active'));
        }

        // ======================= نظام سحب الداتا العنيف (مضاد التعليق) =======================
        async function fetchServerExcel() {
            const statusEl = document.getElementById('status');
            statusEl.innerText = 'جاري السحب الآمن...';
            
            const buster = '&t=' + Date.now();
            // نستخدم Promise.allSettled حتى إذا وكف رابط، الباقيات يكملن
            const results = await Promise.allSettled([
                fetch(URLS.sales + buster).then(r => r.text()),
                fetch(URLS.frz + buster).then(r => r.text()),
                fetch(URLS.slh + buster).then(r => r.text()),
                fetch(URLS.gen + buster).then(r => r.text()),
                fetch(URLS.mat + buster).then(r => r.text()),
                fetch(URLS.pcat + buster).then(r => r.text()),
                fetch(URLS.pslh + buster).then(r => r.text())
            ]);

            if(results[0].status === 'fulfilled') parseSales(results[0].value);
            if(results[1].status === 'fulfilled') parseFrz(results[1].value);
            if(results[2].status === 'fulfilled') parseSlh(results[2].value);
            if(results[3].status === 'fulfilled') parseGen(results[3].value);
            if(results[4].status === 'fulfilled') parseMat(results[4].value);
            if(results[5].status === 'fulfilled') parsePcat(results[5].value);
            if(results[6].status === 'fulfilled') parsePslh(results[6].value);

            statusEl.innerText = 'الأنظمة متصلة 🟢';
        }

        function cleanNum(val) { return parseFloat(String(val).replace(/,/g, '').replace('-', '0')) || 0; }

        // ======================= دوال التحليل (Parsing) للـ 7 أقسام =======================
        function parseSales(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.sales = [];
            for(let i=1; i<rows.length; i++) {
                const c = rows[i]; if(!c[1] && !c[2]) continue;
                ALL_DATA.sales.push({ c0:c[0], c1:c[1], c2:c[2], tons:cleanNum(c[3]), count:cleanNum(c[4]), c5:c[5], agent:c[6]||'غير محدد', item:c[7]||'غير محدد', date:c[9], gov:c[11]||'غير محدد', cat:c[17]||c[16]||'أخرى', ffClass: String(c[8]).includes('مجمد')?'مجمد':'فريش' });
            }
            if(document.getElementById('tab_sales').classList.contains('active')) renderSales();
        }

        function parseFrz(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.frz = [];
            let h = rows[0].map(x=>String(x).toLowerCase());
            let iItem=h.findIndex(x=>x.includes('ماد')), iFrz=h.findIndex(x=>x.includes('ثلاج')), iStart=h.findIndex(x=>x.includes('رصيد')), iProd=h.findIndex(x=>x.includes('نتاج')), iSold=h.findIndex(x=>x.includes('مباع')||x.includes('صادر')), iShort=h.findIndex(x=>x.includes('نقص')), iFin=h.findIndex(x=>x.includes('نهائي'));
            for(let i=1; i<rows.length; i++) { let r=rows[i]; if(!r[iItem]) continue; ALL_DATA.frz.push({ item:r[iItem], frz:r[iFrz], start:cleanNum(r[iStart]), prod:cleanNum(r[iProd]), sold:cleanNum(r[iSold]), short:cleanNum(r[iShort]), final:cleanNum(r[iFin]) }); }
        }

        function parseSlh(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.slh = [];
            for(let i=1; i<rows.length; i++) { let r=rows[i]; if(!r[1] && !r[2]) continue; ALL_DATA.slh.push({ date:r[0], code:r[1], item:r[2], prev:cleanNum(r[3]), prod:cleanNum(r[4]), sold:cleanNum(r[5]), qty:cleanNum(r[6]) }); }
        }

        function parseGen(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.gen = [];
            let h = rows[0].map(x=>String(x).toLowerCase());
            let cCat=h.findIndex(x=>x.includes('تصنيف')), cItem=h.findIndex(x=>x.includes('مادة')), cUnit=h.findIndex(x=>x.includes('وحدة')), cBal=h.findIndex(x=>x.includes('الرصيد')&&!x.includes('/')&&!x.includes('+')), cConf=h.findIndex(x=>x.includes('المثبت')&&!x.includes('/')&&!x.includes('+')&&!x.includes('مطلوب')), cReq=h.findIndex(x=>x.includes('مطلوب')), cCov=h.findIndex(x=>x.includes('يكفي')&&!x.includes('+'));
            for(let i=1; i<rows.length; i++) { let r=rows[i]; if(!r[cItem]) continue; ALL_DATA.gen.push({ cat:r[cCat]||'-', item:r[cItem]||'-', unit:r[cUnit]||'-', bal:cleanNum(r[cBal]), conf:cleanNum(r[cConf]), req:cleanNum(r[cReq]), cov:cleanNum(r[cCov]) }); }
        }

        function parseMat(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.mat = [];
            let hIdx=0; for(let i=0;i<10;i++) if(rows[i]&&rows[i].join('').includes('المادة')) {hIdx=i; break;}
            let h = rows[hIdx].map(x=>String(x).toLowerCase());
            let cDate=h.findIndex(x=>x.includes('تاريخ')), cType=h.findIndex(x=>x.includes('نوع')), cDept=h.findIndex(x=>x.includes('قسم')), cItem=h.findIndex(x=>x.includes('مادة')&&!x.includes('كود')), cQty=h.findIndex(x=>x.includes('كمية')), cBal=h.findIndex(x=>x.includes('رصيد')&&x.includes('حالي')), cCat=h.findIndex(x=>x.includes('تصنيف'));
            for(let i=hIdx+1; i<rows.length; i++) { let r=rows[i]; if(!r[cItem]) continue; ALL_DATA.mat.push({ date:r[cDate], type:r[cType], dept:r[cDept]||'-', item:r[cItem]||'-', qty:cleanNum(r[cQty]), bal:cleanNum(r[cBal]), cat:r[cCat]||'-' }); }
        }

        function parsePcat(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.pcat = [];
            let h = rows[0].map(x=>String(x).toLowerCase());
            let cEmp=h.findIndex(x=>x.includes('موظف')), cComp=h.findIndex(x=>x.includes('شركة')), cReq=h.findIndex(x=>x.includes('مطلوب')), cCur=h.findIndex(x=>x.includes('رصيد')), cItem=h.findIndex(x=>x.includes('مادة')), cDate=h.findIndex(x=>x.includes('تاريخ')), cUnit=h.findIndex(x=>x.includes('وحدة'));
            for(let i=1; i<rows.length; i++) { let r=rows[i]; if(!r[cItem]) continue; ALL_DATA.pcat.push({ date:r[cDate], comp:r[cComp]||'-', item:r[cItem], emp:r[cEmp]||'-', unit:r[cUnit], req:cleanNum(r[cReq]), cur:cleanNum(r[cCur]) }); }
        }

        function parsePslh(csv) {
            const rows = XLSX.utils.sheet_to_json(XLSX.read(csv, {type:'string'}).Sheets[XLSX.read(csv, {type:'string'}).SheetNames[0]], {header:1, defval:""});
            ALL_DATA.pslh = [];
            for (let i = 1; i < rows.length; i++) { let c = rows[i]; if (!c[0] && !c[1] && !c[5] && !c[6]) continue; ALL_DATA.pslh.push({ code:c[0], item:c[1], cat:c[2], dept:c[3], unit:c[4], curBal:cleanNum(c[5]), reqSys:cleanNum(c[6]), comp:c[7]||'-', date:c[8], status:c[9]||'-' }); }
        }

        // ======================= دوال رسم الجارتات الموحدة =======================
        function drawChart(id, type, labels, dataArr, title, bgColors, isDouble=false, dData2=null, label2=null) {
            if(chartInstances[id]) chartInstances[id].destroy();
            const gridColor = isLightMode ? '#e2e8f0' : '#3c4043';
            const isPie = type==='pie'||type==='doughnut';
            
            let datasets = [];
            if(isDouble) {
                datasets = [ { label: title, data: dataArr, backgroundColor: '#f28b82' }, { label: label2, data: dData2, backgroundColor: '#81c995' } ];
            } else {
                datasets = [{ data: dataArr, backgroundColor: bgColors||'#8ab4f8', borderWidth: isPie?0:1 }];
            }

            chartInstances[id] = new Chart(document.getElementById(id).getContext('2d'), {
                type: type,
                data: { labels: labels, datasets: datasets },
                options: { responsive: true, maintainAspectRatio: false, cutout: isPie?'65%':0, plugins: { legend: { display: isPie||isDouble, position: 'top' } }, scales: isPie ? {} : { x: { grid: { display: false } }, y: { grid: { color: gridColor } } } }
            });
        }

        // ======================= دوال العرض للـ 7 أقسام =======================
        function setMetric(m) { currentMetric = m; document.getElementById('btnMetricTons').className = m === 'tons' ? 'metric-btn active' : 'metric-btn'; document.getElementById('btnMetricCount').className = m === 'count' ? 'metric-btn active' : 'metric-btn'; renderSales(); }
        function setDateFilter(type, btn) { document.querySelectorAll('.date-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); renderSales(); }

        // 1. المبيعات
        function renderSales() {
            let d = ALL_DATA.sales; if(!d.length) return;
            let tTons=0, tCount=0, govMap={}, agentMap={}, table='';
            d.forEach(r => {
                tTons += r.tons; tCount += r.count;
                let val = currentMetric === 'tons' ? r.tons : r.count;
                govMap[r.gov] = (govMap[r.gov]||0) + val;
                agentMap[r.agent] = (agentMap[r.agent]||0) + val;
                if(table.length < 3000) table += `<tr><td><span class="${r.ffClass==='فريش'?'text-up':'text-down'}">${r.ffClass}</span></td><td>${r.c0}</td><td>${r.c2}</td><td class="text-teal-400">${r.tons.toFixed(2)}</td><td class="text-amber-400">${r.count}</td><td>${r.c5}</td><td>${r.agent}</td><td class="truncate max-w-[150px]">${r.item}</td><td>${r.date}</td><td>${r.gov}</td></tr>`;
            });
            document.getElementById('totalTons').innerText = tTons.toLocaleString(undefined, {minimumFractionDigits:2}); document.getElementById('totalCount').innerText = tCount.toLocaleString(); document.getElementById('totalDocs').innerText = d.length.toLocaleString(); document.getElementById('salesTable').innerHTML = table;
            
            let gSort = Object.keys(govMap).sort((a,b)=>govMap[b]-govMap[a]);
            drawChart('growthChart', 'bar', gSort, gSort.map(x=>govMap[x]), 'المحافظات', '#8ab4f8');
            let aSort = Object.keys(agentMap).sort((a,b)=>agentMap[b]-agentMap[a]).slice(0,10);
            drawChart('paretoChart', 'bar', aSort, aSort.map(x=>agentMap[x]), 'الوكلاء', '#81c995');
        }

        // 2. مشتريات المجزر
        function renderPurSlh() {
            let d = ALL_DATA.pslh; if(!d.length) return;
            let tR=0, tC=0, comps=new Set(), items=new Set(), cMap={}, iMapReq={}, iMapCur={}, table='';
            d.forEach(r => {
                tR+=r.reqSys; tC+=r.curBal; comps.add(r.comp); items.add(r.item);
                cMap[r.comp] = (cMap[r.comp]||0) + r.reqSys;
                iMapReq[r.item] = (iMapReq[r.item]||0) + r.reqSys; iMapCur[r.item] = (iMapCur[r.item]||0) + r.curBal;
                table += `<tr><td>${r.code}</td><td class="truncate max-w-[150px] text-amber-400 font-bold">${r.item}</td><td>${r.cat}</td><td>${r.dept}</td><td>${r.unit}</td><td class="text-teal-400 font-bold">${r.curBal.toLocaleString()}</td><td class="text-rose-400 font-bold">${r.reqSys.toLocaleString()}</td><td class="text-indigo-400 font-bold">${r.comp}</td><td>${r.date}</td><td>${r.status}</td></tr>`;
            });
            document.getElementById('pslhReq').innerText = tR.toLocaleString(); document.getElementById('pslhCur').innerText = tC.toLocaleString(); document.getElementById('pslhComps').innerText = comps.size; document.getElementById('pslhItems').innerText = items.size; document.getElementById('purSlhTable').innerHTML = table;
            
            let cKeys = Object.keys(cMap); drawChart('pslhCompChart', 'doughnut', cKeys, cKeys.map(x=>cMap[x]), '', govColors);
            let topItems = Object.keys(iMapReq).map(i => ({item:i, req:iMapReq[i], cur:iMapCur[i]})).sort((a,b)=>b.req-a.req).slice(0,10);
            drawChart('pslhCompBarChart', 'bar', topItems.map(x=>x.item.substring(0,15)), topItems.map(x=>x.req), 'المطلوب', null, true, topItems.map(x=>x.cur), 'الرصيد');
        }

        // 3. عام المجزر
        function renderGen() {
            let d = ALL_DATA.gen; if(!d.length) return;
            let tB=0, tC=0, tR=0, crit=0, cMap={}, iMapReq={}, iMapCur={}, table='';
            d.forEach(r => {
                tB+=r.bal; tC+=r.conf; tR+=r.req; if(r.cov > 0 && r.cov < 7) crit++;
                cMap[r.cat] = (cMap[r.cat]||0) + r.bal;
                iMapReq[r.item] = (iMapReq[r.item]||0) + r.req; iMapCur[r.item] = (iMapCur[r.item]||0) + r.bal;
                table += `<tr><td>${r.cat}</td><td class="text-amber-400 truncate max-w-[150px] font-bold">${r.item}</td><td>${r.unit}</td><td class="text-teal-400 font-bold">${r.bal.toLocaleString()}</td><td class="text-indigo-400 font-bold">${r.conf.toLocaleString()}</td><td class="text-rose-400 font-bold">${r.req.toLocaleString()}</td><td>${r.cov}</td></tr>`;
            });
            document.getElementById('genBal').innerText = tB.toLocaleString(); document.getElementById('genConf').innerText = tC.toLocaleString(); document.getElementById('genReq').innerText = tR.toLocaleString(); document.getElementById('genCrit').innerText = crit.toLocaleString(); document.getElementById('genTable').innerHTML = table;
            
            let cKeys = Object.keys(cMap); drawChart('genCatChart', 'doughnut', cKeys, cKeys.map(x=>cMap[x]), '', govColors);
            let topItems = Object.keys(iMapReq).map(i => ({item:i, req:iMapReq[i], cur:iMapCur[i]})).sort((a,b)=>b.cur-a.cur).slice(0,10);
            drawChart('genCompChart', 'bar', topItems.map(x=>x.item.substring(0,15)), topItems.map(x=>x.cur), 'الرصيد', null, true, topItems.map(x=>x.req), 'المثبت');
        }

        // 4. الثلاجات
        function renderFrz() {
            let d = ALL_DATA.frz; if(!d.length) return;
            let tF=0, tP=0, tS=0, tSh=0, fMap={}, sMap={}, table='';
            d.forEach(r => {
                tF+=r.final; tP+=r.prod; tS+=r.sold; tSh+=r.short;
                fMap[r.frz] = (fMap[r.frz]||0) + r.final;
                if(r.short>0) sMap[r.frz] = (sMap[r.frz]||0) + r.short;
                table += `<tr><td class="truncate max-w-[150px]">${r.item}</td><td>${r.frz}</td><td>${r.start.toLocaleString()}</td><td class="text-blue-400 font-bold">${r.prod.toLocaleString()}</td><td class="text-amber-400 font-bold">${r.sold.toLocaleString()}</td><td class="text-rose-400 font-bold">${r.short.toLocaleString()}</td><td class="text-teal-400 font-bold">${r.final.toLocaleString()}</td></tr>`;
            });
            document.getElementById('frzBal').innerText = tF.toLocaleString(); document.getElementById('frzProd').innerText = tP.toLocaleString(); document.getElementById('frzSold').innerText = tS.toLocaleString(); document.getElementById('frzShort').innerText = tSh.toLocaleString(); document.getElementById('frzTable').innerHTML = table;
            
            let fKeys = Object.keys(fMap); drawChart('frzStockChart', 'bar', fKeys, fKeys.map(x=>fMap[x]), '', '#8ab4f8');
            drawChart('frzFlowChart', 'doughnut', ['الإنتاج','المباع'], [tP, tS], '', ['#8ab4f8', '#f28b82']);
        }

        // 5. مخازن المجزر
        function renderSlh() {
            let d = ALL_DATA.slh; if(!d.length) return;
            let tQ=0, tP=0, tS=0, tPrev=0, iMap={}, table='';
            d.forEach(r => {
                tQ+=r.qty; tP+=r.prod; tS+=r.sold; tPrev+=r.prev;
                iMap[r.item] = (iMap[r.item]||0) + r.qty;
                table += `<tr><td>${r.date}</td><td>${r.code}</td><td class="text-amber-400 font-bold truncate max-w-[150px]">${r.item}</td><td>${r.prev.toLocaleString()}</td><td class="text-blue-400 font-bold">${r.prod.toLocaleString()}</td><td class="text-rose-400 font-bold">${r.sold.toLocaleString()}</td><td class="text-teal-400 font-bold">${r.qty.toLocaleString()}</td></tr>`;
            });
            document.getElementById('slhBal').innerText = tQ.toLocaleString(); document.getElementById('slhProd').innerText = tP.toLocaleString(); document.getElementById('slhSold').innerText = tS.toLocaleString(); document.getElementById('slhPrev').innerText = tPrev.toLocaleString(); document.getElementById('slhTable').innerHTML = table;
            
            let iKeys = Object.keys(iMap).sort((a,b)=>iMap[b]-iMap[a]).slice(0,10); drawChart('slhStockChart', 'bar', iKeys.map(k=>k.substring(0,15)), iKeys.map(x=>iMap[x]), '', '#81c995');
            drawChart('slhPieChart', 'doughnut', ['إنتاج','مباع'], [tP, tS], '', ['#8ab4f8', '#f28b82']);
        }

        // 6. المواد الأولية
        function renderMat() {
            let d = ALL_DATA.mat; if(!d.length) return;
            let tB=0, tQ=0, dMap={}, cMap={}, items=new Set(), table='';
            d.forEach(r => {
                tB+=r.bal; tQ+=r.qty; items.add(r.item);
                dMap[r.dept] = (dMap[r.dept]||0) + r.bal; cMap[r.cat] = (cMap[r.cat]||0) + r.bal;
                table += `<tr><td>${r.date}</td><td>${r.type}</td><td class="text-indigo-400">${r.dept}</td><td class="text-amber-400 truncate max-w-[150px]">${r.item}</td><td>${r.cat}</td><td class="text-blue-400">${r.qty.toLocaleString()}</td><td class="text-teal-400 font-bold">${r.bal.toLocaleString()}</td></tr>`;
            });
            document.getElementById('matBal').innerText = tB.toLocaleString(); document.getElementById('matQty').innerText = tQ.toLocaleString(); document.getElementById('matItems').innerText = items.size.toLocaleString(); document.getElementById('matDepts').innerText = Object.keys(dMap).length.toLocaleString(); document.getElementById('matTable').innerHTML = table;
            
            let dKeys = Object.keys(dMap).sort((a,b)=>dMap[b]-dMap[a]); drawChart('matDeptChart', 'bar', dKeys, dKeys.map(x=>dMap[x]), '', '#8ab4f8');
            let cKeys = Object.keys(cMap); drawChart('matCatChart', 'doughnut', cKeys, cKeys.map(x=>cMap[x]), '', govColors);
        }

        // 7. مشتريات المصنفات
        function renderPurCat() {
            let d = ALL_DATA.pcat; if(!d.length) return;
            let tR=0, tC=0, comps=new Set(), emps=new Set(), cMap={}, iMapReq={}, iMapCur={}, table='';
            d.forEach(r => {
                tR+=r.req; tC+=r.cur; comps.add(r.comp); emps.add(r.emp);
                cMap[r.comp] = (cMap[r.comp]||0) + r.req;
                iMapReq[r.item] = (iMapReq[r.item]||0) + r.req; iMapCur[r.item] = (iMapCur[r.item]||0) + r.cur;
                table += `<tr><td>${r.date}</td><td class="text-indigo-400 font-bold">${r.comp}</td><td class="text-amber-400 truncate max-w-[150px] font-bold">${r.item}</td><td>${r.emp}</td><td>${r.unit}</td><td class="text-teal-400 font-bold">${r.cur.toLocaleString()}</td><td class="text-rose-400 font-bold">${r.req.toLocaleString()}</td></tr>`;
            });
            document.getElementById('pcatReq').innerText = tR.toLocaleString(); document.getElementById('pcatCur').innerText = tC.toLocaleString(); document.getElementById('pcatComps').innerText = comps.size; document.getElementById('pcatEmps').innerText = emps.size; document.getElementById('purCatTable').innerHTML = table;
            
            let cKeys = Object.keys(cMap); drawChart('pcatCompChart', 'doughnut', cKeys, cKeys.map(x=>cMap[x]), '', govColors);
            let topItems = Object.keys(iMapReq).map(i => ({item:i, req:iMapReq[i], cur:iMapCur[i]})).sort((a,b)=>b.req-a.req).slice(0,10);
            drawChart('pcatCompBarChart', 'bar', topItems.map(x=>x.item.substring(0,15)), topItems.map(x=>x.req), 'المطلوب', null, true, topItems.map(x=>x.cur), 'الرصيد');
        }

    </script>
</body>
</html>
