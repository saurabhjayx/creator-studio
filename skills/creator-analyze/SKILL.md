---
name: creator-analyze
description: "Post performance analysis: which of a creator's posts perform better or worse and WHY. Reads a CSV export (Instagram, TikTok, YouTube Studio, LinkedIn, X), a pasted metrics table, or public post URLs; computes engagement rate, weighted engagement score, baselines, outliers, best posting windows, format/hook/caption-length/hashtag breakdowns; then forms evidence-graded causal hypotheses and turns them into do-more/stop-doing rules and A/B tests. Use when user says analyze my posts, why did this post flop, why did this go viral, what's working, content performance, engagement rate, best time to post, post analytics, content audit, insights export. Triggers on: analyze, analytics, performance, engagement rate, best time to post, what works, flopped, viral, insights CSV."
user-invocable: true
argument-hint: "<posts.csv | pasted table | post URLs> [--followers N]"
model: opus
allowed-tools: Read, Write, Bash, WebFetch, WebSearch, Agent
license: MIT
metadata:
  author: creator-studio
  version: "1.0.0"
  tier: L
---

# Creator Analyze: what works, what flops, and why

The job is to explain performance, not to describe it. A chart that says "carousels
did better" is half an answer. The full answer says how much better, on how many posts,
what else differed about those posts, and what to test next to be sure.

## Token budget

Tier **L** (opus / high effort).

| Item | Budget |
|------|--------|
| Script calls | Any. Typically 1-3 runs of `post_stats.py` (text + `--json`, maybe `--metric er`) |
| WebFetch | <= 6. Only for the URL input mode, or to read full captions of top/bottom posts missing from the CSV |
| WebSearch | <= 10, usually 0-2. Only to check whether a winning post rode a dated trend or news event |
| Subagent | Delegate to `creator-analyst` when the dataset is > 300 rows or spans several accounts/platforms |
| Output | As long as the evidence supports. The scorecard + rules + tests must fit on one screen; detail below it |

Never paste the whole CSV into context. Let the script summarise it, then read only the
rows you need (top 5, bottom 5, outliers).

## Inputs (in order of preference)

1. **CSV export** (best). Meta Business Suite / Instagram Insights, TikTok Studio, YouTube
   Studio "Content" export, LinkedIn post analytics, X analytics. Column names are matched
   flexibly; see `references/metrics-glossary.md` for the alias map and what each metric means
   on each platform.
2. **Pasted table**. Write it to a temp CSV in the scratchpad (header row + one row per post),
   then treat it exactly like mode 1.
3. **Public post URLs**. WebFetch each (<= 6). Public pages usually expose likes and comments,
   sometimes views; they almost never expose reach, impressions, saves, shares, or watch time.
   Say exactly which metrics were and were not visible. Build a CSV from what you got and
   run the script, but downgrade every conclusion one evidence level (strong -> moderate),
   because engagement without reach cannot separate "good post" from "big distribution".

Ask for follower count if it is not given; ER-by-followers needs it. Proceed without it if
the user doesn't know.

## Workflow

1. **Locate the script.**
   `S="${CLAUDE_SKILL_DIR}/../creator/scripts/post_stats.py"`
2. **Run it.**
   `python3 "$S" posts.csv --followers 12000` for the readable report, and
   `python3 "$S" posts.csv --followers 12000 --json > /tmp/stats.json` if you need exact numbers.
   If the script exits with "no metric columns recognised", show the user their headers and
   map them by hand (rename the header row in a scratch copy). Check `columns_mapped` in the
   JSON: a wrong mapping (e.g. "reach" taken as views on a platform where impressions exist)
   changes every rate.
3. **Pick the ranking metric deliberately.** Default is weighted score
   (saves*3 + shares*4 + comments*2 + likes), which rewards posts that spread and get kept.
   Re-run with `--metric er` when reach varies wildly (one post boosted, one cross-posted)
   so a big-reach post does not win just for being seen. State which metric the verdict uses.
4. **Sanity-check the data.** Under 15 posts: say every pattern is anecdotal. Posts younger
   than ~7 days are still accumulating; exclude or flag them. Paid/boosted posts distort
   reach; ask if any were boosted. A format with n < 3 is never a finding.
5. **Read the top 5 and bottom 5 posts in full** (captions, plus the post itself via URL if
   the caption alone does not explain it). For each, note: hook (first line), topic, promise
   to the viewer, format, length, posting time, trend/news tie-in, CTA.
6. **Form causal hypotheses.** For each candidate driver (hook, topic, format, length,
   timing, trend-riding, hashtags, CTA), write: the claim, the evidence (group medians and
   lift from the script, n per group), and an evidence grade:

   | Grade | Bar |
   |-------|-----|
   | **Strong** | Lift >= 50% on n >= 5 per group, consistent across top AND bottom lists, and no obvious confounder |
   | **Moderate** | Lift >= 25% on n >= 3, or strong lift with one plausible confounder |
   | **Weak** | n < 3, lift < 25%, or the pattern rests on 1-2 outlier posts |

