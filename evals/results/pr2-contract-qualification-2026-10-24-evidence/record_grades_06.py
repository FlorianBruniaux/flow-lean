from grade_helpers import append
append([
('explain-debounce-throttle','A',[4,5,4,4,5],False,'Useful usual trailing-debounce/throttle distinction. Periodic guarantee depends on continued activity and scheduling; leading/trailing options omitted.'),
('explain-debounce-throttle','B',[4,5,4,4,5],False,'Useful basic distinction and choice guidance; throttle immediately/ignore description is a leading-only variant, not all implementations.'),
('factual-vitest-single-file','A',[5,5,5,5,5],False,'Exact correct Vitest run command with file filter.'),
('factual-vitest-single-file','B',[5,5,5,5,5],False,'Exact correct Vitest run command with file filter.'),
('recap-auto-decisions','A',[5,5,5,5,5],False,'One table with stable handles and supplied decisions only.'),
('recap-auto-decisions','B',[3,4,4,5,5],False,'Decision handles and choices preserved, but invents reasons absent from supplied facts. No established contradiction or reversed recommendation.'),
('recap-off-actions','A',[4,5,4,5,4],False,'Three useful metadata/pack/publish steps without invented execution. npm version supplies a tag on Git path, but manual-edit alternative omits tag; assumes intended public visibility for scoped package.'),
('recap-off-actions','B',[4,5,3,5,4],False,'Correct three steps, distributable dry run and no recap. Omits configured footer and manual-edit path tag; scoped public-access assumption remains unqualified.')
])
