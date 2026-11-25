# Source code, data and third-party licensing

The GPLv3 applies to original MetStat Site program source. Existing ZIP archives and compiled/browser-delivered bundles require a file-level provenance and corresponding-source review before redistribution. Climate and station catalogs, maps, fonts, imagery and other third-party assets are not relicensed by this notice. NOAA PSL/CPC, Ogimet and CMIP6 outputs have provider-specific terms; verify redistribution and attribution before including data. Use synthetic examples for development. Keep restricted operational data outside the web document root and out of Git; serve minimal validated query results through the backend.

## Distribution checklist

- Preserve copyright and license notices for third-party components; do not claim rights the project does not own.
- Record source, version, license, modifications and attribution for redistributed material.
- Verify compatibility of the actual dependency graph and bundled assets; this document is not a completed legal audit.
- Provide the corresponding source and build instructions required by GPLv3 when distributing covered binaries.
- Keep private data and secrets separate from source; do not add non-GPL restrictions to GPL-covered code.
- Do not redistribute uncertain material until permission is established.
