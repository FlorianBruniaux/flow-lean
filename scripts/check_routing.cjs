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

function main() {
  const [routerArg, outputArg, skillArg] = process.argv.slice(2);
  if (!routerArg || !outputArg || process.argv.length > 5) {
    throw new Error('Usage: node scripts/check_routing.cjs ROUTER_ROOT NEW_REPORT_JSON [SKILL_DIRECTORY]');
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
      scope: 'Real router processes, disposable dual-host projections, full user catalogs, isolated caches; no native model session',
      probe_status: 'Development regressions, not independent holdout',
      source_hashes: {}, router_hashes: {}, hosts: {},
    };
    for (const name of ['SKILL.md', 'evals/scenarios.json']) {
      const bytes = fs.readFileSync(path.join(source, name));
      if (!bytes.equals(fs.readFileSync(path.join(canonical, name)))) throw new Error('Fixture differs from source');
      report.source_hashes[name] = sha(bytes);
    }
    for (const name of ['evals/routing-probes.json', 'evals/candidates/v3.1-routing-holdout.json', 'scripts/check_routing.cjs']) {
      report.source_hashes[name] = sha(fs.readFileSync(path.join(repo, name)));
    }
    for (const name of ['bm25-suggest.js', ...fs.readdirSync(path.join(router, 'routing')).filter(n => n.endsWith('.js')).map(n => `routing/${n}`)]) {
      report.router_hashes[name] = sha(fs.readFileSync(path.join(router, name)));
    }
    for (const host of ['claude', 'codex']) {
      const env = { ...process.env, SKILL_ROUTER_HOST: host, SKILL_ROUTER_HOME: os.homedir(),
        SKILL_ROUTER_CWD: fixture, SKILL_ROUTER_DATA_DIR: path.join(fixture, `cache-${host}`), SKILL_ROUTER_LOG: '0' };
      for (const key of ['SKILL_ROUTER_EXTRA_ROOTS', 'SKILL_ROUTER_OVERLAY_ROOTS', 'BM25_SKILLS_ROOT', 'SKILL_ROUTER_REQUEST_FILE']) delete env[key];
      const build = run(['-e', `
        const fs = require('node:fs');
        const r = require(process.argv[1]).build();
        if (!r.manifest.source_files.includes(fs.realpathSync(process.argv[2]))) throw new Error('Candidate not discovered');
        console.log(JSON.stringify({active_skills:r.manifest.coverage.active,
          source_fingerprint:r.manifest.source_fingerprint,eligible:r.metrics.eligible.includes('flow-lean'),
          global_gate_passed:r.metrics.globalGatePassed,global:r.metrics.final.global,threshold:r.thresholds['flow-lean']}));
      `, path.join(router, 'routing/build-index.js'), path.join(canonical, 'SKILL.md')], env);
      const hostProbes = [...probes, { prompt: `${host === 'claude' ? '/' : '$'}flow-lean concise`, expected: false }];
      const results = hostProbes.map(probe => {
        const result = run([path.join(router, 'bm25-suggest.js')], env, JSON.stringify({ prompt: probe.prompt, cwd: fixture }));
        const hint = result?.hookSpecificOutput?.additionalContext || '';
        const selected = hint.includes(`${host === 'claude' ? '/' : '$'}flow-lean (`);
        return { ...probe, selected, pass: selected === probe.expected };
      });
      report.hosts[host] = { ...build, results,
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

try { process.exitCode = main(); }
catch (error) { console.error(error.message); process.exitCode = 1; }
