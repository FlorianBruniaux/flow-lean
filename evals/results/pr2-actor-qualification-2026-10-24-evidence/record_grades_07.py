from grade_helpers import append
append([
('tradeoff-ssr-ssg','A',[2,5,4,4,4],True,'Clear SSG recommendation but promises ISR/on-demand revalidation without stale content. Time-based ISR can serve the stale page while regenerating; optional guarantee is false (official Next.js ISR guide).'),
('tradeoff-ssr-ssg','B',[4,5,4,4,5],False,'Clear SSG recommendation; ISR is conditional on platform support, and Astro has adapter-backed ISR. Does not equate plain Astro SSR to automatic ISR. Cheapest/no server load language remains broad and platform configuration is unspecified.'),
('actor-reversed-draft','A',[2,3,3,3,4],True,'Quoted you identifies recipient and author approval is retained, but answer asserts approval you have not granted and no obligation exists until then. Source states neither present approval state nor recipient agreement; it invents definite approval status and obligation.'),
('actor-reversed-draft','B',[1,2,3,3,3],True,'Calls recipient the approval trigger although quoted I is the draft author. Omits a clear action owner and adds an activated obligation; source approver is reversed.'),
('actor-third-party-fr','A',[4,5,4,4,5],False,'Alice acts and Karim approves. Outside her direct control is unnecessary interpretation; no role reversal or asserted approval state.'),
('actor-third-party-fr','B',[4,5,4,4,5],False,'Alice acts after Karim approval. Waiting phrase is conditional on approval not being obtained, not a definite assertion that approval is absent now; redundant status framing.'),
('actor-direct-assistant','A',[3,4,4,4,4],False,'Correct user action and assistant approver, but adds a current waiting state not supplied. I approve is read as the requested role description, not an approval grant in this context.'),
('actor-direct-assistant','B',[5,5,5,5,5],False,'Correct user action and assistant approver; explicitly does not grant approval or act now as requested.'),
('actor-separate-delivery','A',[5,5,5,5,5],False,'Preserves Nora action, Maya delivery and Leo approval in third person.'),
('actor-separate-delivery','B',[5,5,5,5,5],False,'Preserves Nora commitment, Maya recipient and Leo approval condition.'),
('actor-permission-not-promise','A',[5,5,4,4,5],False,'Explicitly maps user review ability and recipient exclusive approval authority; distinguishes ability from a promise. Slightly repetitive.'),
('actor-permission-not-promise','B',[2,2,4,4,4],True,'Roles start correct but no action happens until they approve invents an approval prerequisite for review; source grants review ability separately from approval authority.'),
('actor-ambiguous-approval','A',[2,3,4,4,4],True,'Correctly assigns correction to Carol and notes ambiguity, but replaces the named alternative Alice with an unstated female referent. Source already identifies Alice; invents missing context instead of preserving the supplied alternatives.'),
('actor-ambiguous-approval','B',[2,3,4,4,4],True,'Correct action owner and ambiguity verdict, but says the alternative is an unidentified third person, omitting explicitly named Alice and inventing an unidentified actor.')])
