# سنجش پوشش OGIMET (خلاصهٔ روزانهٔ SYNOP) برای چند ایستگاه ایران در چند ماهِ نمونه. فقط می‌خواند.
# نسخهٔ ۳: نتیجه بعد از هر درخواست ذخیره می‌شود (با لغو/تایم‌اوت چیزی از دست نمی‌رود)، سقف زمان ۳۵ دقیقه، و برای هر تلاش
# کد وضعیت/طول/تعداد ردیف/ابتدای متن ثبت می‌شود تا معلوم شود محدودیت نرخ است یا ساختار صفحه یا مسدودشدن IP.
import urllib.request, urllib.error, re, time, calendar, io, sys
import pandas as pd
T0 = time.time(); BUDGET = 35 * 60
STN = {"40754": "مشهد", "40706": "تبریز", "40766": "کرمان", "40848": "شیراز", "40800": "اصفهان", "40736": "تهران", "40745": "بیرجند", "40829": "بندرعباس"}
MONTHS = [(2018, 4), (2003, 1), (2010, 7), (2024, 5)]
URL = "https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={ind}&ndays={nd}&ano={y}&mes={m:02d}&day={nd:02d}&hora=00&ord=REV&Send=Send"
LOG = open("ogimet_probe.txt", "a", encoding="utf-8")
def log(s): print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
def get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) metstat-probe"}), timeout=60)
        return r.status, r.read().decode("latin1")
    except urllib.error.HTTPError as e: return e.code, ""
    except Exception as e: return 0, "ERR " + repr(e)[:150]
def rows(t): return t.count("<tr")
log(f"شروع {time.strftime('%H:%M:%S')} · سقف زمان {BUDGET//60} دقیقه")
saved = False
for y, m in MONTHS:                     # ماه‌به‌ماه تا همهٔ ایستگاه‌ها زودتر یک نمونه داشته باشند
    for ind, nm in STN.items():
        if time.time() - T0 > BUDGET: log("⏹ سقف زمان؛ توقف"); sys.exit(0)
        nd = calendar.monthrange(y, m)[1]; u = URL.format(ind=ind, nd=nd, y=y, m=m); t = ""; ok = False
        for a in range(2):
            st, t = get(u); n = rows(t)
            log(f"  {ind} {nm} {y}-{m:02d} تلاش{a+1}: HTTP={st} طول={len(t)} tr={n} | {re.sub(chr(10), ' ', re.sub('<[^>]+>', ' ', t))[:110].strip()!r}")
            if st == 200 and "Date" in t and n > 10: ok = True; break
            time.sleep(60)               # محدودیت نرخ یا صفحهٔ کوتاه؛ یک بار با تأخیر
        if not ok: log(f"{ind} {nm} {y}-{m:02d}: ✗ ناموفق"); time.sleep(20); continue
        if not saved: open("ogimet_sample.html", "w", encoding="utf-8").write(t); saved = True
        try:
            tb = max(pd.read_html(io.StringIO(t)), key=lambda d: d.shape[0] * d.shape[1]); cols = [" ".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in tb.columns]; N = len(tb)
            def cnt(pat):
                ci = [i for i, c in enumerate(cols) if re.search(pat, c, re.I)]
                if not ci: return "ستون نیست"
                s = tb.iloc[:, ci[0]].astype(str); return f"{int((~s.str.contains('---|nan|No data', case=False)).sum())}/{N}"
            log(f"{ind} {nm} {y}-{m:02d}: ✓ ردیف={N} Tmax={cnt('Max')} Tmin={cnt('Min')} Prec={cnt('Prec')} | ستون‌ها={cols[:12]}")
        except Exception as e: log(f"{ind} {nm} {y}-{m:02d}: parse خطا {str(e)[:100]} | طول={len(t)}")
        time.sleep(15)
log(f"پایان {time.strftime('%H:%M:%S')}")
