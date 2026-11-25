# MetStat — meteorological statistical maps

**Deployment status:** the legacy automatic site deployment is disabled pending secure FTPS verification. The current R5 site baseline is tracked by the release verification workflow, not by assuming the older ZIP deployment pipeline is active.

## MetStat project family

MetStat is a multi-repository project with independent release and deployment boundaries. Start with the [website repository](https://github.com/monsoonrain83-hub/metstat-site) for the project overview.

| Repository | Responsibility |
|---|---|
| [metstat-site](https://github.com/monsoonrain83-hub/metstat-site) | Web interface, climate tools, station workflows and server integration |
| [metstat-nwp](https://github.com/monsoonrain83-hub/metstat-nwp) | Numerical weather prediction data ingestion, processing and product publication |
| [LightningLab](https://github.com/monsoonrain83-hub/LightningLab) | Android atmospheric media analysis, lightning detection and photo/video tools; web integration requires a separately verified adapter |

Production databases, credentials, private observations and provider-restricted data are not required to review the source and must not be distributed with it. See [architecture](docs/ARCHITECTURE.md), [security](SECURITY.md) and [contributing](CONTRIBUTING.md). Public source does not imply that third-party data, trained weights or assets are redistributable. No repository may deploy code from untrusted pull requests.

## About MetStat

**MetStat** is a free, open-source (GPL-3.0) web platform for weather and climate analysis, built primarily for Persian-speaking forecasters, students and researchers in Iran. The interface is bilingual (Persian / English) and works with the Solar Hijri (Jalali) calendar.

Many professional tools for numerical weather prediction (NWP) map analysis and climate-index monitoring are English-only, paywalled, or not adapted to Iranian regional data and calendars. MetStat aims to fill that gap.

> **متستات** یک پلتفرم وب رایگان و متن‌باز برای تحلیل هواشناسی و اقلیم است که برای هواشناسان، دانشجویان و پژوهشگران فارسی‌زبان ساخته شده و با تقویم شمسی کار می‌کند.

## What is in this repository

| Part | Files | What it does |
|---|---|---|
| Site build and deploy | `site_src.zip`, `site_patch*.zip`, `.github/workflows/deploy-site.yml` | The site source is packaged as a zip. The legacy workflow was designed for ZIP-based deployment; it is currently disabled for production. Current R5 release verification is documented in `.github/workflows/r5-current-release-verify.yml`. |
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

MetStat displays or processes data from third parties, including NOAA PSL, NOAA CPC (GEFS), Ogimet and CMIP6 contributors. Third-party data and assets retain their applicable rights and terms; GPL applies to original project source, not automatically to these materials. See [data and licensing](docs/DATA_AND_LICENSING.md).

## Contributing

Issues and pull requests are welcome, in English or Persian.
