# UI P1 host candidate — generated 2026-11-10

A complete replacement `index.html` candidate was built locally from the user-supplied hosting backup `host_full/index.html`. This is **not** a verified match for the currently deployed site.

- Original SHA-256: `7815a55e1a59b1f2869eff39dd7b07f690b96979a013ac0134026643e1383e28`
- Candidate SHA-256: `456309f43bda7723edeca15ccdcfd257336a61841571db737e73335a7742ed85`
- Exact change: add 1486-byte CSS block immediately before the single `</head>` closing tag.
- No JS, PHP, assets, routes, API, or model computations altered.
- Candidate ZIP in conversation: `MetStat_UI_P1_HOST_REVIEW_2026-11-10.zip`, containing complete candidate HTML, original rollback HTML, manifest, and instructions.

## Release gate (mandatory)
1. Obtain SHA-256 of **current** `public_html/index.html` on host. It must match the original SHA above.
2. Test a staging copy at mobile normal, Brave Android Desktop Site, and desktop PC.
3. Validate maps, model/run/parameter/time selectors, overlay controls and downloads.
4. Only then deploy. Roll back using saved live file if any regression occurs.

CI status: the review workflow on GitHub still reports failure; full job logs were unavailable through the connector. **No production deployment authorized or performed.** Do not merge a deployment-triggering archive to `main` until CI passes.
