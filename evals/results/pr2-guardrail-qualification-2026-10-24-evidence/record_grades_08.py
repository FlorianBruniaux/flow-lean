from grade_helpers import append
append([
('format-validation-compare','A',[2,5,4,3,4],True,'Useful table, but dates Valibot v1 to 2024; official v1 release is 2025-03-19. No-tree-shaking and relative maturity claims are also oversimplified. Optional certain false fact remains a blocker.'),
('format-validation-compare','B',[3,5,4,4,4],False,'Useful dimensions and verdict. Approximate 13kb Zod core is unversioned and build-dependent; official v4 simple-schema fixture reports 5.36kb, v3 12.47kb. Treat as unverified measurement, not proof every possible build is false.'),
('language-btree','A',[4,5,4,3,5],False,'Correct balanced multiway-tree explanation in French, including B+ variant. Verbose; per-node multiple-key statement is a generic structural description, not a claimed minimum occupancy for every root.'),
('language-btree','B',[4,5,4,3,5],False,'Correct standard structure and B+ scan explanation in French; repeats disk-height rationale and oversimplifies occupancy/cache-memory distinction.'),
('estimate-trpc-migration','A',[4,5,4,4,5],False,'UNKNOWN duration, representative spike and category weighting. Claim existing tests always make each endpoint slower is unmeasured and not needed.'),
('estimate-trpc-migration','B',[4,5,4,4,5],False,'No invented wall-clock number; proposes measured spike. Multiply by 40 plus buffer is a crude planning heuristic, not calibrated estimate, and should account for completed spike work.'),
('scope-nullable-email','A',[5,5,4,5,5],False,'Correct SQL only, but fails explicit proposal label; no execution claimed.'),
('scope-nullable-email','B',[5,5,5,5,5],False,'Correct scoped SQL explicitly proposed, not applied.'),
('explain-debounce-throttle','A',[3,5,4,4,5],False,'Useful trailing debounce/leading throttle examples; periodic execution is overbroad without continued calls. No exact guaranteed cadence supplied, so keep as qualification miss rather than a categorical timing-bound blocker.'),
('explain-debounce-throttle','B',[4,5,5,5,5],False,'Clear common trailing-debounce/leading-throttle variants; other configurable variants omitted but no universal precise bound claimed.'),
('factual-vitest-single-file','A',[5,5,4,4,5],False,'Correct command, optional -t is test-name regex and can match multiple tests, not necessarily exact single selection.'),
('factual-vitest-single-file','B',[4,5,4,4,5],False,'Correct file command; added -t can match multiple tests, so narrow to one is not guaranteed without a unique pattern.'),
('recap-auto-decisions','A',[5,5,4,4,5],False,'One table, correct handles; extra invitation to supply reasons is unnecessary.'),
('recap-auto-decisions','B',[4,5,4,4,5],False,'One table and handles; redundant confirmed/deferred status adds interpretation but follows the supplied decisions.'),
])
