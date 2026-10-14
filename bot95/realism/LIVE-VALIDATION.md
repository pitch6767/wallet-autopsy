# Live validation: incomplete, no approval

The protected-shadow strategy is an experiment, not a replica of official M10.
Its returns must not be used to approve or reject official M10 for live execution.

## Implemented

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

## Still required before a meaningful same-strategy comparison

1. Match the official evaluator's trigger timing and preconditions, not just
   invoke M10 on a convenient 50-ms top-of-book timer.
2. Supply the identical official probability and toxicity calculations. Toxicity
   depends on exchange movements, aggressive flow and recent Polymarket prints;
   the existing protected collector does not capture all of those inputs.
3. Connect fills and cancel acknowledgements to the official order objects and
   durable position accounting. Do not inject the experimental hedge/resale
   policy into M10: that would again change the strategy. Establish which exits
   the official strategy actually invokes.
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

Run extraction tests against a deliberately chosen local official snapshot:

```
OFFICIAL_SOURCE=/path/to/reference.js node --test deploy/bot95/official-m10.test.cjs
```

The script skips the reference-specific test if no snapshot is provided. A run
with that test skipped is not evidence about any official version.
