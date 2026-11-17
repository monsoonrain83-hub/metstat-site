# MetStat — وصلهٔ خودکارسازی هم‌بارش (بستهٔ آزمایشی ادغام)

**مبنای تست:** گزارش ۴۶ ایستگاه گیلان از ۲۴ تا ۲۶ آبان ۱۴۰۵ و فایل‌های تقسیمات کشوری ارسالی. این بسته **مستقل از v59 و بدون تغییر بانک رمزگذاری‌شدهٔ ۷٬۰۴۹ ایستگاه** ساخته شده است. روی هاست زنده و روی کد صفحهٔ نصب‌شده تست نشده؛ فقط با افزودن فایل‌ها فعال نمی‌شود و اتصال به صفحهٔ فعلی لازم است.

## ۱. رفتار دقیق جدید

ورودی گزارش از متن به هر تعداد ردیف پردازش می‌شود؛ هیچ محدودیتِ اجباری «انتخاب ۱۰ ایستگاه» نباید در رابط باقی بماند. در تطبیق هر نام، **نام کامل و مستعار + استان + شهرستان** با بانک واقعی ایستگاه‌ها سنجیده می‌شود؛ سپس شبکهٔ **سینوپتیک ← اقلیم‌شناسی ← باران‌سنجی** اولویت دارد. اگر بانک معتبر هیچ ایستگاهی را شناسایی نکند، نام آبادی/شهر از مرجع کشوری بررسی می‌شود و برای به‌دست‌آوردن مختصات، جست‌وجوی خودکار سرور انجام می‌شود. نقاط آبادی/شهر با `not_sensor=true` متمایز می‌شوند، زیرا مختصات آن‌ها لزوماً محل سنسور نیست. همنامی یا تفاوت شهرستان، هرگز به تطبیق خودکارِ بی‌هشدار تبدیل نمی‌شود.

## ۲. فایل‌ها

- `online/assets/metstat_rain_parser.js`: استخراج رقم‌های چسبیده، اعشار فارسی، استان و بازه تاریخ؛ بدون حذف «استانداری»
- `online/assets/metstat_auto_match.js`: انتخاب شبکه با اولویت، قفل اداری و وضعیت‌های خطا
- `online/assets/metstat_auto_flow.js`: فراخوانی خودکار سرویس جغرافیایی برای موارد حل‌نشده، برگشت گزینه‌های بررسی، شمارش کل
- `online/api/metstat_location_lookup.php`: endpoint امن POST (بدون نیاز به مختصات ورودی)، جست‌وجوی Google Geocoding در صورت وجود کلید در سرور، کنترل نام و استان/شهرستان
- `online/assets/metstat_map_tools.js`: دکمهٔ واضح **ذخیره PNG بالای نقشه**، کنترل مرز استان و شهرستان/مراکز آن‌ها، رنگ سیاه و بدون حاشیهٔ سفیدِ برچسب ایستگاه، ترکیب عنوان/تاریخ/لوگو/آمار/حق نشر داخل PNG
- `online/data/iran_places/`: شاخه‌بندی ۱۰۰٬۹۸۹ شهر/آبادی بر اساس استان، با مجوز GPL-3.0 و کدهای شهرستان. این مرجع **مختصات ندارد**.
- `tests/`: متن گزارش و آزمون‌های Node
- `tools/`: مولد شاخص جغرافیایی از ZIP اصلی؛ بانک رمزگذاری‌شدهٔ سنسور ساخته یا تغییر داده نمی‌شود.

## ۳. اتصال به صفحهٔ فعلی

ابتدا فایل‌های موجود سایت را بکاپ بگیرید. فایل‌های JS، PHP و `data/iran_places/` را با حفظ مسیر داخل `public_html/online/` **اضافه** کنید؛ نسخه‌های فعلی صفحه و API را جایگزین نکنید. سپس در فایل اصلی `station_isohyet_vXX.html` یا سورس سازندهٔ آن، پس از بارگیری نقشه و بانک واقعی v59+ این چهار اسکریپت را به ترتیب اضافه کنید:

```html
<script src="/online/assets/metstat_rain_parser.js"></script>
<script src="/online/assets/metstat_auto_match.js"></script>
<script src="/online/assets/metstat_auto_flow.js"></script>
<script src="/online/assets/metstat_map_tools.js"></script>
```

حالا اتصال واقعی با **توابع موجود در صفحه** لازم است. نمونهٔ زیر قرارداد مورد انتظار را نشان می‌دهد؛ نام متغیرها (`currentLeafletMap` و غیره) عمداً placeholder است و باید از سورس واقعی صفحه گرفته شود:

