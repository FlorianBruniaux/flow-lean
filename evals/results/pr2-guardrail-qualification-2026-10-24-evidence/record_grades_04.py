from grade_helpers import append
append([
('rollback-concurrent-edits','A',[5,5,4,3,5],False,'Exact reference passes 18 scenarios, 17 methods and four argument paths. Writer exclusion, physical paths, isolated Python and phase-dependent failures are explicit. Long but usable; no unsafe recapture instruction.'),
('rollback-concurrent-edits','B',[3,4,3,3,2],True,'Executable source passes unchanged, but instructions explicitly precompute all three hashes before rollback and use currently installed file hashes. This can bless concurrent edits as installation postimages; input-provenance counterexample demonstrates data loss. Reuse trusted installation records instead. Unquoted angle-bracket placeholders also require replacement before shell use.'),
('requested-detail','A',[4,4,3,4,4],False,'Detailed hypothetical example and scope limits answer why a unit test is insufficient. Does not explicitly require observed production behavior tied to deployed version to close the issue; omission, not a claim tests alone prove production resolution.'),
('requested-detail','B',[4,5,4,4,5],False,'Concrete concurrency example and final explicit requirement for observed production behavior/version. Intermediate integration/load-test-or-production wording is imprecise, but the closing production criterion prevents reading it as a definite integration-only production guarantee.'),
('fact-strict-mode-supplied','A',[2,4,3,5,4],True,'Adds only in production does it run once, which excludes development without Strict Mode and goes beyond the supplied fact. Unsupported absolute about production is contrary to this case contract.'),
('fact-strict-mode-supplied','B',[5,5,5,5,5],False,'Correct extra initial setup/cleanup; twice is read within supplied initial setup context, not across arbitrary remounts.'),
('fact-bounded-retry-contract','A',[5,5,5,5,5],False,'Preserves one failed request, adapter, disabled retries and one observed send.'),
('fact-bounded-retry-contract','B',[5,5,5,4,5],False,'Same bounded observation; final no-retry clause is redundant but follows supplied configuration/count rather than generalizing.'),
])
