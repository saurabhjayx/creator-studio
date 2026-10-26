# Article templates

Pick by search intent. Word budgets are targets for a 1200-1800 word piece; scale proportionally.
Every template: answer first, no "In this article we will" intro, no "In conclusion" outro.

## 1. News explainer

Intent: news / "what happened with X". Freshness wins; publish fast, update later.

| Section | Words | Content |
|---|---|---|
| Lede (no heading) | 60-90 | What happened, who, when (date from source), why it matters, in 2-3 sentences |
| H2 What happened | 200-300 | Timeline with dates and linked sources |
| H2 Why it matters | 200-300 | Who is affected and how; concrete numbers |
| H2 What people are saying | 150-250 | Reactions from named, linked sources only (Reddit/HN threads ok if linked) |
| H2 What happens next | 100-200 | Known dates, open questions; label speculation as such |
| FAQ | 3-4 Qs | From suggest data |

Title patterns: "<Thing> <did what>: what it means for <audience>", "<Thing> explained: <angle>".
Rule: add an "Updated <date>" line if the story is ongoing.

## 2. How-to

Intent: "how to X". Readers scan; steps must work in order.

| Section | Words | Content |
|---|---|---|
| Intro (no heading) | 50-80 | What they will have at the end, time/cost needed |
| H2 What you need | 80-150 | Bulleted tools/prereqs with prices only if sourced |
| H2 Step 1..N: <verb> <object> | 120-250 each | One action per step; expected result; common mistake |
| H2 Troubleshooting / mistakes | 150-250 | Real failure modes from Reddit/docs research |
| H2 <Next-level question from suggest> | 100-200 | |
| FAQ | 3-5 Qs | |

Title patterns: "How to <X> (<qualifier: in 2026 / on a budget / step by step>)".
Rule: 5-9 steps. More = split into two articles.

## 3. Listicle

Intent: "best X", "X ideas", "ways to X". Each item must earn its slot.

| Section | Words | Content |
|---|---|---|
| Intro | 60-100 | Selection criteria in one sentence; the top pick if it is a "best" list |
| H2 per item: <N>. <Name> | 100-200 each | What it is, who it is for, one specific detail, one downside |
| H2 How we picked / how to choose | 100-200 | Criteria; honest about what was not tested |
| FAQ | 3-4 Qs | |

Title patterns: "<N> <things> for <audience> (<qualifier>)". Use odd or exact numbers, never padded.
Rule: no item without a sourced fact or concrete detail. Every item includes a downside.

## 4. Opinion / hot take

Intent: informational with a point of view. Builds authority, earns links and shares.

| Section | Words | Content |
|---|---|---|
| Thesis (no heading) | 40-80 | The claim, stated plainly in sentence one |
| H2 Why I think <claim> | 300-400 | 2-3 reasons, each with evidence (linked) |
| H2 The best argument against | 200-300 | Steelman the other side fairly |
| H2 Where that argument breaks | 150-250 | Specific rebuttal |
| H2 What to do about it | 100-200 | Practical implications for the reader |

Title patterns: "<Common belief> is wrong", "Why I stopped <X>", "<X> is overrated. Here is what works."
Rules: the opinion must be the author's. Draft the thesis, then mark it
`[CONFIRM: is this your view?]` if the user did not supply the stance. Heavy `[ADD PERSONAL DETAIL]`
use is expected here; opinion without experience reads hollow. No FAQ needed.

## 5. Comparison

Intent: commercial investigation, "X vs Y", "X or Y for <use>".

| Section | Words | Content |
|---|---|---|
| Verdict up front | 60-100 | "Pick X if..., pick Y if..." |
| H2 X vs Y at a glance | table | Price, key features, platforms, best for (sourced, dated) |
| H2 per decision factor (3-5) | 150-250 each | Which wins on this factor and why, with evidence |
| H2 Who should choose X / Y | 150-200 | Persona-based recommendation |
| FAQ | 3-5 Qs | "Is X better than Y for <use>?" etc. |

Title patterns: "<X> vs <Y>: which is better for <use> in <year>".
Rules: prices and features change; cite the pricing page with access date. Disclose if the user
has an affiliate or brand relationship (ask if unclear). If claude-seo is installed, suggest
`/seo-competitor-pages` for schema and conversion layout.

## Intro and headline checks (all templates)

- H1 <= 65 chars, contains the primary keyword, promises one specific thing.
- First sentence would work as the answer in a featured snippet.
- H2s read as a useful table of contents on their own; at least one is a real user question.
- No H2 titled "Introduction" or "Conclusion".
