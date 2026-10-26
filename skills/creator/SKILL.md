---
name: creator
description: "Content-creator command center. Finds what's trending right now (general or in your niche) and turns it into reels/shorts ideas, YouTube scripts, publish-ready blog articles, hooks, captions and calendars; humanizes AI drafts; analyzes which of your posts perform and why; finds competitor gaps. Use when user says: creator, trending topics, what should I post, content ideas, reel ideas, shorts ideas, blog ideas, viral, trend, niche trends, humanize, content calendar, analyze my posts."
user-invocable: true
argument-hint: "[command] [args]"
model: sonnet
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, Agent, Skill
license: MIT
metadata:
  author: creator-studio
  version: "1.0.0"
  tier: M
---

# Creator: content-creator command center

**Invocation:** `/creator <command> <args>`. Routes to one sub-skill; never does the sub-skill's work itself.

## Commands

| Command | Sub-skill | Tier | What you get |
|---------|-----------|------|--------------|
| `trends [--geo US] [--platform x]` | creator-trends | M | Ranked "what's hot now" with Trend Opportunity Score |
| `niche <niche> [--deep]` | creator-niche | M | Top topics + audience questions inside your niche |
| `reels <topic \| --trending \| --niche x>` | creator-reels | M | Reel/Shorts/TikTok ideas with hooks + timed scripts |
| `script <topic>` | creator-script | M | 8-15 min YouTube script with retention beats |
| `article <topic \| --trending [niche]>` | creator-article | L | Researched, cited, humanized blog post + SEO meta |
| `humanize <file> [--mode audit\|rewrite\|voice]` | creator-humanize | L | Benchmark rewrite + before/after human score |
| `analyze <csv \| urls>` | creator-analyze | L | Why posts win/lose, rules, A/B tests, best times |
| `competitor <handles/urls> --niche x` | creator-competitor | M | Their winning topics + your gap list |
| `hooks <topic> \| --score "<hook>"` | creator-hooks | S | 10 hooks or a scored rewrite of yours |
| `captions <post/topic> [--platform]` | creator-captions | S | Captions, hashtags, titles, thumbnail text |
| `repurpose <url/file>` | creator-repurpose | M | One piece -> reels, carousel, thread, LinkedIn, newsletter |
| `calendar [7\|14\|30] [--niche x]` | creator-calendar | M | Dated calendar mixing trends + evergreen pillars |

## Routing

1. Parse `$1`. Known command -> invoke that sub-skill with the remaining args. Done.
2. No command, plain request -> pick by intent:
   - "what's trending / what should I post" with no niche -> creator-trends (mode A)
   - mentions a niche/topic area -> creator-niche (mode B)
   - "my posts / my analytics / why did this flop" -> creator-analyze
   - pasted draft + "make it sound human / less AI" -> creator-humanize
3. First run with no niche known: ask ONE question: "Trending in general, or in your niche (which one)?"
   Then route. If `./.creator/niche.md` exists, use it silently and say so in one line.
4. Chains (only when asked for "end to end"): trends|niche -> reels + article -> captions. Run
   research once and pass results forward; never re-fetch.

## Token budget

Router itself: tier M model but near-zero work: 0 web calls, 0 scripts. Spend nothing beyond parsing and
the one optional question. Sub-skills set their own tier (S haiku / M sonnet / L opus, see CONVENTIONS.md).

## Data sources

`scripts/trends.py` (keyless, stdlib): Google Trends daily RSS, Google News RSS, Google autocomplete,
Reddit RSS, Hacker News, Wikipedia top pageviews, YouTube channel RSS. Platform-native trends
(audios, challenges) have no free API: sub-skills use WebSearch and label them "verify in-app".
Platform specs: `references/platforms.md`.

## Doctor

`/creator doctor`: run `python3 "${CLAUDE_SKILL_DIR}/scripts/trends.py" google --limit 3`
and report which sources respond. Python 3.9+ is the only requirement.
