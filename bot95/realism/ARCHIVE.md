# Archive realism — inactive

Decision: retain this work for possible separate realistic ghost experiments only,
subject to Pitch's agreement. Do not merge into main or deploy this archive.

The official Worker source is pitch6767/wallet-autopsy, directory bot95/.
Only its GitHub Actions deployment pipeline may publish the Worker.
Do not deploy it directly from Replit or the Cloudflare API.

The VPS was restored to its original launcher and cached rapide.js on
2026-10-12 at 11:54:23 UTC. The restored launcher downloaded official
version 12e25dd8efa1. Existing realism code, data and backups remain on disk
but are no longer the service entry point.

Archive contents:
- VPS modules, tests and previous documentation, retained without strategy changes.
- cloudflare-realism.mjs: RealismStore, /api/realism/* and /rapide-realiste.
- deploy-cloudflare.template.js: historical routing/import/binding/migration
  modification used for the earlier deployment. ARCHIVAL ONLY — DO NOT EXECUTE.
- launcher.cjs: historical pinned launcher; do not install it.

The earlier direct Cloudflare deployment occurred at
2026-10-12T11:33:00.724348Z. It used the then-live Worker bundle obtained from
Cloudflare (the preceding Wrangler deployment was at 11:30:42 UTC), plus local
Replit changes, not a build from this GitHub repository.

The earlier README describes that experimental installation, not the current
official VPS runtime. No live orders, wallet keys, secrets or measurement datasets
are included in this archive. Future integration requires explicit approval.
