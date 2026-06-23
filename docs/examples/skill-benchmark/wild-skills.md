# Wild run — skval over 75 installed skills

A real `skval` **structural** run over *every* skill installed locally — Anthropic's
official plugins, the Vercel plugin suite, and Superpowers — deterministic, no model
calls, fully reproducible offline:

```bash
uv run skval structural <skill-source>
```

Where the curated [leaderboard](README.md) hand-picks mostly-clean skills, this is the
**unfiltered population**. That makes it a **false-positive regression set**: these are
widely-used, well-built skills, so most flags *should* come back clean. Running it
surfaced real skval precision bugs — which we fixed and locked with tests.

## Distribution

| Band | Before precision fixes | After |
|------|-----------------------:|------:|
| **100 / A** (clean) | 21 | **34** |
| A (90–99, minor findings) | 47 | 58 |
| B (80–89) | 16 | 11 |
| C (70–79, Revise) | 5 | 2 |
| **F** (safety veto) | 7 | **4** |

The fixes moved **13 skills to a clean 100** and cleared **3 false safety vetoes** — without
weakening any real check (every genuine issue below still flags, and the unsafe fixture still
scores 0/F).

## Precision bugs this run exposed (fixed + regression-tested)

| skval was flagging | Reality | Fix |
|--------------------|---------|-----|
| `missing referenced path: jsonwebtoken` | a regex in YAML frontmatter (`['"](jsonwebtoken)`) parsed as a Markdown link | scan refs in the **body only**, skipping frontmatter + code |
| `0 / F unsafe` — `hook-development`, `writing-rules` | `rm -rf` / `mkfs` sat inside a hook that *blocks* them | skip dangerous tokens in a quoted / defensive context |
| `0 / F unsafe` — `command-development` | `dd if=/dev/zero of=/tmp/file` writes a regular file | only flag `dd … of=/dev/…` (a block device) |
| `unexpected key: version / user-invocable / tools` | valid, widely-used skill frontmatter | broaden the allow-list |

All four are pinned in [`tests/test_precision.py`](../../../tests/test_precision.py) so they
can't regress.

## Genuine findings that remain (real, after the fixes)

### Revise (C) — vendored duplicate `SKILL.md`
The Vercel skills ship a second `upstream/SKILL.md` beside their own, so skval can't tell
which governs (a `critical` check). Worst real-world score in the set:

| Score | Grade | Verdict | Skill | Finding |
|------:|-------|---------|-------|---------|
| 77 | C | Revise | `nextjs` | found 2 packaged SKILL.md files (expected 1) |
| 77 | C | Revise | `workflow` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `ai-sdk` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `chat-sdk` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `next-cache-components` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `next-forge` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `next-upgrade` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `react-best-practices` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `vercel-cli` | found 2 packaged SKILL.md files (expected 1) |
| 85 | B | Ship | `vercel-sandbox` | found 2 packaged SKILL.md files (expected 1) |

Full scorecard: [`raw/nextjs.md`](raw/nextjs.md).

### Size budget — SKILL.md too big
The original finding class (same as `docx`/`skill-creator` in the curated set); remedy is
progressive disclosure (move detail into `references/`).

| Score | Grade | Verdict | Skill | Finding |
|------:|-------|---------|-------|---------|
| 92 | A | Ship | `skill-development` | SKILL.md is 638 lines (> 500); consider splitting |
| 92 | A | Ship | `writing-skills` | SKILL.md is 656 lines (> 500); consider splitting |
| 96 | A | Ship | `benchmark-sandbox` | SKILL.md ~5405 tokens (> 5000); move detail to references/ |
| 96 | A | Ship | `command-development` | SKILL.md is 885 lines (> 500); consider splitting |
| 96 | A | Ship | `hook-development` | SKILL.md is 713 lines (> 500); consider splitting |
| 96 | A | Ship | `m5-onboard` | SKILL.md ~5939 tokens (> 5000); move detail to references/ |
| 96 | A | Ship | `mcp-integration` | SKILL.md is 555 lines (> 500); consider splitting |
| 96 | A | Ship | `plugin-settings` | SKILL.md is 545 lines (> 500); consider splitting |
| 96 | A | Ship | `skill-creator` | SKILL.md ~8246 tokens (> 5000); move detail to references/ |

### Non-standard frontmatter keys
Vercel skills carry proprietary keys (`chainTo`, `retrieval`, `validate`, `summary`) that
aren't part of the skill spec — a `minor` flag, so they still Ship at 88–96/A.

| Score | Grade | Verdict | Skill | Finding |
|------:|-------|---------|-------|---------|
| 88 | B | Ship | `ai-gateway` | unexpected key(s): chainTo, retrieval, validate |
| 88 | B | Ship | `shadcn` | unexpected key(s): retrieval, validate |
| 92 | A | Ship | `vercel-firewall` | unexpected key(s): retrieval |
| 92 | A | Ship | `vercel-storage` | unexpected key(s): chainTo, retrieval, validate |
| 96 | A | Ship | `auth` | unexpected key(s): chainTo, retrieval, validate |
| 96 | A | Ship | `bootstrap` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `deployments-cicd` | unexpected key(s): retrieval, validate |
| 96 | A | Ship | `env-vars` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `marketplace` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `microfrontends` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `routing-middleware` | unexpected key(s): chainTo, retrieval, validate |
| 96 | A | Ship | `runtime-cache` | unexpected key(s): chainTo, retrieval, validate |
| 96 | A | Ship | `turbopack` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `vercel-agent` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `vercel-connect` | unexpected key(s): chainTo, retrieval |
| 96 | A | Ship | `vercel-functions` | unexpected key(s): chainTo, retrieval, validate |
| 96 | A | Ship | `verification` | unexpected key(s): chainTo, retrieval, summary |

### Other
| Score | Grade | Verdict | Skill | Finding |
|------:|-------|---------|-------|---------|
| 88 | B | Ship | `example-command` | description contains '<' or '>' |

### Safety vetoes (4) — real `rm -rf ~/…`
`benchmark-agents`, `benchmark-e2e`, `benchmark-testing`, `vercel-plugin-eval` each run `rm -rf ~/dev/vercel-plugin-testing`
in their instructions — a recursive delete under `$HOME`. skval's least-surprise gate flags
it: a skill shouldn't quietly delete a home directory. Scoped or not, it's worth surfacing.

## Takeaways

- Over 75 real skills, skval lands **34 clean (100 / A)**; the rest
  split into a few honest classes — vendored duplicate `SKILL.md`, over-budget size,
  non-standard vendor keys, and 4 real `rm -rf ~/…`.
- The run **hardened skval itself**: four false-positive classes found and fixed. A benchmark
  over real, in-the-wild skills is as much a test of the *validator* as of the skills — which
  is exactly why this corpus is kept as a regression set.
