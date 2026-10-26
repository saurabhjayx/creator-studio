---
name: creator-reels
description: "Short-form video ideas and scripts for Instagram Reels, YouTube Shorts and TikTok. Turns a topic, today's trends (--trending) or a niche (--niche) into 5-10 ready-to-shoot ideas, each with a 1.5s hook (on-screen text + spoken line), format (talking head, green screen, POV, tutorial, before/after, listicle, storytime, duet/stitch...), 15-45s beat-by-beat script with timestamps, shot/b-roll list, on-screen text, CTA, caption seed, audio suggestion and predicted strength. Use when user says reel ideas, shorts ideas, TikTok ideas, script a reel, short-form video, viral video idea, hook for a reel, what reels should I make. Triggers on: reels, shorts, tiktok, short-form, reel script, hooks."
user-invocable: true
argument-hint: "<topic> | --trending | --niche <niche> [--platform reels|shorts|tiktok] [--count 5-10] [--geo US]"
model: sonnet
allowed-tools: Read, Bash, WebSearch, Agent
license: MIT
metadata:
  author: creator-studio
  version: "1.0.0"
  tier: M
---

# Creator Reels

Trend or topic in, shoot-ready short-form scripts out. Each idea is a full production
card a creator can film on a phone today.

## Quick reference

| Command | Source of ideas |
|---------|-----------------|
| `/creator-reels "sourdough for beginners"` | The given topic (angles generated around it) |
| `/creator-reels --trending` | Today's trends via creator-trends logic (top scorers only) |
| `/creator-reels --niche keto` | Niche research via creator-niche logic |
| `/creator-reels --trending --platform tiktok --count 5` | 5 TikTok-tuned ideas |

Defaults: `--count 7`, `--platform reels` (cards note Shorts/TikTok tweaks), `--geo US`.

## Token budget

Tier M: sonnet / medium effort.
- Script calls: 0-1. Topic mode: optionally `trends.py suggest --q "<topic>"` for real audience phrasing.
  `--trending`: `trends.py pulse`. `--niche`: `trends.py niche`. Skip if that data is already in the conversation (e.g. right after `/creator-trends`).
- WebSearch: <= 3 (1 for trending audio this week; 1-2 for facts a script asserts).
- WebFetch: 0-1.
- Output cap: ~1400 words for 7 ideas (about 180 words/card). For count > 7, compress beats.

## Workflow

1. **Load context.** Read `./.creator/niche.md` if present (niche, pillars, tone). Read
   `references/reel-formats.md` (formats, hook patterns, strength predictors).

2. **Source ideas** (one path):
   - **Topic**: run
     `python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" suggest --q "<topic>"`
     to get real question phrasings; build angles (myth, mistake, how-to, comparison, story).
   - **`--trending`**: if no creator-trends output is in the conversation, run
     `python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" pulse --geo <GEO>`,
     then apply `../creator-trends/references/scoring.md` (including the sensitivity gate).
     Use only candidates with TOS >= 50 and not excluded. `⚠ care` topics get informational
     formats only (green screen explainer, myth vs fact), never POV/comedy/hot take.
   - **`--niche <x>`**: if no creator-niche output is in the conversation, run
     `python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" niche --q "<x>" --subs <mapped>`
     with subs from `../creator-niche/references/niche-subreddits.md`; take top topics.
   - Heavy combos (`--trending` + niche fit across platforms) may delegate sourcing to the
     `creator-researcher` agent and use its JSON.

3. **Audio scan (1 WebSearch).** `<platform> trending audio this week <Month YYYY>`. Keep
   2-4 named sounds with publisher + date. If nothing recent (< 14 days), say "no fresh
   audio roundup; use original audio or pick from in-app Trending".

4. **Match idea → format.** Choose from the 20 formats; vary them (no format more than twice
   in a set). Flash trends → reaction / green screen / trend remix. Evergreen → tutorial,
   listicle, myth vs fact, series.

5. **Write each card** (template below). Rules:
   - Hook works with sound off: on-screen text <= 8 words; spoken line <= 12 words.
   - Beats every 2-5s with timestamps; total 15-45s (tutorial/storytime may hit 45-60s, say so).
   - Every factual claim must come from fetched data or a WebSearch with source; otherwise
     phrase as opinion/experience. No fake stats, no fake comments for Q&A format.
   - CTA is one action (save / comment keyword / follow for part 2), matched to the goal.
   - Caption seed: first line = hook restated, <= 125 chars visible; 3-5 hashtags max.

6. **Predict strength.** High / Medium / Low + one-line reason from the strength predictors.
   Never predict view counts.

7. **Rank** cards by predicted strength, then shelf-life urgency. Close with a shoot order.

## Card template

```markdown
### 1. <Working title> (<Format>) · Strength: High
**Why:** <topic source + date, e.g. "Google Trends 1000+, 26 Oct"> · Shelf: days · Platform tweak: <Shorts/TikTok note>

**Hook (0-1.5s)**: On-screen: "<≤8 words>" · Spoken: "<≤12 words>" · Visual: <first frame>

| Time | Spoken / VO | On-screen text | Shot / b-roll |
|------|-------------|----------------|---------------|
| 0-1.5s | ... | ... | ... |
| 1.5-6s | ... | ... | ... |
| ... | ... | ... | ... |
| 25-30s | CTA: ... | ... | ... |

**Shot list:** 1) ... 2) ... 3) ... (phone-only feasible: yes/no)
**Caption seed:** <first line> + 1-2 lines + #tag #tag #tag
**Audio:** "<sound name>" (<source, date>), *verify trending in-app* | or "original audio"
**Strength reason:** <1 line from predictors>
```

## Output format

```markdown
## Reel ideas: <topic | trending GEO | niche>, <platform>, <date>
Sources: <scripts/searches used, ✓/✗>

<cards 1..N>

### Shoot order
1. #<n> today (flash, expires in hours/days) · 2. #<n> ... · Batch-film: #<a>, #<b> share a setup.

Next: `/creator-hooks` for 10 alt hooks on the winner · `/creator-captions` for full captions · `/creator-calendar` to schedule.
```

## Examples

- `/creator-reels "air fryer meal prep"`: 7 ideas, autocomplete-led angles.
- `/creator-reels --trending --platform shorts --count 5`
- `/creator-reels --niche "personal finance" --count 10`: pillar-tagged ideas from niche research.

## Error handling

| Situation | Action |
|-----------|--------|
| `--trending` yields < 3 safe topics ≥ 50 | Fill with niche/evergreen ideas, label them "evergreen fallback" |
| Topic is a tragedy/sensitive event | Decline opportunity framing; offer a respectful informational format or skip |
| No audio data | Recommend original audio; never invent sound names |
| Script data errors | Continue with topic-only ideation, note missing data |

Next: `/creator-script <winner topic>` to expand the best idea into a long-form YouTube video.
