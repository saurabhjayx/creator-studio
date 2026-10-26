---
name: creator-niche
description: "Niche content research (Mode B: user provides a niche). Pulls Google News, Google autocomplete questions, Hacker News and the niche's subreddits in one call, clusters findings into rising news, audience questions, pain points, debates and evergreen gaps, then returns the top 10 scored topics with the audience question each answers, suggested formats and content pillars. Can save a reusable niche profile to ./.creator/niche.md for other skills. Use when user says research my niche, content ideas for <niche>, what does my audience ask, topic ideas for <niche>, content pillars, niche research, audience questions, pain points in <niche>. Triggers on: niche, my niche, content pillars, audience questions, topic research."
user-invocable: true
argument-hint: "<niche> [--geo US] [--deep]"
model: sonnet
allowed-tools: Read, Write, Bash, WebSearch
license: MIT
metadata:
  author: creator-studio
  version: "1.0.0"
  tier: M
---

# Creator Niche (Mode B: "here's my niche")

Finds what a specific audience is reading, asking, complaining about and arguing over
right now, and turns it into 10 scored topics grouped into content pillars.

## Quick reference

| Command | What it does |
|---------|--------------|
| `/creator-niche keto` | Standard run: news, 5 autocomplete seeds, HN, 3-5 subreddits |
| `/creator-niche "home workout" --deep` | Adds alphabet-soup autocomplete (26 extra queries) for a deep question bank |
| `/creator-niche "personal finance" --geo GB` | UK news edition |

## Token budget

Tier M: sonnet / medium effort.
- Script calls: 1 (`trends.py niche`). `--deep` is the same single call (slower, ~30 requests inside).
  Optionally +1 `trends.py news --q "<sub-topic>"` to check a promising cluster.
- WebSearch: <= 2 (only to find subreddits for an unmapped niche, or to check saturation of the top topic).
- WebFetch: 0.
- Output cap: ~1100 words. Profile file <= 60 lines.
- If `./.creator/niche.md` exists and is < 7 days old for the same niche, offer to reuse its pillars and only refresh the data.

## Workflow

1. **Parse input.** Niche = free text (quote multi-word). Normalise to a short query
   (e.g. "I post about budgeting for students" → `student budgeting`). If no niche given,
   Read `./.creator/niche.md`; if absent, ask for one (one question, then stop).

2. **Map subreddits.** Read `references/niche-subreddits.md`, choose 3-5 subs. Unmapped
   niche → 1 WebSearch `best subreddits for <niche>`, pick 3, tell the user.

3. **Fetch.** Run exactly:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" niche --q "<niche>" --subs <sub1,sub2,sub3> --geo <GEO> [--deep]
   ```
   Output `results[]`: `google_news` (title, date, source), `google_suggest` (list of
   query strings), `hacker_news` (title, points, comments), one `reddit_r/<sub>` per sub
   (title, updated). Sources fail soft. Notes:
   - Reddit 429 (rate limit) is common. Don't retry in a loop; one retry later in the run at most
     via `trends.py reddit --sub <best sub>`, else proceed without Reddit and say so.
   - HN is only useful for tech/business/AI niches. For other niches, ignore weak HN hits
     (points < 20 or off-topic) rather than forcing them in.
   - If `google_suggest` is thin (< 10 items) and `--deep` wasn't set, suggest re-running with `--deep`.

4. **Cluster into 5 themes.** Assign every usable item to one theme (an item can feed two):

   | Theme | Signals |
   |-------|---------|
   | **Rising news** | `google_news` items < 7 days old; product launches, studies, rule changes |
   | **Audience questions** | `google_suggest` items starting how/why/what/is/can/best; Reddit titles ending in `?` |
   | **Pain points** | Reddit/suggest with: struggling, stuck, plateau, can't, not working, help, mistake, worth it |
   | **Debates / controversies** | "vs", "myth", "overrated", "unpopular opinion", "is X bad", conflicting headlines |
   | **Evergreen gaps** | Recurring questions (2+ phrasings) with no recent news coverage = always-searched, under-served |

   Merge near-duplicates ("keto flu symptoms", "keto flu how long") into one topic with the
   phrasings listed.

5. **Score.** Use `../creator-trends/references/scoring.md` (TOS 0-100). In niche mode,
   Fit is usually 8-10; Demand leans on autocomplete breadth; Gap is the key differentiator.
   Apply the sensitivity gate (health misinformation, medical claims → `⚠ care`: cite
   sources, no cure claims).

6. **Pick top 10** across themes (at least one per theme where data allows; don't fill a
   theme with weak items). For each: topic, TOS, the audience question it answers (verbatim
   phrasing from suggest/Reddit where possible), formats (2 max, e.g. "Reel: myth-bust;
   Blog: guide"), shelf life, source + date.

7. **Group into 3-5 content pillars** (recurring series a creator can own, e.g.
   "Plateau fixes", "Budget meal prep", "Myth vs science"). Each pillar lists its topic #s.

8. **Offer to save the profile.** Ask: "Save this as your niche profile (./.creator/niche.md)
   so /creator-trends, /creator-reels and /creator-calendar use it?" Only Write on yes.
   If the file exists, show a one-line diff summary and ask before overwriting.

## Output format

```markdown
## Niche: <niche> (<GEO>), fetched <date>
Sources: News 15 ✓ · Autocomplete 43 ✓ · HN 4 (weak, ignored) · r/keto ✓ · r/loseit ✗ 429

### Top 10 topics
| # | Topic | Theme | TOS | Audience question it answers | Formats | Shelf | Source + date |
|---|-------|-------|-----|------------------------------|---------|-------|---------------|
| 1 | ... | Pain point | 74 | "why am I not losing weight on keto" | Reel: myth-bust · Blog: guide | weeks+ | Autocomplete, 26 Oct |

### Content pillars
- **<Pillar>**: <1-line promise to the audience>. Topics #1, #4, #7.
...

### Question bank (unused, for later)
<8-15 verbatim autocomplete/Reddit questions not in the top 10>

Next: `/creator-reels --niche "<niche>"` for short-form scripts · `/creator-calendar` to schedule the pillars.
```

## Niche profile file (`./.creator/niche.md`)

```markdown
---
niche: <niche>
geo: US
subs: keto,ketorecipes,loseit
updated: YYYY-MM-DD
---
## Audience
<who, level (beginner/intermediate), main goal, main frustration>: inferred from data, mark as inferred.
## Pillars
1. <Pillar>: <promise>
## Seed keywords
<5-10 from niche-subreddits.md + top autocomplete terms>
## Evergreen questions
<5-10 verbatim>
## Tone
<ask user, or "not set">
```

Other skills Read this file; keep its headings stable.

## Examples

- `/creator-niche keto`
- `/creator-niche "AI tools for teachers" --deep`: unmapped niche → maps to r/Teachers + r/ChatGPT + r/edtech after one search.
- `/creator-niche "personal finance" --geo IN`

## Error handling

| Situation | Action |
|-----------|--------|
| Niche too broad ("health", "business") | Ask the user to pick a sub-niche, offer 3 options from autocomplete |
| All Reddit 429 | Proceed with News + Suggest; note it; suggest re-run later |
| Script exit 1 (all sources failed) | WebSearch fallback: <= 4 searches (`<niche> news this week`, `<niche> reddit`, `<niche> questions people ask`, `<niche> trends 2026`); cite site + date, label output "Fallback: web search" |
| Fewer than 10 decent topics | Show what's there; don't pad with invented topics |

Next: `/creator-reels --niche "<niche>"` · `/creator-article <topic #>` · `/creator-calendar`.
