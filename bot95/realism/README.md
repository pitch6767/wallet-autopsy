# Bot95 realism-2 (maker only)

Pinned isolated ghost service, no trading orders or portfolio keys added.
Source baseline SHA256:
`f1c44960002b9c6c9f76dc730eb83b379c9ad75502ece87bddf307698239e886`.

`rapide.cjs` preserves the existing strategies but uses conservative exact-price
SELL prints for maker matching. Public cancellations never advance the queue.
Historical matching is counterfactual, not a live fill guarantee. Identical prints
with the same timestamp may be distinct legitimate prints: deduplication therefore
can undercount. BUY mirror prints and trade-throughs are intentionally excluded.
The old three model fields are identical in this version and must not be presented
as independent estimates. Hypothetical latency is max(100ms, public GET RTT p90),
not calibrated order latency. Maker fees remain assumed zero, not venue-verified.
Taker/signal survival simulations are unchanged and not validated by this patch.

Maker budgets reserve all outstanding orders; requotes wait for cancellation
and a one-second late-print horizon. Source timestamps decide whether delayed
prints occurred before cancellation or expiry, rather than their receipt time.
Terminal no-fill orders remain in result batches. Metrics include unmatched
shares, share-seconds and exposure duration, costs and resolved settlement PnL.
Inventories and settlements use an fsynced write-ahead journal plus atomic
checkpoints. Known positions survive restart. Outstanding quotes are NOT blindly
replayed: the interrupted cycle is blocked from new maker quotes, marked incomplete,
and excluded from validated PnL. Fills possibly missed during downtime are never invented.
The old v1 snapshot is imported as incomplete; past results are not recalculated.

Local data stays in `/opt/bot95-rapide/realism-1/` for migration compatibility:
- `ledger-v2.json`, `ledger-v2.wal`: durable cohort, inventories and fill evidence.
- `daily-report.json`: rolling progress of the fixed 24-hour observation window.
- `publication.json`: acknowledged row hashes; failed updates are retried.
- `measurements.json`, per-run snapshots, `report.html`: current maker observations.
- `completed.ndjson`: cycles removed from the one-hour in-memory window.
- `batches/`: atomic settled result batches; retained without Cloudflare delivery.
- Existing raw cycle recorder remains enabled.

Cloudflare's legacy aggregates are NOT fed these corrected batches.
`/rapide-realiste` and `/api/realism/status` expose the corrected maker cohort,
through a separate RealismStore Durable Object in the existing Bot95 Worker.
`/api/realism/ingest` accepts only the existing VPS IPv4. Sequence and timestamp
checks make duplicate/out-of-order deliveries idempotent. Original bindings,
trading configuration and routes are preserved; HTML pages gain a navigation link.
Other VPS services, Caddy, ports and system runtimes are not changed.
Original launcher and latest old batch are backed up before restarting.
The pinned launcher disables implicit remote code upgrades.

Tests: `node --test deploy/bot95/*.test.cjs`.
Deploy these modules to `/opt/bot95-rapide/realism-code/`, with launcher.cjs copied
to `/opt/bot95-rapide/launcher.js`; use existing private Node and systemd service.

## Reading the 24-hour report

The window begins at the next five-minute boundary after cohort creation, and ends
24 hours later (UTC timestamps also visible in JSON). It persists across restarts.
Only settled, completed, uninterrupted rows in that window contribute to validated
PnL. Single-leg and imbalance rates use filled cycles as denominator, never all
zero-fill cycles. The report relates maker fills to their actual public print,
checks volume conservation and simulated arrival/cancellation times, and reports
public message lag. Fee sensitivities are not a verified fee schedule.
A finished wall-clock window is not proof of full coverage or profitability.

Cloudflare deployment template is an initial migration, not a repeatable update:
its guards intentionally reject an existing REALISM binding. Future updates must
preserve the new class/namespace and migration tag, as well as original bindings.
