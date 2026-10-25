from grade_helpers import append
append([
('tradeoff-ssr-ssg','A',[4,5,5,5,5],False,'Clear SSG recommendation and update path. Cheapest/fastest and no SSR benefit are broad architectural shorthand rather than measured universal guarantees; no cache configuration claimed as inspected.'),
('tradeoff-ssr-ssg','B',[3,5,4,5,5],False,'Clear recommendation, but webhook-triggered on-demand builds are not inherently incremental or alternatives to a full rebuild. Configuration-dependent claim left unverified rather than asserting no platform can support partial builds.'),
('actor-reversed-draft','A',[2,3,3,4,3],True,'Source roles correct, but assigns a binding obligation to the recipient from the author draft alone; no recipient agreement is supplied.'),
('actor-reversed-draft','B',[1,2,3,4,3],True,'Invents approval not yet given and recipient agreement recorded in the author draft. Correct role nouns do not preserve modality or evidence.'),
('actor-third-party-fr','A',[4,5,4,4,5],False,'Alice acts, Karim approves. Conditional until wording does not assert a definite current missing approval; non-date clause is unnecessary.'),
('actor-third-party-fr','B',[2,3,4,4,4],True,'Correct actors, but explicitly asserts approval encore en attente et non acquise, a current state absent from the source.'),
('actor-direct-assistant','A',[3,4,4,5,4],False,'Correct direct roles and explicit no approval/action. Waiting assertion is unsupported conversational shorthand, recorded as contract miss rather than an approval grant.'),
('actor-direct-assistant','B',[4,5,4,5,4],False,'Correct roles. Present-tense I approve is potentially ambiguous, but read in the requested role explanation, not as an explicit present endorsement or independent promise.'),
('actor-separate-delivery','A',[5,5,5,5,5],False,'Nora acts, Maya receives, Leo approves; condition retained.'),
('actor-separate-delivery','B',[5,5,5,5,5],False,'All actors and conditional delivery retained without added state.'),
])
