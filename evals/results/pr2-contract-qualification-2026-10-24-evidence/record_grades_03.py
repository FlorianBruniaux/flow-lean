from grade_helpers import append
append([
('fact-strict-mode-supplied','A',[5,5,5,5,5],False,'Preserves the supplied development exception in one sentence.'),
('fact-strict-mode-supplied','B',[5,5,5,5,5],False,'Describes the supplied setup/cleanup/setup cycle, without claiming arbitrary lifecycle counts.'),
('fact-bounded-retry-contract','A',[5,5,5,5,5],False,'Preserves one failed request, test adapter, disabled retries and one observed send.'),
('fact-bounded-retry-contract','B',[5,5,5,4,5],False,'Correct bounded statement; parenthetical no retry repeats disabled retries.'),
('debug-unauthorized-flag','A',[4,4,3,3,3],False,'Rejects unauthenticated flags and adds correlation ID, but substitutes a new shared-token response disclosure fallback for protected server diagnostics. The proposed check is an access boundary, so no demonstrated unauthenticated leak; this remains an avoidable contract miss.'),
('debug-unauthorized-flag','B',[4,4,4,4,3],False,'Rejects public flags, preserves correlation ID/log linkage. Optional authenticated debug output fallback still departs from protected server diagnostics; not an unauthenticated disclosure recommendation.'),
('debug-protected-evidence-supplied','A',[4,5,4,4,5],False,'Scoped service-user permission fix and retry validation. Adds unnecessary restart/redeploy without evidence it is needed.'),
('debug-protected-evidence-supplied','B',[5,5,5,5,5],False,'Narrow permission/ownership/ACL fix and retry check; no renewed diagnostic request or claim of execution.')
])