7. **Separate correlation from causation.** For every Strong/Moderate claim, check the
   confounders explicitly: did the winning format also use the winning hook more often? Did
   the winners cluster in one month (account growth, algorithm change, seasonal topic)? Is
   "best weekday" just where the best topic happened to land? Cross-tab two dimensions by
   hand from the JSON posts when needed. Say "X is associated with Y" unless a confounder check
   holds up; reserve "X drives Y" for patterns that survive it. Timing results are the most
   confounded of all; treat them as weak unless n is large.
8. **Check trend-riding** for the top 1-3 outliers only: did the topic match a news event
   or trend that week? One WebSearch or `trends.py news --q "<topic>" --days 30` each. A
   trend-driven spike is not a repeatable format win; label it.
9. **Write the report** in the format below. Compare against `references/benchmarks.md` only
   as rough context, never as a pass/fail.
10. **Offer to save** the report as `analysis-YYYY-MM-DD.md` next to the CSV so the next
    run can compare.

## Output format

```markdown
# Performance analysis: <account> (<platform>), <date range>, n=<posts>

## Scorecard
| Metric | Value | Rough benchmark | Read |
|---|---|---|---|
| Median ER by views | 7.7% | (account's own IQR 6.5-10%) | ... |
| Median ER by followers | 6.5% | IG roughly 0.5-3% (varies by source/year) | Above typical range |
| Median views | ... | (account's own IQR) | ... |
| Cadence | 3.1 posts/week | ... | ... |
| Trend, 2nd half vs 1st | -15% | n/a | Slight decline, check confounders |
One-line verdict: <the single most important finding>.

## Winners vs losers
| | Top 5 | Bottom 5 |
|---|---|---|
| Formats | 4 carousel, 1 reel | 4 image, 1 reel |
| Hooks | 3 question, 2 contrarian | 3 other, 1 story, 1 number |
| Median caption length | ... | ... |
| Hashtags | ... | ... |
| Posting times | ... | ... |
| Trend tie-in | ... | ... |

## Why (hypotheses, graded)
| # | Hypothesis | Evidence | Grade | Confounders checked |
|---|---|---|---|---|
| 1 | Question hooks lift saves+comments | question n=8 median +93% vs all; 3 of top 5 | Strong | Not explained by format (question+reel also above median) |

## Rules
**Do more of**
1. ... (one line, backed by hypothesis #)
**Stop doing**
1. ...
(5 rules total, each tied to a hypothesis; no rule without evidence)

## Next 3 A/B tests
| Test | Variant A | Variant B | Hold constant | Success metric | Posts needed |
|---|---|---|---|---|---|
| Hook | Question | Statement, same topic | format, time, length | saves per 1K views, +25% | 4 per arm |

## Best posting windows
| Window | n | Median lift | Confidence |
|---|---|---|---|
Caveat: timing is the weakest signal; test before reorganising the calendar.

## Data notes
What was missing, what was excluded, which metric ranked posts.

Next: ...
```

Rules for the report:
- Every number comes from the script output or the fetched page. No invented benchmarks,
  no fake precision ("posts at 6:47 pm perform 23.4% better").
- Name n next to every group claim.
- A/B tests change one variable, hold the rest, and name a metric + minimum posts per arm
  (>= 3, ideally 5). Success metric should be a rate (ER, saves per 1K views, % watched), not
  raw views, so reach luck doesn't decide the test.
- If the data cannot support a finding, say "not enough data" instead of guessing.

## Examples

```
/creator-analyze ~/Downloads/instagram_insights.csv --followers 12000
/creator-analyze  (then paste a table of last 20 TikToks: date, views, likes, comments, shares, saves)
/creator-analyze https://www.youtube.com/watch?v=... https://www.youtube.com/watch?v=...
"Why did my last three reels flop?"   (ask for the export, or the URLs)
```

Try it on the bundled synthetic dataset:
`python3 "${CLAUDE_SKILL_DIR}/../creator/scripts/post_stats.py" "${CLAUDE_SKILL_DIR}/../../tests/fixtures/sample_posts.csv" --followers 12000`
(`tests/fixtures/sample_posts.csv` is **fake data** for a cooking account, built with known
patterns: carousels and question/contrarian hooks win, 11+ hashtags lose. Use it to see the
output shape; never quote it as real benchmarks.)

## References

- `references/metrics-glossary.md`: every metric, formula, platform naming, column aliases, pitfalls
- `references/benchmarks.md`: rough engagement-rate ranges by platform, with caveats
- Platform specs: `skills/creator/references/platforms.md`
- Heavy datasets: delegate to the `creator-analyst` agent with the CSV path and follower count

Next: turn the winning hooks into new drafts with `/creator-hooks`, plan the A/B tests into
the calendar with `/creator-calendar`, or see what peers do differently with `/creator-competitor`.
