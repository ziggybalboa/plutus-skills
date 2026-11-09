# Plutus skills

Portable agent skills for public company research. Currently includes **funder-research** only: search the public Plutus funder directory, inspect profiles, and report cited findings with explicit unknowns. Cash analysis and financial-document extraction are not included.

## Install

Requires Node.js 22.20+ for the skills CLI:

```sh
npx skills add ziggybalboa/plutus-skills --skill funder-research
```

Select your agent interactively, or install to a Codex project:

```sh
npx skills add ziggybalboa/plutus-skills --skill funder-research -a codex -y
```

Run from the intended project; omit `-g` for project-local installation. Review the skill before running scripts. Agents need internet access and either HTTP MCP support or Python 3 for the dependency-free fallback. No Plutus account or API key is required.

## Use

Ask your agent to use `funder-research`, for example: “Research MCA providers in California using public profiles. Cite sources and flag unknown criteria.” Clarify product/geography where ambiguous. See [the skill](skills/funder-research/SKILL.md) and [API reference](skills/funder-research/references/api.md).

This is research, not underwriting, matching, submission, financial advice, or a funding guarantee. Profiles may be AI-enriched and unverified. Source references do not verify individual fields. Do not send customer data, statements, account numbers, or private contacts.

## Verification

```sh
python3 -m unittest discover -s tests -v
python3 tests/live_contract.py
```

The first command runs offline helper tests. The second makes read-only public requests and prints assertion summaries, not a catalog dump. Live data can change; failures require investigation rather than replacing results with fixtures. Agent behavior review cases are in [tests/agent-cases.md](tests/agent-cases.md); HTTP tests alone do not establish instruction-following quality.

Skills directory indexing is controlled by skills.sh and its installation telemetry, not this repository. Installation does not guarantee a listing time or ranking.

MIT applies to this repository's original code and instructions, not to third-party directory content or linked sources.
