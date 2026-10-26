# Rewrite playbook

Four passes, in order. Each pass has one job; doing them together causes drift in meaning.

## Before you touch anything: the locked list

Write it down (scratch, not output): H1-H6 text, every URL, every number and unit, quotes,
proper nouns, product/brand names, code, and SEO keywords with their current counts.
After the rewrite, diff against it. Any loss is a bug, not a style choice.

## Pass 1: structure and rhythm

Goal: burstiness cv >= 0.5, paragraph cv >= 0.5, no reveal bridges.

- **Cut the first paragraph** if it only sets the scene ("In today's...", "Have you ever wondered...").
  Test: does the piece lose any information without it? Usually not.
- **Cut the outro** if it summarizes what was just said. End on the last useful point, a concrete
  next step, or an opinion.
- **Vary length deliberately.** Pattern to aim for: long explanatory sentence, short punch,
  medium. Never three sentences of the same length in a row.
- **Uneven paragraphs.** One-line paragraphs for emphasis; longer ones for explanation. Avoid
  four paragraphs of 3 sentences each.
- **Reveal bridges -> direct statement.**
  - Before: "Here's the thing: most creators quit too early."
  - After: "Most creators quit around video 20, right before the algorithm has enough data."
- **Rhetorical question chains -> one question at most**, and only if the next sentence answers it.

## Pass 2: vocabulary and punctuation

Goal: vocab >= 90, em_dash >= 80, triads >= 80, hedges >= 90, openers >= 85.

- Use the replacement table in `ai-tells.md`. If the plain version says nothing, delete the sentence.
- **Triads.** Keep the strongest one or two items, or turn a real list into bullets.
  - Before: "It boosts engagement, builds trust, and drives growth."
  - After: "It gets more replies. Replies are what the algorithm counts."
- **Em dashes.** Period for a new thought, comma for an aside, colon for a payoff, parentheses for
  a true aside. Keep one only where nothing else works.
- **Transition openers.** Delete "Moreover/Furthermore/Additionally". If the link between
  sentences is unclear without it, the sentences are in the wrong order.
- **Hedges.** Delete "very/really/quite/essentially/ultimately". Replace "may potentially" with
  the honest claim or a source.
- **Synonym cycling.** Pick one name for a thing and reuse it.

## Pass 3: voice and specificity

Goal: specificity >= 70 without inventing anything.

- Promote specifics already present: move the number, name or date to the front of the sentence.
- Replace generic nouns with the specific one from the source material ("a popular tool" -> "Canva").
- Add a point of view where the piece is neutral to the point of uselessness: which option would you
  pick and why? Mark it as opinion.
- Placeholders where only the author can supply truth:
  - `[ADD PERSONAL DETAIL: a time you tried this and what happened, 1-2 sentences]`
  - `[ADD PERSONAL DETAIL: your real number, e.g. subscribers before/after]`
  - `[ADD SOURCE: citation for this claim]` when a claim has none.
  Max one placeholder per ~300 words; more means the draft needs an interview, not a rewrite.
- Never invent: anecdotes, customers, names, quotes, numbers, test results, credentials.

## Pass 4: read aloud

Read every sentence as speech. Fix:
- Anything you would not say to a smart friend across a table.
- Tongue-twisters and noun stacks ("content strategy optimization framework").
- Paragraphs ending on a moral or a slogan.
- Openers that repeat ("You... You... You...").
- Any sentence that survived passes 1-3 but still sounds like a brochure.

## Voice card

For `--mode voice`. Fill from the samples, then rewrite toward it. Show it in the output.

| Trait | Value from samples |
|---|---|
| Sentence length | mean __ words, cv __ (from scorer on samples) |
| Paragraphs | typical __ sentences; one-liners: often / rare |
| Person | I / we / you / impersonal |
| Contractions | always / mixed / never |
| Signature words/phrases | up to 8, quoted from samples |
| Punctuation habits | parentheses? colons? em dashes? exclamation marks? |
| Openers | how they start pieces (story, claim, number, question) |
| Closers | how they end (CTA, joke, question, flat stop) |
| Humor | none / dry / self-deprecating / playful |
| Never says | words in AI_VOCAB that do not appear in samples, plus anything off-voice |

Rules: copy habits, not sentences. If the samples themselves score low (the user writes in an AI-ish
style), say so and ask whether to match the voice or improve it.

## Worked example

Before (score 34):
> In today's fast-paced digital landscape, email marketing remains a crucial tool for businesses.
> It's important to note that a robust strategy can help you foster engagement, build trust, and
> drive conversions. Let's dive in.

After (score 88):
> Email still pays. Litmus puts the return at about $36 per $1 spent [ADD SOURCE: confirm the
> current Litmus figure and link it]. The catch is that most lists go stale in a year, so the work
> is less about writing and more about keeping the list alive.
>
> [ADD PERSONAL DETAIL: your own open rate or list size, if you want to share it]

What changed: intro clause cut, 4 AI words removed, triad collapsed to one claim, generic claim
replaced by a sourced number flagged for verification, placeholder instead of an invented story.
