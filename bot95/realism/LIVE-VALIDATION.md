# Official-input replay: connected, no live approval

The protected-shadow strategy is an experiment, not a replica of official M10.
Its returns must not be used to approve or reject official M10 for live execution.

## Implemented

- `official-execution.cjs` connects extracted decisions to order arrival,
  partial fills, delayed cancel acknowledgements, expiry and confirmed simulated
  settlement. Fill feedback updates the same order objects read by `coter`.
  It runs on completed official cycle recordings, not on invented entry signals.
- Authorized recording is maintained in the official GitHub repository, in
  bot95/rapide/rapide.js and its generated bot95/src/rapide_code.js. The strategy
  rules are unchanged. Raw book/trade events are captured before the old sampling
  filters, plus the probability, toxicity, prices and timing passed to M10.
  Recording uses fast asynchronous 512-KiB gzip blocks, with at most sixteen
  in flight (8 MiB of queued raw text) to absorb bursts before callbacks run.
  Bounds are 128 MiB raw and 8 MiB compressed per cycle; overflow, compression
  backpressure and unfinished blocks are explicit and excluded.
  Schema 3 stores token identifiers and constant market metadata once, then
  losslessly encodes events as tuples. No event sampling or signal fields are
  removed. The decoder remains compatible with schemas 1 and 2.
- `recorded-comparison.cjs` converts that recording to execution events and
  invokes the matching official decision code. A bounded timer on the VPS runs
  `comparison-service.cjs`, with 100/250/500-ms latency assumptions.
  Version mismatches, missing decisions, late-start recordings, ambiguous prints
  and missing execution books are excluded. Rounding corrections are limited to
  0.111 ms, reflecting the original raw timestamps rounded to 0.1 ms.
- Summaries live under /opt/bot95-comparison/public; private state and reference
  source versions live under its data directory. No port is opened. The existing
  monitoring publisher reads only the public comparison summary.
- `replay-official.cjs` replays one canonical market-cycle file and returns its
  execution journal. It refuses files without complete official decision inputs.
  The existing protected collector's files do not contain these inputs.

- `official-m10.cjs` extracts the actual official M10 decision block and its
  shared `coter` function from a supplied source snapshot. No paraphrased rules.
- It requires explicit market, probability, bid and toxicity inputs. It does not
  synthesize missing toxicity signals, launch the official source program,
  connect to a venue, or send an order.
- The execution adapter supplies `poser` and `annuler`; its order objects must
  receive fills and cancellation acknowledgements before subsequent decisions.
- Tests against the official snapshot check 50-dollar budgets, recotations,
  spending after fills, toxic withdrawals and time windows. Unknown source
  layouts fail closed.
- Public monitoring identifies the frozen source by version and SHA-256 and
  explicitly reports the unfinished integration. A copied reference is not proof
  of the version currently loaded in the official process.

## Still required before a live decision

1. Evaluate enough complete recordings and compare latency sensitivity; no
   minimum sample size or profit threshold alone proves live suitability.
2. Verify feed continuity and recording overhead. The replay currently does not
   certify that every upstream feed remained uninterrupted.
3. Check inventory and budget overruns, notably fills arriving after a requote.
   Do not inject the experimental hedge/resale policy into M10: that would again
   change the strategy. The replay adds no automatic protective exit to M10.
4. Test cancellation/requote overlaps, partial fills, late receipts, depth,
   budget exhaustion, feed gaps, restarts and confirmed settlement through the
   complete adapter. Unit tests of isolated functions are not this proof.
5. Compare aligned, versioned samples under explicitly different execution
   assumptions. Never pool different official versions as one experiment.
6. Calibrate actual execution separately, with explicit authorization for any
   capped real-money trial. Public data alone cannot prove queue position or
   private execution. Profit alone is never a live-approval criterion.

The existing accounting, public-book handling, persistence and partial-fill tests
remain useful; they do not by themselves supply strategy fidelity.

The replay expires orders at the cycle boundary and accepts only Gamma closed +
resolved winner confirmation. These are declared simulation rules, not private
venue acknowledgements. Maker fees are assumed zero only for a recognized
crypto_fees_v2 schedule. Queue position, delay, cancellations and settlement of
actual account balances are not calibrated by public observations.

Run extraction tests against a deliberately chosen local official snapshot:

```
OFFICIAL_SOURCE=/path/to/reference.js node --test deploy/bot95/official-m10.test.cjs
```

The script skips the reference-specific test if no snapshot is provided. A run
with that test skipped is not evidence about any official version.
