# از ماسک ماه‌های خالی اطلس، پنجره‌های ≤۵۰روزهٔ OGIMET می‌سازد: python3 make_jobs.py stn_mask.json jobs.json [سال میلادی شروع=2000]
import json, sys, datetime
from jcal import j2g, jdays
src, out = sys.argv[1], sys.argv[2]; Y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
d = json.load(open(src)); JY0 = d["jy0"]; CAP = (1405 - JY0) * 12 + 5; W = 50
jobs = []; nm = 0
for s in d["out"]:
    if not s["id"].startswith("W"): continue
    ms = set()
    for p in ("tmax", "tmin", "prcp"):
        m = s.get(p + "_m")
        if not m or s[p][0] < 0: continue
        f, l, _ = s[p]; st = f - m.index("1")
        ms.update(st + k for k, ch in enumerate(m) if ch == "0" and f <= st + k <= l); ms.update(range(l + 1, CAP + 1))
    iv = []
    for i in sorted(ms):
        y, mo = JY0 + i // 12, i % 12 + 1
        a = j2g(y, mo, 1); b = j2g(y, mo, jdays(y, mo))
        if b.year < Y0: continue
        a = max(a, datetime.date(Y0, 1, 1)); nm += 1
        if iv and (a - iv[-1][1]).days <= 20: iv[-1][1] = max(iv[-1][1], b)
        else: iv.append([a, b])
    for a, b in iv:
        e = b
        while e >= a:
            jobs.append({"ind": s["id"][1:], "end": e.isoformat(), "nd": min(W, (e - a).days + 1)}); e -= datetime.timedelta(days=W)
# ترتیب: ابتدا بازه‌های جدیدتر (داده‌ی معتبرتر)، سپس ایستگاه
jobs.sort(key=lambda j: (-int(j["end"][:4]), j["ind"], j["end"]))
json.dump(jobs, open(out, "w"), separators=(",", ":")); print("ایستگاه-ماه:", nm, "| درخواست:", len(jobs), "| ایستگاه:", len({j["ind"] for j in jobs}))
