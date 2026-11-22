# Design references and attribution

All three codebases supplied by the administrator were inspected as GitHub ZIP source distributions.

| Project | Source | License / holder | Use in this MetStat package |
| --- | --- | --- | --- |
| Tabler core v1.7.5 source | https://github.com/tabler/tabler | MIT, Copyright (c) 2018–2026 The Tabler Authors | Main design and control vocabulary; no minified bundle copied from source ZIP |
| shadcn/ui source | https://github.com/shadcn-ui/ui | MIT, Copyright (c) 2023 shadcn | Accessible interaction design patterns and semantic color variables; no React runtime copied |
| Magic UI source | https://github.com/magicuidesign/magicui | MIT, Copyright (c) Magic UI | Motion references and decorative status patterns; no React/Framer library copied |

The repository source ZIPs themselves must **not** be copied wholesale into the public cPanel tree; they include build tools, examples, dependencies, and files unsuitable for runtime exposure. Before shipping a compiled Tabler asset or any other third-party substantial code, retain the corresponding MIT copyright and permission notice and pin/check dependencies. No font files are bundled here.