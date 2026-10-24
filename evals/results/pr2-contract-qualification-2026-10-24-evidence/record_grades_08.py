from grade_helpers import append
append([
('simple-choice-prose','A',[5,5,5,5,5],False,'Correct supplied choice and reason in short prose.'),
('simple-choice-prose','B',[5,5,5,5,5],False,'Correct supplied choice and reason in short prose.'),
('speaker-commitment','A',[5,5,4,4,5],False,'Correct speaker and recipient approval condition; no current approval inference. Elaborates obligation/time limits beyond requested core.'),
('speaker-commitment','B',[2,2,3,3,4],True,'Changes recipient approval into your approval while addressing the committing speaker. This reverses the actor controlling the trigger. Also adds unnecessary satisfaction/attempt contrast.'),
('no-automatic-recap','A',[4,5,4,4,5],False,'All three changes and local checks preserved once. Adds No blockers without that status being supplied.'),
('no-automatic-recap','B',[4,5,4,4,5],False,'All three changes and local checks preserved once. Adds No blockers without that status being supplied.'),
('unknown-scope','A',[5,5,5,5,5],False,'Preserves functionality validation and 16 integration tests; unknown limited to production latency.'),
('unknown-scope','B',[5,5,5,5,5],False,'Preserves functionality validation and 16 integration tests; unknown limited to production latency.')
])
