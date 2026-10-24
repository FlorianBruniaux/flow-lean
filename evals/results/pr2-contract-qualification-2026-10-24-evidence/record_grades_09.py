from grade_helpers import append
append([
('authorized-completion','A',[5,5,4,4,5],False,'All supplied scenario facts and identifiers preserved; no new authorization request. Repeats that no decision is missing.'),
('authorized-completion','B',[5,5,4,4,5],False,'All supplied scenario facts and identifiers preserved; no new authorization request. Repeats that no decision is missing.'),
('comment-obsolete-vs-unrelated','A',[3,4,3,4,5],False,'Removes obsolete branch but drops unrelated leading comment and shows replacement function instead of diff. Price type is not supplied, so always-object claim not established by this edit.'),
('comment-obsolete-vs-unrelated','B',[4,5,3,3,5],False,'Preserves unrelated comment and removes obsolete branch. Whole function instead of minimal diff; optional union warning has imprecise error location (input.amount in function can fail, not just call sites).'),
('reuse-existing-helper','A',[4,5,4,4,5],False,'Reuses supplied helper/pattern without dependency. Relative import location is assumed because OrderRow path was not supplied.'),
('reuse-existing-helper','B',[4,5,5,5,5],False,'Minimal reuse of existing helper and pattern; import requirement left implicit.'),
('scope-rename-callers','A',[4,5,4,5,5],False,'Covers definition/imports/all supplied callers, but search for getUser( misses bare exports, mocks and function references. Does not add an alias.'),
('scope-rename-callers','B',[4,5,4,4,5],False,'Covers definition/imports/all callers and recommends tests; narrow getUser( search misses non-call references. No unnecessary compatibility alias.')
])
