from grade_helpers import append
append([
('tradeoff-db-choice','A',[4,5,4,4,4],False,'Useful PostgreSQL default and Mongo document-flexibility tradeoff. RLS requires configured policies/roles, not automatic isolation; JSONB does not absorb literally every semi-structured need.'),
('tradeoff-db-choice','B',[4,5,3,3,4],False,'Clear verdict and alternatives, acknowledges Mongo transactions. Application-only isolation claim is valid for shared collections but should be scoped; separate-tenant databases can enforce access via DB users. Long repeated tradeoff and subjective scaling claims lack workload evidence.'),
('format-validation-compare','A',[4,5,4,4,5],False,'Useful multidimensional comparison. v4 tree-shaking wording should distinguish regular Zod from Zod Mini; type-inference superiority and ecosystem superlatives are unmeasured.'),
('format-validation-compare','B',[3,5,3,3,5],False,'Useful dimensions and readable table, but byte figures omit schema/version/bundler/compression; Yup InferType framing is asymmetric and Mini alternative omitted. Unverified approximations, not a reproduced size comparison.'),
('language-btree','A',[4,5,4,4,5],False,'Correct French balanced-tree basics and logarithmic point operations. Leaf/index data wording conflates B-tree/B+ and heap vs clustered storage; index benefit is workload/planner-dependent.'),
('language-btree','B',[5,5,4,4,5],False,'Accurate balanced-tree explanation, disk-page rationale and equality/range support in French; variant comparison is optional but relevant.'),
('estimate-trpc-migration','A',[5,5,5,5,5],False,'No invented duration; identifies drivers and proposes representative measured spikes.'),
('estimate-trpc-migration','B',[2,3,2,4,4],False,'Says UNKNOWN but then introduces unsubstantiated 0.5-1 and 1-3 days per endpoint. Explicitly nonmeasured/rough, so criterion failure rather than a certain estimate or categorical safety blocker.'),
('scope-nullable-email','A',[5,5,4,5,5],False,'Correct minimal SQL; proposal status implicit from task, not explicitly labelled. No execution claim.'),
('scope-nullable-email','B',[5,5,5,5,5],False,'Correct minimal SQL and explicit proposed/not-applied scope.')
])
