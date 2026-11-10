# Local validation — 2026-11-10

Test basis: user-supplied `site_src_reconstructed_r193.zip`, **not** the latest binary `site_src.zip` from GitHub.

- Unpacked the archive into a clean temporary directory.
- Applied the P1 CSS candidate to `site/src/css/app.css` after verifying the expected anchor and absence of an existing P1 block.
- Executed `python build_site.py index.html`: **PASS** (output ~17,912 KB reported by the build tool).
- Executed `node --check` on `34_online.js` and `82_nv_rows.js`: **PASS**.
- Ran all 8 static assertions from `check_source.py`: **PASS**.
- Browser rendering/touch testing: **NOT VERIFIED**.
- Latest live source parity: **NOT VERIFIED**.

GitHub Actions `UI review P1 (no deploy)` runs 1 and 3 returned **failure**. The connector returned job records without steps, and the job-log download returned a missing blob, so the failure cannot be attributed reliably to code or infrastructure. No production deployment attempted.

The browser smoke runner was changed to a self-contained test at `docs/ui-review-20261110/browser_smoke.js`, because the reconstructed archive does **not** contain `site/tests/smoke.js` referenced by the site's original deployment workflow.

**Release gate: CLOSED.** Do not merge deployment-triggering archive changes into main until source parity and rendered tests pass.
