#!/usr/bin/env node
'use strict';

// Exercise an installed router against both full host catalogs, without model calls.
// Only a disposable fixture and a new report file are written.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const repo = path.resolve(__dirname, '..');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function run(args, env, input) {
  const result = spawnSync(process.execPath, args, {
    encoding: 'utf8', env, input, timeout: 120000, maxBuffer: 4 * 1024 * 1024,
  });
  if (result.error || result.status !== 0) {
    throw new Error(result.error?.message || result.stderr || `Process exited ${result.status}`);
  }
  return result.stdout.trim() ? JSON.parse(result.stdout) : null;
}

// Snapshot only the effective routing catalog; no installed source is writable.
function copyPreviewCatalog(home, host, skills, candidate) {
  if (!['claude', 'codex'].includes(host) || skills.some(s => !/^[a-z0-9][a-z0-9:_-]{0,127}$/.test(s.name))) {
    throw new Error('Invalid preview host or skill name');
  }
  const root = path.join(home, host === 'claude' ? '.claude' : '.agents', 'skills');
  if (fs.existsSync(root)) throw new Error('Preview catalog already exists');
  const snapshots = skills.map(skill => {
    const corpus = path.join(skill.directory, 'evals/scenarios.json');
    return { name: skill.name, document: fs.readFileSync(skill.skillMd),
      corpus: fs.existsSync(corpus) ? fs.readFileSync(corpus) : null };
  });
  fs.mkdirSync(root, { recursive: true });
  for (const item of snapshots.filter(s => s.name !== 'flow-lean')) {
    const dir = path.join(root, item.name);
    fs.mkdirSync(dir);
    fs.writeFileSync(path.join(dir, 'SKILL.md'), item.document);
    if (item.corpus) {
      fs.mkdirSync(path.join(dir, 'evals'));
      fs.writeFileSync(path.join(dir, 'evals/scenarios.json'), item.corpus);
    }
  }
  fs.cpSync(candidate, path.join(root, 'flow-lean'), { recursive: true });
  return { source_skills: skills.length,
    mirrored_skills: new Set([...skills.map(s => s.name), 'flow-lean']).size,
    source_fingerprint: sha(JSON.stringify(snapshots.map(s => [s.name, sha(s.document), s.corpus && sha(s.corpus)]).sort())) };
}

