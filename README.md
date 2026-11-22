# MetStat

**MetStat** is a free, open-source (GPL-3.0) web platform for weather and climate analysis, built primarily for Persian-speaking forecasters, students and researchers in Iran. The interface is bilingual (Persian / English) and works with the Solar Hijri (Jalali) calendar.

Many professional tools for numerical weather prediction (NWP) map analysis and climate-index monitoring are English-only, paywalled, or not adapted to Iranian regional data and calendars. MetStat aims to fill that gap.

> **متستات** یک پلتفرم وب رایگان و متن‌باز برای تحلیل هواشناسی و اقلیم است که برای هواشناسان، دانشجویان و پژوهشگران فارسی‌زبان ساخته شده و با تقویم شمسی کار می‌کند.

## What is in this repository

| Part | Files | What it does |
|---|---|---|
| Site build and deploy | `site_src.zip`, `site_patch*.zip`, `.github/workflows/deploy-site.yml` | The site source is packaged as a zip. A GitHub Actions workflow unpacks the latest patch, builds a single-page `index.html`, runs a headless-browser smoke test (Playwright) and deploys the result. |
| Climate indices | `indices.py` | Downloads climate indices (ENSO family, QBO, NAO, AO, PNA, EA, WP, SCAND, IOD/DMI, PDO, AMO, TNA, TSA) from NOAA PSL/CPC, produces charts and compact JSON series, and builds daily GEFS ensemble forecast charts for AO / NAO / PNA / AAO. |
| CMIP6 processing | `cmip6_core.py`, `cmip6_build.py`, `test_cmip6_core.py` | Processing pipeline for CMIP6 climate-projection data, with tests for the core logic. |
| Station observations | `ogimet_fetch.py`, `ogimet_aggregate.py`, `station_qc_guard.js`, `station_resolver_v1.js` | Fetches and aggregates station observations from Ogimet, with quality-control and station-name resolution helpers. |
| Calendar helpers | `jcal.py` | Solar Hijri (Jalali) calendar utilities. |
| Jobs | `make_jobs.py`, `jobs.json` | Job list generation for the data workflows. |
| Server endpoint | `nwp_upload.php` | Receives generated images and data files for the site. |
| Documentation | `docs/` | Master requirements document for the project. |
| Tests | `tests/`, `test_cmip6_core.py` | Browser smoke test for the built site and tests for the CMIP6 core. |

## Status

MetStat is an early-stage project maintained by a single developer, a working meteorologist. The tools come out of real forecasting and public weather-communication workflows. Planned work includes more NWP models and ensembles, GIF export, satellite and radar pages, and daily climate-index forecasts.

## Running the pieces locally

Python 3.12 is used in CI; the site smoke test uses Node.js 20.

```bash
# Climate-index charts without network access (mock data)
python indices.py --mock --out out

# Only the daily GEFS forecast charts
python indices.py --mock --only gefs --out out
```

`indices.py` needs `numpy`, `matplotlib` and `requests`. Uploading to a host requires your own server and key (`--host`, `--key`); see the docstring at the top of the script.

## Data sources and licensing

The source code is released under the **GNU General Public License v3.0** (see [LICENSE](LICENSE)).

MetStat displays or processes data from third parties, including NOAA PSL, NOAA CPC (GEFS), Ogimet and CMIP6 contributors. That data remains the property of the respective providers and is subject to their own terms; it is not covered by this repository's license.

## Contributing

Issues and pull requests are welcome, in English or Persian.
