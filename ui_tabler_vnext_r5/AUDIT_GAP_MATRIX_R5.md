# MetStat r5 — user-approved sitemap and implementation gap report

## Exactly seven top-level content groups

1. **پایش و پیش‌بینی**: مدل‌های هواشناسی؛ متئوگرام؛ تصویر ماهواره و رادار؛ شاخص‌های اقلیمی؛ پیش‌بینی ماهانه و فصلی؛ شاخص خطر سیل ناگهانی؛ رصد لحظه‌ای ایستگاه‌ها؛ تهیه نقشه‌های همبارش از داده‌های ایستگاهی. The weather-model editor has five period tabs plus custom multimodel under the same child route.
2. **هواشناسی کاربردی**: وضعیت کلی؛ گزارش چندمدلی؛ هواشناسی کوهستان؛ گردشگری و سفر؛ هایکینگ و طبیعت‌گردی؛ هشدار ۷۲ ساعته؛ کیفیت هوا و گردوغبار؛ زلزله‌های اخیر.
3. **تحلیل همدیدی**: تحلیل سینرژی.
4. **هسته تحلیل اقلیم**: اطلس اقلیمی؛ کارگاه تغییر اقلیم و خشکسالی [تحلیل ایستگاهی، وضعیت منطقه‌ای، تغییر اقلیم مشاهده‌ای، پیش‌نگری آینده CMIP6، تیلور و هدف CMIP6، شاخص‌های اقلیمی xclim، تحلیل موجک]؛ اقلیم‌نما؛ بارش شبکه‌ای GPCC.
5. **ترکیب نقشه‌های آفلاین و آنلاین**: ترکیب خودکار؛ تحلیل چندمدلی؛ هشدار جوی؛ همرفت؛ اصلاح با ارتفاع؛ weather.us؛ WeatherBELL؛ WeatherModels؛ TropicalTidbits؛ سایر وب‌سایت‌های نقشه؛ تراکم رعدوبرق.
6. **جعبه ابزار هواشناسی**: تبدیل واحدهای هواشناسی؛ مبدل فایل‌های هواشناسی؛ مبدل فایل‌های تصویری و ویدئویی؛ مبدل فایل‌های اسنادی.
7. **استودیو آوا**: تهیه گزارش صوتی هواشناسی از روی متن؛ ویرایش ویدئو؛ ویرایش عکس؛ تشخیص رعدوبرق و تهیه عکس رعدوبرق از روی ویدئو.

Separate header **حساب کاربری**: ورود، ثبت‌نام، علاقه‌مندی‌ها، حساب/رمز، پنل مدیر، تأیید آمار ماهانه. Home is separate from the seven content groups.

## Fixed relative to r4

- **Navigation did not change pages**: wrong child-tree root in JS fixed; body-level dropdown portal prevents clipping by horizontal header scroll. Clicking menu anchors now changes right panel, map/workspace, breadcrumb and route.
- Incorrect group nesting replaced with **the exact user-provided hierarchy**, including climate workshop 3rd level.
- Ava Studio was absent: four browser sections and local-only runnable preview workflows added; standalone browser-native behavior demonstrated. Android-specific engines, AI weights and codecs are **not** silently presumed ported.
- Model flag emoji replaced by actual compact local SVG image assets in `<img>` elements; weekly/monthly/seasonal map rail stays short text, model sidebar shows full names and small images.
- Sound now enabled on user interaction by default and pressed state clearly animated. Status colors of original model chips are excluded from the general red/white theme.
- Drawing tools remain for synoptic map/fullscreen; non-map Ava Studio hides map-only zoom, layer, palette, fake timeline and drawing widgets.

## Explicit pending integration / release blockers

| Area | r5 review build | Production integration |
|---|---|---|
| 7 content groups | Full clickable hierarchy | Must map to actual live URI resolver, 301 only after confirmed routes/aliases |
| 68 review paths | Distinct path/title/panel incl. account | Not all 68 URLs are live; verify `.htaccess` and cPanel page types |
| User accounts | Role-labeled mock, zero credential transmission | Server session/roles/CSRF/permissions required |
| Synoptic drawing | SVG pointer drawing, H/L, fronts, undo | Real map CRS/projection and geodesic scale, save/reload/export |
| Forecast and custom multimodel | UI/state preview | Forecast manifest availability, same-cycle sourcing and scientific blend |
| PNG/GIF model export | PNG schematic, GIF settings UI | Real meteorological raster/GIF encoder, provenance, legend values |
| Photo editor | Local brightness/contrast/saturation + PNG download works | Port remaining LightningLab layers, undo, masks, professional export |
| Video editor | Video seek, range preview, frame PNG works | Real trim/render/export, audio/video track handling, codec QA |
| Lightning detection | Bounded brightness-jump heuristic works in local browser | Port and calibrate existing Detector/FlashAnalyzer, performance and false-positive validation |
| Audio studio | Native speech synthesis attempts locally | Reliable Persian voice selection, production export, speed/recording UX |
| Mobile UX | Chromium in-memory desktop/landscape/portrait tested | Physical Android pinch, touch, font/readability and overflow to be confirmed |
| Site security | Preview no remote network/auth | CSP, deployed asset pinning, cPanel backup, rollback, server-side guards |

**Do not merge the experimental preview into production until the live site's exact source tree has been compared and an authenticated staging release passes screenshot, route, click/tap, and rollback tests.**