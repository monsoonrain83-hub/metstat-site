# سنجش پوشش OGIMET (خلاصهٔ روزانهٔ SYNOP) برای چند ایستگاه ایران در چند ماهِ نمونه.
# فقط می‌خواند؛ به دیتابیس سایت دست نمی‌زند. خروجی: ogimet_probe.txt + ogimet_sample.html (برای دیدن ساختار صفحه)
import urllib.request, re, time, calendar, io, sys
import pandas as pd
STN = {"40754": "مشهد", "40706": "تبریز", "40766": "کرمان", "40848": "شیراز", "40800": "اصفهان", "40736": "تهران", "40745": "بیرجند", "40829": "بندرعباس"}
MONTHS = [(2003, 1), (2010, 7), (2018, 4), (2024, 5)]
URL = "https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind={ind}&ndays={nd}&ano={y}&mes={m:02d}&day={nd:02d}&hora=00&ord=REV&Send=Send"
def get(u):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 metstat-probe"}), timeout=90).read().decode("latin1")
        except Exception as e: err = e; time.sleep(5 * (a + 1))
    return "ERR " + str(err)
out = []; saved = False
for ind, nm in STN.items():
    for y, m in MONTHS:
        nd = calendar.monthrange(y, m)[1]; t = get(URL.format(ind=ind, nd=nd, y=y, m=m))
        if not saved and not t.startswith("ERR"): open("ogimet_sample.html", "w", encoding="utf-8").write(t); saved = True
        if t.startswith("ERR"): out.append(f"{ind} {nm} {y}-{m:02d}: {t[:120]}"); continue
        try:
            tabs = pd.read_html(io.StringIO(t)); tb = max(tabs, key=lambda d: d.shape[0] * d.shape[1])
            cols = [" ".join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in tb.columns]
            body = tb.iloc[:, :]; n = len(body)
            def cnt(pat):
                ci = [i for i, c in enumerate(cols) if re.search(pat, c, re.I)]
                if not ci: return "ستون نیست"
                s = body.iloc[:, ci[0]].astype(str); return f"{int((~s.str.contains('---|nan|No data', case=False)).sum())}/{n}"
            out.append(f"{ind} {nm} {y}-{m:02d}: ردیف={n} Tmax={cnt('Max')} Tmin={cnt('Min')} Prec={cnt('Prec')} | ستون‌ها={cols[:12]}")
        except Exception as e: out.append(f"{ind} {nm} {y}-{m:02d}: parse خطا {str(e)[:100]} | طول={len(t)}")
        time.sleep(4)
open("ogimet_probe.txt", "w", encoding="utf-8").write("\n".join(out)); print("\n".join(out))
