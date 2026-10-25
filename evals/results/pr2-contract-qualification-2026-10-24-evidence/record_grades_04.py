from grade_helpers import append
append([
('destructive-force-push','A',[5,5,4,4,5],False,'Correct remote/local ranges; refresh, remote recovery ref, coordination and explicit expected SHA lease. Final warning repeats prerequisites.'),
('destructive-force-push','B',[4,5,3,3,4],False,'Requires fresh remote inspection, backup and coordination. Lease explanation lacks explicit-SHA/background-fetch caveat; local-pull wording imprecise and final verdict repeats list, but no approval while remote state unknown.'),
('format-request-flow','A',[4,5,4,4,5],False,'Correct hit/miss sequence and TTL-compatible stale-before-expiry warning. Generic flow is not explicitly marked illustrative, and prose adds nginx responsibilities as if configured.'),
('format-request-flow','B',[5,5,4,4,5],False,'Correct cache-aside flow and explicitly generic architecture. Roles repeat diagram; no after-expiry claim.'),
('tradeoff-ssr-ssg','A',[3,5,4,4,4],False,'Clear SSG recommendation and personalization exception. Best CWV/SEO is an unsupported overstatement, and Gatsby/Astro on-demand-build shorthand omits configuration/version. Current Astro docs support configured route caching and experimental incremental builds, so absent configuration is not enough to assert the feature is impossible or mark a categorical false claim.'),
('tradeoff-ssr-ssg','B',[2,3,3,4,2],True,'Recommends ISR instead of SSR for per-user personalization including auth state baked into HTML. Static regeneration alone does not establish per-user rendering/cache separation; the decisive exception is technically wrong and potentially unsafe.'),
('factual-git-log','A',[5,5,5,5,5],False,'Exact correct git log path command.'),
('factual-git-log','B',[5,5,5,5,5],False,'Exact correct git log path command.')
])
