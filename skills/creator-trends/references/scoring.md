# Trend Opportunity Score (TOS)

Shared scoring rubric for `creator-trends`, `creator-niche`, `creator-reels` and the
`creator-researcher` agent. Every score must be reproducible from the fetched data:
show the six sub-scores, not just the total.

## Formula

```
TOS = Velocity (0-25) + Demand (0-20) + Gap (0-20) + Shelf (0-15) + Fit (0-10) + Safety (0-10)
```

Total 0-100. Round sub-scores to integers. If a signal is missing (source errored),
score that factor at its midpoint and mark it `~` (e.g. `Demand ~10`). Never invent data
to fill a factor.

## 1. Velocity / freshness (0-25)

How new and how fast. Based on timestamps in the fetched data (`started`, `date`,
`updated`, `pubDate`) relative to `fetched_at`.

| Signal | Points |
|--------|--------|
| Appears in Google Trends daily RSS AND >=1 other source within 24h | 22-25 |
| Google Trends RSS, started < 12h ago | 18-22 |
| Multiple news items in last 48h, or HN front page | 13-17 |
| News / Reddit top-of-week, 3-7 days old | 7-12 |
| Older than 7 days, or no timestamp | 0-6 |

Cross-source presence (same entity in 2+ of google_trends / wikipedia_top / hacker_news /
reddit / google_news) is the strongest velocity signal. Count it explicitly.

## 2. Search demand signal (0-20)

Proxy for how many people are actively looking. Use only numbers present in the data.

| Signal | Points |
|--------|--------|
| Google Trends `traffic` >= 50,000+ or Wikipedia views >= 500k | 17-20 |
| traffic 10,000+ / wiki 100k-500k | 12-16 |
| traffic 1,000+ / wiki 30k-100k / HN points >= 300 | 7-11 |
| traffic 100-500+ / autocomplete hits only | 3-6 |
| No demand data | ~10 (midpoint, flagged) |

Autocomplete (`google_suggest`) proves the query exists but not volume: max 6 alone,
+2 if the term produces 5+ distinct question-form completions.

## 3. Competition / saturation gap (0-20)

Inverse of how crowded it already is. Higher = more room.

| Signal | Points |
|--------|--------|
| Very new (<12h), few explainers yet; niche angle available | 16-20 |
| Mainstream-covered but a clear angle is missing (how-to, explainer, local, creator-POV) | 10-15 |
| Wall-to-wall coverage from major outlets, many creators already posting | 4-9 |
| Pure results/score/answer lookup (e.g. "wordle today", game scores) | 0-3 |

Judge from the `news` titles: 5+ near-identical headlines from big outlets = saturated.

## 4. Shelf life: evergreen vs flash (0-15)

Classify, then score. The shelf-life label is also output in the table.

| Label | Meaning | Points |
|-------|---------|--------|
| `weeks+` | Underlying question stays searched (how-to, health, money, tools) | 12-15 |
| `days` | Story arc runs 2-7 days (product launch, season, big announcement) | 7-11 |
| `hours` | Spikes and dies within 24-48h (game result, celebrity moment, meme) | 0-6 |

A flash trend can still win on Velocity; shelf life tells the creator how fast to ship.

## 5. Creator fit (0-10)

Fit with the user's niche (`./.creator/niche.md` if present) and the chosen platform.

| Signal | Points |
|--------|--------|
| Directly in niche, natural format for the platform | 8-10 |
| Adjacent; can be bridged with a credible angle | 4-7 |
| Off-niche, would read as trend-jacking | 0-3 |
| No niche known | 5 (neutral) |

## 6. Brand safety (0-10)

| Category | Points | Framing |
|----------|--------|---------|
| Neutral / positive (products, culture, how-to, sport, entertainment) | 9-10 | Opportunity |
| Mild controversy, politics-adjacent policy (taxes, student debt, regulation) | 5-8 | Opportunity, factual tone |
| Partisan politics, elections, legal cases, layoffs, health scares | 2-4 | **Handle with care** |
| Death, disaster, violence, crime victims, war, terror, abuse, suicide, active tragedy | 0 | **Exclude from opportunity list** |

## Sensitivity gate (applied BEFORE ranking)

1. **Exclude** (score 0, never in top 3, never suggest a hook/content idea): deaths,
   obituaries within 7 days, disasters, shootings, wars and attacks, crimes with victims,
   missing persons, suicide, self-harm, child harm. List them only in a collapsed
   "Excluded (sensitive)" line by name, so the user knows they were seen.
2. **Handle with care** (allowed, capped at TOS 60, flagged `⚠ care`): elections and
   partisan politics, public-health advisories, layoffs, lawsuits, a celebrity's health,
   financial crashes. Content idea must be informational/service-oriented (explain, help,
   resources), never a joke, meme, or "hot take" format.
3. Obituary of a public figure: excluded from opportunity; a tribute is the user's call,
   not a recommendation.

When in doubt, gate it. A missed trend costs a post; a tone-deaf post costs an account.

## Output conventions

- Show TOS plus sub-scores compactly: `78 (V22 D14 G15 S9 F8 B10)`.
- Bands: 80-100 **ship today**, 60-79 **strong**, 40-59 **maybe / angle-dependent**, <40 skip.
- Every row cites `source + date` taken from the JSON (e.g. `Google Trends, 26 Oct 04:50`).
- Ties: prefer higher Shelf, then higher Fit.

## Worked example

`trump administration student debt collection`: Google Trends traffic 1000+, started
<12h, 2 news items. V18 (fresh, single source) D9 (1000+) G12 (covered, but "what this
means for your loan" explainer angle open) S10 (days: policy rollout) F5 (no niche)
B6 (policy, politics-adjacent) = **60, strong, factual tone**.
