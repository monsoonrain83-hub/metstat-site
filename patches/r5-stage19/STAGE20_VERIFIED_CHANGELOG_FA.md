# اصلاح عملی ادامه R5 — ۲ آذر ۱۴۰۵

## تغییرات کد در همین PR
- فایل `patches/r5-stage19/assets/metstat_r5_stage19_controls.css`: هندسه دسکتاپ دو‌ستونه برای shellهای واقعی دارای `aside + main` در هشت شناسه (`app`, `dsApp`, `cvApp`, `ltApp`, `onApp`, `wnApp`, `anAuto`, `caApp`)، ستون راست ۳۲۸px و فضای اصلی در چپ، بدون تغییر موتور داده و DOM.
- فایل `patches/r5-stage19/assets/metstat_r5_stage19_controls.js`: رفع نشت زبان دکمه پیش‌فرض مدل/پارامتر شامل حالت ترکیبی فارسی/انگلیسی؛ فقط متن و aria-label اصلاح می‌شوند، شناسه/داده/رویداد تغییر نمی‌کنند.
- شیوه کد: همان assetهای Stage19 اصلاح شدند؛ اسکریپت تکراری دیگری روی صفحه ایجاد نشده است.

## شواهد آزمایشی
- Stage19 full index واقعی از Library بازیابی شد: SHA256=`d06bcb5b8504385f35334c21a1f120aa7d7ee72568476f026194d4814869f7f0`.
- ۴ اندازه × ۲ زبان (۸ مورد) با Chromium offline، `#onApp`: سمت راست sidebar، عدم ID تکراری، هفت منو، پنج select جغرافیایی، تغییر زبان/پیش‌فرض، حفظ option.value و نبود pageerror.
- ۱۴ inline script با Node syntax-check موفق؛ ۲۰ داده Base64 بدون تغییر.
- HTML تجمیعی Stage20 SHA256=`f6c8019be25300971a3d3032540477bab732d3490296abfc402b9bd961adaf4f`.
- آرشیو ZIP کامل Stage20 به Library پروژه با نام `MetStat_R5_STAGE20_DESKTOP_SHELL_I18N_STAGING.zip` انتقال یافته، دارای ۱۰ فایل از جمله HTML و سه asset اصلی، QA و نصب‌کننده تطبیق هش Stage19.

## واقعیت استقرار
- این اصلاح روی **شاخه آزمایشی PR #21** است و main/هاست ACTIVE تغییر نکرده‌اند. موفقیت روی HTML offline، عملکرد tile، PNG/GIF، backend، مسیریابی cPanel و تمام صفحات را اثبات نمی‌کند.
- قبل از انتشار باید active index و دارایی‌ها از cPanel دریافت، hash شوند، روی staging با داده واقعی و مسیرها سنجیده و rollback خارج از web root تهیه شود.
- برای پیگیری کامل، سند `docs/METSTAT_R5_UNIFIED_ROADMAP_20261123.md` همچنان قرارداد اصلی P0–P7 است.