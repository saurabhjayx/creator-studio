# AI tells catalog

What `scripts/humanize_score.py` measures, why each matters, and the tells it cannot measure
(you catch those in the read-aloud pass). Thresholds are the scorer's own, so you can predict a score.

## Measured by the scorer

| Metric | Weight | What it counts | Score formula (0-100) | Human-typical |
|---|---|---|---|---|
| vocab | 22 | `AI_VOCAB` words/phrases + regex patterns per 100 words | 100 - 30 x density | < 0.3 per 100 |
| specificity | 18 | numbers (x1.5) + mid-sentence capitalized words + first-person pronouns per 100 words | 20 + 16 x density | 4-8 per 100 |
| burstiness | 12 | sentence-length std-dev / mean (cv) | (cv - 0.2) / 0.45 x 100 | cv 0.5-0.9 |
| reveal_bridges | 11 | "Here's the thing", "The truth?", "But here's", "Let that sink in", "Plot twist" | 100 - 30 x count | 0 |
| em_dash | 8 | em dashes, ` -- `, spaced en dashes per 1000 words | 100 - 8 x (d - 2) | <= 2 per 1000 |
| triads | 8 | share of sentences with "X, Y, and Z" | 100 - 250 x (share - 0.08) | < 8% of sentences |
| openers | 8 | top repeated first word share; transition openers (Moreover, Furthermore, Additionally, However, Overall...) | 100 - 250 x (top - 0.2) - 300 x transitions | top < 20%, transitions ~0 |
| hedges | 7 | very, really, quite, arguably, potentially, essentially, ultimately, in order to, a wide range of... per 100 words | 100 - 18 x (d - 1) | < 1 per 100 |
| paragraph_uniformity | 6 | cv of paragraph word counts | cv / 0.5 x 100 | cv > 0.5 |

Ignored by the scorer: headings (`#`), tables, code fences, URLs (link text kept), list markers.
Fewer than 4 sentences or 3 paragraphs: rhythm metrics default to 70 (neutral).

### AI vocabulary, grouped by replacement

| Tell | Say instead |
|---|---|
| delve, dive into, deep dive, explore | look at, get into, cover, or just start |
| leverage, harness, utilize | use |
| robust, comprehensive, holistic | solid, full, complete, or cut |
| seamless(ly) | smooth, easy, or cut |
| crucial, pivotal, paramount, vital | key, important, or show why it matters instead |
| elevate, enhance, optimize, unlock, empower | improve, raise, get, let, help |
| navigate (the complexities of) | deal with, handle, get through |
| landscape, realm, world of | field, market, area, or name it ("the US podcast ad market") |
| tapestry, symphony, labyrinth, beacon | cut the metaphor |
| testament to, stands as, serves as | shows, is |
| foster, bolster, underscore, spearhead | build, support, show, lead |
| myriad, plethora, a wide range of | many, lots, or the actual number |
| vibrant, bustling, nestled, hidden gem | describe one real detail instead |
| intricate, nuanced, multifaceted | complicated, subtle, or explain the actual nuance |
| transformative, groundbreaking, game-changer, cutting-edge | new, big, or say what changed |
| in today's fast-paced / digital age | cut the whole clause |
| it's important/worth noting that | cut; just state it |
| in conclusion, in summary, key takeaway | cut, or end on the last real point |
| not just X but Y / it's not about X, it's about Y | say Y |
| whether you're a beginner or a pro | name the actual reader |

## Not measured (catch on read-aloud)

- **Throat-clearing intros** that restate the title. Start at the first useful sentence.
- **Moralizing outros**: "Ultimately, the choice is yours." "The future is bright."
- **Symmetry**: every section has 3 bullets, every bullet has a bold label and a colon.
- **Staccato fragments for drama.** "No fluff. No filler. Just results." One is a choice; three is a template.
- **Performed sincerity**: "Honestly,", "Let's be real,", "I'll be the first to admit".
- **Rhetorical question chains**: "But what does this mean? And why should you care?"
- **Vague attribution**: "experts say", "studies show", "many believe" with no source.
- **Synonym cycling**: "the tool... the platform... the solution... the software" for one thing.
- **Over-signposting**: "In this article, we will explore...", "Let's break it down."
- **Emoji bullets and bolded first words** on every line in long-form prose.
- **Everything positive**: no tradeoffs, no "this did not work", no opinion.
- **Generic examples**: "a small business owner", "Sarah, a marketing manager". Use real ones from sources or a placeholder.

## Limits

The score is a style heuristic. Technical docs, recipes and legal copy legitimately use lists and
precise vocabulary; a 75 there may be correct. Report that instead of mangling the text to hit 85.
