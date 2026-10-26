---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Bash, WebSearch, WebFetch, Write, Agent]
---

/creator-trends --geo US --platform shorts

This test environment has no network. Instead of running trends.py, use the pre-fetched trends.py output at tests/fixtures/pulse_US.json (captured live; treat its fetched_at as "now").
