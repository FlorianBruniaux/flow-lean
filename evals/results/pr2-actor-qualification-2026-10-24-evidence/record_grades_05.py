from grade_helpers import append
append([
('requested-detail','A',[3,4,4,4,4],False,'Useful isolated-versus-production example and no false resolution claim. Overgeneralizes unit tests as necessarily mocked and does not state the requested requirement to observe relevant production behavior/version before closing.'),
('requested-detail','B',[5,5,5,4,5],False,'Provides detailed hypothetical example and explicitly requires production observations tied to deployment/SHA; does not substitute integration tests for production evidence.'),
('fact-strict-mode-supplied','A',[5,5,5,5,5],False,'Single-sentence rejection preserves exactly the supplied development extra setup/cleanup exception.'),
('fact-strict-mode-supplied','B',[3,4,4,4,4],False,'Rejects the all-environments absolute and gives setup/cleanup/setup. Before mounting for real is imprecise phase wording, and only holds outside Strict Mode is an overbroad paraphrase, not an explicit promise of exactly one invocation across arbitrary remounts. No certain remount guarantee inferred.'),
('fact-bounded-retry-contract','A',[5,5,5,5,5],False,'Preserves one failed request, test adapter, retries disabled and exactly one observed send.'),
('fact-bounded-retry-contract','B',[5,5,5,5,5],False,'Preserves bounded supplied test result; confirming no retry occurred is consistent with disabled retries and one send.')])
