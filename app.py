<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>تطبيق الشامل</title>

    <!-- ربط الملفات محلياً بدون إنترنت -->
    <script src="tailwind.js"></script>
    <script src="xlsx.js"></script>

    <style>
        /* استخدمنا خط النظام الأساسي للأندرويد حتى يشتغل بدون نت */
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }

        /* ستايل شاشة الدخول */
        .auth-top-curve { background-color: #ffffff; color: #0f172a; border-bottom-left-radius: 50px; border-bottom-right-radius: 50px; padding: 40px 20px; text-align: center; position: relative; z-index: 10; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.2); }
        .auth-bottom { background-color: #18202f; flex: 1; padding: 40px 24px; display: flex; flex-direction: column; justify-content: center; }
        .auth-input { width: 100%; padding: 14px 16px; margin-bottom: 16px; background-color: #111827; border: 1px solid #334155; color: white; border-radius: 12px; font-size: 0.95rem; outline: none; transition: border-color 0.2s; text-align: center; letter-spacing: 8px;}
        .auth-input:focus { border-color: #3b82f6; }
        .auth-btn { width: 100%; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; font-weight: bold; font-size: 1.1rem; padding: 14px; border-radius: 12px; border: none; cursor: pointer; transition: transform 0.1s; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);}
        .auth-btn:active { transform: scale(0.96); }

        /* الشاشات الداخلية */
        .app-card { transition: all 0.2s ease-in-out; }
        .app-card:active { transform: scale(0.97); }

        .glass-panel { background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(51, 65, 85, 0.5); }
        .input-field { width: 100%; padding: 12px; background-color: #111827; border: 1px solid #334155; color: white; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.2s;}
        .input-field:focus { border-color: #cca344; }

        /* أزرار اختيار الخط */
        .radio-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .radio-label { text-align: center; padding: 10px 4px; background-color: #111827; border: 1px solid #334155; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.2s; color: #94a3b8; font-size: 0.85rem;}
        .radio-input { display: none; }
        .radio-input:checked + .radio-label.go { background-color: #f59e0b; color: #fff; border-color: #f59e0b; }
        .radio-input:checked + .radio-label.return { background-color: #3b82f6; color: #fff; border-color: #3b82f6; }
        .radio-input:checked + .radio-label.full { background-color: #10b981; color: #fff; border-color: #10b981; }
        .radio-input:checked + .radio-label.pay { background-color: #ef4444; color: #fff; border-color: #ef4444; }

        .btn-gold { background-color: #cca344; color: white; font-weight: bold; transition: all 0.2s; }
        .btn-gold:hover { background-color: #b8923e; }
        .btn-gold:active { transform: scale(0.97); }
        .btn-rose { background-color: #e11d48; color: white; font-weight: bold; transition: all 0.2s; }
        .btn-emerald { background-color: #10b981; color: white; font-weight: bold; transition: all 0.2s; }

        .fade-in { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

        .pin-dot { width: 12px; height: 12px; border-radius: 50%; background: #334155; transition: all 0.2s; }
        .pin-dot.filled { background: #3b82f6; box-shadow: 0 0 8px #3b82f6; }

        /* أزرار التبويبات في الأرشيف */
        .tab-btn { flex: 1; text-align: center; padding: 12px; font-size: 0.9rem; font-weight: bold; color: #94a3b8; border-bottom: 2px solid transparent; transition: all 0.2s; }
        .tab-btn.active { color: #3b82f6; border-bottom-color: #3b82f6; }
    </style>
</head>
<body class="w-full min-h-screen flex justify-center items-center">

<div class="w-full max-w-md bg-[#18202f] min-h-screen md:min-h-[850px] flex flex-col relative md:rounded-[30px] md:shadow-2xl overflow-hidden md:border-[8px] md:border-slate-800">

    <!-- ================= نافذة التنبيهات المخصصة ================= -->
    <div id="customDialog" class="hidden absolute inset-0 bg-black/80 z-[200] flex items-center justify-center p-4 transition-opacity">
        <div class="glass-panel w-full max-w-[280px] rounded-2xl p-6 border border-slate-600 shadow-2xl fade-in text-center bg-[#1e293b]">
            <h3 id="dialogTitle" class="text-lg font-bold text-white mb-2">تنبيه</h3>
            <p id="dialogMessage" class="text-slate-300 text-sm mb-6"></p>
            <div class="flex gap-3 justify-center">
                <button id="dialogConfirm" class="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-bold hover:bg-blue-500 transition">موافق</button>
                <button id="dialogCancel" class="hidden flex-1 bg-slate-700 text-white py-2.5 rounded-lg font-bold hover:bg-slate-600 transition">إلغاء</button>
            </div>
        </div>
    </div>

    <!-- ================= نافذة تغيير الرمز ================= -->
    <div id="changePinModal" class="hidden absolute inset-0 bg-black/80 z-[100] flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-sm p-6 rounded-2xl border border-slate-700 fade-in bg-[#1e293b]">
            <h3 class="text-lg font-bold text-white mb-4 text-center">⚙️ تغيير رمز الدخول</h3>
            <div class="flex flex-col gap-3">
                <div>
                    <label class="text-xs text-slate-400 mb-1 block">الرمز القديم الحالي:</label>
                    <input type="tel" id="oldPinInput" placeholder="••••" maxlength="4" class="input-field text-center tracking-widest text-lg font-bold text-white">
                </div>
                <div>
                    <label class="text-xs text-slate-400 mb-1 block">الرمز الجديد (4 أرقام):</label>
                    <input type="tel" id="newPinInput" placeholder="••••" maxlength="4" class="input-field text-center tracking-widest text-lg font-bold text-emerald-400">
                </div>
                <div class="flex gap-2 mt-3">
                    <button onclick="confirmChangePin()" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2.5 rounded-lg font-bold transition">حفظ الرمز ✅</button>
                    <button onclick="closeChangePinModal()" class="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-2.5 rounded-lg font-bold transition">إلغاء ❌</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ================= [1] شاشة الدخول (PIN) ================= -->
    <div id="authScreen" class="flex flex-col h-full w-full absolute top-0 left-0 z-50 bg-[#18202f]">
        <div class="auth-top-curve flex flex-col items-center justify-center pt-12 md:pt-16">
            <div class="w-24 h-24 mb-4 bg-slate-100 rounded-full flex items-center justify-center shadow-inner">
                <span class="text-6xl font-black text-blue-600">S</span>
            </div>
            <h1 class="text-3xl font-black mb-2 text-slate-800">الشامل</h1>
            <p class="text-sm text-slate-500 font-semibold">بوابتك الشخصية لإدارة أعمالك</p>
        </div>

        <div class="auth-bottom">
            <h2 id="authTitle" class="text-xl font-bold text-white mb-2 text-center">🔐 رمز الدخول</h2>
            <p id="authSubtitle" class="text-xs text-slate-400 text-center mb-6">أدخل رمز PIN مكون من 4 أرقام</p>

            <div class="flex justify-center gap-3 mb-8" id="pinDots">
                <div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div><div class="pin-dot"></div>
            </div>

            <form onsubmit="handlePinSubmit(event)">
                <input type="tel" id="pinInput" maxlength="4" inputmode="numeric" pattern="[0-9]*" class="auth-input" placeholder="••••" autocomplete="off" style="letter-spacing:16px; font-size:1.5rem; font-weight:bold;">
                <button type="submit" id="authSubmitBtn" class="auth-btn mt-2">دخول</button>
            </form>
            <div class="mt-6 text-center text-xs text-slate-500">
                <p id="pinHint">للحفاظ على سرية بياناتك المالية.</p>
            </div>
        </div>
    </div>

    <!-- ================= [2] الشاشة الرئيسية ================= -->
    <div id="mainScreen" class="flex-col h-full w-full hidden overflow-y-auto bg-[#0f172a]">
        <header class="p-4 bg-[#111827] border-b border-slate-800 flex justify-between items-center sticky top-0 z-40">
            <h1 class="text-lg font-bold text-white flex items-center gap-2">
                <span class="bg-blue-600 w-7 h-7 rounded-lg flex items-center justify-center text-white text-sm shadow-lg shadow-blue-600/30">S</span>
                الشامل
            </h1>
            <div class="flex gap-2">
                <button onclick="openChangePinModal()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white transition-colors text-sm" title="تغيير الرمز">⚙️</button>
                <button onclick="logout()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:bg-rose-500 hover:text-white transition-colors text-sm" title="تسجيل خروج">🚪</button>
            </div>
        </header>

        <main class="flex-1 p-5 flex flex-col gap-4">
            <div>
                <h2 class="text-white font-bold text-2xl mb-1">مرحباً بك 👋</h2>
                <p class="text-slate-400 text-sm mb-2">اختر النظام الذي تريد العمل عليه:</p>
            </div>

            <button onclick="openScreen('tripsScreen')" class="app-card w-full bg-gradient-to-l from-slate-800 to-slate-900 border border-slate-700 rounded-2xl p-5 flex items-center gap-4 hover:border-blue-500 text-right group">
                <div class="w-16 h-16 min-w-[4rem] bg-blue-500/10 rounded-xl flex items-center justify-center text-4xl group-hover:scale-110 transition-transform">🚗</div>
                <div class="flex-1">
                    <h3 class="text-white font-bold text-xl mb-1 group-hover:text-blue-400 transition-colors">حسابات الخطوط</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">سجل رحلاتك، احسب كروة السواق، وسدد ديونك.</p>
                </div>
            </button>

            <button onclick="openScreen('salaryScreen')" class="app-card w-full bg-gradient-to-l from-slate-800 to-slate-900 border border-slate-700 rounded-2xl p-5 flex items-center gap-4 hover:border-emerald-500 text-right group">
                <div class="w-16 h-16 min-w-[4rem] bg-emerald-500/10 rounded-xl flex items-center justify-center text-4xl group-hover:scale-110 transition-transform">💼</div>
                <div class="flex-1">
                    <h3 class="text-white font-bold text-xl mb-1 group-hover:text-emerald-400 transition-colors">الراتب والدوام</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">حاسبة الدقائق، أجور الساعات، وتتبع الحضور اليومي.</p>
                </div>
            </button>

            <button onclick="openScreen('tasksScreen')" class="app-card w-full bg-gradient-to-l from-slate-800 to-slate-900 border border-slate-700 rounded-2xl p-5 flex items-center gap-4 hover:border-amber-500 text-right group">
                <div class="w-16 h-16 min-w-[4rem] bg-amber-500/10 rounded-xl flex items-center justify-center text-4xl group-hover:scale-110 transition-transform">📝</div>
                <div class="flex-1">
                    <h3 class="text-white font-bold text-xl mb-1 group-hover:text-amber-400 transition-colors">إدارة المهام الذكية</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">تذكير بالدفعات، تسجيل الدوام، والأقساط المالية.</p>
                </div>
            </button>

            <button onclick="openScreen('archiveScreen')" class="app-card w-full bg-[#111827] border border-slate-700 rounded-2xl p-4 flex items-center gap-4 hover:border-indigo-500 text-right group mt-2">
                <div class="w-12 h-12 min-w-[3rem] bg-indigo-500/10 rounded-full flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">🗄️</div>
                <div class="flex-1">
                    <h3 class="text-white font-bold text-lg mb-1 group-hover:text-indigo-400 transition-colors">الأرشيف والسجلات</h3>
                    <p class="text-slate-400 text-xs leading-relaxed">استعرض كل بياناتك السابقة، وقم بتصديرها لملف إكسل.</p>
                </div>
            </button>

        </main>
    </div>

    <!-- ================= [3] شاشة الخطوط ================= -->
    <div id="tripsScreen" class="flex-col h-full w-full hidden overflow-y-auto bg-[#0f172a]">
        <header class="p-4 bg-[#111827] border-b border-slate-800 flex justify-between items-center sticky top-0 z-40 shadow-md">
            <div class="flex items-center gap-3">
                <button onclick="backToMain()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:bg-slate-700 hover:text-white transition-colors text-sm">🔙</button>
                <h1 class="text-lg font-bold text-blue-400">حسابات الخطوط 🚗</h1>
            </div>
        </header>

        <main class="flex-1 p-4 flex flex-col gap-4">
            <div class="glass-panel p-3 rounded-xl text-center border-t-2 border-t-amber-500">
                <p class="text-[10px] text-slate-400 mb-1">إجمالي الديون التراكمية النشطة</p>
                <h2 id="trips_totalAmount" class="text-2xl font-bold text-white">0</h2>
            </div>

            <div class="glass-panel p-4 rounded-xl border border-blue-500/30">
                <h3 class="text-sm font-bold text-blue-400 mb-3">➕ تسجيل حركة جديدة</h3>
                <form onsubmit="saveTrip(event)" class="flex flex-col gap-3">
                    <div class="radio-grid">
                        <div><input type="radio" id="typeGo" name="tripType" value="go" class="radio-input" onchange="updateFare()" checked><label for="typeGo" class="radio-label go block">ذهاب ☀️</label></div>
                        <div><input type="radio" id="typeReturn" name="tripType" value="return" class="radio-input" onchange="updateFare()"><label for="typeReturn" class="radio-label return block">عودة 🌙</label></div>
                        <div><input type="radio" id="typeFull" name="tripType" value="full" class="radio-input" onchange="updateFare()"><label for="typeFull" class="radio-label full block">يوم كامل 🔄</label></div>
                        <div><input type="radio" id="typePay" name="tripType" value="pay" class="radio-input" onchange="updateFare()"><label for="typePay" class="radio-label pay block">تسديد 💸</label></div>
                    </div>
                    <input type="text" id="driverName" required placeholder="اسم السائق (مثال: أبو كرار)" class="input-field" list="savedDrivers" autocomplete="off">
                    <datalist id="savedDrivers"></datalist>
                    <div class="grid grid-cols-2 gap-3">
                        <div><label id="fareLabel" class="text-xs text-slate-400 mb-1 block">المبلغ (دينار):</label><input type="number" id="tripFare" required class="input-field font-bold text-amber-500"></div>
                        <div><label class="text-xs text-slate-400 mb-1 block">التاريخ:</label><input type="date" id="tripDate" required class="input-field text-xs"></div>
                    </div>
                    <button id="saveTripBtn" type="submit" class="w-full bg-blue-600 text-white font-bold py-3 rounded-lg mt-1 active:scale-95 transition">حفظ السجل ✅</button>
                </form>
            </div>

            <div class="glass-panel p-4 rounded-xl border border-slate-700">
                <h3 class="text-sm font-bold text-slate-300 mb-2">⚙️ إعدادات الأجرة الافتراضية</h3>
                <div class="grid grid-cols-3 gap-2">
                    <div><label class="text-[10px] text-slate-400">ذهاب:</label><input type="number" id="defGo" value="3000" min="0" class="input-field py-2 text-xs" onchange="saveTripSettings()"></div>
                    <div><label class="text-[10px] text-slate-400">عودة:</label><input type="number" id="defRet" value="3000" min="0" class="input-field py-2 text-xs" onchange="saveTripSettings()"></div>
                    <div><label class="text-[10px] text-slate-400">كامل:</label><input type="number" id="defFull" value="6000" min="0" class="input-field py-2 text-xs" onchange="saveTripSettings()"></div>
                </div>
            </div>

            <div class="glass-panel p-4 rounded-xl">
                <h3 class="text-sm font-bold text-slate-200 mb-2 border-b border-slate-700 pb-2">💳 الديون الحالية (للسواق)</h3>
                <div id="trips_driversSummary" class="flex flex-col gap-2 max-h-40 overflow-y-auto pr-1"></div>
            </div>

            <div class="glass-panel p-4 rounded-xl mb-4">
                <div class="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                    <h3 class="text-sm font-bold text-slate-200">📜 أحدث الحركات</h3>
                </div>
                <div id="tripsLog" class="flex flex-col gap-2 max-h-60 overflow-y-auto pr-1"></div>
            </div>
        </main>
    </div>

    <!-- ================= [4] شاشة الراتب والدوام ================= -->
    <div id="salaryScreen" class="flex-col h-full w-full hidden overflow-y-auto bg-[#0f172a]">
        <header class="p-4 bg-[#111827] border-b border-slate-800 flex justify-between items-center sticky top-0 z-40 shadow-md">
            <div class="flex items-center gap-3">
                <button onclick="backToMain()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:bg-slate-700 hover:text-white transition-colors text-sm">🔙</button>
                <h1 class="text-lg font-bold text-emerald-400">حاسبة الراتب 💼</h1>
            </div>
        </header>

        <main class="flex-1 p-4 flex flex-col gap-5">
            <div class="grid grid-cols-2 gap-3">
                <div class="glass-panel p-3 rounded-xl text-center border-t-2 border-t-[#cca344]">
                    <p class="text-[10px] text-slate-400 mb-1">المستحق التراكمي</p>
                    <h2 id="finalTotal" class="text-xl font-bold text-white">0</h2>
                    <p class="text-[10px] text-[#cca344]">دينار عراقي</p>
                </div>
                <div class="glass-panel p-3 rounded-xl text-center border-t-2 border-t-blue-500">
                    <p class="text-[10px] text-slate-400 mb-1">إجمالي الدقائق</p>
                    <h2 id="totalMinutes" class="text-xl font-bold text-white">0</h2>
                </div>
            </div>

            <div class="glass-panel p-4 rounded-xl">
                <h3 class="text-sm font-bold text-[#cca344] mb-3">➕ تسجيل دوام اليوم</h3>
                <form id="workForm" class="flex flex-col gap-3" onsubmit="saveWork(event)">
                    <div class="grid grid-cols-2 gap-3">
                        <div><label class="text-xs text-slate-400 mb-1 block">التاريخ:</label><input type="date" id="workDate" required class="input-field text-xs"></div>
                        <div><label class="text-xs text-slate-400 mb-1 block">الدقائق:</label><input type="number" id="workMinutes" required placeholder="420" min="1" max="1440" class="input-field font-bold text-[#cca344]"></div>
                    </div>
                    <button id="saveWorkBtn" type="submit" class="w-full btn-gold py-3 rounded-lg mt-1">حفظ الدوام ✅</button>
                    <button type="button" onclick="cancelEditWork()" id="cancelWorkBtn" class="w-full btn-rose py-2 rounded-lg hidden text-sm">إلغاء التعديل ❌</button>
                </form>
            </div>

            <div class="glass-panel p-4 rounded-xl">
                <h3 class="text-sm font-bold text-slate-200 mb-3 border-b border-slate-700 pb-2">⚙️ إعدادات الراتب (تسديد وخصم)</h3>
                <div class="flex flex-col gap-3">
                    <div>
                        <label class="text-xs text-slate-400 mb-1 block">أجرة الساعة (دينار):</label>
                        <input type="number" id="hourlyRate" placeholder="مثال: 5000" min="1" class="input-field font-bold text-[#cca344]" onchange="saveSalarySettings()">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="text-xs text-slate-400 mb-1 block">مبالغ مستلمة (تسديد):</label>
                            <input type="number" id="deductions" placeholder="0" min="0" value="0" class="input-field text-rose-500" onchange="saveSalarySettings()">
                        </div>
                        <div>
                            <label class="text-xs text-slate-400 mb-1 block">إضافة/بونص (دينار):</label>
                            <input type="number" id="prevBalance" placeholder="0" min="0" value="0" class="input-field text-emerald-400" onchange="saveSalarySettings()">
                        </div>
                    </div>
                </div>
            </div>

            <div class="glass-panel p-4 rounded-xl mb-6">
                <div class="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                    <h3 class="text-sm font-bold text-slate-200">📜 أحدث سجلات الدوام</h3>
                </div>
                <div id="workLog" class="flex flex-col gap-2 max-h-72 overflow-y-auto pr-1"></div>
            </div>
        </main>
    </div>

    <!-- ================= [5] شاشة إدارة المهام ================= -->
    <div id="tasksScreen" class="flex-col h-full w-full hidden overflow-y-auto bg-[#0f172a]">
        <header class="p-4 bg-[#111827] border-b border-slate-800 flex justify-between items-center sticky top-0 z-40 shadow-md">
            <div class="flex items-center gap-3">
                <button onclick="backToMain()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:bg-slate-700 hover:text-white transition-colors text-sm">🔙</button>
                <h1 class="text-lg font-bold text-amber-400">إدارة المهام الذكية 📝</h1>
            </div>
        </header>

        <main class="flex-1 p-4 flex flex-col gap-4">
            <div class="glass-panel p-4 rounded-xl border border-amber-500/30">
                <h3 class="text-sm font-bold text-amber-400 mb-3">➕ إضافة مهمة جديدة</h3>
                <form onsubmit="saveTask(event)" class="flex flex-col gap-3">
                    <div>
                        <select id="taskType" class="input-field py-2 text-xs" onchange="onTaskTypeChange()">
                            <option value="driver">🚗 تذكير بدفعة (سائق)</option>
                            <option value="work">💼 تذكير بتسجيل دوام</option>
                            <option value="financial">💰 هدف / قسط مالي</option>
                            <option value="general">📝 مهمة عامة أخرى</option>
                        </select>
                    </div>
                    <input type="text" id="taskTitle" required placeholder="مثال: استلم باقي أبو كرار" class="input-field text-sm">
                    <div class="grid grid-cols-2 gap-3">
                        <input type="number" id="taskAmount" placeholder="المبلغ (اختياري)" class="input-field text-sm">
                        <input type="date" id="taskDate" required class="input-field text-xs">
                    </div>
                    <button type="submit" class="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-2.5 rounded-lg text-sm transition">حفظ المهمة ✅</button>
                </form>
            </div>

            <div class="glass-panel p-4 rounded-xl mb-6">
                <div class="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                    <h3 class="text-sm font-bold text-slate-200">📋 قائمة المهام</h3>
                    <span id="tasksCount" class="text-xs text-amber-400 font-bold">0</span>
                </div>
                <div id="tasksLog" class="flex flex-col gap-2 max-h-96 overflow-y-auto pr-1"></div>
            </div>
        </main>
    </div>

    <!-- ================= [6] شاشة الأرشيف ================= -->
    <div id="archiveScreen" class="flex-col h-full w-full hidden overflow-y-auto bg-[#0f172a]">
        <header class="p-4 bg-[#111827] border-b border-slate-800 flex justify-between items-center sticky top-0 z-40 shadow-md">
            <div class="flex items-center gap-3">
                <button onclick="backToMain()" class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:bg-slate-700 hover:text-white transition-colors text-sm">🔙</button>
                <h1 class="text-lg font-bold text-indigo-400">الأرشيف والسجلات 🗄️</h1>
            </div>
        </header>

        <div class="flex bg-[#111827] border-b border-slate-800">
            <button id="tabArchiveTrips" onclick="switchArchiveTab('trips')" class="tab-btn active">أرشيف الخطوط 🚗</button>
            <button id="tabArchiveSalary" onclick="switchArchiveTab('salary')" class="tab-btn">أرشيف الدوام 💼</button>
        </div>

        <main class="flex-1 p-4 flex flex-col gap-4">

            <!-- أرشيف الخطوط -->
            <div id="archiveTripsContent" class="flex flex-col gap-4">
                <div class="glass-panel p-3 rounded-xl flex flex-col gap-2 border-t-2 border-indigo-500">
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-slate-400">الإجمالي الكلي المعروض:</span>
                        <span id="archiveTripsTotal" class="font-bold text-white text-lg">0</span>
                    </div>
                </div>

                <div class="glass-panel p-3 rounded-xl flex flex-col gap-2">
                    <input type="text" id="archiveTripsSearch" oninput="updateArchiveTripsUI()" placeholder="بحث عن سائق..." class="input-field py-2 text-sm">
                    <div class="flex gap-2">
                        <select id="archiveTripsMonth" onchange="updateArchiveTripsUI()" class="input-field py-2 text-xs flex-1">
                            <option value="all">📅 كل السجلات التراكمية</option>
                        </select>
                        <button onclick="exportTripsCSV()" class="bg-indigo-600 text-white px-4 rounded-lg text-xs font-bold whitespace-nowrap">تصدير CSV 📥</button>
                    </div>
                </div>

                <div class="glass-panel p-4 rounded-xl">
                    <div class="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                        <h3 class="text-sm font-bold text-slate-200">📜 كل سجلات الخطوط</h3>
                        <button onclick="clearTripsData()" class="text-[10px] text-rose-500 hover:underline">تصفير الكل 🗑️</button>
                    </div>
                    <div id="archiveTripsLog" class="flex flex-col gap-2 max-h-96 overflow-y-auto pr-1"></div>
                </div>
            </div>

            <!-- أرشيف الدوام -->
            <div id="archiveSalaryContent" class="hidden flex-col gap-4">
                <div class="glass-panel p-3 rounded-xl flex flex-col gap-2 border-t-2 border-indigo-500">
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-slate-400">إجمالي المبالغ المعروضة:</span>
                        <span id="archiveSalaryTotalMoney" class="font-bold text-white text-lg">0</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-slate-400">إجمالي الدقائق المعروضة:</span>
                        <span id="archiveSalaryTotalMins" class="font-bold text-amber-400 text-sm">0</span>
                    </div>
                </div>

                <div class="glass-panel p-3 rounded-xl flex gap-2">
                    <select id="archiveSalaryMonth" onchange="updateArchiveSalaryUI()" class="input-field py-2 text-xs flex-1">
                        <option value="all">📅 كل السجلات التراكمية</option>
                    </select>
                    <button onclick="exportSalaryCSV()" class="bg-indigo-600 text-white px-4 rounded-lg text-xs font-bold whitespace-nowrap">تصدير CSV 📥</button>
                </div>

                <div class="glass-panel p-4 rounded-xl">
                    <div class="flex justify-between items-center mb-3 border-b border-slate-700 pb-2">
                        <h3 class="text-sm font-bold text-slate-200">📜 كل سجلات الدوام</h3>
                        <div class="flex gap-2">
                            <button onclick="backupSalaryData()" class="text-[10px] text-blue-400 hover:underline">💾 نسخة</button>
                            <button onclick="document.getElementById('restoreFile').click()" class="text-[10px] text-emerald-400 hover:underline">📥 استعادة</button>
                        </div>
                    </div>
                    <div id="archiveSalaryLog" class="flex flex-col gap-2 max-h-96 overflow-y-auto pr-1"></div>
                </div>
            </div>
        </main>
    </div>

</div>

<input type="file" id="restoreFile" style="display:none;" accept=".json" onchange="restoreSalaryData(this)">

<!-- ======================= البرمجة (JavaScript) ======================= -->
<script>
    const STORAGE_PREFIX = 'shamelApp_';

    // ======================= دوال التنبيهات المخصصة =======================
    function customAlert(msg, title = "تنبيه") {
        return new Promise(resolve => {
            const modal = document.getElementById('customDialog');
            document.getElementById('dialogTitle').innerText = title;
            document.getElementById('dialogMessage').innerText = msg;
            document.getElementById('dialogCancel').classList.add('hidden');

            const confirmBtn = document.getElementById('dialogConfirm');
            confirmBtn.className = "flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-bold hover:bg-blue-500 transition";
            confirmBtn.innerText = "موافق";

            modal.classList.remove('hidden');

            confirmBtn.onclick = () => {
                modal.classList.add('hidden');
                resolve(true);
            };
        });
    }

    function customConfirm(msg, title = "تأكيد") {
        return new Promise(resolve => {
            const modal = document.getElementById('customDialog');
            document.getElementById('dialogTitle').innerText = title;
            document.getElementById('dialogMessage').innerText = msg;
            document.getElementById('dialogCancel').classList.remove('hidden');

            const confirmBtn = document.getElementById('dialogConfirm');
            confirmBtn.className = "flex-1 bg-rose-600 text-white py-2.5 rounded-lg font-bold hover:bg-rose-500 transition";
            confirmBtn.innerText = "نعم، متأكد";

            modal.classList.remove('hidden');

            confirmBtn.onclick = () => {
                modal.classList.add('hidden');
                resolve(true);
            };
            document.getElementById('dialogCancel').onclick = () => {
                modal.classList.add('hidden');
                resolve(false);
            };
        });
    }

    function escapeHtml(text) {
        if (text === null || text === undefined) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    function getToday() {
        const n = new Date();
        n.setMinutes(n.getMinutes() - n.getTimezoneOffset());
        return n.toISOString().split('T')[0];
    }

    function isFutureDate(d) {
        return new Date(d) > new Date(getToday());
    }

    // ======================= PIN تغيير وإدارة =======================
    const pinInput = document.getElementById('pinInput');
    const pinDots = document.querySelectorAll('.pin-dot');

    pinInput.addEventListener('input', (e) => {
        const val = e.target.value.replace(/\D/g, '').slice(0,4);
        e.target.value = val;
        pinDots.forEach((dot, i) => dot.classList.toggle('filled', i < val.length));
    });

    async function handlePinSubmit(e) {
        e.preventDefault();
        const val = pinInput.value.replace(/\D/g, '');
        if (val.length !== 4) { await customAlert('الرجاء إدخال 4 أرقام'); return; }

        const savedPin = localStorage.getItem(STORAGE_PREFIX + 'pin');
        if (!savedPin) {
            if (await customConfirm('هل تريد إنشاء رمز PIN جديد؟')) {
                localStorage.setItem(STORAGE_PREFIX + 'pin', val);
                enterApp();
            }
        } else if (savedPin === val) {
            enterApp();
        } else {
            await customAlert('❌ رمز غير صحيح');
            pinInput.value = '';
            pinDots.forEach(d => d.classList.remove('filled'));
        }
    }

    function enterApp() {
        document.getElementById('authScreen').classList.add('hidden');
        document.getElementById('mainScreen').classList.remove('hidden');
        document.getElementById('mainScreen').classList.add('flex');
    }

    function logout() {
        pinInput.value = '';
        pinDots.forEach(d => d.classList.remove('filled'));
        ['mainScreen','tripsScreen','salaryScreen','tasksScreen','archiveScreen'].forEach(id => {
            document.getElementById(id).classList.add('hidden');
            document.getElementById(id).classList.remove('flex');
        });
        document.getElementById('authScreen').classList.remove('hidden');
    }

    function openChangePinModal() { document.getElementById('changePinModal').classList.remove('hidden'); }
    function closeChangePinModal() {
        document.getElementById('changePinModal').classList.add('hidden');
        document.getElementById('oldPinInput').value = '';
        document.getElementById('newPinInput').value = '';
    }

    async function confirmChangePin() {
        const oldPin = document.getElementById('oldPinInput').value;
        const newPin = document.getElementById('newPinInput').value;
        const savedPin = localStorage.getItem(STORAGE_PREFIX + 'pin');

        if (oldPin !== savedPin) { await customAlert('❌ الرمز القديم الحالي غير صحيح!'); return; }
        if (!/^\d{4}$/.test(newPin)) { await customAlert('❌ الرمز الجديد يجب أن يتكون من 4 أرقام فقط!'); return; }

        localStorage.setItem(STORAGE_PREFIX + 'pin', newPin);
        await customAlert('✅ تم تغيير الرمز بنجاح!');
        closeChangePinModal();
    }

    // ======================= التنقل =======================
    function openScreen(id) {
        document.getElementById('mainScreen').classList.add('hidden');
        document.getElementById('mainScreen').classList.remove('flex');
        document.getElementById(id).classList.remove('hidden');
        document.getElementById(id).classList.add('flex');

        if (id === 'tripsScreen') {
            document.getElementById('tripDate').value = getToday();
            loadTripSettings(); updateFare(); updateTripsUI();
        } else if (id === 'salaryScreen') {
            setSalaryToday(); loadSalarySettings(); updateSalaryUI();
        } else if (id === 'tasksScreen') {
            document.getElementById('taskDate').value = getToday(); updateTasksUI();
        } else if (id === 'archiveScreen') {
            updateArchiveTripsUI(); updateArchiveSalaryUI();
        }
    }

    function backToMain() {
        ['tripsScreen','salaryScreen','tasksScreen','archiveScreen'].forEach(id => {
            document.getElementById(id).classList.add('hidden');
            document.getElementById(id).classList.remove('flex');
        });
        const main = document.getElementById('mainScreen');
        main.classList.remove('hidden');
        main.classList.add('flex');
    }

    // ======================= تطبيق الخطوط =======================
    let trips = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'trips')) || [];
    let uniqueDrivers = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'drivers')) || [];
    let tripSettings = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'tripSettings')) || { go: 3000, ret: 3000, full: 6000 };

    function loadTripSettings() {
        document.getElementById('defGo').value = tripSettings.go;
        document.getElementById('defRet').value = tripSettings.ret;
        document.getElementById('defFull').value = tripSettings.full;
    }

    function saveTripSettings() {
        tripSettings = {
            go: parseFloat(document.getElementById('defGo').value) || 0,
            ret: parseFloat(document.getElementById('defRet').value) || 0,
            full: parseFloat(document.getElementById('defFull').value) || 0
        };
        localStorage.setItem(STORAGE_PREFIX + 'tripSettings', JSON.stringify(tripSettings));
        updateFare();
    }

    function getTripLabel(type) {
        const map = { go: 'ذهاب ☀️', return: 'عودة 🌙', full: 'يوم كامل 🔄', pay: 'تسديد 💸' };
        return map[type] || type;
    }

    function updateFare() {
        const type = document.querySelector('input[name="tripType"]:checked').value;
        const fareInput = document.getElementById('tripFare');
        const label = document.getElementById('fareLabel');
        const btn = document.getElementById('saveTripBtn');

        fareInput.classList.remove('text-amber-500', 'text-emerald-400', 'text-rose-500');
        btn.classList.remove('bg-blue-600', 'bg-emerald-600', 'bg-rose-600');

        if (type === 'pay') {
            label.innerText = "المبلغ المسدد:"; fareInput.value = ""; fareInput.placeholder = "شكد انطيت السايق؟";
            fareInput.classList.add('text-rose-500'); btn.innerText = "تسديد وتنزيل الديون 💸"; btn.classList.add('bg-rose-600');
        } else if (type === 'full') {
            label.innerText = "الكروة:"; fareInput.value = tripSettings.full;
            fareInput.classList.add('text-emerald-400'); btn.innerText = "حفظ كدين ✅"; btn.classList.add('bg-emerald-600');
        } else {
            label.innerText = "الكروة:"; fareInput.value = type === 'go' ? tripSettings.go : tripSettings.ret;
            fareInput.classList.add('text-amber-500'); btn.innerText = "حفظ كدين ✅"; btn.classList.add('bg-blue-600');
        }
    }

    async function saveTrip(e) {
        e.preventDefault();
        const driver = document.getElementById('driverName').value.trim();
        const fare = parseInt(document.getElementById('tripFare').value);
        const dateStr = document.getElementById('tripDate').value;
        const type = document.querySelector('input[name="tripType"]:checked').value;

        if (!driver || !fare || !dateStr) return;
        if (isFutureDate(dateStr)) { await customAlert('❌ لا يمكن إدخال تاريخ مستقبلي'); return; }

        trips.unshift({ id: Date.now(), driver, fare, date: dateStr, type });
        localStorage.setItem(STORAGE_PREFIX + 'trips', JSON.stringify(trips));
        if (!uniqueDrivers.includes(driver)) { uniqueDrivers.push(driver); localStorage.setItem(STORAGE_PREFIX + 'drivers', JSON.stringify(uniqueDrivers)); }

        document.getElementById('driverName').value = ''; document.getElementById('typeGo').checked = true;
        updateFare(); document.getElementById('tripDate').value = getToday();
        updateTripsUI(); updateArchiveTripsUI();
    }

    async function delTrip(id) {
        if (!(await customConfirm('هل أنت متأكد من حذف السجل؟'))) return;
        trips = trips.filter(t => t.id !== id);
        localStorage.setItem(STORAGE_PREFIX + 'trips', JSON.stringify(trips));
        updateTripsUI(); updateArchiveTripsUI();
    }

    async function clearTripsData() {
        if (!(await customConfirm('هل أنت متأكد من مسح جميع الديون والخطوط وتصفيرها بالكامل؟'))) return;
        trips = []; localStorage.setItem(STORAGE_PREFIX + 'trips', JSON.stringify(trips));
        updateTripsUI(); updateArchiveTripsUI();
    }

    function generateTripsHtml(recordsList) {
        let html = '';
        recordsList.forEach(t => {
            const isPay = t.type === 'pay';
            const typeColor = isPay ? 'text-rose-500' : (t.type === 'full' ? 'text-emerald-400' : 'text-amber-500');
            const label = getTripLabel(t.type);
            html += `<div class="bg-[#111827] p-3 rounded-lg border border-slate-700 relative ${isPay ? 'border-r-4 border-r-rose-500' : ''} fade-in">
                <button onclick="delTrip(${t.id})" class="absolute top-2 left-2 text-rose-500 text-xs w-6 h-6 bg-rose-500/10 rounded-full hover:bg-rose-500/30 transition">✕</button>
                <div class="flex justify-between text-xs mb-1 pr-8"><span class="${typeColor} font-bold">${escapeHtml(label)}</span><span class="text-slate-400">${escapeHtml(t.date)}</span></div>
                <div class="flex justify-between text-sm font-bold text-white"><span class="pr-8">${escapeHtml(t.driver)}</span><span class="${isPay ? 'text-rose-500' : 'text-emerald-400'}">${isPay ? '-' : '+'} ${t.fare.toLocaleString('ar-IQ')}</span></div>
            </div>`;
        });
        return html || '<p class="text-xs text-slate-500 text-center">لا توجد حركات</p>';
    }

    function updateTripsUI() {
        let debt = 0; let dDebts = {};
        // الحساب للديون الإجمالية (لأنها تراكمية)
        trips.forEach(t => {
            if (!dDebts[t.driver]) dDebts[t.driver] = 0;
            if (t.type === 'pay') { dDebts[t.driver] -= t.fare; debt -= t.fare; }
            else { dDebts[t.driver] += t.fare; debt += t.fare; }
        });

        document.getElementById('trips_totalAmount').innerText = Math.max(0, debt).toLocaleString('ar-IQ');
        
        let htmlD = '';
        Object.keys(dDebts).sort((a, b) => dDebts[b] - dDebts[a]).forEach(d => {
            const v = dDebts[d];
            if (v === 0) return;
            const status = v > 0 ? `<span class="text-amber-500 font-bold">${v.toLocaleString('ar-IQ')}</span>` : `<span class="text-emerald-400 font-bold">${Math.abs(v).toLocaleString('ar-IQ')} تسديد زائد</span>`;
            htmlD += `<div class="flex justify-between items-center bg-[#111827] p-2 rounded-lg border border-slate-700"><div><h4 class="text-sm text-white">${escapeHtml(d)}</h4></div><div>${status}</div></div>`;
        });
        document.getElementById('trips_driversSummary').innerHTML = htmlD || '<p class="text-xs text-slate-500 text-center">تم تصفية جميع الديون</p>';

        // عرض أحدث 15 حركة بالشاشة الرئيسية
        const recentTrips = [...trips].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 15);
        document.getElementById('tripsLog').innerHTML = generateTripsHtml(recentTrips);
        document.getElementById('savedDrivers').innerHTML = uniqueDrivers.map(d => `<option value="${escapeHtml(d)}">`).join('');
    }

    // ======================= تطبيق الراتب =======================
    let salaryRecords = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'salaryRecords')) || [];
    let salarySettings = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'salarySettings')) || { rate: '', prev: 0, deduct: 0 };
    let editingWorkId = null;

    function setSalaryToday() { document.getElementById('workDate').value = getToday(); }
    function loadSalarySettings() {
        document.getElementById('hourlyRate').value = salarySettings.rate || '';
        document.getElementById('prevBalance').value = salarySettings.prev || 0;
        document.getElementById('deductions').value = salarySettings.deduct || 0;
    }

    function saveSalarySettings() {
        salarySettings = { 
            rate: parseFloat(document.getElementById('hourlyRate').value) || 0, 
            prev: parseFloat(document.getElementById('prevBalance').value) || 0, 
            deduct: parseFloat(document.getElementById('deductions').value) || 0 
        };
        localStorage.setItem(STORAGE_PREFIX + 'salarySettings', JSON.stringify(salarySettings));
        updateSalaryUI(); updateArchiveSalaryUI();
    }

    function formatTime(mins) { const h = Math.floor(mins / 60); const m = mins % 60; return `${h} س و ${m} د`; }

    async function saveWork(e) {
        e.preventDefault();
        const date = document.getElementById('workDate').value;
        const mins = parseInt(document.getElementById('workMinutes').value);
        const rate = parseFloat(document.getElementById('hourlyRate').value) || 0;

        if (!date) return;
        if (!mins || mins < 1 || mins > 1440) { await customAlert('الدقائق يجب أن تكون بين 1 و 1440'); return; }
        if (isFutureDate(date)) { await customAlert('❌ لا يمكن إدخال تاريخ مستقبلي'); return; }
        if (rate <= 0) { await customAlert('يرجى إدخال أجرة الساعة في الإعدادات أولاً'); return; }

        const amount = (mins / 60) * rate;
        const timeStr = formatTime(mins);

        if (editingWorkId) {
            const idx = salaryRecords.findIndex(r => r.id === editingWorkId);
            if (idx !== -1) salaryRecords[idx] = { id: editingWorkId, date, minutes: mins, amount, timeStr, rateAtTime: rate };
            cancelEditWork();
        } else {
            if (salaryRecords.find(r => r.date === date) && !(await customConfirm(`التاريخ مسجل. إضافة دوام آخر لنفس اليوم؟`))) return;
            salaryRecords.unshift({ id: Date.now(), date, minutes: mins, amount, timeStr, rateAtTime: rate });
        }

        localStorage.setItem(STORAGE_PREFIX + 'salaryRecords', JSON.stringify(salaryRecords));
        document.getElementById('workMinutes').value = ''; setSalaryToday();
        updateSalaryUI(); updateArchiveSalaryUI();
    }

    function editWork(id) {
        const r = salaryRecords.find(x => x.id === id);
        if (!r) return;
        document.getElementById('workDate').value = r.date; document.getElementById('workMinutes').value = r.minutes;
        document.getElementById('saveWorkBtn').textContent = '💾 حفظ التعديل'; document.getElementById('cancelWorkBtn').classList.remove('hidden');
        editingWorkId = id; window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function cancelEditWork() {
        editingWorkId = null; document.getElementById('saveWorkBtn').textContent = 'حفظ الدوام ✅'; document.getElementById('cancelWorkBtn').classList.add('hidden');
        document.getElementById('workMinutes').value = ''; setSalaryToday();
    }

    async function deleteWork(id) {
        if (!(await customConfirm('متأكد من حذف هذا الدوام؟'))) return;
        salaryRecords = salaryRecords.filter(r => r.id !== id);
        if (editingWorkId === id) cancelEditWork();
        localStorage.setItem(STORAGE_PREFIX + 'salaryRecords', JSON.stringify(salaryRecords));
        updateSalaryUI(); updateArchiveSalaryUI();
    }

    function generateSalaryHtml(recordsList) {
        let html = '';
        recordsList.forEach(r => {
            const formatted = new Date(r.date).toLocaleDateString('ar-IQ', { month: 'short', day: 'numeric', year: 'numeric' });
            html += `<div class="bg-[#111827] p-3 rounded-lg border border-slate-700 relative fade-in">
                <button onclick="deleteWork(${r.id})" class="absolute top-2 left-2 text-rose-500 bg-rose-500/10 rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-rose-500/30 transition">✕</button>
                <button onclick="editWork(${r.id})" class="absolute top-2 left-9 text-blue-400 bg-blue-500/10 rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-blue-500/30 transition">✎</button>
                <div class="flex justify-between items-start mb-1 pr-14"><span class="text-xs font-bold text-[#cca344]">${escapeHtml(formatted)}</span><span class="text-[10px] text-slate-400">${escapeHtml(r.timeStr)}</span></div>
                <div class="flex justify-between items-end mt-1"><span class="text-[10px] text-slate-400">سعر الساعة: ${(r.rateAtTime || 0).toLocaleString('ar-IQ')}</span><span class="text-sm font-bold text-emerald-400" dir="ltr">+ ${Math.round(r.amount).toLocaleString('ar-IQ')} د.ع</span></div>
            </div>`;
        });
        return html || '<p class="text-xs text-slate-500 text-center py-2">لا توجد سجلات</p>';
    }

    function updateSalaryUI() {
        const rate = parseFloat(document.getElementById('hourlyRate').value) || 0;
        const plusBonus = parseFloat(document.getElementById('prevBalance').value) || 0;
        const minusDeduct = parseFloat(document.getElementById('deductions').value) || 0;

        let totalAmount = 0; let totalMins = 0;
        // الحساب الكلي التراكمي
        salaryRecords.forEach(r => { totalAmount += r.amount; totalMins += r.minutes; });
        const final = totalAmount + plusBonus - minusDeduct;

        document.getElementById('finalTotal').textContent = Math.round(final).toLocaleString('ar-IQ');
        document.getElementById('totalMinutes').textContent = totalMins.toLocaleString('ar-IQ');
        
        // عرض أحدث 15 سجل بالشاشة الرئيسية
        const recentSalary = [...salaryRecords].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 15);
        document.getElementById('workLog').innerHTML = generateSalaryHtml(recentSalary);
    }

    // ======================= إدارة المهام الذكية =======================
    let tasks = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'tasks')) || [];

    function onTaskTypeChange() {
        const type = document.getElementById('taskType').value;
        const titleInput = document.getElementById('taskTitle');
        if (type === 'driver') titleInput.placeholder = "مثال: استلام دفعة من السائق";
        else if (type === 'work') titleInput.placeholder = "مثال: مراجعة دوام يوم الخميس";
        else if (type === 'financial') titleInput.placeholder = "مثال: دفع قسط شهري";
        else titleInput.placeholder = "مثال: مهمة شخصية";
    }

    function saveTask(e) {
        e.preventDefault();
        const type = document.getElementById('taskType').value;
        const title = document.getElementById('taskTitle').value.trim();
        const amount = parseFloat(document.getElementById('taskAmount').value) || 0;
        const date = document.getElementById('taskDate').value;
        if (!title || !date) return;

        tasks.unshift({ id: Date.now(), type, title, amount, date, completed: false });
        localStorage.setItem(STORAGE_PREFIX + 'tasks', JSON.stringify(tasks));
        document.getElementById('taskTitle').value = ''; document.getElementById('taskAmount').value = ''; document.getElementById('taskDate').value = getToday();
        updateTasksUI();
    }

    function toggleTaskComplete(id) {
        const t = tasks.find(x => x.id === id);
        if (t) { t.completed = !t.completed; localStorage.setItem(STORAGE_PREFIX + 'tasks', JSON.stringify(tasks)); updateTasksUI(); }
    }

    async function deleteTask(id) {
        if (!(await customConfirm('هل أنت متأكد من حذف هذه المهمة؟'))) return;
        tasks = tasks.filter(x => x.id !== id); localStorage.setItem(STORAGE_PREFIX + 'tasks', JSON.stringify(tasks)); updateTasksUI();
    }

    function updateTasksUI() {
        document.getElementById('tasksCount').innerText = `${tasks.length}`;
        const container = document.getElementById('tasksLog');
        if (tasks.length === 0) { container.innerHTML = '<p class="text-xs text-slate-500 text-center py-4">لا توجد مهام مسجلة حالياً</p>'; return; }

        let html = '';
        tasks.forEach(t => {
            let badgeColor = 'bg-blue-500/20 text-blue-400'; let typeName = 'عامة';
            if (t.type === 'driver') { typeName = 'تذكير دفعة'; badgeColor = 'bg-amber-500/20 text-amber-400'; }
            else if (t.type === 'work') { typeName = 'تذكير دوام'; badgeColor = 'bg-emerald-500/20 text-emerald-400'; }
            else if (t.type === 'financial') { typeName = 'هدف مالي'; badgeColor = 'bg-purple-500/20 text-purple-400'; }

            html += `<div class="bg-[#111827] p-3 rounded-lg border border-slate-700 relative fade-in flex items-center justify-between ${t.completed ? 'opacity-50' : ''}">
                <div class="flex items-start gap-3 flex-1">
                    <input type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleTaskComplete(${t.id})" class="mt-1 w-4 h-4 accent-amber-500 cursor-pointer">
                    <div class="flex flex-col">
                        <div class="flex items-center gap-2 mb-1"><span class="text-[10px] px-2 py-0.5 rounded font-bold ${badgeColor}">${typeName}</span><span class="text-[10px] text-slate-400">📅 ${escapeHtml(t.date)}</span></div>
                        <h4 class="text-sm font-bold text-white ${t.completed ? 'line-through text-slate-500' : ''}">${escapeHtml(t.title)}</h4>
                        ${t.amount > 0 ? `<p class="text-xs font-bold text-emerald-400 mt-1">المبلغ: ${t.amount.toLocaleString('ar-IQ')} د.ع</p>` : ''}
                    </div>
                </div>
                <button onclick="deleteTask(${t.id})" class="text-rose-500 bg-rose-500/10 rounded-full w-7 h-7 flex items-center justify-center text-xs hover:bg-rose-500/30 transition">✕</button>
            </div>`;
        });
        container.innerHTML = html;
    }

    // ======================= قسم الأرشيف (التراكمي) =======================
    function switchArchiveTab(tab) {
        document.getElementById('tabArchiveTrips').classList.toggle('active', tab === 'trips');
        document.getElementById('tabArchiveSalary').classList.toggle('active', tab === 'salary');
        document.getElementById('archiveTripsContent').classList.toggle('hidden', tab !== 'trips');
        document.getElementById('archiveTripsContent').classList.toggle('flex', tab === 'trips');
        document.getElementById('archiveSalaryContent').classList.toggle('hidden', tab !== 'salary');
        document.getElementById('archiveSalaryContent').classList.toggle('flex', tab === 'salary');
    }

    function populateMonths(selectId, records) {
        const sel = document.getElementById(selectId);
        const currentVal = sel.value;
        const months = new Set();
        records.forEach(r => { if (r.date) months.add(r.date.slice(0, 7)); });
        const arr = Array.from(months).sort().reverse();
        
        let html = '<option value="all">📅 كل السجلات (من البداية)</option>';
        arr.forEach(m => { const [y, mo] = m.split('-'); html += `<option value="${m}">📅 شهر ${mo} سنة ${y}</option>`; });
        sel.innerHTML = html;
        if (currentVal && Array.from(sel.options).some(o => o.value === currentVal)) { sel.value = currentVal; }
    }

    function updateArchiveTripsUI() {
        const searchTerm = document.getElementById('archiveTripsSearch').value.toLowerCase();
        const monthFilter = document.getElementById('archiveTripsMonth').value;
        populateMonths('archiveTripsMonth', trips);
        
        let filtered = trips.filter(t => t.driver.toLowerCase().includes(searchTerm));
        if (monthFilter !== 'all') filtered = filtered.filter(t => t.date && t.date.startsWith(monthFilter));
        
        // حساب إجمالي الديون المعروضة بالفلتر
        let debt = 0;
        filtered.forEach(t => { if(t.type === 'pay') debt -= t.fare; else debt += t.fare; });
        document.getElementById('archiveTripsTotal').innerText = Math.max(0, debt).toLocaleString('ar-IQ') + ' د.ع';

        filtered.sort((a, b) => { const da = new Date(a.date), db = new Date(b.date); return db - da; });
        document.getElementById('archiveTripsLog').innerHTML = generateTripsHtml(filtered);
    }

    function updateArchiveSalaryUI() {
        const monthFilter = document.getElementById('archiveSalaryMonth').value;
        populateMonths('archiveSalaryMonth', salaryRecords);
        
        let filtered = salaryRecords;
        if (monthFilter !== 'all') filtered = salaryRecords.filter(r => r.date && r.date.startsWith(monthFilter));
        
        // حساب الإجمالي المعروض
        let totalMoney = 0; let totalMins = 0;
        filtered.forEach(r => { totalMoney += r.amount; totalMins += r.minutes; });
        document.getElementById('archiveSalaryTotalMoney').innerText = Math.round(totalMoney).toLocaleString('ar-IQ') + ' د.ع';
        document.getElementById('archiveSalaryTotalMins').innerText = totalMins.toLocaleString('ar-IQ') + ' دقيقة';

        filtered.sort((a, b) => { const da = new Date(a.date), db = new Date(b.date); return db - da; });
        document.getElementById('archiveSalaryLog').innerHTML = generateSalaryHtml(filtered);
    }

    // ======================= التصدير والاستعادة =======================
    function downloadBlob(data, filename, type) {
        const blob = (data instanceof Blob) ? data : new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = filename;
        document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
    }

    async function exportTripsCSV() {
        const monthFilter = document.getElementById('archiveTripsMonth').value;
        let filteredToExport = trips;
        if (monthFilter !== 'all') filteredToExport = trips.filter(t => t.date && t.date.startsWith(monthFilter));

        if (!filteredToExport.length) return await customAlert("لا توجد بيانات لتصديرها!");
        
        let csv = "\uFEFFالرقم,التاريخ,الحركة,السائق,الكروة (دين),تسديد\n";
        filteredToExport.forEach((t, i) => { 
            const isPay = t.type === 'pay'; 
            csv += `${filteredToExport.length - i},${t.date},${getTripLabel(t.type).replace(/[^\u0600-\u06FF\s]/g,'').trim()},${t.driver},${isPay ? 0 : t.fare},${isPay ? t.fare : 0}\n`; 
        });
        downloadBlob(csv, `ارشيف_الخطوط_${monthFilter === 'all' ? 'شامل' : monthFilter}.csv`, 'text/csv;charset=utf-8;');
    }

    async function exportSalaryCSV() {
        const monthFilter = document.getElementById('archiveSalaryMonth').value;
        let filteredToExport = salaryRecords;
        if (monthFilter !== 'all') filteredToExport = salaryRecords.filter(r => r.date && r.date.startsWith(monthFilter));

        if (filteredToExport.length === 0) { await customAlert('لا توجد بيانات للراتب لتصديرها!'); return; }
        
        let total = 0; let csv = "\uFEFFالرقم,التاريخ,الوقت,الدقائق,سعر الساعة,المبلغ\n";
        filteredToExport.forEach((r, i) => { total += r.amount; csv += `${filteredToExport.length - i},${r.date},${r.timeStr},${r.minutes},${r.rateAtTime},${Math.round(r.amount)}\n`; });
        csv += `\n,,,,المجموع,${Math.round(total)}\n`;
        
        downloadBlob(csv, `ارشيف_الراتب_${monthFilter === 'all' ? 'شامل' : monthFilter}.csv`, 'text/csv;charset=utf-8;');
    }

    function backupSalaryData() {
        const payload = { records: salaryRecords, settings: salarySettings, exportedAt: new Date().toISOString() };
        downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }), `نسخة_دوام_احتياطية_${getToday()}.json`, 'application/json');
    }

    function restoreSalaryData(input) {
        const file = input.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = async function(e) {
            try {
                const data = JSON.parse(e.target.result);
                if (!data.records || !(await customConfirm('هل أنت متأكد من استبدال بيانات الدوام الحالية بالنسخة الاحتياطية؟'))) return;
                salaryRecords = data.records || [];
                if (data.settings) { salarySettings = data.settings; localStorage.setItem(STORAGE_PREFIX + 'salarySettings', JSON.stringify(salarySettings)); loadSalarySettings(); }
                localStorage.setItem(STORAGE_PREFIX + 'salaryRecords', JSON.stringify(salaryRecords));
                updateSalaryUI(); updateArchiveSalaryUI(); await customAlert('✅ تمت الاستعادة بنجاح');
            } catch (err) { await customAlert('❌ ملف النسخة الاحتياطية غير صالح'); }
        };
        reader.readAsText(file); input.value = '';
    }

    // ======================= التشغيل الأولي =======================
    window.onload = () => {
        const savedPin = localStorage.getItem(STORAGE_PREFIX + 'pin');
        if (savedPin) {
            document.getElementById('authTitle').innerText = '🔐 أدخل رمز PIN';
            document.getElementById('authSubtitle').innerText = 'رمز الحماية الخاص بك';
        } else {
            document.getElementById('authTitle').innerText = '🔐 إنشاء رمز PIN';
            document.getElementById('authSubtitle').innerText = 'أدخل 4 أرقام لحماية بياناتك';
        }
        switchArchiveTab('trips');
    };
</script>
</body>
</html>
