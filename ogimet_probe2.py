# سنجش ظرفیت یک درخواست OGIMET: ndays=۶۲/۹۳/۱۸۶/۳۶۶ چند ردیف روزانه برمی‌گرداند؟ (برای کم‌کردن شمار درخواست‌ها در دانلودر کامل)
# هم‌چنین: مقدار «Prec.» برای روز بی‌باران چه شکلی است (۰٫۰ / Tr / خالی)، و زمان پاسخ. فقط می‌خواند. خروجی: ogimet_probe2.txt
import urllib.request, urllib.error, re, time, io, sys
import pandas as pd
T0 = time.time(); BUDGET = 30 * 60
URL = "https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={ind}&ndays={nd}&ano={y}&mes={m:02d}&day={d:02d}&hora=00&ord=REV&Send=Send"
CASES = [("40754", 2024, 12, 31, 62), ("40754", 2024, 12, 31, 93), ("40754", 2024, 12, 31, 186), ("40754", 2024, 12, 31, 366), ("40736", 2018, 12, 31, 366), ("40736", 2018, 12, 31, 731), ("40848", 2021, 6, 30, 366)]
LOG = open("ogimet_probe2.txt", "a", encoding="utf-8")
def log(s): print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
def get(u):
    t1 = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) metstat-probe"}), timeout=120); return r.status, r.read().decode("latin1"), time.time() - t1
    except urllib.error.HTTPError as e: return e.code, "", time.time() - t1
    except Exception as e: return 0, "ERR " + repr(e)[:150], time.time() - t1
log(f"شروع {time.strftime('%H:%M:%S')}")
for ind, y, m, d, nd in CASES:
    if time.time() - T0 > BUDGET: log("⏹ سقف زمان"); break
    u = URL.format(ind=ind, nd=nd, y=y, m=m, d=d); ok = False
    for a in range(3):
        st, t, dt = get(u); n = len(re.findall(r"<tr", t, re.I)); log(f"  {ind} {y}-{m:02d}-{d:02d} nd={nd} تلاش{a+1}: HTTP={st} طول={len(t)} tr={n} زمان={dt:.0f}s")
        if st == 200 and "date" in t.lower() and n > 10: ok = True; break
        time.sleep(60)
    if not ok: log(f"{ind} nd={nd}: ✗"); continue
    try:
        tb = max(pd.read_html(io.StringIO(t)), key=lambda x: x.shape[0] * x.shape[1]); cols = [" ".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in tb.columns]
        dates = tb.iloc[:, 0].astype(str).tolist(); pc = [i for i, c in enumerate(cols) if "Prec" in c][0]; pv = tb.iloc[:, pc].astype(str)
        vals = pv.value_counts().head(6).to_dict()
        log(f"{ind} nd={nd} ✓ ردیف={len(tb)} (انتظار {nd}) اولین={dates[0]} آخرین={dates[-1]} | شکل مقدار بارش: {vals}")
    except Exception as e: log(f"{ind} nd={nd}: parse خطا {str(e)[:120]}")
    if nd >= 366 and not open("ogimet_sample2.html", "a").tell(): open("ogimet_sample2.html", "w", encoding="utf-8").write(t)
    time.sleep(25)
log(f"پایان {time.strftime('%H:%M:%S')}")
