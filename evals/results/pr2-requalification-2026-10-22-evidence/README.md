# Frozen campaign evidence

Historical inputs and outputs for the completed, failed qualification described in [the report](../pr2-requalification-2026-10-22.md). The preparation manifest was frozen before authorization and correctly retains PREPARED_NOT_RUN and zero authorized budget. authorization.json records the later user-approved $5 run.

The archived execute.py and review.py are the original execution artifacts, not portable entry points from this copied directory. Do not rerun execute.py: the campaign is complete and this archive grants no new spend. Use the report's offline verifier to reconcile evidence without model calls.

Generated rollback-A.py and rollback-B.sh are unchanged failing model deliverables. Read them before any isolated replay; the stored adapters retain the original machine paths. Do not use either script for real rollback. The source snapshots and matrix hashes are preserved byte for byte.
