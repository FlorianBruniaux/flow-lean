from grade_helpers import append
append([
('actor-permission-not-promise','A',[5,5,5,4,5],False,'Correct ability/approval roles and no promise; explanatory contrast is unnecessary but does not alter authority.'),
('actor-permission-not-promise','B',[4,4,4,5,4],False,'Correct roles and exclusive authority. Approval required regardless of review outcome adds an unspecified requirement, but does not explicitly make review conditional on approval.'),
('actor-ambiguous-approval','A',[4,4,4,5,5],False,'Carol acts and ambiguity retained. Someone else mentioned earlier can refer to Alice earlier in the supplied sentence; it does not explicitly invent an unstated person. Naming Alice would be clearer, but do not manufacture a blocker from this ambiguity.'),
('actor-ambiguous-approval','B',[4,5,4,5,5],False,'Names Carol and Alice as alternatives. Bobs implied other party is awkward because Alice is explicit, but the roles and ambiguity are preserved.'),
('factual-git-log','A',[5,5,5,5,5],False,'Exact path-filtered last-commit command.'),
('factual-git-log','B',[5,5,5,5,5],False,'Exact path-filtered last-commit command.'),
('tradeoff-db-choice','A',[2,5,3,3,2],True,'Categorically says MongoDB tenant isolation depends entirely on application query discipline. Separate databases with scoped users contradict this; RLS/configuration is also insufficiently scoped.'),
('tradeoff-db-choice','B',[3,5,3,5,3],False,'Clear verdict and document alternative. RLS/schema isolation prerequisites and restricted roles are omitted, failing strengthened criteria. Read as a capability recommendation, not a definite assertion that selecting PostgreSQL automatically enforces isolation; no concrete false MongoDB exclusion.'),
])
