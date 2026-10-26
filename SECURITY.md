# Security Policy

## Supported versions
Only the latest release receives fixes.

## Reporting a vulnerability
Use GitHub's **private vulnerability reporting** (Security tab → Report a vulnerability). Please don't open public issues for security problems.
You can expect a response within 7 days.

## Scope
- `skills/creator/scripts/*.py`: these make outbound HTTPS requests to fixed public hosts only (Google, Reddit, HN Algolia, Wikimedia, YouTube). Report any way to redirect them to arbitrary hosts.
- Prompt injection: skills treat fetched pages and RSS as data. Report any case where fetched content makes a skill run commands, write files or send data.
- No credentials are stored or required.