```js
const tools = MetStatMapTools.install({
  map: currentLeafletMap,
  mapElement: document.getElementById('existing-map-id'),
  layers: {
    provinceBorders: existingProvinceLayer,
    countyBorders: existingCountyLayer,
    provinceCenters: existingProvinceCentersLayer,
    countyCenters: existingCountyCentersLayer
  },
  logoUrl: '/path/to/site-logo.png',
  attribution: '© OpenStreetMap contributors | MetStat',
  exportScale: 3
});

const result = await MetStatAutoFlow.processReport(pastedRainfallText, {
  // MUST return decoded station records from the existing v59+ station API/database.
  // Each record: id, name/name_fa, aliases, province, county, lat, lon, station_type.
  getStations: async (rows) => existingStationCatalog,
  mapTools: tools,
  renderMapped: (resolvedRows) => existingDrawStationsAndIsohyet(resolvedRows),
  renderReview: (pendingRows) => existingReviewPanel(pendingRows),
  onProgress: (done, total, counts) => updateExistingProgress(done, total, counts)
});
```

**مهم:** این نمونه تا وقتی به توابع واقعی صفحه و بانک رمزگذاری‌شدهٔ جاری وصل نشود، تغییری در رابط عملیاتی ایجاد نمی‌کند. فایل‌های `station_key_v45.hex` و `station_db_v45.enc` عمداً در بسته نیستند. مختصات و شناسهٔ هیچ سنسوری تغییر نمی‌کند.

## ۴. اتصال Geocoding به گوگل

فراخوانی از خودِ سرور انجام می‌شود و هیچ کاربری مختصات وارد نمی‌کند. روی هاست، مقدار `METSTAT_GOOGLE_GEOCODING_KEY` را به‌صورت **متغیر محیطی سرور** یا تنظیم امن خارج از `public_html` تعیین کنید و دسترسی سرویس و سهمیه/هزینهٔ API را فعال کنید. کلید را در JS عمومی قرار ندهید.

بدون کلید یا وقتی سرویس پاسخ معتبر ندارد، خروجی `unavailable`/`not_found` برمی‌گردد و فقط رکوردهای حل‌نشده در پنل بررسی می‌آیند. **نباید نقطهٔ تصادفی یا مرکز شهرستان به‌عنوان سنسور قطعی ثبت شود.** API عمومی OSM Nominatim برای جست‌وجوی انبوهِ خودکارِ اپلیکیشن استفاده نشده است.

## ۵. لایه‌ها و PNG

دکمهٔ بالای نقشه داخل toolbar ساخته می‌شود. مرزهای استان/شهرستان و مراکز آن‌ها فقط هنگامی فعال می‌شوند که صفحهٔ اصلی **لایهٔ واقعی** به `layers` پاس داده باشد؛ این بسته دادهٔ مرز جعلی تولید نمی‌کند. برچسب‌ها باید کلاس `metstat-station-label` یا `metstat-station-tooltip` داشته باشند. برای خروجی PNG لازم است کتابخانهٔ `html2canvas` نسخهٔ ۱٫۴ یا بالاتر در صفحه موجود باشد و سرور کاشی‌/لوگو اجازهٔ CORS بدهد. تهیهٔ PNG با اندازهٔ بزرگ‌تر، کیفیت کاشی‌های کم‌وضوح را ذاتاً افزایش نمی‌دهد؛ برای تصویر واقعاً شارپ، لایهٔ برداری مرزها و کاشی‌های Retina یا خروجی سرور لازم است.

## ۶. نتیجهٔ آزمون و محدودیت‌ها

- ۸ آزمون Node: **۸/۸ موفق**.
- گزارش اصلی گیلان: **۴۶/۴۶** مقدار با حفظ ترتیب/بارش/استان خوانده شد. چابکسر=۱۵۴٫۵؛ امامزاده اسحاق=۱۳۴٫۲؛ استانداری رشت=۵۹٫۱؛ جیرنده=۰٫۰.
- API محلی PHP بدون کلید: «چابکسر» در **گیلان/رودسر** و «شیاده بالا» در **مازندران/بابل** به‌صورت منبع اداری پیدا شدند؛ به‌طور صحیح مختصات جعلی نداد.
- «امامزاده اسحاق» در دادهٔ آبادی‌های موجود **دزفول/خوزستان** است؛ بنابراین نباید به‌جای گزارش گیلان/شفت انتخاب شود. جست‌وجوی خارجی در کلید فعالِ عملیاتی هنوز اجرا نشده.
- انطباق واقعی ۷٬۰۴۹ رکورد، کیفیت کانتور/درون‌یابی بارش، نمایش لایه‌های سایت، export با کاشی‌های واقعی، عملکرد و هزینهٔ Google API، سازگاری با فایل HTML جاری، و درصد خودکارسازی **هنوز روی نسخهٔ عملیاتی آزمایش نشده‌اند**. ادعای موفقیت ۹۹٪ وجود ندارد.

## ۷. آزمون‌های سریع

```sh
node --test tests/test_auto_station.js
php -l online/api/metstat_location_lookup.php
python tools/build_places_json.py list-of-cities-in-Iran-main.zip online/data/iran_places
```

منبع دادهٔ آبادی‌ها: https://github.com/sajaddp/list-of-cities-in-Iran — مجوز GPL-3.0 در `online/data/iran_places/LICENSE-GPL-3.0.txt`. منبع دیگر: https://github.com/ahmadazizi/iran-cities — MIT. این بسته دادهٔ خروجی آبادی‌ها را از مخزن اول استخراج می‌کند و باید شرایط مجوز انتشار داده رعایت شود.
