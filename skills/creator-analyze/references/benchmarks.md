# Engagement benchmarks (rough context only)

**Read this first.** These are rough industry ranges, compiled from the kind of annual reports
social analytics vendors publish (Rival IQ, Hootsuite, Sprout Social, Socialinsider, HypeAuditor
and similar). They disagree with each other, sometimes by 2-3x, because they:

- divide by different denominators (followers vs reach vs impressions vs views),
- sample different account types (brands vs creators, big vs small),
- count different interactions (some include saves/shares, some only likes + comments),
- and shift every year as platforms change what they show and reward.

So: use them to say "roughly typical", "well above typical" or "well below typical".
Never as a pass/fail line, never with decimals, and never quoted as a single "the benchmark is X%".
When you cite one in a report, write "rough industry range, varies by source/year". If the user
needs a current, citable figure, do one WebSearch for the latest vendor report and cite it by
name and year.

The account's own history (median and IQR from `post_stats.py`) is always the better benchmark.

## ER by followers (engagements / followers per post)

| Platform | Rough typical range | Notes |
|----------|---------------------|-------|
| Instagram | ~0.5% - 3% | Brands sit at the low end; small creators (< 10K) often 2-6%. Carousels typically out-engage single images |
| TikTok | ~2% - 8% | Higher because the For You feed shows posts to non-followers; follower-based ER is less meaningful here |
| YouTube (long-form) | ~1% - 5% of views (likes + comments / views) | Use ER by views; subscriber counts poorly predict per-video reach |
| LinkedIn | ~1% - 5% | Personal profiles usually beat company pages by a wide margin |
| X | ~0.02% - 1% | Low across vendor reports; replies/reposts matter more than likes |
| Facebook pages | ~0.05% - 0.5% | Mostly low for organic page posts |

## ER by views / reach

Typically higher than by followers, often roughly 3-10% on short-form video and carousels for
healthy creator accounts. Varies too much by niche and definition to give a tighter range.

## Retention (% of video watched)

| Content | Rough typical | Notes |
|---------|---------------|-------|
| Short-form (< 60 s) | ~30% - 70% avg watched | Shorter videos naturally score higher; compare like-for-like lengths |
| YouTube long-form (8-20 min) | ~30% - 50% avg view duration | Below ~25% usually signals a hook/pacing problem |

## Size effect

Engagement rate falls as audience size grows on almost every platform. A 2% ER at 500K followers
can be stronger than 6% at 3K. Always state follower band when comparing.

## How to word it in a report

Good: "Median ER by followers is 6.5%, above the rough 0.5-3% range typically reported for
Instagram (ranges vary by source and year)."

Bad: "Your ER of 6.53% beats the Instagram benchmark of 1.94%."
