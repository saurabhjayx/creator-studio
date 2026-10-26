#!/usr/bin/env python3
"""Static checks for every skill and agent. Exit 1 on any failure."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TIER_MODEL = {"S": "haiku", "M": "sonnet", "L": "opus"}
errors = []


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append("%s: no frontmatter" % path)
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        k = re.match(r"^\s*([\w-]+):\s*(.*)$", line)
        if k:
            fm.setdefault(k.group(1), k.group(2).strip().strip('"'))
    return fm, text


skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
for d in skills:
    f = d / "SKILL.md"
    if not f.exists():
        errors.append("%s: missing SKILL.md" % d.name)
        continue
    fm, text = frontmatter(f)
    if fm.get("name") != d.name:
        errors.append("%s: name '%s' != folder" % (d.name, fm.get("name")))
    desc = fm.get("description", "")
    if not 40 <= len(desc) <= 1024:
        errors.append("%s: description length %d" % (d.name, len(desc)))
    tier = fm.get("tier")
    if TIER_MODEL.get(tier) != fm.get("model"):
        errors.append("%s: tier %s but model %s" % (d.name, tier, fm.get("model")))
    if "CLAUDE_PLUGIN_ROOT" in text:
        errors.append("%s: uses CLAUDE_PLUGIN_ROOT (unset at runtime); use CLAUDE_SKILL_DIR" % d.name)
    if "## Token budget" not in text:
        errors.append("%s: no '## Token budget' section" % d.name)
    if d.name != "creator" and "Next:" not in text:
        errors.append("%s: no 'Next:' follow-up" % d.name)
    for ref in re.findall(r"(?:\.\./[\w-]+/)?references/[\w.-]+\.md", text):
        if not (d / ref).exists() and not (ROOT / "skills/creator" / ref).exists():
            errors.append("%s: broken link %s" % (d.name, ref))
    for script in set(re.findall(r"scripts/([\w-]+\.py)", text)):
        if not (ROOT / "skills/creator/scripts" / script).exists():
            errors.append("%s: references missing script %s" % (d.name, script))
    for agent in set(re.findall(r"\bcreator-(?:researcher|writer|analyst|quick)\b", text)):
        if not (ROOT / "agents" / (agent + ".md")).exists():
            errors.append("%s: references missing agent %s" % (d.name, agent))

for f in sorted((ROOT / "agents").glob("*.md")):
    fm, _ = frontmatter(f)
    for k in ("name", "description", "model", "effort", "tools"):
        if not fm.get(k):
            errors.append("agent %s: missing %s" % (f.name, k))
    if fm.get("name") != f.stem:
        errors.append("agent %s: name mismatch" % f.name)

for j in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
    json.loads((ROOT / j).read_text(encoding="utf-8"))

print("skills: %d  agents: %d" % (len(skills), len(list((ROOT / "agents").glob("*.md")))))
for d in skills:
    fm, _ = frontmatter(d / "SKILL.md")
    print("  %-20s tier %s  %s" % (d.name, fm.get("tier"), fm.get("model")))
if errors:
    print("\nFAIL (%d):" % len(errors))
    print("\n".join("  - " + e for e in errors))
    sys.exit(1)
print("\nPASS: static validation")
