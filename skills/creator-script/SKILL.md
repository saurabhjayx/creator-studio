---
name: creator-script
description: "Long-form YouTube video script (8-15 min) with retention engineering: 3 title options, thumbnail text concepts, a 0-30s cold-open hook, pattern interrupts every 60-90s, open loops, chapters with timestamps, B-roll cues, CTA placement, and a ready-to-paste description + chapters block. Input a topic or a trend. Use when user says YouTube script, video script, long-form script, write my video, script outline, retention, YouTube video about <topic>, turn this trend into a video. Triggers on: youtube script, video script, long-form video, retention script, chapters."
user-invocable: true
argument-hint: "<topic or trend> [--length 8-15] [--style explainer|tutorial|story|listicle|review] [--audience <who>]"
model: sonnet
allowed-tools: Read, Bash, WebSearch, WebFetch
license: MIT
metadata:
  author: creator-studio
  version: "1.0.0"
  tier: M
---

# Creator Script (long-form YouTube)

Writes a full 8-15 minute YouTube script engineered for retention: strong cold open,
open loops that pay off later, a pattern interrupt every 60-90 seconds, and chapters
that match what viewers search for.

## Quick reference

| Command | Result |
|---------|--------|
| `/creator-script "why sourdough fails"` | 10-min explainer (default) |
| `/creator-script "best budget mics 2026" --style review --length 12` | Review structure, 12 min |
| `/creator-script --from-trend` | Uses the #1 topic from a `/creator-trends` run in this conversation |

Defaults: `--length 10`, `--style` inferred from topic, audience from `./.creator/niche.md` or "curious beginner".

## Token budget

Tier M: sonnet / medium effort.
- Script calls: 1 (`trends.py suggest --q "<topic>"` to harvest real viewer questions for chapters).
  Plus `trends.py news --q "<topic>" --days 14` only if the topic is a trend/news item.
- WebSearch: <= 4 (facts, figures and 1 search of what already ranks on YouTube for the topic).
- WebFetch: <= 2 (primary sources for key facts).
- Output: script ~140-150 spoken words/min (10 min ≈ 1,450 words of VO) plus packaging. This
  skill is allowed to exceed the M ~1200-word cap for the script body itself; keep everything
  else tight.

## Workflow

1. **Frame.** Read `./.creator/niche.md` if present. Settle: topic, audience, length,
   style, and the **one promise** of the video (what the viewer can do/know by the end).
   If topic is vague, pick the sharpest angle and state it; don't ask unless it's ambiguous
   between two very different videos.

2. **Research.**
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" suggest --q "<topic>"
   ```
   For trends also:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/trends.py" news --q "<topic>" --days 14
   ```
   Autocomplete questions become chapter candidates. Then WebSearch for facts the script
   will state; collect a source list (publisher, date). One WebSearch
   `site:youtube.com <topic>` to see the angles already taken: differentiate, don't copy.
   Sensitive/tragic topics: apply the gate in `../creator-trends/references/scoring.md`;
   informational, respectful tone only, no clickbait packaging.

3. **Package first** (titles + thumbnails before script; the script must deliver on them):
   - 3 titles, each a different lever: curiosity, specific outcome, contrarian. <= 60 chars,
     front-load the keyword. No claims the video doesn't prove.
   - 3 thumbnail concepts: <= 4 words of text, the visual, and how it complements (not
     repeats) the title.

4. **Structure the timeline** (scale timings to `--length`):

   | Block | Time (10-min) | Job |
   |-------|---------------|-----|
   | Cold open | 0:00-0:30 | Payoff tease / stakes, confirm the title's promise in 1 line, open Loop A |
   | Setup | 0:30-1:15 | Why this matters to *you*, credibility in 1 line, roadmap (no "before we start" fluff) |
   | Chapters 1-N | 1:15-8:30 | 3-6 chapters; each = mini hook → point → proof/demo → takeaway |
   | Climax / payoff | 8:30-9:30 | Close Loop A; biggest insight last-but-one chapter |
   | Outro + CTA | 9:30-10:00 | Next-video CTA (end screen), not "thanks for watching" |

   Retention devices (mark them inline in the script):
   - `[LOOP A OPEN]` / `[LOOP A CLOSE]`: at least 2 loops; one opened at 0:00-0:30 closes after 60% runtime.
   - `[INTERRUPT]` every 60-90s: change of shot, graphic, b-roll montage, on-screen question,
     tonal shift, quick story, or a "but here's the problem" turn. List them with timestamps.
   - `[RE-HOOK]` at each chapter start: one line on why the next part matters.
   - `[B-ROLL: ...]`, `[GRAPHIC: ...]`, `[ON-SCREEN TEXT: ...]` cues on their own lines.
   - CTAs: soft subscribe at ~30-40% runtime *after* delivering value (one line);
     comment prompt mid-video tied to a question; end-screen CTA to a specific next video.
     Never in the first 60 seconds.

5. **Write the script.** Spoken, second person, short sentences, contractions. Every fact
   cites a source in a `[SRC: publisher, date]` tag (stripped before recording). No invented
   stats; if unknown, say "estimate" or rephrase as experience.

6. **Self-check** before output: promise stated by 0:30? Interrupt gap never > 90s?
   Every loop closed? Each title delivered? Runtime ≈ words / 145. Fix, then output.

## Output format

```markdown
## <Working title>: <length> min <style>
Promise: <one line> · Audience: <who> · Sources: suggest ✓, news ✓, WebSearch ×N

### Titles
1. <curiosity>  2. <outcome>  3. <contrarian>
### Thumbnail concepts
| # | Text (≤4 words) | Visual | Pairs with title |

### Retention map
| Time | Device | Note |
|------|--------|------|
| 0:00 | Loop A open | ... |
| 1:20 | Interrupt | b-roll montage |
...

### Script
#### [0:00] Cold open
<VO lines> [B-ROLL: ...] [LOOP A OPEN]
#### [0:30] Setup
...
#### [1:15] Chapter 1: <name>
...

### Description (paste-ready)
<2-line hook with keyword> \n <3-4 lines summary> \n Sources: <list> \n
Chapters:
0:00 <Cold open name>
0:30 ...
(first chapter must be 0:00, >= 3 chapters, each >= 10s: YouTube's chapter rules)

### Source list
- <publisher, title, date, URL>

Next: `/creator-reels "<topic>"` to cut 3 Shorts from chapters · `/creator-repurpose` for blog/LinkedIn versions.
```

## Examples

- `/creator-script "how to start running at 40"`: tutorial, 10 min.
- `/creator-script "EQT buys Range Resources: what it means for gas prices" --style explainer --length 8`: trend-led.
- `/creator-script "I tried 5 AI note apps" --style review --length 14`

## Error handling

| Situation | Action |
|-----------|--------|
| No reliable source for a key claim | Cut the claim or reframe as opinion; flag in Source list |
| Topic too thin for 8 min | Say so; offer a 4-6 min version or a Shorts series |
| Topic too broad for 15 min | Narrow to one promise; list leftovers as follow-up videos |

Next: `/creator-reels "<topic>"` to promote the video with Shorts.