function main() {
  const [routerArg, outputArg, skillArg, previewArg] = process.argv.slice(2);
  if (!routerArg || !outputArg || process.argv.length > 6 || (previewArg && previewArg !== '--preview-personal')) {
    throw new Error('Usage: node scripts/check_routing.cjs ROUTER_ROOT NEW_REPORT_JSON [SKILL_DIRECTORY] [--preview-personal]');
  }
  const router = fs.realpathSync(routerArg);
  const output = path.resolve(outputArg);
  const source = fs.realpathSync(skillArg || path.join(repo, 'skills/flow-lean'));
  if (fs.existsSync(output)) throw new Error('Report already exists; use a new path');
  const corpus = JSON.parse(fs.readFileSync(path.join(source, 'evals/scenarios.json'), 'utf8'));
  if (corpus.skill !== 'flow-lean' || corpus.positive.length < 8 || corpus.negative.length < 2) {
    throw new Error('Expected flow-lean corpus with at least 8 positive and 2 negative scenarios');
  }
  const publicProbes = JSON.parse(fs.readFileSync(path.join(repo, 'evals/routing-probes.json'), 'utf8'));
  const development = JSON.parse(fs.readFileSync(path.join(repo, 'evals/candidates/v3.1-routing-holdout.json'), 'utf8'));
  const probes = [
    ...publicProbes.positive.map(prompt => ({ prompt, expected: true })),
    ...publicProbes.negative.map(prompt => ({ prompt, expected: false })),
    ...development.probes,
    { prompt: 'Vas-y', expected: false },
    { prompt: 'stop flow-lean', expected: false },
  ];
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'flow-lean-routing-'));
  try {
    fs.mkdirSync(path.join(fixture, '.git'));
    const canonical = path.join(fixture, '.agents/skills/flow-lean');
    fs.cpSync(source, canonical, { recursive: true });
    fs.mkdirSync(path.join(fixture, '.claude/skills'), { recursive: true });
    fs.symlinkSync(canonical, path.join(fixture, '.claude/skills/flow-lean'), 'junction');
    const report = {
      schema_version: 1, provider_calls: 0, node_version: process.version,
      scope: previewArg ? 'Real router, disposable effective personal catalog mirrors with candidate replacing Flow Lean; no live installation or native model session' : 'Real router processes, disposable dual-host projections, full user catalogs, isolated caches; no native model session',
      probe_status: 'Development regressions, not independent holdout',
      source_hashes: {}, router_hashes: {}, hosts: {},
    };
    for (const name of ['SKILL.md', 'evals/scenarios.json', 'scripts/rollback_reference.py', 'references/rollback.md'].filter(name => fs.existsSync(path.join(source, name)))) {
      const bytes = fs.readFileSync(path.join(source, name));
      if (!bytes.equals(fs.readFileSync(path.join(canonical, name)))) throw new Error('Fixture differs from source');
      if (fs.realpathSync(path.join(fixture, '.claude/skills/flow-lean', name)) !== fs.realpathSync(path.join(canonical, name))) throw new Error('Host resource projections differ');
      report.source_hashes[name] = sha(bytes);
    }
    for (const name of ['evals/routing-probes.json', 'evals/candidates/v3.1-routing-holdout.json', 'scripts/check_routing.cjs']) {
      report.source_hashes[name] = sha(fs.readFileSync(path.join(repo, name)));
    }
    for (const name of ['bm25-suggest.js', ...fs.readdirSync(path.join(router, 'routing')).filter(n => n.endsWith('.js')).map(n => `routing/${n}`)]) {
      report.router_hashes[name] = sha(fs.readFileSync(path.join(router, name)));
    }
    const catalogSource = path.join(fixture, 'catalog-source');
    fs.mkdirSync(path.join(catalogSource, '.git'), { recursive: true });
    for (const host of ['claude', 'codex']) {
      let home = os.homedir(), preview = null, expectedSkill = path.join(canonical, 'SKILL.md');
      if (previewArg) {
        const discovery = require(path.join(router, 'routing/discovery.js'));
        const live = discovery.discoverSkills(discovery.discoverRoots({ cwd: catalogSource, home, host }), { host });
        home = path.join(fixture, `home-${host}`);
        preview = copyPreviewCatalog(home, host, [...live.skills.values()], source);
        if (host === 'claude') expectedSkill = path.join(home, '.claude/skills/flow-lean/SKILL.md');
        if (!fs.readFileSync(expectedSkill).equals(fs.readFileSync(path.join(canonical, 'SKILL.md')))) {
          throw new Error('Personal preview differs from canonical candidate');
        }
      }
      const env = { ...process.env, SKILL_ROUTER_HOST: host, SKILL_ROUTER_HOME: home,
        SKILL_ROUTER_CWD: fixture, SKILL_ROUTER_DATA_DIR: path.join(fixture, `cache-${host}`), SKILL_ROUTER_LOG: '0' };
      for (const key of ['SKILL_ROUTER_EXTRA_ROOTS', 'SKILL_ROUTER_OVERLAY_ROOTS', 'BM25_SKILLS_ROOT', 'SKILL_ROUTER_REQUEST_FILE']) delete env[key];
      const build = run(['-e', `
        const fs = require('node:fs');
        const r = require(process.argv[1]).build();
        if (r.manifest.active_skills['flow-lean']?.skillMd !== fs.realpathSync(process.argv[2])) throw new Error('Candidate not selected (check host homonym precedence)');
        console.log(JSON.stringify({active_skills:r.manifest.coverage.active,
          source_fingerprint:r.manifest.source_fingerprint,eligible:r.metrics.eligible.includes('flow-lean'),
          global_gate_passed:r.metrics.globalGatePassed,global:r.metrics.final.global,threshold:r.thresholds['flow-lean']}));
      `, path.join(router, 'routing/build-index.js'), expectedSkill], env);
      const hostProbes = [...probes, { prompt: `${host === 'claude' ? '/' : '$'}flow-lean concise`, expected: false }];
      const results = hostProbes.map(probe => {
        const result = run([path.join(router, 'bm25-suggest.js')], env, JSON.stringify({ prompt: probe.prompt, cwd: fixture }));
        const hint = result?.hookSpecificOutput?.additionalContext || '';
        const selected = hint.includes(`${host === 'claude' ? '/' : '$'}flow-lean (`);
        return { ...probe, selected, pass: selected === probe.expected };
      });
      report.hosts[host] = { ...build, preview, results,
        pass: build.eligible && build.global_gate_passed && results.every(r => r.pass) };
    }
    report.pass = Object.values(report.hosts).every(host => host.pass);
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
    console.log(JSON.stringify({ pass: report.pass, provider_calls: 0,
      hosts: Object.fromEntries(Object.entries(report.hosts).map(([host, r]) => [host,
        { eligible: r.eligible, passed: r.results.filter(p => p.pass).length, total: r.results.length }])) }));
    return report.pass ? 0 : 1;
  } finally {
    fs.rmSync(fixture, { recursive: true, force: true });
  }
}

module.exports = { copyPreviewCatalog };
if (require.main === module) {
  try { process.exitCode = main(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
