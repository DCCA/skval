# Paisagem competitiva — validação de Agent Skills (julho/2026)

> **Método:** pesquisa executada em 2026-07-30 por um workflow de 7 agentes (5 varreduras
> paralelas por ângulo + 2 verificadores adversariais), ~40 buscas e fetches na web.
> **Caveat de confiança:** vários sites-alvo (getskillcheck.com, skillsbench.ai, arxiv.org,
> glama.ai, entre outros) retornaram 403 no gateway do ambiente de pesquisa; a evidência
> desses casos vem de snippets de busca cruzados entre 2+ fontes independentes. Números
> pontuais (stars, preços, datas) têm confiança moderada — revalide antes de decisões de
> negócio. Os achados completos e os vereditos estão nos apêndices, na saída original dos
> agentes (inglês).

## TL;DR

A dor que o skval ataca — *"esta skill é boa o suficiente pra shippar?"* — é real, crescente
e **disputada**: o ecossistema saiu de zero (out/2025) para ~20 ferramentas, 6+ papers e 2
aquisições em nove meses. Dos 9 diferenciais que reivindicávamos, a verificação adversarial
**refutou 5 e rebaixou 3 para parciais**. O que sobrevive não é nenhuma técnica isolada — é a
**integração num veredito único e opinado** (score composto 0–100 + veto de safety +
Ship/Revise/Reject + gate de CI + custo pré-run), que nenhum concorrente cobre por inteiro.

## Sinais de mercado

- **Escala:** Agent Skills virou padrão aberto (agentskills.io, dez/2025), adotado por
  VS Code/GitHub, Cursor, Goose, Amp e OpenCode; `anthropics/skills` em ~165k stars
  (~+12k/mês) em jul/2026.
- **Dor de segurança comprovada:** skills maliciosas em produção (incidente ClawHub /
  ToxicSkills da Snyk); Anthropic construindo camada oficial de confiança (Directory
  Policy + partner network).
- **Dor de qualidade comprovada:** média de 57/100 nas skills públicas (SkillCheck);
  estudos acadêmicos confirmam a prevalência de "skill slop".
- **Consolidação:** promptfoo adquirido pela OpenAI (mar/2026); Humanloop absorvido pela
  Anthropic.

## Posicionamento — skval vs. os 5 mais próximos

| Produto | Natureza | O que cobre | O que falta vs. skval | Ameaça |
|---|---|---|---|---|
| **Anthropic skill-creator 2.0** | first-party, grátis | evals with/without, benchmark N× (média±σ), A/B cego, otimização de triggering | sem score composto, sem verdito, sem gate de safety, sem CI, sem custo pré-run | 🔴 define o default do ecossistema |
| **SkillTester** (skilltester.ai + arXiv) | serviço público + paper | utilidade vs. baseline sem skill; score de segurança separado não-compensatório | sem verdito integrado, sem roteamento por tipo, sem CI action | 🔴 nosso pitch central, publicado |
| **agent-skills-eval** / **skill-eval-harness** | OSS (644★ / v0.6.0) | baseline lift, significância pareada, custo por run, vendor-agnostic | sem dimensões estruturais/safety, sem score/verdito | 🔴 vence em cross-platform |
| **promptfoo** (OpenAI) | OSS + plataforma, 350k devs | guia dedicado de Agent Skills, asserts skill-used/not-used, A/B de versões | genérico — sem modelo de dimensões de skill, sem verdito | 🔴 distribuição |
| **SkillCheck** (getskillcheck.com) | freemium ($79 Pro) | 0–100 estático em 28 categorias, badge PASSED, diretório público, 2.568 skills escaneadas | **sem execução comportamental** (sem lift, sem pass^k) | 🟡 dono do flywheel comercial |

Complementos do mapa: ~8 linters estáticos (claudelint com 43 regras;
agent-ecosystem/skill-validator em Go com suporte a 25+ plataformas e dimensão de
*novelty*); camada de marketplace/segurança (Glama, Smithery+mcp-scan, Vercel skills.sh com
auditoria Snyk, cisco skill-scanner, MCPJam, Tessl Registry); e a onda acadêmica
(SkillsBench com 7.308 trajetórias e +16,2pp de lift médio; SkillSieve, SkillSafetyBench,
SkillCoach; contaminação de treino já publicada em agentskillreport.com).

## Vereditos adversariais sobre os diferenciais reivindicados

| Diferencial reivindicado | Veredito | Derrubado por |
|---|---|---|
| Lift comportamental vs. baseline sem skill | ❌ REFUTADO | skill-creator, SkillTester, agent-skills-eval, SkillsBench |
| Triggering (D5) como dimensão medida | ❌ REFUTADO | skill-creator mede **e otimiza** |
| pass^k para skills | ❌ REFUTADO | tau-bench (origem), Inspect AI, skill-eval-harness |
| CI Action que falha por verdito | ❌/🟡 | pulser eval, cisco skill-scanner, agent-ecosystem |
| Estudo de variância + contaminação publicado | ❌ REFUTADO | SkillsBench (escala ~1000×); agentskillreport.com |
| Open-source + self-validating | ❌ REFUTADO | norma da categoria |
| **Safety como VETO no verdito composto** | 🟡 PARCIAL | near-equivalents existem; semântica exata é nossa |
| **Roteamento por tipo (5 tipos → estratégia de eval)** | 🟡 PARCIAL | componentes existem separados; a tabela de roteamento é única |
| **Estimador de custo pré-run** | 🟡 PARCIAL | ninguém tem (ragas tem issue aberta pedindo); facilmente copiável |

**O diferencial que de fato sobrevive:** ser **a camada de veredito** — a única ferramenta
que integra as seis dimensões num score composto com veto de safety e decisão acionável
(Ship/Revise/Reject) plugada em CI, com custo previsto antes de gastar. Cada rival entrega
números; o skval entrega uma decisão.

## Maiores ameaças

1. **Absorção first-party:** skill-creator já faz eval + benchmark + otimização de
   triggering, grátis e sem fricção dentro do Claude Code.
2. **promptfoo sob a OpenAI:** distribuição massiva com suporte dedicado a Agent Skills.
3. **Comoditização acadêmica:** a "munição publicável" (lift, variância, contaminação) já
   foi publicada em escala maior por terceiros.
4. **Claude-only vs. spec cross-platform:** os rivais OSS são vendor-agnostic; o skval hoje
   não valida skills fora do mundo Claude.
5. **Crise de credibilidade do safety estático:** pesquisa da CSA (jun/2026) mostra
   scanners de skills sendo bypassados "across the board" — atinge o D6 de todo mundo,
   inclusive o nosso.

## Recomendações

1. **Reposicionar de "eval harness" para "camada de veredito".** Parar de competir em
   "medimos lift" (commodity) e competir em "transformamos medição em decisão de ship com
   veto de segurança" — integração + opinião codificada é o que ninguém replica por
   feature.
2. **Ir cross-platform.** Suportar o spec aberto (skills de Cursor/VS Code/Goose) e
   executores plugáveis. Elimina a maior fraqueza estrutural apontada pelos dois
   verificadores.
3. **Produtizar os dois pontos onde chegamos primeiro:** (a) `skval probe` — o
   baseline-probe de 1 trial que responde *"seu eval discrimina ou o modelo já sabe?"*
   (hoje é guidance em markdown; virar comando); (b) tratar o estimador de custo pré-run
   como bandeira de marketing enquanto for único.

---
## Apêndice — os 58 achados completos (saída dos agentes de varredura, em inglês)


### Ângulo A — Validadores diretos de skills (10 achados)

