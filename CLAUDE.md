# creator-studio: notes for Claude

Claude Code plugin with content-creator skills. Read CONVENTIONS.md before editing a skill.

- Skills: `skills/<name>/SKILL.md`. Agents: `agents/`. Scripts: `skills/creator/scripts/` (stdlib only, Python 3.9).
- Scripts are referenced as `${CLAUDE_SKILL_DIR}/../creator/scripts/x.py`, never `CLAUDE_PLUGIN_ROOT` (it is unset at runtime).
- Keep the model tier matched to the work (validate.py enforces tier ↔ model).
- Test: `./tests/run_tests.sh`, then `claude plugin validate .`. Evals: `./tests/run_tests.sh --evals`.
- Don't add dependencies or API-key requirements.
