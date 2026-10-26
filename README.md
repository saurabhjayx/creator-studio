# creator-studio

**Trend-to-content toolkit for Claude Code.** Find what's trending right now, in general or in your
niche, and turn it into reels, Shorts, YouTube scripts and publish-ready articles. It also humanizes
AI drafts and tells you why some of your posts work and others don't.

13 skills, 4 subagents, no API keys. The trend data comes from free public feeds, and the bundled
Python scripts use only the standard library.

```
/creator trends                      → what's hot right now, ranked by opportunity
/creator niche "home workouts"       → trending topics + real audience questions in your niche
/creator reels --niche "home workouts" → 5-10 reel ideas with hooks and timed scripts
/creator article --trending ai-tools  → researched, cited, humanized blog post + SEO meta
/creator humanize draft.md            → benchmark rewrite with a before/after human score
/creator analyze my_posts.csv         → which posts win or lose and why, plus A/B tests to run next
```

## Two ways to find ideas

| Mode | Command | Use when |
|------|---------|----------|
| **A. Pick trending content for me** | `/creator trends [--geo IN] [--platform reels]` | You want to ride what's hot today (news, searches, culture) |
| **B. My niche** | `/creator niche "<your niche>" [--deep]` | You have a niche and want what *your* audience is asking about this week |

Mode B can save a niche profile to `./.creator/niche.md`. The calendar, reels and article skills then
reuse it automatically.

## Skills

| Skill | Tier | What it does |
|-------|------|--------------|
| `creator` | router | Command center that routes `/creator <cmd>` to the right skill |
| `creator-trends` | M | Live trends with a transparent Trend Opportunity Score, shelf life and best format |
| `creator-niche` | M | Niche radar: news, autocomplete questions, Reddit pain points, debates, evergreen gaps |
| `creator-reels` | M | Reels/Shorts/TikTok ideas: hook, format, beat-by-beat script, shot list, CTA |
| `creator-script` | M | 8-15 min YouTube script with retention engineering, chapters and title/thumbnail options |
| `creator-article` | L | Trend → researched, cited, SEO-ready article, auto-humanized to a score of 85 or higher |
| `creator-humanize` | L | Benchmark humanizer: scores, rewrites in passes and re-scores. Audit and voice-match modes |
| `creator-analyze` | L | Post performance: winners vs losers, causal hypotheses, best times, A/B tests |
| `creator-competitor` | M | Competitor top topics, cadence and gap list crossed with your niche's trends |
| `creator-hooks` | S | 10 scroll-stopping hooks from 25 formulas, or scores and rewrites your hook |
| `creator-captions` | S | Platform-native captions, hashtag sets, titles, thumbnail text, alt text |
| `creator-repurpose` | M | One piece → reels, carousel, X thread, LinkedIn, newsletter, pins |
| `creator-calendar` | M | 7/14/30-day calendar mixing trend slots with evergreen pillars, exported as CSV |

## Token tiers

Each skill pins a model tier, so simple jobs cost little and hard jobs get more reasoning.

| Tier | Model / effort | Budget | Skills |
|------|----------------|--------|--------|
| **S** light | Haiku / low | 0-2 web calls, ~400 words | hooks, captions |
| **M** medium | Sonnet / medium | ≤5 searches, ≤3 fetches | trends, niche, reels, script, repurpose, calendar, competitor |
| **L** heavy | Opus / high | ≤10 searches, ≤6 fetches | article, humanize, analyze |

Skills fetch cheap structured JSON (`skills/creator/scripts/trends.py`) before spending web searches, never re-fetch
data already in the conversation, and escalate to a heavier tier only when needed. Each SKILL.md has a
`## Token budget` section. The full rules are in [CONVENTIONS.md](CONVENTIONS.md).

## Data sources (keyless)

`skills/creator/scripts/trends.py` reads these feeds and fails soft if one is down:

- Google Trends daily trending searches (RSS, per country)
- Google News search (RSS)
- Google autocomplete, to find what people actually ask (`--deep` runs the alphabet-soup expansion)
- Reddit top posts per subreddit (RSS)
- Hacker News (Algolia API)
- Wikipedia most-viewed articles
- YouTube channel uploads with view counts (RSS)

Platform-native signals such as trending audios or challenges have no free API. The skills find them
with web search and label them **verify in-app**.

```bash
python3 skills/creator/scripts/trends.py pulse --geo US
```

## Install

Requirements: Claude Code, which is included with **Claude Pro and Max** plans (or an API key), and
Python 3.9+.

**Option 1: plugin marketplace (recommended)**

```
/plugin marketplace add saurabhjayx/creator-studio
/plugin install creator-studio@creator-studio
```

**Option 2: manual**

```bash
git clone https://github.com/saurabhjayx/creator-studio && cd creator-studio && ./install.sh
```

Restart Claude Code, then run `/creator trends`.

Windows: `./install.ps1`. Uninstall: `./uninstall.sh` / `./uninstall.ps1`, or `/plugin uninstall creator-studio`.

**Claude.ai (web/desktop chat):** zip any single `skills/<name>/` folder and upload it under
Settings → Capabilities → Skills. Skills that call `trends.py` need code execution enabled, and
without it they fall back to web search.

## Testing

```bash
./tests/run_tests.sh          # static validation + script self-tests + live source check
./tests/run_tests.sh --evals  # also runs 14 real eval cases (one per skill) through `claude plugin eval`
```

The eval sandbox has no network, so the trends and niche cases replay feed snapshots recorded live
(`tests/fixtures/pulse_US.json`, `niche_home-espresso.json`). Live fetching is covered by the
live-source step of `run_tests.sh`. Set `CLAUDE_BIN` if `claude` is not on your PATH.

## Honest limits

- No private platform analytics. `creator-analyze` works from your CSV export or what's publicly visible.
- View and volume numbers appear only when a source returned them. Everything else is labelled as an estimate.
- The humanizer improves readability and voice. Don't use it to pass off AI writing where disclosure is required (school, journalism).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md) and [CHANGELOG.md](CHANGELOG.md).

## License

MIT