**Notas do agente:** Method: 8 web searches + 6 successful WebFetches (GitHub pages fetched fine; getskillcheck.com, validate.getskillcheck.com, claudelint.com, and alirezarezvani.github.io returned 403 through the agent proxy, and the scoped GitHub MCP only allows dcca/skval — those entries rely on search snippets plus GitHub-hosted mirrors, flagged per finding; nothing fabricated). Key landscape takeaways for skval: (1) The category has bifurcated into ~8 static linters/spec validators (SkillCheck, claudelint, agent-ecosystem, jorgealves, moutons, moonrunnerkc, emasoft) and only TWO behavioral-eval competitors — Anthropic's own skill-creator and darkrishabh/agent-skills-eval (644 stars). (2) No competitor found combines behavioral lift + composite 0-100 + Ship/Revise/Reject verdict + CI gate; skval features with no observed competitor equivalent anywhere: paired statistical significance on lift, pass^k reliability formalism, triggering precision/recall/F1 (skill-creator uses raw trigger pass rates; SkillCheck only does static 'trigger collision'), position-swapped A/B (skill-creator's comparator is blind but not documented as position-swapped), safety as a veto gate, type-routed eval generation incl. multi-turn user simulator, pre-run token/$ estimator, and the training-contamination baseline-probe guard — the variance study + contamination finding appears unique and is publishable ammunition. (3) Biggest strategic threat is skill-creator: free, first-party, already does with/without-skill baseline benchmarking with mean±std and an analyzer for flaky evals, and its triggering loop OPTIMIZES descriptions rather than just measuring — skval's cleanest positioning is 'the impartial scored gate/leaderboard for CI and marketplaces' vs skill-creator's 'authoring loop'. (4) Biggest commercial threat is SkillCheck ($79 one-time / $15 pass, 28 categories, PASSED badges ≥90 score, public report directory, claims 2,568 skills scanned across 22 repos) — it owns the badge/trust motion despite being static-only; skval could outflank it on substance (measured behavior vs pattern-matching) but currently lacks its distribution surfaces (badges, public reports, browser validator). (5) Name-collision hazard: two unrelated 'SkillCheck' products (olgasafonova vs moonrunnerkc) plus two 'claudelint's (pdugan20 active; stbenjam renamed skillsaw, unmaintained). (6) mcpmarket.com hosts at least 5 validator listings (skillcheck-for-claude, skillcheck-claude-skill-validator-1, skill-check, quality-checker-for-claude-skills, skill-validator-8) but these are catalog mirrors of the tools above, not independent products. (7) No evidence surfaced of a formal scored Anthropic plugin-marketplace review process; anthropics/claude-plugins-official distributes skill-creator itself, and third-party coverage (tessl.io 'Anthropic brings evals to skill-creator — why that's a big deal', thetoolnerd.com 'Skill Creator 2.0') confirms evals arriving officially is recent and high-attention — a window for skval to claim the independent-benchmark niche (its ~200-skill benchmark has no observed rival; nearest is SkillCheck's static corpus scan and agent-ecosystem's agent-skill-implementation platform research).


#### Anthropic skill-creator (official, Eval/Benchmark modes)
- **URL:** <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md>
- **Overlap com o skval:** high
- **O que faz:** Anthropic's first-party meta-skill (also shipped in anthropics/claude-plugins-official) for creating, editing, evaluating, and benchmarking skills. Its Eval/Benchmark modes are the closest official equivalent to skval: it generates 2-3 eval prompts from a user interview, runs with-skill vs no-skill (or old-vs-new version) in parallel, grades via a grader subagent, aggregates pass rate / tokens / timing with mean±std over N runs, runs an analyzer pass for flaky/non-discriminating assertions, offers an optional blind A/B comparator, and has a description-optimization loop that generates 20 should/should-not trigger queries, splits 60/40 train/test, and iteratively rewrites the description (3 runs per query).
- **Como mede:** Behavioral, prompt-orchestrated (not a deterministic engine): parallel with_skill vs without_skill subagent runs; assertion-based grading by an LLM grader (programmatic scripts encouraged where checkable); benchmark = N repeated runs reporting pass rate and mean±std tokens/duration plus with-vs-baseline delta; analyzer flags high-variance evals; blind A/B comparator (blind to labels but no documented position swap); trigger evals are pass/fail rates, not precision/recall/F1. No composite 0-100 score, no Ship/Revise/Reject verdict, no safety gate, no statistical significance testing, no cost estimator, no CI gate.
- **Licença/preço:** Free; open repo anthropics/skills (license not verified this pass); model cost is the user's own Claude usage.
- **Maturidade:** Official and actively developed; 'Skill Creator 2.0' evals/benchmarks update covered by third parties (tessl.io, thetoolnerd.com) as a notable ecosystem event; four composable subagents (executor, grader, comparator, analyzer).
- **Onde é melhor que o skval:** First-party distribution inside Claude Code (zero install friction), free, polished human-in-the-loop eval viewer HTML with feedback capture, and an automated description-optimization loop that improves triggering (skval only measures it). It defines the defaults most skill authors will meet first.
- **Evidência:** "With-skill run → skill path provided; Baseline run → no skill" \| "benchmark mode runs it N times... pass rate as mean and standard deviation (e.g., 85% ± 5%)"

#### agent-skills-eval (darkrishabh)
- **URL:** <https://github.com/darkrishabh/agent-skills-eval>
- **Overlap com o skval:** high
- **O que faz:** A standalone test runner for agentskills.io-style skills that answers skval's D2 question empirically: define evals in evals/evals.json (prompt, files, expected_output, assertions), run the same prompt with and without the skill in context, and see side-by-side whether the skill actually improves the model. Outputs JSON benchmark files, static HTML reports with pass rates, per-assertion judge reasoning, timing/token metrics, and JSONL event streams.
- **Como mede:** Behavioral with baseline: `--baseline` flag runs with_skill and without_skill; a judge model grades both outputs against the same assertions; auto-promotes expected_output to assertions when none given; supports deterministic tool-call assertions. CI via `--strict` mode + YAML config + JSON artifact diffing. No composite 0-100 score, no verdict, no triggering precision/recall, no structural/safety dimensions, no documented significance testing or pass^k formalism, no cost estimator.
- **Licença/preço:** MIT, free.
- **Maturidade:** 644 GitHub stars; active (contribution guidelines, security policy); the strongest independent OSS behavioral-eval competitor found.
- **Onde é melhor que o skval:** Vendor-agnostic via an OpenAI-compatible Provider interface (OpenAI, Together, Groq, Anthropic, local Llama), meaningful adoption (644 stars), and JSONL event streams for custom dashboards — skval is Claude-only.
- **Evidência:** "Write a SKILL.md, drop in some evals, and find out — empirically — whether your skill actually makes the model better." \| "output side by side for with_skill and without_skill"

#### SkillCheck (getskillcheck.com, Olga Safonova)
- **URL:** <https://www.getskillcheck.com/>
- **Overlap com o skval:** high
- **O que faz:** The most commercially productized direct competitor: validates Claude Code / Agent Skills (plus plugins and MCP servers) against the agentskills 1.x/2.x spec, outputs a 0-100 quality score with fix suggestions and a PASSED badge (score ≥90 and ≤2 warnings), publishes a public directory of validated-skill reports, and sells a Pro tier with 28 check categories. Free tier is a browser WASM validator plus the SkillCheck-Free repo; positions on privacy ('no skill content ever leaves your machine').
- **Como mede:** Predominantly static/deterministic pattern analysis across categories: structure, body, naming, semantic contradiction/ambiguity, design-pattern classification (Reviewer/Generator/Pipeline/Tool Wrapper), quality patterns, knowledge density, plugin manifest, 8 deterministic OWASP Agentic Top-10 security signals; Pro adds grader-based (LLM) OWASP evaluation, artifact contract validation, trigger collision detection, an 'eval kit', anti-slop detection, secrets/PII scanning, token budget analysis, WCAG checks, Agent Readiness scoring, and a CI/CD binary. No with/without-skill behavioral execution or lift measurement found; trigger analysis is collision/heuristic, not measured precision/recall.
- **Licença/preço:** Freemium: free browser/repo tier; Pro $79 one-time (no subscription/seats/API keys); $15 30-day Pro Pass; Pro delivered partly as an MCP server + CI/CD binary.
- **Maturidade:** Indie (Olga Safonova); SkillCheck-Free repo 36 stars; marketing via Substack ('I validated 100+ Claude Code Skills'); listed on skills.sh and mcpmarket. Note: getskillcheck.com and validate.getskillcheck.com were 403-blocked by our proxy; details come from the GitHub free-tier repo and search snippets, so Pro 'eval kit' internals are unverified.
- **Onde é melhor que o skval:** Go-to-market: badges + public report directory create a trust/distribution flywheel; claimed corpus scale (2,568 skills scanned across 22 repos); cross-platform positioning (Claude, Cursor, VS Code/Copilot); checks skval lacks (anti-slop, WCAG, secrets/PII, plugin/MCP manifests); in-browser privacy story.
- **Evidência:** "Pro version costing $79 unlocks all 28 categories" \| "validated 97 skills in detail from a corpus of 2,568 scanned across 22 community repositories" \| "Skills scoring 90+ with 2 or fewer warnings earn the PASSED badge"

#### skill-validator (agent-ecosystem)
- **URL:** <https://github.com/agent-ecosystem/skill-validator>
- **Overlap com o skval:** medium
- **O que faz:** Go single-binary validator of skill content against the Agent Skills spec with content-density/quality analytics and an optional LLM-as-judge scoring command. Checks directory layout, frontmatter, extraneous files, unclosed code fences, internal/external link resolution, token counts (o200k_base), imperative-sentence ratio, instruction specificity, and cross-language contamination. Ships pre-commit hooks for 13+ named agent platforms (claude, codex, copilot, cursor, gemini, goose, windsurf...).
- **Como mede:** Static analysis plus optional LLM-judge: `score evaluate` rates SKILL.md 1-5 on Clarity, Actionability, Token Efficiency, Scope Discipline, Directive Precision, Novelty (reference files on a parallel rubric), with a follow-up call to name novel details when novelty ≥3. Explicitly no behavioral execution and no baseline comparison. CI: GitHub Actions with PR-diff annotations and markdown summaries; brew/go install.
- **Licença/preço:** MIT, free.
- **Maturidade:** 210 stars / 30 forks; org also publishes agent-skill-implementation (empirical per-platform skill-loading research) and sits adjacent to the agentskills spec community.
- **Onde é melhor que o skval:** Breadth and ops ergonomics: 25+ platform support matrix, Homebrew/Go single binary, pre-commit hooks, PR annotations, token counting, and a 'novelty' dimension (does the skill add anything the model doesn't know?) that skval doesn't score.
- **Evidência:** "offers LLM-as-judge scoring to evaluate skill quality across dimensions like clarity, actionability, and novelty" \| "This is static analysis only — no behavioral evaluation"

#### skill-tester meta-skill (alirezarezvani/claude-skills)
- **URL:** <https://github.com/alirezarezvani/claude-skills/blob/main/engineering/skill-tester/SKILL.md>
- **Overlap com o skval:** medium
- **O que faz:** The QA gatekeeper meta-skill inside the 345-skill alirezarezvani/claude-skills mega-repo: validates, tests, and scores repo skills for BASIC / STANDARD / POWERFUL tier classification. Three capabilities: structure validation (directories, file formats, docs standards), script testing (Python syntax, imports, functionality, output format compliance), and quality scoring; used as both a quality gate and an author-guidance tool.
- **Como mede:** Prompt-driven: Claude applies the checklist when the skill is invoked — deterministic-style rules executed by an LLM, plus actual execution of bundled Python scripts. Tier classification rather than a calibrated 0-100 composite; no with/without-skill baseline lift, no triggering precision/recall, no standalone CI binary (repo-internal gating only).
- **Licença/preço:** Free within the claude-skills repo (repo license not verified this pass).
- **Maturidade:** v1.0.0, last updated 2026-02-16 per its marketplace page; direct SKILL.md fetch 404'd via proxy so details rest on search snippets + the repo's GitHub Pages catalog.
- **Onde é melhor que o skval:** Embedded in one of the largest multi-agent skill collections (345 skills targeting Claude Code, Codex, Gemini CLI, Cursor + 8 more), so it ships with a built-in audience; it also actually executes bundled scripts, which skval's D1 does not.
- **Evidência:** "comprehensive meta-skill designed to validate, test, and score the quality of skills... POWERFUL tier classification and version 1.0.0" \| "the gatekeeping system for skill quality"

#### skill-validation-skill (emasoft/claude-plugins-validation)
- **URL:** <https://lobehub.com/skills/emasoft-claude-plugins-validation-skill-validation-skill>
- **Overlap com o skval:** medium
- **O que faz:** A validation meta-skill performing comprehensive rule-based review of Claude Code skill directories using a consolidated ruleset drawn from AgentSkills OpenSpec, Nixtla Quality Standards, meta-skill validation pillars, and component validators.
- **Como mede:** 190+ static rules applied by the model when the skill is invoked (LLM-executed checklist, no deterministic engine); no behavioral with/without baseline, no reliability trials, no triggering metrics, no CI binary surfaced.
- **Licença/preço:** Free (open skill; license not verified).
- **Maturidade:** Distributed via lobehub skill catalog; adoption signals not found — appears niche.
- **Onde é melhor que o skval:** Largest advertised rule count in the category (190+ vs skval's D1 check set), aggregating multiple community specs into one checklist.
- **Evidência:** "performs comprehensive validation of Claude Code skill directories using a consolidated set of 190+ rules drawn from AgentSkills OpenSpec, Nixtla Quality Standards"

#### claudelint (pdugan20)
- **URL:** <https://github.com/pdugan20/claudelint>
- **Overlap com o skval:** medium
- **O que faz:** An eslint-style linter for the whole Claude Code project surface — CLAUDE.md (size limits, import syntax), skills (frontmatter + security), settings JSON schema, hook event names, MCP transport types, and plugins — with a dedicated Skills validator documented at claudelint.com listing 43 rules. Installable as npm CLI or as a Claude Code plugin; supports custom rules in .claudelint/rules/.
- **Como mede:** Purely static/deterministic lint: errors + warnings, `--strict` zero-tolerance mode, `check-all --fix` autofix. No scoring, no LLM judge, no behavioral evals, no baseline, no triggering measurement. CI usable via exit codes (GitHub Actions badge on repo; no packaged Action confirmed).
- **Licença/preço:** MIT; free; npm `claude-code-lint`.
- **Maturidade:** Early: ~10 stars, minimal fork activity, but polished docs site (claudelint.com — 403-blocked by our proxy; rule details from search snippets). A second, unrelated 'claudelint' by stbenjam was renamed skillsaw and is unmaintained.
- **Onde é melhor que o skval:** Covers the entire Claude Code config surface (CLAUDE.md, hooks, settings, MCP, plugins), not just skills, and offers autofix — a familiar linter DX skval doesn't have.
- **Evidência:** "The Skills validator checks Claude Code skill definitions for correctness, security, documentation quality, and best practices. This validator includes 43 rules."

#### skillcheck (moonrunnerkc) — name collision, distinct product
- **URL:** <https://github.com/moonrunnerkc/skillcheck>
- **Overlap com o skval:** medium
- **O que faz:** A cross-agent quality gate for SKILL.md files, unrelated to getskillcheck.com despite the identical name: validates frontmatter, scores description discoverability, verifies file references, enforces three-tier token budgets, and flags cross-platform compatibility issues.
- **Como mede:** Static/deterministic checks plus a heuristic discoverability score for the description (a lightweight cousin of skval's D5 triggering, without measured precision/recall); no behavioral execution, no LLM judge confirmed, no baseline.
- **Licença/preço:** Free OSS (license not verified).
- **Maturidade:** Small/early GitHub project; no notable adoption signals found.
- **Onde é melhor que o skval:** Explicit cross-agent compatibility checking (Claude Code, VS Code/Copilot, Codex, Cursor) and token-budget tiers as first-class gates.
- **Evidência:** "Validates frontmatter, scores description discoverability, checks file references, enforces three-tier token budgets, and flags compatibility issues"

#### skill-validator (jorgealves/agent_skills)
- **URL:** <https://claudemarketplaces.com/skills/jorgealves/agent_skills/skill-validator>
- **Overlap com o skval:** low
- **O que faz:** A lightweight skill that validates agent skill definitions against the agentskills.io spec and AGENTS.md rules — catches missing fields, malformed YAML, incomplete documentation — pitched for blocking non-compliant PRs in CI.
- **Como mede:** Contract/spec validation only, run locally with read access and no external calls; explicitly not a logic or behavior tester; no scoring, no LLM judge, no baseline, no triggering metrics.
- **Licença/preço:** Free (license not verified).
- **Maturidade:** Small; visibility mainly via claudemarketplaces.com and mcpmarket.com listings.
- **Onde é melhor que o skval:** One-line install (`npx -y skills add jorgealves/agent_skills --skill skill-validator`) and a zero-data-exfiltration posture that is easy to approve in locked-down repos.
- **Evidência:** "purely a contract validator, not a logic tester, so it won't tell you if your skill actually works, just whether it's properly structured"

#### skills-validator (moutons)
- **URL:** <https://github.com/moutons/skills-validator>
- **Overlap com o skval:** low
- **O que faz:** Validates agent skills against the Agent Skills specification, informed by how OpenCode and Claude Code actually implement skill loading.
- **Como mede:** Static spec-conformance checks only; no scoring, no LLM judge, no behavioral evals, no baseline; CI/adoption details not surfaced.
- **Licença/preço:** Free OSS (license not verified).
- **Maturidade:** Small/early; found only via GitHub search, no adoption signals.
- **Onde é melhor que o skval:** Grounds its rules in observed OpenCode + Claude Code loader behavior rather than the spec text alone.
- **Evidência:** "validates agent skills according to the Agent Skills specification, informed by the OpenCode and Claude Code implementations"

### Ângulo B — Frameworks gerais de eval de LLM (11 achados)

**Notas do agente:** DIRECT ANSWERS TO THE BRIEF. (1) Agent-Skills-specific support announced in 2026: YES, three actors. promptfoo has a dedicated 'Test Agent Skills' guide (site/docs/guides/test-agent-skills.md, verified from repo source) with skill-used/not-skill-used assertions, --repeat sampling, and skill-version A/B — and was acquired by OpenAI on 2026-03-09 (TechCrunch, CNBC, openai.com), remaining MIT. LangChain published an 'Evaluating Skills' blog post and shipped 'LangSmith CLI & Skills' + the langchain-ai/langsmith-skills repo (skills that help agents BUILD evals — the inverse of validating skills). And first-party: Anthropic's skill-creator got a ~March 2026 update adding eval writing, benchmark execution, and A/B testing (third-party reporting; corroborated by the current skill-creator skill description, which now advertises 'run evals to test a skill, benchmark skill performance with variance analysis,' and triggering-accuracy optimization). (2) What incumbents would need to add to eat skval's lunch — the still-unoccupied bundle: (a) skill-artifact ingestion + structural lint + static safety VETO over the SKILL.md/scripts themselves (nobody does this; promptfoo guide explicitly does not, verified); (b) with/without-skill baseline LIFT with paired significance — every adjacent tool compares version-vs-version or score-vs-threshold, none runs a no-skill control arm; (c) triggering precision/recall/F1 (promptfoo alone has the primitives); (d) type-routed eval generation + multi-turn user simulator (DeepEval's conversation simulator and LangSmith's multi-turn dataset types are partial analogs); (e) composite 0-100 + Ship/Revise/Reject verdict and a pre-run token/$ estimator (absent everywhere). Fastest credible threats, in order: promptfoo-under-OpenAI adding a baseline arm + artifact lint to its existing skills guide (distribution: 350k devs, >25% F500); Anthropic making skill-creator's built-in evals good enough that a third-party validator is redundant inside Claude Code (Humanloop team absorbed Sept 2025); Braintrust or LangSmith reframing existing baseline-regression CI machinery around skills. Methodology overlaps to cite in positioning: Inspect AI's epochs reducers are the exact pass^k analog of D3 (plus bootstrap stderr), and DeepEval's DAG judge parallels D4's decomposed binary rubric — skval's defensible claim is the integrated verdict pipeline, not any single metric. RESEARCH CAVEATS: proxy 403-blocked promptfoo.dev, blog.langchain.com, and zenvanriel.com; load-bearing content was instead verified via raw.githubusercontent.com (promptfoo guide + agent-skill integration doc, inspect_ai docs/metrics.qmd, LICENSE files for Phoenix=ELv2 and Inspect=MIT) and via multi-outlet news for the acquisition. Pricing figures come from search snippets (several from SEO-grade 2026 'review' sites — qaskills.sh, aitestingguide.com, aitoolsbakery.com) and should be treated as approximate; DeepEval/Confident AI entry pricing sources conflict ($9.99/user vs $19/mo). LangChain 'Evaluating Skills' post content could not be read (403), so its methodology is characterized from titles + LangSmith docs only. Key sources: promptfoo repo (test-agent-skills.md, agent-skill.md), techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/, openai.com/index/openai-to-acquire-promptfoo/, inspect.aisi.org.uk + UKGovernmentBEIS/inspect_ai docs/metrics.qmd, langfuse.com/blog/2025-06-04-open-sourcing-langfuse-product, wandb.ai Humanloop-sunset report, blog.langchain.com/evaluating-skills/ (title only), docs.langchain.com/langsmith/evaluation-types, confident-ai.com/frameworks/deepeval, braintrust.dev articles + cekura.ai pricing breakdown, github.com/Arize-ai/phoenix LICENSE.


#### promptfoo (OpenAI)
- **URL:** <https://www.promptfoo.dev/docs/guides/test-agent-skills/>
- **Overlap com o skval:** high
- **O que faz:** MIT open-source LLM eval + red-teaming CLI/library with declarative YAML evals, multi-provider matrices, and CI/CD gating (exit codes + GitHub Action). The ONLY adjacent framework with a dedicated 'Test Agent Skills' guide: it runs identical tasks across Claude Agent Skill versions with the model/files/permissions held constant, and it also ships its own promptfoo Agent Skill bundle so coding agents write evals correctly. Acquired by OpenAI on 2026-03-09; staying MIT and folding into 'OpenAI Frontier' for agentic security testing.
- **Como mede:** Layered assertions: `skill-used` / `not-skill-used` (a triggering precision/recall proxy — closest thing anywhere to skval D5), JS scorers for task quality (e.g. issue recall), LLM rubrics, cost/latency thresholds, weighted `max-score` composites, and `--repeat 3` to sample nondeterminism (crude D3). Verified against the guide's source: it only compares skill-version vs skill-version — NO with/without-skill baseline lift, no paired significance, no structural SKILL.md validation, no safety scan, no standardized 0-100 composite, no Ship/Reject verdict, no pre-run cost estimator; final call is left to human judgment.
- **Licença/preço:** MIT, core fully free (pay only your own model API costs); paid enterprise/cloud red-team tiers; OpenAI says it will keep serving existing customers post-acquisition.
- **Maturidade:** Very high: 23k+ stars, 350k devs / 130k MAU, >25% Fortune 500 (OpenAI announcement figures); acquisition covered by TechCrunch, CNBC, Forbes (Mar 2026).
- **Onde é melhor que o skval:** Distribution and trust skval can't match: ~23k GitHub stars, 350k developers, 130k monthly active, >25% of Fortune 500, now OpenAI-owned with a maintained CI ecosystem. Its red-team/security scanning is far deeper than skval's D6 static veto, and it tests across many model providers. To eat skval's lunch it 'only' needs to add: a no-skill control arm with significance, structural+safety dimensions over the skill artifact itself, and a composite verdict — all incremental for them.
- **Evidência:** Guide: "Does the agent use the skill when the task calls for it?"; "The better skill is the one that holds up across the tasks you care about, not the one that wins a single lucky run"; OpenAI: "Promptfoo will remain open source under the current license"

#### DeepEval / Confident AI
- **URL:** <https://github.com/confident-ai/deepeval>
- **Overlap com o skval:** medium
- **O que faz:** Most popular open-source (Apache-2.0) 'pytest for LLMs' eval framework (Python + TypeScript), with the Confident AI cloud on top. 50+ research-backed metrics spanning RAG, agents (tool correctness, task completion), chatbots, safety; G-Eval and DAG (decision-tree decomposed) LLM judges; a multi-turn conversation simulator; DeepTeam for red teaming. Cited in 2026 roundups as one of the three OSS eval standards (with promptfoo and Inspect).
- **Como mede:** Unit-test-style assertions with pass/fail thresholds run natively in pytest/CI (a de facto CI gate); LLM-judge rubrics including DAG — the closest analog to skval's D4 decomposed binary rubric; conversation simulation is a partial analog to skval's user-simulator for interactive skills. No skill-artifact ingestion, no triggering metrics, no with/without-skill lift, no repeat-trial pass^k framing, no composite 0-100 or Ship/Reject.
- **Licença/preço:** Apache-2.0 OSS free; Confident AI cloud has a free tier, paid entry ~$10–20/user/mo (2026 sources conflict: $9.99/user Starter vs $19/mo team plan).
- **Maturidade:** High for OSS: broadest metric coverage of any open-source eval tool per multiple 2026 comparisons; active v4.x releases.
- **Onde é melhor que o skval:** Breadth of validated metrics and a large community; simulator + DAG judge + pytest CI are the right building blocks — it would need a skill loader, a triggering harness, and baseline-lift statistics to compete directly. Nothing Agent-Skills-specific announced as of Jul 2026.
- **Evidência:** "50+ research-backed metrics covering RAG, agents, chatbots, single-turn, multi-turn, and safety use cases"; "DeepEval is the testing framework you run locally or in CI/CD, and Confident AI is where those evals go to live"

#### Braintrust
- **URL:** <https://www.braintrust.dev>
- **Overlap com o skval:** medium
- **O que faz:** Commercial eval-first platform: datasets, Experiments with baseline comparison and regression diffs, LLM-judge + sandboxed code scorers (open-source autoevals library), human review queues, prompt playground, Loop AI assistant, and a native GitHub Action that posts eval regressions on PRs. Positioned as 'best overall' in several 2026 eval-platform roundups.
- **Como mede:** Experiment-vs-baseline diffing (functionally closest to skval's A/B compare, though vs a prior experiment rather than a no-skill control), configurable trial counts for repeat runs, 0-1 scorers aggregated per experiment, CI gating via the GitHub Action. Dataset-first and model-agnostic. No skill/prompt-artifact concept, no triggering tests, no structural or safety dimensions, no significance testing surfaced as a verdict.
- **Licença/preço:** Proprietary SaaS (autoevals scorer lib is OSS); Free tier ~10k scores/mo, Pro $249/mo flat (no per-seat), Enterprise custom with hybrid/self-hosted deploy.
- **Maturidade:** High: a16z-backed, repeatedly ranked best-overall eval platform in 2026 comparisons; heavy content/SEO presence in the category.
- **Onde é melhor que o skval:** Enterprise polish, dataset management, human-in-the-loop review, marquee AI-native customers (Stripe, Notion, Airtable, Vercel cited in roundups), hybrid self-host. Would need skill ingestion + triggering + no-skill baseline semantics; its CI-regression machinery means the gap is product framing, not infrastructure. No Agent-Skills-specific support announced.
- **Evidência:** "native CI/CD integration with a GitHub Action for automated eval runs"; Pro is "$249/month flat" incl. "50,000 scores" and 30-day retention

#### LangSmith (LangChain)
- **URL:** <https://blog.langchain.com/evaluating-skills/>
- **Overlap com o skval:** medium
- **O que faz:** LangChain's eval + observability platform. In 2026 it moved explicitly onto skill territory: published an 'Evaluating Skills' blog post and shipped 'LangSmith CLI & Skills' plus the open langchain-ai/langsmith-skills repo — Agent Skills that teach coding agents to build datasets and evaluators from traces. Core product: offline dataset evals, LLM-as-judge, heuristic checks, annotation queues, online evals, trace→dataset conversion.
- **Como mede:** Four evaluator types (human, heuristic, LLM-judge, pairwise); pairwise comparison of prompt/model versions with relative-quality judging (analog of skval's A/B compare, though no position-swap discipline documented); repetitions parameter for repeat runs; regression detection vs a baseline experiment; multi-turn/trajectory dataset types for agent evals. No skill-artifact scoring, no triggering F1, no safety veto, no structural checks, no composite verdict.
- **Licença/preço:** Proprietary SaaS, per-trace usage pricing; free Developer tier (~5k traces/mo), Plus ~$39/seat/mo + usage; enterprise self-host. Costs 'grow quickly' for large teams per 2026 comparisons.
- **Maturidade:** High: de facto standard for LangChain shops; actively shipping eval features through 2026.
- **Onde é melhor que o skval:** Ecosystem gravity (LangChain/LangGraph installed base), production trace flywheel into eval datasets, 2026 AI helpers that summarize traces and surface failure modes. It is the vendor closest to skval in *narrative* (it literally wrote 'Evaluating Skills') but its skills work is about agents USING skills to write evals, not a validator that scores a skill artifact — it would need the whole D1/D5/D6 + lift/verdict layer.
- **Evidência:** "pairwise comparisons between model or prompt versions"; "LangSmith CLI and skills give AI coding agents expertise in tracing, debugging, datasets, and evaluation"; blog post 'Evaluating Skills' (fetch blocked, title/URL verified)

#### Inspect AI (UK AISI)
- **URL:** <https://inspect.aisi.org.uk/>
- **Overlap com o skval:** medium
- **O que faz:** UK AI Security Institute's MIT-licensed Python framework for reproducible LLM/agent evaluations: dataset → Task → Solver → Scorer primitives, multi-turn agent workflows with tools, sandboxed execution (Docker built-in, K8s/Proxmox adapters), VS Code log viewer, and 200+ prebuilt evals in inspect_evals. Government-backed and used for frontier-model safety evaluation.
- **Como mede:** The most statistically rigorous adjacent tool — verified in repo docs: epochs (repeated trials) with reducers including "Probability of at least 1 correct sample given k epochs" (pass@k) AND probability that all k attempts succeed — the exact mathematical analog of skval's D3 pass^k — plus accuracy, stderr, and bootstrap_stderr error bars, and model-graded scorers. But it's a benchmark-construction framework: no skill/prompt-artifact lifecycle, no CI ship-gate product, no triggering concept, no baseline-lift verdicts.
- **Licença/preço:** MIT (LICENSE verified), completely free; no commercial tier.
- **Maturidade:** High in research/safety circles: v0.3.2xx, 200+ prebuilt evals, cited as one of the three OSS eval standards in 2026.
- **Onde é melhor que o skval:** Statistical credibility and sandboxed agent environments stronger than skval's executor; neutral government provenance. It would eat skval's lunch only if someone builds a skill-validation harness ON it (plausible: it's MIT and composable) — methodology overlap is high, product overlap is low.
- **Evidência:** "Probability of at least 1 correct sample given k epochs"; "Probability that all k epoch attempts succeed"; "Standard deviation of a bootstrapped estimate" (docs/metrics.qmd, verified via repo)

#### Langfuse (ClickHouse)
- **URL:** <https://github.com/langfuse/langfuse>
- **Overlap com o skval:** medium
- **O que faz:** MIT open-source LLM engineering platform (YC W23; acquired by ClickHouse Jan 2026, MIT identity confirmed unchanged): tracing, versioned prompt management (the closest OSS thing to a prompt-artifact registry), datasets + experiments, managed LLM-as-a-judge (MIT since Jun 2025), and Code Evaluators (Python/TS eval functions in the UI, shipped May 2026).
- **Como mede:** Run versioned prompts against datasets with judge + code evaluators and compare experiment runs before deploying — a generic 'validate a prompt artifact before shipping' loop. No skill concept, no repeat-trial statistics, no triggering, no safety gate, no composite score/verdict; CI gating is DIY via SDK.
- **Licença/preço:** MIT core incl. evals (commercial license only for enterprise security features like SCIM/audit logs); Cloud free to 50k units/mo, paid tiers above; self-host free without limitation.
- **Maturidade:** High for OSS: most-deployed open-source LLM engineering platform; ClickHouse acquisition + $400M Series D context, Jan 2026.
- **Onde é melhor que o skval:** Fully free unlimited self-hosting and one of the largest OSS LLMOps communities; prompt versioning UX. Post-ClickHouse it has resources to move fast, but nothing Agent-Skills-specific announced; it would need skill ingestion, trial statistics, and verdict semantics.
- **Evidência:** "managed LLM-as-a-judge evaluations are now freely available to self-host under the MIT license"; ClickHouse "acquired Langfuse, and the MIT license and open-source identity were confirmed as unchanged" (Jan 2026)

#### W&B Weave (CoreWeave)
- **URL:** <https://wandb.ai/site/weave>
- **Overlap com o skval:** low
- **O que faz:** LLM eval/tracing layer on Weights & Biases (owned by CoreWeave): Evaluations with code + LLM scorers, side-by-side comparisons, leaderboards, playground, guardrails. Became the official migration target when Humanloop sunset after its Anthropic acquisition (Sept 2025).
- **Como mede:** Dataset-driven evals with scorers, comparison views, and leaderboards (a surface analog of skval's batch leaderboards). 2026 roundups characterize Weave as an add-on with limited depth vs eval-first rivals. No skill concept, triggering, safety gate, repeat-trial statistics, or verdicts.
- **Licença/preço:** SDK open-source; platform proprietary — free tier, then usage/seat pricing bundled with the W&B subscription (not decoupled for LLM workloads).
- **Maturidade:** Medium-high: large W&B user base, but consistently framed as secondary to eval-first platforms in 2026 comparisons.
- **Onde é melhor que o skval:** Experiment-tracking pedigree, enterprise ML installed base, and inherited Humanloop customers; would need essentially all of skval's skill-specific layer.
- **Evidência:** W&B: "Humanloop is sunsetting. Migrate to Weights & Biases as an alternative"; roundups: "Weave is an LLM add-on with limited depth; pricing is tied to the broader W&B subscription"

#### Arize Phoenix / Arize AX
- **URL:** <https://github.com/Arize-ai/phoenix>
- **Overlap com o skval:** low
- **O que faz:** Open-source (Elastic License 2.0 — LICENSE verified) LLM tracing + evaluation: OTel-native tracing, LLM-judge eval library, datasets/experiments, prompt playground; Arize AX is the commercial enterprise platform with online evals and monitoring.
- **Como mede:** Judge-based evals over traces and datasets, experiments comparing runs; fundamentally observability-first / post-hoc rather than pre-ship artifact validation. No skill or prompt-artifact lifecycle, no triggering, no safety veto, no pass^k, no verdicts.
- **Licença/preço:** Phoenix ELv2 (source-available, restricts commercial hosting), free to self-host; Arize AX free 25k spans/mo, paid from ~$50/mo, enterprise custom.
- **Maturidade:** High as OSS observability; eval capabilities are a supporting feature rather than the product core.
- **Onde é melhor que o skval:** Best-in-class open tracing and a real enterprise base via Arize; free self-host. Distant from skill validation; no Agent-Skills support announced.
- **Evidência:** LICENSE file verified as Elastic License 2.0; "Arize AX has a free tier with 25K spans/month, and the paid plan starts at $50/month"

#### Galileo
- **URL:** <https://galileo.ai>
- **Overlap com o skval:** low
- **O que faz:** Enterprise agent-reliability platform: proprietary Luna-2 small-language-model judges for cheap high-volume scoring, real-time guardrails, agent metrics (tool selection quality etc.), insights engine, plus offline experiments. Publishes its own 2026 agent-evaluation-platform roundups.
- **Como mede:** Fast low-cost model judges scoring traces in CI experiments and — its real focus — at runtime as guardrails. Production-protection orientation, not pre-ship artifact validation. No skill concept, no structural/safety-of-the-artifact scan, no baseline lift, no verdicts.
- **Licença/preço:** Proprietary; free tier (~5k traces), enterprise custom pricing.
- **Maturidade:** Established enterprise vendor, active in 2026 agent-eval discourse.
- **Onde é melhor que o skval:** Cost-efficient judging at scale (Luna-2) and enterprise compliance posture; would need an entire pre-ship skill-validation product to compete.
- **Evidência:** "Galileo is for teams that want packaged, real-time guardrails powered by fast, low-cost evaluation models"

#### OpenAI Evals (OSS repo + platform Evals API)
- **URL:** <https://github.com/openai/evals>
- **Overlap com o skval:** low
- **O que faz:** Registry-based open-source framework for reproducible benchmark-style evals (MIT, ~16k stars) — effectively in maintenance mode, with OpenAI's energy moved to the platform Evals API/dashboard and, since March 2026, to promptfoo as its acquired eval/security arm.
- **Como mede:** YAML registry evals with exact-match and model-graded scoring; benchmark orientation. No skill/prompt-artifact lifecycle, no CI gate product, no triggering or lift analysis.
- **Licença/preço:** MIT repo, free; platform Evals API billed as normal model usage.
- **Maturidade:** Large historical adoption, low current momentum.
- **Onde é melhor que o skval:** Brand only; the strategic threat transferred to promptfoo. Searches found no 2026 deprecation announcement, but also no meaningful new development of the OSS repo.
- **Evidência:** Described in 2026 roundups as a "registry-based framework for reproducible benchmark-style evals"; OpenAI acquired promptfoo (Mar 2026) to "strengthen agentic security testing and evaluation capabilities"

#### Humanloop (defunct — acquired by Anthropic)
- **URL:** <https://humanloop.com>
- **Overlap com o skval:** low
- **O que faz:** Was the archetypal 'validate a prompt artifact before shipping' platform: prompt/agent versioning, code + LLM + human evaluators, CI evals, observability. As part of its acquisition by Anthropic it shut the platform down on 2025-09-08; W&B ran the official migration campaign.
- **Como mede:** (Historical) versioned prompts evaluated against datasets with judge/code/human evaluators and CI regression checks — the closest pre-2026 product to skval's job, minus skill-specific dimensions.
- **Licença/preço:** N/A — enterprise SaaS, discontinued.
- **Maturidade:** Defunct since Sept 2025.
- **Onde é melhor que o skval:** N/A as a product. Its competitive relevance now: the team that built prompt-artifact eval tooling sits inside Anthropic — likely upstream of skill-creator's 2026 eval features, i.e. a first-party path that could make third-party skill validation redundant inside Claude Code.
- **Evidência:** "As part of its acquisition by Anthropic, Humanloop shut down its AI platform on September 8, 2025"; W&B: "Humanloop is sunsetting"

### Ângulo C — Ecossistema MCP / marketplaces / segurança (13 achados)

**Notas do agente:** METHOD: 11 web searches; all 7 attempted WebFetches (glama.ai, mcpskills.io, agentman.ai, vercel.com, modelcontextprotocol.io, agensi.io, skillgate.app) returned 403 — the agent gateway policy-denies CONNECT to these hosts (confirmed via proxy status; it also logged earlier denials for getskillcheck.com and claudelint.com). GitHub MCP tools are session-scoped to dcca/skval only, and gh CLI is absent. All evidence therefore comes from search snippets cross-corroborated across independent sources; marketplace self-descriptions (Skillgate, Agensi buyer's guides) are self-interested and should be re-verified before quoting publicly. Nothing was fabricated; secondhand figures are flagged inline.

ANGLE-C HEADLINE: Marketplaces overwhelmingly gate on STATIC SECURITY and rank by POPULARITY; almost nobody measures whether a skill actually works. The gates that exist: Vercel skills.sh (Snyk install-time audits + Claude-rated prompt-injection risk pre-publish), Anthropic community marketplace (automated validation + safety screening + Verified badge), Agensi (8-point security checklist), Smithery (0-100 static quality score drives ranking + mcp-scan), Glama (published multi-dim score + tiers, 'B and above is passing'), mcpskills.io (composite ≥7.0 Verified badge), NanoSkill.ai (hand review). The only behavioral-eval gate found for skills is Skillgate (sandbox + benchmark tasks + reliability review — early, unverified). On the MCP side, MCPJam is building premium behavioral evals (mock-agent simulation, tool-selection accuracy, CI regression). NOBODY marketplace-side measures effectiveness LIFT vs baseline, pass^k reliability with error bars, triggering precision/recall, or contamination — skval's D2/D3/D5 and the variance/contamination work have no marketplace-side competitor today.

AGENT SKILLS SPEC GOING CROSS-PLATFORM: Anthropic released the spec Dec 18, 2025 at agentskills.io. Within 48 hours Microsoft (VS Code/Copilot) and OpenAI (ChatGPT + Codex CLI) adopted it. By Mar 2026: 32 adopters incl. Google Gemini CLI, JetBrains Junie, Sourcegraph Amp, Block Goose, Snowflake, Databricks, ByteDance, Mistral, Spring AI. By Jun 2026: ~40 products incl. Cursor, OpenCode, Databricks Genie Code, Snowflake Cortex Code. Validation tooling that shipped alongside is ALL STATIC: official skills-ref reference library (+ Rust port skills-ref-rs) in the agentskills org, plus community linters (skill-lint, Swival/skillscheck with 8-agent compat testing, skillscan-lint, agent-ecosystem/skill-validator, getskillcheck.com, llmvlab.com). Spec discussion #282 shows reference-path validation still being designed. Cross-platform adoption strengthens skval's TAM (one skill format, ~40 runtimes) but also raises the bar: skval currently evaluates in a Claude-centric harness; skillscheck already markets cross-agent compat and MCPJam markets cross-LLM evals.

WHO IS POSITIONED TO MAKE VALIDATION A MARKETPLACE-SIDE FEATURE (ranked): 1) Vercel+Snyk — install-time enforcement on ~90K skills, an API, and measured detectors (90-100% recall, 0% FP claim); adding a quality/eval score to the leaderboard is one product decision away. 2) Anthropic — already gates its community marketplace and issues Verified badges; community demand for an official verified marketplace is on record (claude-code#30727). 3) Glama — the proven scored-listing model with published weights/tiers; porting its methodology from MCP servers to skills is trivial. 4) Smithery — score→ranking loop plus Invariant integration. 5) MCPJam — behavioral evals as a paid product, one artifact-class away from skills. 6) Snyk — mcp-scan-derived Agent Scan gives it the enterprise security seat for both ecosystems. Independent pressure point: a scan of Smithery's top 100 servers found 22 with security findings (mostly tool-description injection), and SkillsBench found the average public skill scores 6.2/12 with only top-quartile skills usable for research — both are quotable demand evidence for skval.

STRATEGIC IMPLICATIONS FOR SKVAL: (1) The moat is behavioral: lift-vs-baseline with paired significance, pass^k with error bars, triggering P/R/F1, contamination guard — no marketplace or scanner found does any of these; static D1/D6 territory is commoditizing fast (free linters, Snyk/Invariant on security). (2) Distribution risk: validation is consolidating INTO marketplaces at install/publish time; skval's GitHub Action CI gate is author-side — a partnership (skills.sh API, Glama, or Anthropic community marketplace screening) would convert skval from tool to infrastructure. (3) Benchmark credibility: cite SkillsBench (arXiv 2602.12670) — its +16.6pp average skill lift independently validates skval's D2 premise; adjacent academic threads to watch: SkillSafetyBench (arXiv 2605.12015), 'Skill Coverage: A Test Adequacy Metric for Agent Skills' (arXiv 2606.20659), 'Agent Skill Evaluation and Evolution' (arXiv 2606.11435). (4) Also-seen, not broken out: mcp-scorecard.ai (per-server trust scores), NanoSkill.ai (hand review), GuildSkills (cross-agent registry), mcpmarket.com and claudemarketplaces.com (directories: 23,400+ skills / 12,700+ MCP servers, daily GitHub refresh, no scoring gate found).


#### Skillgate
- **URL:** <https://skillgate.app/>
- **Overlap com o skval:** high
- **O que faz:** A 'security-first' agent-skills marketplace that vets every skill before listing: sandboxed execution, evaluation against benchmark tasks, and review for reliability, security, and observability. The only marketplace found that gates listings on behavioral evaluation, not just static scans.
- **Como mede:** Pre-listing pipeline: sandbox the skill, run it against benchmark tasks, review reliability/security/observability; automated scanning produces a per-skill security score shown as a trust signal before install.
- **Licença/preço:** Commercial marketplace; pricing not verified (claims come from Skillgate's own buyer's-guide blog — self-interested source).
- **Maturidade:** Early-stage (2026 entrant in 'best marketplaces' roundups); direct fetch blocked, details unverified firsthand.
- **Onde é melhor que o skval:** Vetting is fused with distribution — the gate sits at the point of discovery/install rather than in the author's CI; includes an observability review dimension skval lacks.
- **Evidência:** "every skill is sandboxed, evaluated against benchmark tasks, and reviewed for reliability, security, and observability before listing" — skillgate.app blog

#### SkillsBench (BenchFlow)
- **URL:** <https://www.skillsbench.ai/>
- **Overlap com o skval:** high
- **O que faz:** Academic benchmark (Stanford/CMU/Berkeley/Oxford/BenchFlow) for how well Agent Skills work: 87 tasks across 8 domains paired with curated skills and deterministic verifiers; measures pass-rate lift with-vs-without skills — the same core quantity as skval's D2. A companion analysis graded ~47,150 public skills on a 12-point quality rubric (avg 6.2/12).
- **Como mede:** Fixed task suite + deterministic verifiers; reports skill-induced pass-rate delta (33.9%→50.5% avg, +16.6pp; per-config +4.1 to +25.7pp); v1.1 ships 87 BenchFlow task.md packages; policy/implementation rubrics in repo.
- **Licença/preço:** Open academic project (github.com/benchflow-ai/skillsbench); arXiv paper 2602.12670.
- **Maturidade:** Published 2026, v1.1 shipped; it is a fixed benchmark for research, NOT a per-skill validator CLI — measures the ecosystem, not your skill. The 47,150-skill/12-point figure is secondhand (via agensi.io) and unconfirmed on skillsbench.ai.
- **Onde é melhor que o skval:** Peer-reviewed neutrality and citable numbers (arXiv 2602.12670); far larger corpus analysis (~47K skills vs skval's ~200); cross-domain deterministic verifiers.
- **Evidência:** "Curated Skills raise the average pass rate from 33.9% to 50.5% (+16.6 percentage points; 25.5% normalized gain)" — skillsbench.ai; "average quality score of just 6.2 out of 12" — agensi.io citing SkillsBench

#### MCPJam (Inspector + Evals)
- **URL:** <https://www.mcpjam.com/>
- **Overlap com o skval:** high
- **O que faz:** 'Postman for MCP' — open-source inspector plus a commercial evals platform that benchmarks MCP server performance behaviorally: a mock agent connects to your server and simulates how Claude Code/Cursor/ChatGPT would use it; positioned for CI/CD regression gating. The closest functional twin to skval's D2/D3/D5 loop, aimed at MCP servers instead of skills.
- **Como mede:** LLM playground across providers (OpenAI, Claude, Ollama); evals track tool-selection accuracy, token usage, run duration, and performance across multiple LLMs; CI/CD integration to catch regressions between versions.
- **Licença/preço:** Inspector is open source (200→1,000+ GitHub stars in two months); evals framework announced as a premium product.
- **Maturidade:** Active, venture-backed, enterprise launch 2026; evals framework still rolling out. Does not score Agent Skills — an obvious adjacent expansion for them.
- **Onde é melhor que o skval:** Cross-LLM eval matrix (skval is Claude-centric); tracks actual token/latency per run (skval only pre-estimates cost); hosted enterprise platform with funding (Open Core Ventures) and fast community traction.
- **Evidência:** "A mock agent is launched and connected to your MCP server, simulating how clients like Claude Code, Cursor, or ChatGPT would interact with it" — mcpjam.com/blog/mcp-evals

#### Glama MCP directory scoring
- **URL:** <https://glama.ai/mcp/methodology>
- **Overlap com o skval:** medium
- **O que faz:** MCP hosting/directory that automatically scores every listed MCP server with a public multi-dimensional quality score plus regular security/codebase scans — the proven model for marketplace-side scored listings. Scores rank and badge listings; they do not hard-block them.
- **Como mede:** Overall = Tool Definition Quality 70% + Server Coherence 30%. TDQ: each tool 1–5 on six dimensions (Purpose Clarity 25%, Usage Guidelines 20%, Behavioral Transparency 20%, Parameter Semantics 15%, Conciseness 10%, Contextual Completeness 10%); server TDQ = 60% mean + 40% minimum (one bad tool drags the score). Coherence: disambiguation, naming, tool count, completeness. Tiers A≥3.5…F<1.0; 'B and above is considered passing'. Plus recurring scans confirming the server works and has no obvious security issues.
- **Licença/preço:** Scoring free on listings; Glama monetizes hosting/gateway.
- **Maturidade:** Mature, large index, published methodology page. Targets MCP servers, not skills — but the methodology ports directly to skills and Glama is well-positioned to do so.
- **Onde é melhor que o skval:** Runs continuously and automatically over thousands of listings at zero cost to authors; score is attached to the discovery surface itself. Static/LLM-inspection only — no behavioral pass-rate or lift measurement.
- **Evidência:** "quality score combines two components: Tool Definition Quality (70%) and Server Coherence (30%)"; "B and above is considered passing" — glama.ai/mcp/methodology (via search snippet)

#### Agent Skills spec linter ecosystem (skills-ref, skillscheck, skill-lint, skillscan-lint, SkillCheck)
- **URL:** <https://github.com/agentskills/agentskills/tree/main/skills-ref>
- **Overlap com o skval:** medium
- **O que faz:** The validation tooling that shipped alongside the Agent Skills open spec: skills-ref is the official reference library (validate/parse SKILL.md, emit <available_skills> XML; Rust port skills-ref-rs); community tools add lint layers — skillscheck validates against the spec and tests compatibility with 8 agents (Claude Code, Codex, Copilot, Cursor, Gemini CLI, Roo, Swival, Windsurf); skillscan-lint catches weasel words, ambiguous instructions, missing metadata, skill-graph cycles/dangling refs; also skill-lint (himself65), agent-ecosystem/skill-validator (spec + content-density checks), getskillcheck.com and llmvlab.com free web validators.
- **Como mede:** Static conformance and content-quality lint only: frontmatter/structure checks, reference-path validation (spec discussion #282), broken links, contamination checks, per-agent compat matrix. No execution, no pass-rate, no judge, no triggering eval.
- **Licença/preço:** Open source (various); web validators free.
- **Maturidade:** Growing fast since the Dec 2025 spec; all stop at skval's D1 tier — none measure effectiveness, reliability, artifact quality, or triggering.
- **Onde é melhor que o skval:** Free, instant, zero-token CI checks; official-spec standing (skills-ref lives in the agentskills org); cross-agent compatibility testing skval doesn't do.
- **Evidência:** skillscheck: "validates skill directories against the agentskills.io specification and tests compatibility with every major AI coding agent" — github.com/Swival/skillscheck

#### Vercel skills.sh + Snyk audits
- **URL:** <https://vercel.com/changelog/automated-security-audits-now-available-for-skills-sh>
- **Overlap com o skval:** medium
- **O que faz:** The largest skills marketplace (launched Jan 20, 2026; ~89,753 skills; top skill hit 20K installs in 6 hours) with automated security auditing: Snyk's scanning API is triggered on install via `npx skills`, and a Claude model rates prompt-injection risk pre-publish with re-evaluation as detection improves. Quality ranking, however, is installs/leaderboard-based.
- **Como mede:** Security only: skills@1.4.0 displays audit results and risk levels before installation; Snyk CRITICAL-level detectors tuned on a confirmed-malicious corpus; discovery ranking = total installs + source reputation + GitHub stars.
- **Licença/preço:** Marketplace free; Snyk provides the commercial audit engine (also basis of Snyk Agent Scan).
- **Maturidade:** Production, API available, Snyk launch partnership — the strongest candidate to make validation a default marketplace-side feature for skills.
- **Onde é melhor que o skval:** Massive distribution and an install-time enforcement point authors can't skip; measured detector performance; continuous re-scanning. No effectiveness/reliability/quality scoring at all — popularity is the only quality proxy.
- **Evidência:** "CRITICAL-level detectors achieve 90-100% recall on confirmed malicious skills while maintaining a 0% false positive rate on the top 100 legitimate skills" — snyk.io/vercel

#### Smithery registry quality score (+ Invariant mcp-scan integration)
- **URL:** <https://smithery.ai/>
- **Overlap com o skval:** medium
- **O que faz:** Largest open MCP registry (6,000+ servers, open submission, no formal verification) that assigns each listing a 0–100 quality score which directly drives search ranking and featuring, and scans all servers for vulnerabilities via a partnership with Invariant's mcp-scan.
- **Como mede:** Five static dimensions — schema quality, reliability, docs, ecosystem, maintenance — scored to 0–100 with prioritized fixes; security = mcp-scan of tool/prompt/resource metadata (not a code audit). Independent scan found 22 of the top 100 Smithery servers had security findings, mostly tool-description injection.
- **Licença/preço:** Free registry; monetizes hosting/gateway/OAuth.
- **Maturidade:** Mature, widely used; MCP servers only, no skills scoring.
- **Onde é melhor que o skval:** Score→ranking incentive loop at registry scale; authors optimize toward it. Static metadata only; 'reliability' here is a docs/metadata proxy, not pass^k trials.
- **Evidência:** "ranks results by a quality score that directly determines where servers appear in search results" — medium.com/@francofuji; "all MCP servers on Smithery are now scanned for vulnerabilities" — invariantlabs.ai/blog/smithery-mcp-scan

#### mcp-scan (Invariant Labs) + Snyk Agent Scan
- **URL:** <https://invariantlabs.ai/blog/introducing-mcp-scan>
- **Overlap com o skval:** medium
- **O que faz:** The de facto standard MCP security scanner: detects tool poisoning, prompt injection, tool shadowing, cross-origin escalation, and rug pulls across Claude/Cursor/Windsurf configs. Two modes — passive one-time scan and active runtime proxy with guardrail enforcement; tool pinning hashes descriptions to catch post-install changes. Foundation of Snyk's enterprise Agent Scan; also validated academically (MCP-Scanner, ACM/IEEE 2026).
- **Como mede:** Multi-layered: keyword detection + semantic analysis + LLM evaluation of tool descriptions; hash-based tool pinning over time; runtime guardrails in proxy mode.
- **Licença/preço:** Open source (2,000+ GitHub stars); Snyk commercializes the enterprise tier.
- **Maturidade:** Most widely adopted MCP security scanner; embedded into Smithery marketplace-side.
- **Onde é melhor que o skval:** Covers skval's D6 territory far deeper for MCP: runtime enforcement and rug-pull detection, not just pre-ship static scan; enterprise channel via Snyk. Security-only — no quality/effectiveness dimensions.
- **Evidência:** "scans MCP server configurations for prompt injection, tool poisoning, tool shadowing, and cross-origin escalation attacks"; "foundation for Snyk's enterprise Agent Scan product"

#### Anthropic Claude Code plugin marketplaces (official + community)
- **URL:** <https://code.claude.com/docs/en/discover-plugins>
- **Overlap com o skval:** medium
- **O que faz:** Anthropic runs two first-party marketplaces: claude-plugins-official (~36 curated plugins, no public application; LSP, workflow, service integrations) and claude-plugins-community, where third-party submissions must pass automated validation and safety screening before listing; an 'Anthropic Verified' badge marks plugins with additional review. This is a real listing GATE, but static/safety-level — no scoring shown to users.
- **Como mede:** Automated validation + safety screening on submission; manual curation for official; verified badge for extra review. Docs explicitly caveat 'there are limits to what Anthropic is able to review' and tell users to inspect contents themselves.
- **Licença/preço:** Free, first-party.
- **Maturidade:** Live since Dec 2025; screening depth unpublished.
- **Onde é melhor que o skval:** Default trust position inside the product every Claude Code user already has; distribution is unbeatable. No published rubric, no numeric score, no behavioral eval — which is exactly the gap skval fills (and a GitHub issue, anthropics/claude-code#30727, requests an official verified marketplace for skills/MCP/agents).
- **Evidência:** "third-party plugins that have passed Anthropic's automated validation and safety screening"; "'Anthropic Verified' badge have undergone additional review"

#### Agensi
- **URL:** <https://www.agensi.io/>
- **Overlap com o skval:** medium
- **O que faz:** Curated paid skills marketplace (creators keep 80% of revenue) where every skill is security-scanned before listing against an 8-point checklist; also publishes the widely-cited 2026 marketplace comparison content.
- **Como mede:** 8-point pre-listing security gate: prompt injection, data exfiltration, secret detection, dangerous commands, obfuscation, external fetches, credential access, privilege escalation. No effectiveness or reliability evaluation described.
- **Licença/preço:** Commercial marketplace, 80/20 revenue split with creators.
- **Maturidade:** 2026 entrant; claims come from its own comparison content (self-interested), direct fetch blocked.
- **Onde é melhor que o skval:** Monetized distribution channel gives creators an incentive to pass the gate; checklist maps closely to skval's D6 categories but is the whole story rather than one dimension.
- **Evidência:** "every skill is security-scanned before listing... scanned against an 8-point checklist including prompt injection, data exfiltration, secret detection, dangerous commands"

#### MCP Skills (mcpskills.io) — 15-Signal Trust Method
- **URL:** <https://mcpskills.io/>
- **Overlap com o skval:** medium
- **O que faz:** 'Pre-install trust layer for MCP servers': turns public source, package, vulnerability, and supply-chain signals into composite score pages, gold 'Verified' badges maintainers can claim, monitoring, and API workflows teams gate on before a tool reaches an agent.
- **Como mede:** 15-signal composite with dimension floors; Verified requires composite ≥ 7.0, all dimension floors met, and no disqualifiers. Purely static/supply-chain metadata — no runtime or behavioral testing found.
- **Licença/preço:** Score pages public; monitoring/API suggest paid tiers (unverified).
- **Maturidade:** Live 2026; niche visibility.
- **Onde é melhor que o skval:** Consumes supply-chain/vuln feeds skval ignores; badge + monitoring + API productization of trust. No effectiveness/quality measurement; MCP servers only.
- **Evidência:** "Verified means the repo meets trust criteria (composite ≥ 7.0, dimension floors, no disqualifiers)" — mcpskills.io/methodology (via snippet; direct fetch 403)

#### SkillsMP
- **URL:** <https://skillsmp.com/>
- **Overlap com o skval:** low
- **O que faz:** Largest skill aggregator by catalog (351K → claimed 1.5M+ SKILL.md files indexed from public GitHub) serving Claude Code, Codex CLI, and ChatGPT. Ranks and filters listings but with zero editorial review — instant publish from any public repo, abuse handled post-hoc.
- **Como mede:** GitHub-proxy signals only: minimum 2 stars to appear; ranking by star count, commit recency, README quality. Explicitly does not certify safety or quality.
- **Licença/preço:** Free aggregator.
- **Maturidade:** Large, active, frequently covered; no gate, no score.
- **Onde é melhor que o skval:** Sheer index scale and cross-agent reach; nothing else. Its known weakness ('half-finished experiments alongside production-ready skills') is the demand signal for skval-style scoring.
- **Evidência:** "zero editorial review — instant publish via GitHub public repo (abuse handled post-hoc)"; "it needs a minimum of 2 stars on GitHub" — smartscope.blog / korben.info

#### MCP Inspector (Anthropic / MCP team)
- **URL:** <https://modelcontextprotocol.io/docs/tools/inspector>
- **Overlap com o skval:** low
- **O que faz:** Official interactive developer tool for testing and debugging MCP servers — a browser UI (npx @modelcontextprotocol/inspector) that connects as a client, lists tools/resources/prompts with schemas, lets you invoke tools manually, and shows raw JSON-RPC traffic.
- **Como mede:** It doesn't score anything: purely manual, interactive inspection ('Postman of the MCP world'); no verdicts, no metrics, no CI mode for quality.
- **Licença/preço:** Open source, free.
- **Maturidade:** Mature, canonical; complementary rather than competitive to skval.
- **Onde é melhor que o skval:** Official standing and ubiquitous DX for the debugging step that precedes evaluation; Snyk and others build workflows around it.
- **Evidência:** "official interactive developer tool for testing and debugging MCP servers" — modelcontextprotocol.io (via snippet)

### Ângulo D — Prior art metodológico (papers e benchmarks) (14 achados)

**Notas do agente:** ANGLE D adversarial verdicts on skval's five methodology claims (evidence from WebSearch snippets; ALL WebFetch attempts — skillsbench.ai, tessl.io, emergentmind, the-decoder, arxiv.org — were 403 policy-denied by the egress proxy, so quotes come from search-result excerpts and exact figures/dates/authors carry moderate confidence). (1) LIFT VS NO-SKILL BASELINE: pre-empted, the crowded finding of this research. SkillsBench (arXiv 2602.12670, ~Feb 2026) is the canonical paired with/without benchmark (+16.2pp, 7,308 trajectories, 95% bootstrap CIs, leakage-prevention authoring rules); arXiv 2605.31408 already publishes PAIRED significance (sign-flip permutation p, 10k-resample bootstrap over paired task differences); Anthropic's skill-creator 2.0 and adewale/skill-eval-harness productize with/without lift. skval should claim 'productized per-skill lift scoring', never 'novel lift methodology'. (2) PASS^K: pure tau-bench (arXiv 2406.12045, June 2024) inheritance, now in Anthropic model cards; no one found branding pass^k-for-skills before skval, so D3 is defensible as application only; skill-creator's multi-run variance benchmark delivers equivalent signal. (3) CONTAMINATION / RECALL-SATURATION: primacy is contestable. Deephaven (Medium, May 2026) published 'evals pass at or near 100% in both configurations, because the underlying model already knows... from training' plus the probe-the-baseline-first remedy; CTA (arXiv 2605.11946, May 28 2026) published academic saturation ('pass rate is already saturated and therefore cannot reflect those effects'); skill-creator's 'non-discriminating assertion' flag and skill-eval-harness's leakage lint are shipped baseline-probe-guard analogues (the latter targets eval-answer leakage, a distinct failure mode from training memorization — skval's clearest surviving nuance is naming TRAINING-data memorization of public skill content specifically, but the window for a primacy claim is closed unless skval's study verifiably predates May 2026). (4) JUDGE DEBIASING: not a differentiator anywhere — position-swap is MT-Bench 2023 default hygiene (and 2026 work like 'Judging the Judges', arXiv 2604.23178, shows swap-with-ties is a known compromise), decomposed binary rubrics are CheckEval (2403.18771, EMNLP 2025)/HealthBench/TICK standard practice with human-agreement validation skval lacks. Cite as lineage, drop as differentiator. (5) TRIGGERING P/R: measured before skval by skill-creator (explicit FP/FN description optimization, validated on Anthropic's own skills), Scott Spence (activation rates vs the real claude binary in Daytona sandboxes), community GitHub issues #32184/#36570 (literal 'precision/recall' vocabulary), and academically at far larger scale by arXiv 2604.04323 (selection from 34k skills with distractors; only 49%→31% of Claude runs load curated skills). skval's F1 formalization is incremental. METHODOLOGICAL THREATS TO SKVAL ITSELF: (a) issues #32184/#36570 report claude -p auto-triggering recall of 0% — if skval's D5 harness runs headless claude -p, it may measure a harness artifact; document the invocation path. (b) 2604.04323 implies lift measured with the skill pre-loaded (skval's D2) overstates production value. (c) CTA and SkillCoach show outcome-only pass-rate misses behavioral effects and 'accidental task success'. WHAT SURVIVES AS SKVAL DIFFERENTIATION: no single technique — the integration: one 0-100 composite with Ship/Revise/Reject verdict, safety as a VETO gate (adjacent prior art exists: 'Formal Analysis and Supply Chain Security for Agentic AI Skills' arXiv 2603.00195; attack papers SkillJect 2602.14211, POISE 2606.07943), type-routed eval generation incl. multi-turn user-simulator (no direct prior art found for type routing), pre-run token/$ estimator (none found elsewhere), and a GitHub Action failing on Reject (none found; nearest is generic CI eval patterns). Also note: an obaydata/claude-agent-skills-benchmark dataset exists on HuggingFace and SkillsBench 1.1 covers 87 tasks x 24 configs — dents the '~200 real skills benchmark' uniqueness pitch. Additional context sources: Anthropic 'Demystifying evals for AI agents' (anthropic.com/engineering), agensi.io SKILL.md eval guide, dev.to 'Skills Without Evals Are Just Markdown and Hope', pasqualepillitteri.it 'Claude Code Skills 2.0' (A/B testing coverage), thetoolnerd.com and tessl.io on skill-creator 2.0, the-decoder.com coverage of 2604.04323, mbrenndoerfer.com position-bias explainer, lechmazur/position_bias benchmark. Search count: 11 WebSearch queries; 7 WebFetch attempts all proxy-denied (per /root/.ccr policy, denials were not retried).


#### Anthropic skill-creator 2.0 (evals, benchmarks, triggering optimization)
- **URL:** <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md>
- **Overlap com o skval:** high
- **O que faz:** Anthropic's first-party skill for creating AND testing skills, updated ("2.0") to run evals, benchmark skill performance with variance analysis across multiple runs, A/B test variants, and optimize a skill's description for triggering accuracy. Ships inside Claude Code itself.
- **Como mede:** With/without-skill benchmark over multiple runs with variance analysis; an analyst pass flags assertions that always pass regardless of skill (non-discriminating — a baseline-probe guard in effect), flaky high-variance evals, and time/token tradeoffs; triggering optimizer scores description against sample prompts to reduce false positives and false negatives (i.e., precision/recall of firing). Anthropic reports improved triggering on 5 of 6 of its own document skills.
- **Licença/preço:** Free; open anthropics/skills repo (license not verified via fetch — proxy-blocked). Model-call costs only.
- **Maturidade:** Shipped and maintained by Anthropic; heavily covered (tessl.io, thetoolnerd.com, third-party guides) — de facto default tooling.
- **Onde é melhor que o skval:** First-party and zero-install: every Claude Code user already has it. Its non-discriminating-assertion check pre-empts skval's baseline-probe guard, and its FP/FN triggering optimizer pre-empts D5. Weakens skval claims on D2 lift, D3 variance, D5 triggering, and the contamination guard simultaneously. skval's remaining edge is the 0-100 composite score, safety veto, CI gate, and cost estimator.
- **Evidência:** "benchmark skill performance with variance analysis, and optimizing a skill's description for better triggering accuracy" \| "assertions that always pass regardless of skill (non-discriminating)" \| "reduce both false positives (firing when it shouldn't) and false negatives (not firing when it should)"

#### SkillsBench (arXiv 2602.12670 / skillsbench.ai)
- **URL:** <https://arxiv.org/abs/2602.12670>
- **Overlap com o skval:** high
- **O que faz:** Academic benchmark (Xiangyi Li + ~76 co-authors per search snippet) of 86-87 containerized tasks across 11 domains, each with human-authored instructions, oracle solutions, and deterministic verifiers, evaluated under three conditions: no Skills, curated Skills, self-generated Skills. v1.1 release: 87 tasks, 24 model-harness configs, 3 public trials per task.
- **Como mede:** Pass-rate lift vs no-skill baseline — the exact shape of skval's D2 — at far larger scale: +16.2pp average lift across 7,308 trajectories, 5 trials per task-model-condition in the paper, mean pass rates with 95% bootstrap CIs, plus explicit leakage-prevention authoring policies (skills must be procedural, not instance-specific).
- **Licença/preço:** arXiv preprint + public release on skillsbench.ai; free (exact code/data license unverified — fetch proxy-blocked).
- **Maturidade:** Active: paper (~Feb 2026), v1.1 release, HuggingFace paper page, follow-on studies citing it; widely covered in press.
- **Onde é melhor que o skval:** Scale and credibility: 7,308 trajectories, 24 model-harness configs, deterministic verifiers, cross-model evidence. Directly weakens any claim that skval invented with/without-skill lift measurement or that its ~200-skill benchmark is uniquely large. skval's edge: it scores YOUR arbitrary skill and emits a verdict; SkillsBench is a fixed task suite.
- **Evidência:** "curated Skills increase average agent pass rate by +16.2 percentage points across 7,308 trajectories" \| "strict authoring and leakage-prevention policies" \| "mean pass rates with 95% bootstrap confidence intervals"

#### adewale/skill-eval-harness
- **URL:** <https://github.com/adewale/skill-eval-harness>
- **Overlap com o skval:** high
- **O que faz:** OSS Python CLI whose entire purpose is measuring the causal lift of a single Agent Skill: runs identical case/model/repetition with and without the skill, validates experimental identity, and reports what changed — the closest open-source twin of skval's D2 pipeline.
- **Como mede:** Paired with/without comparison with tune/holdout/holdback split discipline, leakage lint (detects when the eval leaks its own answer), materialized ablations with provenance gates, per-model lift, and deterministic local grading with no model call in the grade path (mirroring skval's deterministic-tier philosophy).
- **Licença/preço:** Open source on GitHub; license and stars not verified (fetch proxy-blocked).
- **Maturidade:** Early-stage single-maintainer OSS; adoption unknown.
- **Onde é melhor que o skval:** Its holdout/holdback split discipline and eval-leakage lint are experimental-hygiene features skval does not advertise; "provenance gates" exceed skval's contamination guard on the eval-leakage axis (note: eval-answer leakage is a different failure mode than training-data memorization, so it complements rather than fully pre-empts skval's contamination finding).
- **Evidência:** "measures the causal lift of an Agent Skill" \| "paired with/without comparison, tune/holdout/holdback split discipline, leakage lint, materialized ablations with provenance gates, and per-model lift" \| "whether the eval leaked its own answer"

#### Controlled SkillsBench Study: Skill Availability and Presentation Granularity (arXiv 2605.31408)
- **URL:** <https://arxiv.org/abs/2605.31408>
- **Overlap com o skval:** high
- **O que faz:** Controlled experimental study on SkillsBench isolating the causal effect of skill availability and how skills are presented to the agent, using paired task-level contrasts.
- **Como mede:** 5 trials aggregated per task-condition-model cell over 30 tasks, then paired contrasts: mean paired task-level difference, 95% bootstrap CI over tasks (10,000 resamples), and a paired Monte Carlo sign-flip permutation p-value (100,000 samples).
- **Licença/preço:** arXiv preprint, open access.
- **Maturidade:** Preprint (~May 2026).
- **Onde é melhor que o skval:** This is published academic precedent for exactly skval's "paired significance" claim on skill lift — and with heavier statistical machinery (permutation tests) than skval documents. skval's D2 significance testing should be framed as adopting, not pioneering, this methodology. (Caveat: authorship unverified via fetch; if it turns out to share authors with skval's own variance study, it stops being independent prior art.)
- **Evidência:** "a 95% bootstrap confidence interval over tasks with 10,000 resamples, and a paired Monte Carlo sign-flip permutation p-value with 100,000 samples"

#### How Well Do Agentic Skills Work in the Wild (arXiv 2604.04323)
- **URL:** <https://arxiv.org/abs/2604.04323>
- **Overlap com o skval:** high
- **O que faz:** First large-scale study (UCSB/MIT CSAIL et al., ~Apr 2026; covered by the-decoder) of skill utility when agents must retrieve/select skills from a realistic 34k-skill repository with distractors, instead of being handed the right skill.
- **Como mede:** Pass rates vs no-skill baselines under progressively realistic retrieval settings; measures the selection stage explicitly: only 49% of Claude runs load all curated skills, dropping to 31% with distractors; weaker models score BELOW their no-skill baseline (e.g., Kimi K2.5 19.8% with skills vs 21.8% without).
- **Licença/preço:** arXiv preprint, open access.
- **Maturidade:** Preprint with significant press pickup (the-decoder, substack analyses, Medium).
- **Onde é melhor que o skval:** Pre-empts D5's core question (does the skill get selected when it should?) at 34k-skill scale with distractor sets — far beyond skval's triggering eval — and adversarially implies skval's D2 lift, measured with the skill pre-loaded, systematically overstates real-world value. A reviewer citing this paper can argue a "Ship" verdict says little about production behavior.
- **Evidência:** "performance gains degrade consistently as settings become more realistic, with pass rates approaching no-skill baselines" \| "only 49 percent of Claude runs load all curated skills... 31 percent when distractors are introduced"

#### Counterfactual Trace Auditing of LLM Agent Skills (arXiv 2605.11946)
- **URL:** <https://arxiv.org/abs/2605.11946>
- **Overlap com o skval:** medium
- **O que faz:** Framework (ASU/USC/Adobe Research, May 28 2026) that pairs each with-skill agent trace with a without-skill counterpart on the same task, aligns goal-directed phases, and emits Skill Influence Pattern annotations describing HOW the skill changed behavior, not just whether pass rate moved. Evaluated with Claude on 49 SWE tasks.
- **Como mede:** Trace-level counterfactual comparison; surfaces effects invisible to pass-rate lift: literal template copying, off-task artifacts, excess planning, task recovery — and shows high-baseline tasks carry most skill effects while their pass rate is saturated.
- **Licença/preço:** arXiv preprint, open access.
- **Maturidade:** Preprint; academic prototype, not a product.
- **Onde é melhor que o skval:** Two hits on skval: (1) independently publishes the saturation-of-recall-style finding in academic form (May 2026), contesting primacy of skval's contamination/saturation claim; (2) is a direct methodological critique of pass-rate-lift-only scoring — skval's D2 cannot detect the behavioral effects CTA measures.
- **Evidência:** "pairs each with-skill agent trace with a without-skill counterpart on the same task" \| "their pass rate is already saturated and therefore cannot reflect those effects"

#### Deephaven Data Labs — Skill evals for measurable agent self-improvement
- **URL:** <https://medium.com/@deephavendatalabs/skill-evals-for-measurable-agent-self-improvement-225f56479b0b>
- **Overlap com o skval:** medium
- **O que faz:** Practitioner write-up (May 2026) of building with/without-skill evals for a Deephaven coding skill, centered on the discovery that most evals saturate because the model already knows the public documentation from training.
- **Como mede:** Paired with/without-skill success-rate comparison plus secondary metrics (time, tokens, cost, turns); prescribes probing the no-skill baseline first and deleting skill content the model already handles.
- **Licença/preço:** Free blog post; internal harness not packaged as a product.
- **Maturidade:** Vendor engineering blog; methodology write-up, not a maintained tool.
- **Onde é melhor que o skval:** Directly weakens skval's claim to the "recall evals saturate / training contamination" finding: this is the same insight — public guidance memorized in training makes both arms pass — published May 2026 with the same remedy (probe the baseline first). Unless skval's variance study is verifiably earlier, the finding is at best concurrent, not original. Also adds a design consequence skval doesn't: strip memorized content from the skill itself.
- **Evidência:** "Most evals pass at or near 100% in both configurations, because the underlying model already knows enough Deephaven from training" \| "see what the agent gets right and what it gets wrong, because that's your baseline"

#### tau-bench pass^k (Sierra, arXiv 2406.12045) + reliability-science follow-ons
- **URL:** <https://arxiv.org/abs/2406.12045>
- **Overlap com o skval:** medium
- **O que faz:** The June 2024 benchmark that introduced pass^k — probability that ALL k i.i.d. trials succeed — as the standard agent-reliability metric, contrasting with pass@k. Follow-on work (e.g., "Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents", arXiv 2603.29231) generalizes it.
- **Como mede:** pass^k = p^k averaged across tasks over repeated i.i.d. trials; showed even SOTA agents collapse under repetition (gpt-4o pass^8 < 25% in retail). Now cited in Anthropic model cards.
- **Licença/preço:** MIT-licensed benchmark code (Sierra); open access paper.
- **Maturidade:** Mature, canonical; successor tau2-bench exists; industry-wide adoption.
- **Onde é melhor que o skval:** Canonical origin: skval's D3 is a straight application of a two-year-old industry-standard metric, so "pass^k over repeated trials" is not a differentiator — it's table stakes. No source found that brands pass^k specifically for skill validation, so skval's application is defensible as packaging, but SkillsBench's multi-trial + bootstrap-CI approach and skill-creator's variance benchmarking already deliver the same reliability signal for skills without the branding.
- **Evidência:** "pass^k measures 'all k attempts succeeded'" \| "terribly inconsistent (pass^8 < 25% in retail)" \| "Anthropic's model cards now discuss the pass^k reliability metric"

#### MT-Bench / Judging LLM-as-a-Judge (Zheng et al. 2023) — position-swap debiasing
- **URL:** <https://arxiv.org/abs/2306.05685>
- **Overlap com o skval:** medium
- **O que faz:** The paper that defined LLM-as-a-judge, documented position bias (judge prefers whichever answer is shown first), and established the standard mitigation: judge twice with orders swapped, inconsistent verdicts become ties. Wang et al. 2023 published swap-augmented calibration the same year.
- **Como mede:** Pairwise judging in both orders; consistency rate under swap; bias magnitude measured at 10-15pp in later replications; 2026 work ("Judging the Judges", arXiv 2604.23178; lechmazur/position_bias) now benchmarks the mitigations themselves.
- **Licença/preço:** Open access; MT-Bench code Apache-2.0.
- **Maturidade:** Canonical (NeurIPS 2023); thousands of citations; standard practice.
- **Onde é melhor que o skval:** Kills any framing of skval's A/B position-swap as a differentiator: it has been the default hygiene for pairwise LLM judging since mid-2023. Worse, 2026 literature notes swap-with-tie "does not improve the reliability of LLM judges" and doubles cost — so skval's comparator inherits a known-compromise technique, not an innovation.
- **Evidência:** "MT-bench alleviates position bias by judging twice with original and reverse order" \| "the verdict changes when the positions are swapped"

#### CheckEval / HealthBench / TICK — decomposed binary rubric judging
- **URL:** <https://arxiv.org/abs/2403.18771>
- **Overlap com o skval:** medium
- **O que faz:** Line of work establishing checklist-decomposed binary (yes/no) criteria as the reliable form of LLM-judge rubrics: CheckEval (2024, EMNLP 2025), WildBench and TICK (2024) generating per-instance checklists, HealthBench (OpenAI 2025) with 48,562 physician-authored binary criteria, RocketEval (2025).
- **Como mede:** Decomposes subjective quality into sets of binary questions scored independently, then aggregates; CheckEval reports inter-evaluator agreement improved by 0.45 and reduced score variance vs scalar ratings.
- **Licença/preço:** Open access papers; CheckEval code on GitHub (yukyunglee/CheckEval).
- **Maturidade:** Mature and peer-reviewed (EMNLP 2025); adopted by OpenAI (HealthBench).
- **Onde é melhor que o skval:** Establishes that skval's D4 "decomposed binary rubric" is standard practice with published validation (human-agreement studies at scale) that skval lacks. skval can cite this lineage as justification but cannot claim it as methodology novelty.
- **Evidência:** "decomposes high-level subjective criteria into structured sets of binary (yes/no) questions" \| "HealthBench... 48,562 physician-authored binary criteria" \| "improves the average agreement across evaluator models by 0.45"

#### Scott Spence — sandboxed skill-activation evals (+ Claude Code recall-0% issues)
- **URL:** <https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals>
- **Overlap com o skval:** medium
- **O que faz:** Blog series with a reproducible harness measuring whether Claude Code skills actually activate: runs claude -p inside isolated Daytona sandboxes against the real Claude Code binary with real skills/hooks, comparing intervention strategies. Companion community evidence: GitHub issues #32184/#36570 report auto-trigger recall of 0% in headless mode using literal precision/recall terminology.
- **Como mede:** Activation/trigger rate per prompt across repeated runs: Sonnet 4.5 baseline 55% activation without intervention, 100% with forced-eval and llm-eval hook strategies (Haiku 4.5: 84%/80%); GitHub issues measure "precision at 100%... recall persistently at 0%" for claude -p.
- **Licença/preço:** Free blog posts; harness code shared; GitHub issues public.
- **Maturidade:** Active practitioner series (multiple posts, updated across model releases); not a packaged product.
- **Onde é melhor que o skval:** Ecological validity: measures triggering against the real claude binary, not a simulated router. And it surfaces a direct threat to skval's D5: if headless claude -p never auto-triggers skills (per both issues), any D5 harness built on claude -p measures a harness artifact, not description quality — skval must document which invocation path its triggering evals use.
- **Evidência:** "the baseline without intervention jumped to 55% skill activation" \| issue #32184: "precision at 100% (no false positives) but recall persistently at 0%"

#### SkillCoach: Self-Evolving Rubrics for Agentic Skill-Use (arXiv 2607.01874)
- **URL:** <https://arxiv.org/abs/2607.01874>
- **Overlap com o skval:** medium
- **O que faz:** July 2026 framework that evaluates skill-USE as a trajectory-level meta-ability across four dimensions — skill selection, skill following, skill composition, skill-grounded reflection — using per-task rubrics evolved from real rollouts, kept separate from the outcome verifier.
- **Como mede:** LLM-graded process rubrics per trajectory dimension plus an independent outcome verifier, explicitly distinguishing process quality from accidental task success; rubric scores then drive training-data selection.
- **Licença/preço:** arXiv preprint, open access.
- **Maturidade:** Very recent preprint (July 2026); research framework.
- **Onde é melhor que o skval:** Shows multi-dimensional skill scoring is not unique to skval, includes a selection dimension overlapping D5, and its process/outcome separation catches "accidental task success" that inflates skval's outcome-only D2/D3. Weakens the "six dimensions" framing as a structural differentiator (though skval's specific dimensions differ).
- **Evidência:** "four dimensions: skill selection, skill following, skill composition, and skill-grounded reflection" \| "allowing process quality to be distinguished from accidental task success"

#### Skill Coverage: A Test Adequacy Metric for Agent Skills (arXiv 2606.20659)
- **URL:** <https://arxiv.org/abs/2606.20659>
- **Overlap com o skval:** low
- **O que faz:** June 2026 paper proposing a test-adequacy metric for agent skills — measuring whether an eval suite actually exercises the constraints a skill encodes, borrowed from software-testing coverage theory.
- **Como mede:** Coverage of skill constraints by the test suite, with failed-constraint labels as fine-grained diagnostic signals for improving skills.
- **Licença/preço:** arXiv preprint, open access.
- **Maturidade:** Recent preprint; academic metric, no tooling ecosystem yet.
- **Onde é melhor que o skval:** Attacks a gap skval shares with everyone: skval's type-routed eval generator has no adequacy measure, so a "Ship" verdict from a weak generated eval set is unfalsifiable. Prior art for the obvious next criticism of skval's generated evals.
- **Evidência:** "fine-grained signals for observing skill-use behavior" \| "actionable evidence for improving agent skill effectiveness through failed constraint labels"

#### MLflow — Testing and Refining Claude Code Skills
- **URL:** <https://mlflow.org/blog/evaluating-skills-mlflow/>
- **Overlap com o skval:** low
- **O que faz:** Official MLflow (Databricks ecosystem) blog showing how to build eval loops for Claude Code skills using MLflow's evaluation and tracing stack — evidence that major MLOps vendors are absorbing skill evals into general-purpose platforms.
- **Como mede:** Standard MLflow eval runs over skill-driven prompts with tracked metrics/traces across iterations of the skill (details from search snippets; page fetch proxy-blocked).
- **Licença/preço:** MLflow is Apache-2.0 OSS; managed on Databricks.
- **Maturidade:** Backed by the MLflow project; tutorial-level skill support today.
- **Onde é melhor que o skval:** Distribution and integration: teams already on MLflow/Databricks get skill evals inside existing experiment tracking, dashboards, and CI. Commoditization pressure on skval's harness value rather than a methodology pre-emption.
- **Evidência:** Title: "Testing and Refining Claude Code Skills with MLflow" (mlflow.org blog)

### Ângulo E — Sinais de mercado e demanda (10 achados)

**Notas do agente:** ANGLE E — market shape & demand signals (all web fetches were 403-blocked at the proxy gateway, so evidence is from search-snippet layer cross-corroborated across 2+ independent sources; anthropics/skills numbers are first-party via GitHub API today).

(1) ECOSYSTEM SIZE, mid-2026: Skills launched Oct 16, 2025; open standard (agentskills.io) Dec 18, 2025, adopted by Microsoft VS Code/GitHub, Cursor, Goose, Amp, OpenCode. anthropics/skills: 165,227 stars / 19,639 forks / 1,053 open issues as of 2026-07-30 (verified via GitHub API; was ~71k stars Feb 18, ~149k Jun 11 — still ~12k stars/30d). Registries went from 1 (Dec 2025) to ~8 major marketplaces by Q2 2026. Vercel skills.sh: ~669,670 skills and a 2.0M-install top skill five months after Jan 20, 2026 launch. SkillsMP claims 1.9–2.4M skills (inflated GitHub scrape). Best deduped estimate of distinct real skills: SkillsBench's 47,150 uniques (12,847 OSS repos + 28,412 Claude Code ecosystem + 5,891 corporate). Curated tier is tiny by comparison: Tessl registry ~2,000+ evaluated skills. Creator monetization exists but is cottage-scale: Agensi (70% rev share), Agent37 (80%), Gumroad private-repo sales, individual $10k anecdotes.

(2) QUALITY/SECURITY COMPLAINTS are loud and quantified: SkillsBench scored the 47,150-skill corpus at avg 6.2/12 ('Most Agent Skills Are Junk' is now a blog genre; HN threads 45607117/45619537 from launch, plus a DIY 'anti-slop skill' attempt, 45684305). Security: Snyk ToxicSkills (Feb 2026) — 36.82% of 3,984 skills flawed, 13.4% critical, 76 confirmed malicious, all malicious skills pairing code payloads with prompt injection; 3 lines of SKILL.md sufficed for SSH-key exfil. Incidents: Axios (Dec 2, 2025) researchers got a Claude Skill to deploy MedusaLocker ransomware; ClawHavoc (Feb 2026) 341–472+ poisoned ClawHub skills; malicious npm package exfiltrating Claude user dirs (May 2026); reversec 'Skill Issues' offensive research (May 2026); Microsoft advisory on Claude Code GitHub Action secret exposure (fixed in 2.1.128); anthropics/skills issue #492 (community skills under anthropic/ namespace = trust-boundary abuse). Demand for validation is no longer speculative — it has CVE-grade receipts.

(3) ANTHROPIC'S SIGNALS: real but deliberately narrow. It human-reviews its own Skills Directory ('initial and ongoing reviews' for safety/security/compatibility), ships enterprise admin allowlisting, and tells everyone else to 'use Skills only from trusted sources.' The Partner Network (Mar 12, 2026, $100M investment; Pearson VUE exams; 10,000+ certified consultants) certifies people and agencies, NOT skills. No published per-skill rubric, no grades, no lift measurement, no signals of a skill-certification product. Anthropic is absorbing trust at its own distribution boundary and externalizing the long tail.

(4) FUNDING/COMMERCIAL MOVES: Tessl ($125M raised, $500M+ valuation; Snyk's founder) pivoted into 'the package manager for agent skills' with quality + task evals + Snyk security scores — the strongest absorption datapoint. Snyk itself is setting the security-scanning standard via the Tessl partnership. BenchFlow ($1M seed) is commercializing SkillsBench-style eval infra. Vercel runs skills.sh as a free strategic registry with zero review. Indie scanners (SkillShield, SkillScan, NVIDIA SkillSpector) are multiplying.

VERDICT — category or feature? Skill validation is bifurcating, and each half has a different absorber. The SECURITY half is already commoditizing into a registry feature: Snyk scans inside Tessl, SkillShield-style badges, platform review at Anthropic's directory — a standalone security-only skill scanner has ~12 months before it's table stakes. The EFFECTIVENESS half (does this skill measurably lift agent performance?) is still unclaimed commercially: academia (SkillsBench, SkillTester) has validated the methodology skval uses — paired no-skill baselines, deterministic pass rates — but nobody ships it as an author-facing product; Tessl's 'task evaluations' are the only commercial instance and are opaque/registry-side. Net: validation becomes a FEATURE of registries post-publish (Tessl model wins that slot), while the pre-publish, author-side slot — CI gates, graded scorecards, statistical rigor (paired significance, pass^k, variance, contamination probes), registry-neutral — is the defensible position for skval as of Jul 2026. Risks to that position: SkillTester is a near-methodological-twin one hosting decision away from productizing; Tessl could expose its evals as a CLI; and if Anthropic ever adds a 'verified skill' badge with published criteria, it instantly owns the standard and third parties compete on depth. Recommended posture: position skval as the neutral, open-rubric CI gate ('the pytest of skills') rather than a directory/marketplace — the directory war is already lost to funded players, but none of them run where skills are authored.


#### SkillTester (skilltester.ai)
- **URL:** <https://skilltester.ai>
- **Overlap com o skval:** high
- **O que faz:** Hosted QA harness (arXiv 2603.28815, Peking Univ + Northwestern Polytechnical) that evaluates an individual agent skill's utility AND security — the closest methodological twin to skval, deployed as a public web service.
- **Como mede:** Paired execution: matched no-skill baseline vs with-skill runs, normalized into a utility score (comparative lift, not absolute performance); an invocation gate prevents ambient model capability being misattributed to the skill; separate dynamic security probe suite yields a security score plus a three-level security status label.
- **Licença/preço:** Public research deployment; pricing not published; paper on arXiv (Mar 2026)
- **Maturidade:** Research prototype with live public service, 2026; academic team, no known funding
- **Onde é melhor que o skval:** Zero-setup hosted service; dynamic security probing (skval's D6 is static-only). skval is broader: 6-dim composite incl. pass^k reliability, triggering P/R/F1, LLM-judge artifact rubric, cost estimator, CI gate, A/B compare.
- **Evidência:** "evaluate utility comparatively rather than absolutely, using matched no-skill execution as the reference condition for judging skill-contributed value"

#### SkillsBench / BenchFlow
- **URL:** <https://www.skillsbench.ai/>
- **Overlap com o skval:** high
- **O que faz:** First large benchmark of whether skills actually improve agents (arXiv 2602.12670; Stanford/CMU/Berkeley/Oxford/BenchFlow, 77 authors). Also quality-scored a deduped corpus of 47,150 public skills (avg 6.2/12) — the ecosystem's canonical 'most skills are junk' number. Open-source (benchflow-ai/skillsbench), HF dataset, Kaggle 'Agent Skill Lift' competition.
- **Como mede:** 87 tasks / 8 domains with deterministic binary verifiers; three conditions per task (no skills, curated skills, self-generated skills) across Claude Code, Gemini CLI, Codex CLI; primary metric is pass-rate delta vs no-skill baseline — same lift philosophy as skval D2. Corpus scoring uses a 0-12 rubric plus structural/AI-detection/leakage audits.
- **Licença/preço:** Benchmark open source; BenchFlow (SF, founded 2024) is commercial — $1M seed, sells sandboxed eval runtime
- **Maturidade:** Active: paper Feb 2026, v1.1 shipped, Kaggle competition live
- **Onde é melhor que o skval:** Multi-institution credibility and cross-agent coverage (Gemini/Codex, not just Claude); public dataset. But it benchmarks the ecosystem — it is not a per-skill pre-ship validator with verdicts, safety veto, triggering eval, or CI integration.
- **Evidência:** "Curated Skills raise the average pass rate from 33.9% to 50.5% (+16.6 percentage points; 25.5% normalized gain)"

#### Tessl Skills Registry (+ Snyk security scores)
- **URL:** <https://tessl.io/registry>
- **Overlap com o skval:** high
- **O que faz:** Commercial 'package manager for agent skills' (pivoted to skills Jan 29, 2026) — versioned registry of 2,000+ evaluated skills with quality scores, impact ratings, and per-skill Snyk security scores shown before install; org-level skill lifecycle management. Founded by Guy Podjarny (Snyk founder); the clearest case of validation being absorbed as a registry feature.
- **Como mede:** Every published skill passes automated review: "review evaluations" (structure/best-practice checks ≈ skval D1) and "task evaluations" (real-world performance testing ≈ skval D2), plus a Snyk security scan score displayed alongside quality scores in the registry UI.
- **Licença/preço:** Commercial SaaS; registry free to browse; Snyk partnership announced 2026
- **Maturidade:** Funded commercial product; skills registry launched Jan 29, 2026; security scores added via Snyk partnership
- **Onde é melhor que o skval:** Distribution + validation in one funded product ($125M at $500M+ valuation: Index, GV, Accel, Boldstart) with enterprise lifecycle features; methodology is proprietary/undisclosed vs skval's open rubric, and no published lift-with-significance, pass^k, or triggering metrics.
- **Evidência:** "run through both review evaluations (structure and best-practice checks) and task evaluations (real-world performance testing)"

#### Snyk ToxicSkills
- **URL:** <https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/>
- **Overlap com o skval:** medium
- **O que faz:** First comprehensive security audit of the skills ecosystem (Feb 5, 2026): scanned 3,984 skills from ClawHub and skills.sh; found 36.82% (1,467) with ≥1 security flaw, 76 confirmed malicious payloads, and 100% of malicious skills combining code payloads with prompt injection. The scanning tech now powers Tessl registry security scores — security validation commoditizing fast.
- **Como mede:** Static + payload analysis of SKILL.md instruction layer and bundled code: prompt-injection detection, malware/exfil patterns, hardcoded secrets, insecure credential handling; severity-tiered (critical/high/etc.). Overlaps only skval's D6 static safety gate, but at industrial depth.
- **Licença/preço:** Snyk commercial security platform; research public
- **Maturidade:** Production security vendor; embedded in Tessl registry via partnership
- **Onde é melhor que o skval:** Far deeper security research corpus and vendor-grade detection; demonstrated 3-line SKILL.md SSH-key exfiltration. No quality, effectiveness, reliability, or triggering measurement at all.
- **Evidência:** "13.4% of all skills (534 total) contain at least one critical-level security issue"

#### SkillShield
- **URL:** <https://skillshield.dev/>
- **Overlap com o skval:** medium
- **O que faz:** Security-scored skill directory with mandatory pre-scan of SKILL.md repos — positions as 'the only skill marketplace with mandatory security scanning'; 33,000+ skills scanned claiming a 12% malware detection rate; badges + trust scores. Part of a crowded scanner wave (SkillScan.dev, NVIDIA SkillSpector, Sentry skill-scanner).
- **Como mede:** 4-layer analysis — manifest checks, static code analysis, dependency scan, LLM behavioral checks — plus sandboxed execution observing runtime/network behavior; outputs a 0-100 trust score and security badges. Security-plus-structure only; no effectiveness or triggering evaluation.
- **Licença/preço:** Free browsing and OSS submissions; premium plans for commercial/high-volume priority scanning
- **Maturidade:** Indie/early-stage; Product Hunt + BetaList launches, 2026
- **Onde é melhor que o skval:** Sandbox dynamic analysis and a consumer-facing scored directory; skval's statistical effectiveness/reliability/triggering dimensions have no equivalent here.
- **Evidência:** "Security-scored directory for AI agent skills and MCP servers. 33,000+ scanned, 12% malware detection." (GitHub repo description)

#### Anthropic official trust layer (Skills Directory + Directory Policy + Partner Network)
- **URL:** <https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy>
- **Overlap com o skval:** medium
- **O que faz:** Anthropic's own validation signals mid-2026: a curated Skills Directory (claude.com/connectors) with partner-built skills (Atlassian, Canva, Figma, Notion, Cloudflare, Stripe, Zapier, Vercel); a Software Directory Policy of human review; enterprise admin provisioning/allowlisting; Agent Skills open standard (agentskills.io, Dec 18, 2025, adopted by Microsoft VS Code/GitHub, Cursor, Goose, Amp, OpenCode); Claude Partner Network (Mar 12, 2026, $100M ecosystem investment) — which certifies PEOPLE/orgs (10,000+ consultants), not skills.
- **Como mede:** Pass/fail curation, not scoring: "initial and ongoing reviews" for safety, security, and compatibility on its own directory only; docs otherwise tell users to "use Skills only from trusted sources." No published per-skill rubric, no quality grades, no lift measurement; the entire GitHub/skills.sh/ClawHub long tail is outside its review boundary (see anthropics/skills issue #492 on anthropic/-namespace trust-boundary abuse).
- **Licença/preço:** Directory free; Partner Network free to join; certifications via Pearson VUE
- **Maturidade:** Production: directory + admin controls shipped Dec 18, 2025; Services Track/Partner Hub Jun 3, 2026
- **Onde é melhor que o skval:** Owns the distribution choke point and enterprise admin surface; but validation is binary, manual, opaque, and limited to its own directory — leaving graded, evidence-based validation open for third parties.
- **Evidência:** "Anthropic conducts both initial and ongoing reviews of Software, and may require developers to address compliance issues"

#### Vercel skills.sh
- **URL:** <https://skills.sh/>
- **Overlap com o skval:** low
- **O que faz:** The distribution incumbent: open agent-skills registry launched Jan 20, 2026, GA Jun 5, 2026; ~669,670 skills listed with the top skill at 2.0M installs within five months; one-command install (npx skills add) into 20+ agents (Claude Code, Cursor, Copilot, Codex, Gemini, Zed).
- **Como mede:** It deliberately doesn't: leaderboard ranks purely by install telemetry with no submission or review flow — popularity as the only quality proxy. Its skills were part of the corpus where Snyk found 36.82% flawed. Overlaps skval only in the 'leaderboard' concept (installs vs quality scores).
- **Licença/preço:** Free, OSS registry backed by Vercel (corporate strategic play, not a revenue product)
- **Maturidade:** GA production, Vercel-operated
- **Onde é melhor que o skval:** Massive distribution and telemetry scale; validation is explicitly externalized, making it a channel/partner surface rather than a competitor.
- **Evidência:** "~669,670 skills listed as of June 2026, with the top skill (vercel-labs find-skills) at 2.0M installs"

#### SkillsMP
- **URL:** <https://skillsmp.com/>
- **Overlap com o skval:** low
- **O que faz:** Mega-aggregator claiming the largest catalog — ~1.9M–2.4M 'public skills' scraped from GitHub across Claude/Codex ecosystems. Its inflated scrape count vs SkillsBench's 47,150 deduped uniques illustrates how noisy raw ecosystem-size claims are.
- **Como mede:** No validation — search/browse aggregation only; counts include forks/duplicates/junk. Pure scale/noise demand signal for validation tooling.
- **Licença/preço:** Free directory
- **Maturidade:** Live aggregator site, 2026
- **Evidência:** "SkillsMP catalogs 2,396,488 public skills" (site claim; ~1.9M scraped from GitHub per ecosystem reports)

#### ClawHavoc / ClawHub poisoning incident (SlowMist, Koi Security)
- **URL:** <https://slowmist.medium.com/threat-intelligence-analysis-of-clawhub-malicious-skills-poisoning-0448ffd49c80>
- **Overlap com o skval:** low
- **O que faz:** Largest skill supply-chain attack to date (Feb 2026) on OpenClaw's ClawHub marketplace: crypto-stealer skills, typosquats, Base64-hidden two-stage loaders. Koi Security found 341 malicious of 2,857 scanned; SlowMist consolidated IOCs across 472 affected skills; later reports up to 1,184. Covered by Unit 42, DarkReading, eSecurityPlanet — the demand catalyst that made 'unreviewed skill registries' a mainstream security story.
- **Como mede:** Not a tool — an incident. Root cause per coverage: SKILL.md turns markdown into an operational entry point, and ClawHub's 'permissive upload process lacks rigorous reviews.' Evidence for skval's D6-veto framing rather than an overlap.
- **Maturidade:** Incident (Feb 2026) with ongoing copycat waves
- **Evidência:** "Koi Security scanned 2,857 ClawHub skills, identifying 341 malicious ones in a campaign dubbed ClawHavoc"

#### Academic skill-eval wave (SkillSieve, SkillSafetyBench, SkillScope, SkillFlow + survey)
- **URL:** <https://arxiv.org/html/2606.11435v1>
- **Overlap com o skval:** low
- **O que faz:** Five+ arXiv frameworks in five months beyond SkillsBench/SkillTester: SkillSieve (hierarchical triage of malicious skills, 2604.06550), SkillSafetyBench (agent safety under skill-facing attacks, 2605.12015), SkillScope (least-privilege enforcement, 2605.05868), SkillFlow (lifelong skill evolution, 2604.17308), plus a survey 'Agent Skill Evaluation and Evolution: Frameworks and Benchmarks' (2606.11435). Methodology is commoditizing in the open literature.
- **Como mede:** Mostly security-side: malicious-skill classifiers, attack-surface benchmarks, runtime permission enforcement — overlapping skval D6 and parts of D2 methodology, but shipped as papers/prototypes, not author-facing validators with verdicts or CI gates.
- **Licença/preço:** Open access papers; code availability varies
- **Maturidade:** Research; no commercial products yet
- **Evidência:** arXiv 2603.28815, 2604.06550, 2604.17308, 2605.05868, 2605.12015, 2606.11435 — six skill-eval/security papers between Mar and Jun 2026


## Apêndice — vereditos adversariais completos


### Verificador 1 (lente produto-paridade)

- **[REFUTED]** Behavioral with/without-skill BASELINE-LIFT scoring (not just static analysis)
  - Raciocínio: At least four shipped products/publications already run the same task with and without the skill and score the lift: Anthropic's skill-creator (first-party; runs each eval with-skill vs no-skill, 3x per configuration, with variance analysis), darkrishabh/agent-skills-eval (--baseline flag, judge grades both arms, 644 stars), adewale/skill-eval-harness (paired with_skill/without_skill runs with exact case/model/repetition matching AND paired sign-flip significance testing at p<=0.05 — verified from its README), and the SkillsBench paper (matched no-Skills vs curated-Skills conditions across 87 tasks, 7,308 trajectories). Even skval's paired-significance sub-claim is already shipped by adewale's harness. What remains unique is only folding lift into a composite 0-100 + Ship/Revise/Reject verdict — packaging, not the differential as stated.
  - Contra-evidência mais forte: adewale/skill-eval-harness — https://github.com/adewale/skill-eval-harness (paired with/without runs + sign-flip paired significance testing, MIT, v0.6.0, actively maintained)
- **[REFUTED]** Triggering (D5) as a first-class measured dimension
  - Raciocínio: Measured (not just static) triggering already ships in three places: Anthropic's skill-creator generates ~20 should/should-not trigger queries, runs each 3x, and measures/optimizes triggering accuracy (its false-positive/false-negative counts are precision and recall components in all but name); adewale/skill-eval-harness has a dedicated 'skill-trigger-matrix' command measuring autonomous trigger rates across agent-by-model cells with provenance gates; promptfoo's Agent Skills guide provides skill-used/not-skill-used assertions. Community posts (Scott Spence's sandboxed skill-activation evals) show the practice is spreading. skval's residual is only the explicit precision/recall/F1 labeling — a reporting convention, trivially replicable, not a defensible differential.
  - Contra-evidência mais forte: Anthropic skill-creator description-optimization loop (should/should-not trigger queries, measured accuracy, auto-optimization) — https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md
- **[PARTIAL]** Safety as a VETO gate (not a weighted score component)
  - Raciocínio: Dedicated skill-security scanners already implement safety as a hard fail: cisco-ai-defense/skill-scanner (7 engines incl. behavioral dataflow + LLM judge, --fail-on-findings / --fail-on-severity exits nonzero on HIGH/CRITICAL, SARIF for GitHub Code Scanning), plus getsentry/skills skill-scanner, Mondoo's agent-skill scanner, and the OWASP Agentic Skills Top-10 skill-scanner integration — all functionally 'safety vetoes shipping' regardless of any quality score. What no competitor does is embed that veto inside a composite quality score (SkillCheck treats security as weighted categories). So the architectural choice is distinctive within scored validators, but the mechanism is shipped elsewhere and the combination is easily replicated by bolting any of these scanners in front of any scorer.
  - Contra-evidência mais forte: cisco-ai-defense/skill-scanner — https://github.com/cisco-ai-defense/skill-scanner (multi-engine skill security scan with CI hard-fail gating)
- **[PARTIAL]** Type-routed eval strategies incl. multi-turn user-simulator
  - Raciocínio: No shipped product was found that classifies a skill by type (task/file_transform/interactive/discipline/reference) and routes the eval strategy accordingly — that routing table appears unique. But every component exists elsewhere: multi-turn user simulation is tau-bench's core method (LM-simulated users driving agents) and a shipped DeepEval feature (conversation simulator); LangSmith has multi-turn/trajectory dataset types; skill-creator generates evals from an interview about the skill's purpose (implicit routing); adewale/skill-eval-harness supports multi-turn evaluation. The differential is an orchestration recipe over commodity parts — real today, but replicable by any competitor in weeks and impossible to defend once described publicly (skval's own agents/*.md prompt guides are open source).
  - Contra-evidência mais forte: DeepEval conversation simulator + tau-bench user-simulation methodology — https://github.com/confident-ai/deepeval and https://arxiv.org/abs/2406.12045
- **[REFUTED]** Purpose-built CI Action failing on verdict
  - Raciocínio: CI gates that fail builds on skill-validation outcomes are commonplace across the category: cisco-ai-defense/skill-scanner (--fail-on-findings, SARIF into GitHub Code Scanning), agent-ecosystem/skill-validator (GitHub Actions with PR-diff annotations, pre-commit hooks), agent-skills-eval (--strict mode + JSON artifact diffing, pitched for CI), claudelint (--strict, exit codes), promptfoo (packaged GitHub Action), SkillCheck Pro (CI/CD binary), and jorgealves/skill-validator (pitched for blocking non-compliant PRs). Failing on 'Ship/Revise/Reject' rather than a severity threshold is skval's own label for the identical mechanism — a threshold-fail exit code. The vocabulary is novel; the capability is not.
  - Contra-evidência mais forte: agent-ecosystem/skill-validator GitHub Actions integration with PR annotations — https://github.com/agent-ecosystem/skill-validator (plus cisco skill-scanner's --fail-on-severity + SARIF)
- **[PARTIAL]** Pre-run cost estimator (token/$ preview before a full run)
  - Raciocínio: No competitor skill validator was found offering a pre-run cost preview of an eval run — searches for this specifically came up empty, and the closest tools do it post-hoc: adewale/skill-eval-harness ships per-run token/dollar telemetry and a suite cost ledger (after the fact), promptfoo tracks cost per eval and has --dry-run only for model scanning. However, the primitive is fully commoditized (AgentOps tokencost covers 400+ models; a dozen token-price calculators exist; 'dry-run cost estimate' is a standard UX pattern from BigQuery et al.), so this is a genuine but shallow first: convenient, easily replicated in a day by any competitor, and not a moat.
  - Contra-evidência mais forte: adewale/skill-eval-harness cost ledger (per-run token/$ telemetry, lift-per-dollar) — https://github.com/adewale/skill-eval-harness; commodity layer: https://github.com/AgentOps-AI/tokencost
- **[REFUTED]** Published variance study + contamination finding with baseline-probe guard
  - Raciocínio: Both halves have shipped prior art. Variance study: SkillsBench (arXiv 2602.12670, skillsbench.ai) is a published with/without-skill study across 87 tasks, 18 model-harness configurations, and 7,308 trajectories, explicitly quantifying variance (+16.2pp average lift, range +4.5 to +51.9pp by domain, 16/84 tasks with negative deltas), and skill-creator's benchmark mode reports mean±std with an analyzer for flaky evals. Contamination/baseline-probe: adewale/skill-eval-harness ships leakage lint, canary tripwires, and n-gram overlap memorization detection; agentskillreport.com published the finding that most skills restate what the model already knows; agent-ecosystem/skill-validator scores 'novelty' as a dimension; and academic practice (knowledge-novelty validation filtering items the base model already answers) predates all of it. skval's specific numbers may be new but the finding and the guard are not publishable firsts.
  - Contra-evidência mais forte: SkillsBench — https://arxiv.org/abs/2602.12670 (published with/without variance study at far larger scale than skval's internal study)
- **[REFUTED]** pass^k reliability formalism for skills
  - Raciocínio: pass^k (all k i.i.d. trials succeed) was introduced by Sierra's tau-bench paper (arXiv 2406.12045, ICLR) explicitly as an agent-reliability metric and is now standard: Inspect AI implements it as an epochs reducer ('probability all k attempts succeed', verified in its docs by the sweep), and — decisively — adewale/skill-eval-harness already applies both pass@k and pass^k to skill evaluation specifically, from repeated with/without runs. skval neither invented the formalism nor is first to apply it to skills. The only residual is bundling it into a composite scorecard dimension (D3), which is presentation.
  - Contra-evidência mais forte: tau-bench (origin of pass^k) — https://arxiv.org/abs/2406.12045; applied to skills: https://github.com/adewale/skill-eval-harness
- **[REFUTED]** Open-source + self-validating
  - Raciocínio: Open source is the category norm, not a differential: agent-skills-eval (MIT-style, 644 stars), adewale/skill-eval-harness (MIT), cisco-ai-defense/skill-scanner, claudelint, agent-ecosystem/skill-validator (Go, brew-installable), moonrunnerkc/skillcheck, moutons/skills-validator, and Inspect AI are all open source, and skill-creator is free and first-party. Self-validation ('validator must score 100/A/Ship on itself') is dogfooding — the same pattern as ESLint linting itself and alirezarezvani's skill-tester gating its own 345-skill repo — and any competitor whose tool is itself a skill can claim it instantly. It is good hygiene and decent marketing copy, but not prior-art-free and not defensible.
  - Contra-evidência mais forte: darkrishabh/agent-skills-eval — https://github.com/darkrishabh/agent-skills-eval (open-source behavioral skill eval with meaningful adoption, undercutting both halves of the claim)

**Maiores ameaças segundo este verificador:**
- Anthropic skill-creator (first-party, free, zero install friction inside Claude Code): its 2026 update already does with/without-skill benchmarking with variance analysis, flaky-eval detection, blind A/B, and triggering-accuracy optimization (it improves descriptions where skval only measures them). If Anthropic adds a composite score or ship-gate semantics, a third-party validator becomes redundant for most Claude Code authors — and Anthropic controls the surface skval runs on.
- adewale/skill-eval-harness: a live, MIT, actively-maintained project (v0.6.0) that already ships skval's core methodological claims — paired with/without lift, sign-flip paired significance (p<=0.05), pass@k AND pass^k, contamination/leakage guards (canary tripwire, n-gram overlap), a skill-trigger-matrix, multi-turn support, and token/$ cost ledgers. It directly falsifies most of skval's 'no one else does this' positioning and is the closest thing to a methodological twin; at 59 stars it is small today but one influential blog post from parity.
- promptfoo under OpenAI: the only major eval framework with a dedicated Agent Skills guide plus skill-used/not-skill-used assertions, backed by ~350k developers, >25% of Fortune 500, and OpenAI's resources post-acquisition. Adding a no-skill control arm, a structural/safety pass, and a composite verdict to its existing guide is incremental engineering for them and would instantly outdistribute skval.
- SkillCheck (getskillcheck.com): owns the commercial trust/distribution flywheel skval lacks — PASSED badges, public report directory, browser validator, claimed 2,568-skill corpus, paid CI binary. Even though it is static-only, badges and directories are what marketplaces and buyers actually see; skval can win on substance and still lose the badge motion.
- The academic/benchmark wave commoditizing skval's 'publishable ammunition': SkillsBench (87 tasks, 7,308 trajectories, published with/without variance findings) plus the 2026 flood of skill-eval papers (SkillAudit, SkillGenBench, Counterfactual Trace Auditing, agentskillreport.com's novelty finding) means skval's variance study and contamination finding arrive into an already-crowded literature rather than an open field, eroding the independent-benchmark niche it hoped to claim.

### Verificador 2 (lente prior-art de pesquisa)

- **[REFUTED]** (1) Behavioral with/without-skill baseline-lift scoring (not just static analysis)
  - Raciocínio: At least four shipped/published systems already run paired with-skill vs no-skill behavioral comparisons: SkillTester (arXiv 2603.28815, Mar 2026; live service at skilltester.ai, code at github.com/skilltester-ai/skilltester) defines utility explicitly 'relative to matched no-skill execution' and normalizes results into a utility score; SkillsBench (arXiv 2602.12670, benchflow-ai/skillsbench) runs 87 tasks under matched no-Skills vs Skills conditions across 18-24 model-harness configs with 3 trials/task; Anthropic's skill-creator runs with-skill vs no-skill baseline benchmarking with mean±std; darkrishabh/agent-skills-eval ships a --baseline flag with judge grading of both arms. skval's residual novelty is only the paired significance test layered on top of lift, which is an increment, not the differential as claimed.
  - Contra-evidência mais forte: SkillTester: Benchmarking Utility and Security of Agent Skills — https://arxiv.org/abs/2603.28815 (deployed at skilltester.ai, open source)
- **[REFUTED]** (2) Triggering (D5) as a first-class measured dimension
  - Raciocínio: Anthropic's skill-creator (shipped, first-party) makes triggering a first-class measured concern: it generates 20 should/should-not trigger queries, splits train/test, measures trigger accuracy over 3 runs per query, and then OPTIMIZES the description — going a step beyond skval, which only measures. promptfoo ships skill-used/not-skill-used assertions. In the literature, trigger precision/recall is established: SkillAxe (arXiv 2606.10546) refines skills based on low trigger recall vs low trigger precision, and SkillRet (arXiv 2605.05726) benchmarks skill retrieval with precision/recall; SkillsFlow/SkillRouter cover routing. skval's exact P/R/F1-as-a-scored-dimension packaging inside a validator composite is a formatting novelty, not a category novelty.
  - Contra-evidência mais forte: Anthropic skill-creator description-optimization/trigger-accuracy loop — https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- **[PARTIAL]** (3) Safety as a VETO gate
  - Raciocínio: No competitor uses the exact 'security caps the verdict regardless of composite score' semantics, but near-equivalents ship: SkillTester reports a separate security score plus a three-level security status label deliberately non-compensatory with utility; SkillCheck's PASSED badge requires score >=90 AND <=2 warnings (a hard gate); claudelint --strict is zero-tolerance fail. Veto semantics are trivially replicable (an if-statement over existing security scores). Worse, the substance behind skval's veto — static safety scanning — was publicly discredited in June-July 2026: CSA research and the SkillCloak technique showed the best static skill scanners drop from ~99% to ~10% detection under self-extracting packing, and Bitdefender/Koi found hundreds of malicious skills sailing past scanners. The gate architecture holds narrowly; its detection layer is known-bypassable, which weakens the claim as a differentiator.
  - Contra-evidência mais forte: CSA 'AI Agent Skill Scanners: Bypassed Across the Board' + SkillCloak — https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-agent-skill-scanner-bypass-20260610-csa/ (gate near-equivalent: SkillTester's separate three-level security status, https://arxiv.org/abs/2603.28815)
- **[PARTIAL]** (4) Type-routed eval strategies incl. multi-turn user simulator
  - Raciocínio: Every component exists separately as prior art: LLM user simulators for multi-turn agent evaluation were established by tau-bench (arXiv 2406.12045, Sierra) and productized in DeepEval's conversation simulator and LangSmith's multi-turn dataset types; skill-type classification exists in SkillCheck (Reviewer/Generator/Pipeline/Tool Wrapper design-pattern classes). What no shipped skill validator was found to do is the routing itself — classify a skill's type and select the eval strategy (incl. simulator for interactive skills) accordingly. That combination holds, but it is assembly of published parts, easily replicable by skill-creator or promptfoo within one release cycle.
  - Contra-evidência mais forte: tau-bench LLM-simulated users for tool-agent-user evaluation — https://arxiv.org/abs/2406.12045
- **[PARTIAL]** (5) Purpose-built CI Action failing on verdict
  - Raciocínio: Purpose-built CI gates for skill validation already ship: pulser eval offers a GitHub Action that fails PRs on broken Claude Code skills (structural/frontmatter/antipatterns; dev.to writeup reports 23 caught issues in week one), agent-ecosystem/skill-validator ships GitHub Actions with PR-diff annotations, agent-skills-eval has --strict CI mode with JSON artifact diffing, SkillCheck Pro sells a CI/CD binary, and jorgealves/skill-validator is pitched for blocking non-compliant PRs. None of these gates on a behavioral composite Ship/Revise/Reject verdict — they gate on lint errors or assertion failures — so the verdict-semantics slice holds, but 'CI Action for skill validation' as a category is occupied and the verdict wrapper is easily replicable.
  - Contra-evidência mais forte: pulser eval + GitHub Action for Claude Code skills in CI — https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9
- **[PARTIAL]** (6) Pre-run cost estimator
  - Raciocínio: Genuinely absent from every adjacent eval product searched: promptfoo tracks cost only from post-hoc usage metadata (no dry-run), ragas has an OPEN feature request for exactly this (issue #2696, 'Pre-flight Token Estimation (Dry Run)'), and no skill validator ships one. However it is commodity functionality, not a moat: tiktoken/Anthropic token-counting API plus a pricing table is a documented playbook (multiple 2026 guides and standalone calculators — promptcostcalculator.com, token-calculator.net), and SkillCheck Pro already does token-budget analysis on the skill artifact. First-mover convenience, easily replicated the moment any incumbent prioritizes it.
  - Contra-evidência mais forte: ragas issue #2696 showing the pattern is a known, requested, unshipped commodity — https://github.com/vibrantlabsai/ragas/issues/2696
- **[REFUTED]** (7) Published variance study + contamination finding w/ baseline-probe guard
  - Raciocínio: The 'publishable ammunition' is already published by others. agentskillreport.com's Agent Skill Analysis is precisely a contamination study: 66 skills with hidden contamination in reference files, novelty scoring ('most skills restate what the LLM already knows'), and a behavioral A/B under baseline vs skill-loaded vs skill+context conditions, including the negative result that structural contamination does not predict behavioral degradation (r=0.077). The baseline-probe logic ('high baseline score = model already knows the domain, skill adds little') is stated verbatim in tessl.io's cross-model skill benchmarking post, and SkillTester's utility definition encodes it formally. Variance study: skill-creator now advertises 'benchmark skill performance with variance analysis' first-party, and SkillsBench runs multi-trial paired evaluations with leakage audits. skval's specific numbers may be new; the findings and the guard are not.
  - Contra-evidência mais forte: Agent Skill Analysis — Interactive Report (contamination + baseline/skill-loaded behavioral study) — https://agentskillreport.com/
- **[PARTIAL]** (8) pass^k reliability for skills
  - Raciocínio: The pass^k formalism ('all k attempts succeed', p^k decay) is tau-bench's published contribution (arXiv 2406.12045, 2024) for agent reliability, and Inspect AI ships it as an epochs reducer ('probability that all k attempts succeed') alongside bootstrap stderr — verified in inspect_ai docs. SkillsBench already runs 3 trials per task on skills specifically, though it reports pass rates rather than pass^k. Applying tau-bench's metric to skill validation is a sensible transplant skval can claim as first-in-category framing, but it is a borrowed, well-documented metric that any competitor can adopt in an afternoon; it is not defensible IP.
  - Contra-evidência mais forte: tau-bench pass^k metric — https://arxiv.org/abs/2406.12045 (shipped implementation: Inspect AI epochs reducers, https://inspect.aisi.org.uk/)
- **[REFUTED]** (9) Open-source + self-validating
  - Raciocínio: Open-source is table stakes in this category, not a differential: SkillsBench (benchflow-ai), SkillTester (skilltester-ai on GitHub), agent-skills-eval (644 stars), claudelint, agent-ecosystem/skill-validator, moonrunnerkc/skillcheck, promptfoo (MIT, ~23k stars) are all open. Self-validation is likewise practiced: alirezarezvani's skill-tester meta-skill exists specifically as the internal quality gate over its own 345-skill repo, and any validator can trivially run on itself — SkillCheck's own directory of validated reports serves the same 'we pass our own bar' trust function via badges. Dogfooding is good hygiene and a nice README line; it is not prior-art-free and confers no moat.
  - Contra-evidência mais forte: benchflow-ai/skillsbench (open-source skill evaluation with published methodology) — https://github.com/benchflow-ai/skillsbench

**Maiores ameaças segundo este verificador:**
- Anthropic skill-creator (first-party, free, zero install friction): its ~March 2026 update added eval generation, with/without-skill benchmarking with variance analysis, flaky-eval analysis, blind A/B, and a triggering-accuracy OPTIMIZATION loop — it defines the default workflow every skill author meets first, and each release shrinks the residual gap (composite score, verdict, significance) skval depends on.
- SkillTester (skilltester.ai, arXiv 2603.28815, open source) — missed by the sweep digest entirely: a deployed public service that already does paired no-skill-baseline utility scoring plus a separate security probe suite with a three-level security status, i.e. it occupies skval's exact claimed niche (behavioral lift + safety-aware scored verdict) with a peer-reviewed paper behind it.
- SkillsBench (arXiv 2602.12670, benchflow-ai) plus the 2026 academic wave (SkillAxe, SkillRet, SkillSieve, SkillSafetyBench, SkillAudit, agentskillreport.com): the 'independent skill benchmark' and 'contamination finding' niches skval planned to claim as publishable ammunition are already claimed — skval's ~200-skill benchmark now has a direct, published, open-source rival with 18-24 model-harness configs and deterministic verifiers.
- promptfoo under OpenAI: 350k developers, >25% of Fortune 500, a dedicated Test Agent Skills guide with skill-used/not-skill-used assertions and --repeat sampling; adding a no-skill control arm, an artifact lint, and a composite verdict is an incremental release for them and would erase skval's remaining bundle advantage at distribution scale skval cannot match.
- Static-safety credibility collapse + SkillCheck's distribution flywheel: June-July 2026 research (CSA scanner-bypass note, SkillCloak — best scanners fall ~99% to ~10% detection) publicly undermines the static scanning behind skval's D6 veto, while SkillCheck keeps owning the badge/public-report/browser-validator trust surfaces — skval risks being both out-marketed on trust and technically discredited on the safety gate it markets as a differentiator.
