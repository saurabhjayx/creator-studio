#!/usr/bin/env python3
"""Score text 0-100 for "human-ness" with a transparent per-metric breakdown. Stdlib only (py3.9+).

Usage:
  humanize_score.py draft.md            Markdown report
  humanize_score.py draft.md --json     JSON (for skills/agents)
  cat draft.md | humanize_score.py -    read stdin
  humanize_score.py --selftest          run built-in asserts

This measures readability/voice patterns that make prose read as machine-written.
It is a writing-quality heuristic, not an AI detector, and makes no detection claims.
"""
import argparse
import json
import re
import statistics
import sys

# Words/phrases that cluster in LLM output. Single words match common inflections (stem + \w*).
AI_VOCAB = (
    "delve", "tapestry", "testament", "landscape", "realm", "navigate", "leverage", "seamless",
    "robust", "pivotal", "crucial", "elevate", "unlock", "embark", "intricate", "nuanced",
    "vibrant", "foster", "underscore", "multifaceted", "showcase", "streamline", "holistic",
    "paramount", "meticulous", "comprehensive", "dynamic", "synergy", "paradigm", "harness",
    "empower", "bolster", "beacon", "cornerstone", "game-changer", "game changer", "transformative",
    "unwavering", "ever-evolving", "ever-changing", "cutting-edge", "groundbreaking", "revolutionize",
    "myriad", "plethora", "endeavor", "commendable", "noteworthy", "invaluable", "resonate",
    "captivate", "intricacies", "underpin", "spearhead", "facilitate", "optimize", "enhance",
    "boast", "nestled", "bustling", "symphony", "labyrinth", "treasure trove", "hidden gem",
    "in today's fast-paced", "in today's digital age", "in the world of", "it's important to note",
    "it is important to note", "it's worth noting", "it is worth noting", "in conclusion",
    "in summary", "let's dive in", "let's dive into", "dive into", "deep dive", "let's explore",
    "at the end of the day", "when it comes to", "a testament to", "plays a crucial role",
    "plays a vital role", "stands as", "serves as a", "whether you're", "look no further",
    "unlock the power", "the power of", "embark on a journey", "navigate the complexities",
    "key takeaway", "furthermore", "moreover", "additionally",
)
# Regex tells that are not plain phrases.
AI_PATTERNS = (
    (r"\bnot (?:just|only|merely) [^.,;!?]{1,40}?,? but(?: also)?\b", "not-just-X-but-Y"),
    (r"\bit'?s not about [^.;!?]{1,40}?,? it'?s about\b", "it's-not-X-it's-Y"),
    (r"\b(?:isn't|aren't|wasn't) just [^.;!?]{1,40}?[.,;:—-] ?(?:it'?s|they'?re)\b", "isn't-just-X"),
)
HEDGES = (
    "very", "really", "quite", "arguably", "potentially", "perhaps", "essentially", "basically",
    "actually", "simply", "generally", "typically", "ultimately", "overall", "somewhat",
    "relatively", "in order to", "a variety of", "a wide range of", "various", "numerous",
    "it can be said", "one could argue", "to some extent", "in many ways", "certainly", "truly",
)
REVEALS = (
    r"here'?s the (?:thing|truth|kicker|catch|deal|problem|secret)", r"here'?s why\b",
    r"\bthe (?:truth|catch|kicker|twist|result|answer|secret|best part|real reason|reality)\?",
    r"\bbut here'?s\b", r"\bspoiler:", r"\bplot twist", r"\blet that sink in",
    r"\bthe bottom line\??:", r"\band honestly\?", r"\bwant to know (?:the|a) secret",
)
TRANSITIONS = ("moreover", "furthermore", "additionally", "however", "consequently", "ultimately",
               "overall", "importantly", "notably", "in addition", "in conclusion", "firstly")
TRIAD = re.compile(r"\b[\w'-]+(?: [\w'-]+){0,2}, [\w'-]+(?: [\w'-]+){0,2},? (?:and|or) [\w'-]+", re.I)
FIRST_PERSON = re.compile(r"\b(?:I|I'm|I've|I'd|me|my|mine|we|our|us)\b")
NUMBER = re.compile(r"\b\d[\d,.:%$]*\b|\$\d")
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")

WEIGHTS = {"vocab": 22, "burstiness": 12, "em_dash": 8, "triads": 8, "hedges": 7,
           "paragraph_uniformity": 6, "openers": 8, "reveal_bridges": 11, "specificity": 18}

_vocab_res = [(re.compile(r"\b%s%s" % (re.escape(p.rstrip("e")) if " " not in p and "-" not in p
                                       else re.escape(p), r"\w*" if " " not in p else r"\b"), re.I), p)
              for p in AI_VOCAB]
# ponytail: stem matching (navigat\w*) over-matches rare words like "elevator"; swap for an
# explicit inflection list if false positives show up in real drafts.
_pat_res = [(re.compile(p, re.I), name) for p, name in AI_PATTERNS]
_hedge_res = [re.compile(r"\b%s\b" % re.escape(h), re.I) for h in HEDGES]
_reveal_res = [re.compile(r, re.I) for r in REVEALS]


def clamp(x):
    return max(0, min(100, int(round(x))))


def prose_lines(text):
    """Yield (line_no, cleaned_line) for prose; skip code fences, headings, tables, URLs."""
    fence = False
    for n, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or not s or s.startswith(("#", "|", "<!--", "---")):
            yield n, ""
            continue
        s = re.sub(r"\]\([^)]*\)", "]", s)          # keep link text, drop URL
        s = re.sub(r"https?://\S+", "", s)
        s = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", s)  # list markers
        yield n, s.replace("**", "").replace("__", "")


def split_sentences(line):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[\"'A-Z0-9(\[])", line) if WORD.search(s)]


def analyze(text):
    sents, paras, cur = [], [], 0  # sents: (line_no, sentence)
    for n, line in prose_lines(text):
        if not line:
            if cur:
                paras.append(cur)
            cur = 0
            continue
        for s in split_sentences(line):
            sents.append((n, s))
            cur += len(WORD.findall(s))
    if cur:
        paras.append(cur)
    body = " ".join(s for _, s in sents)
    words = WORD.findall(body)
    nw = max(len(words), 1)
    per100 = lambda c: 100.0 * c / nw
    flags, m = [], {}

    def flag(n, s, reason):
        flags.append({"line": n, "sentence": s[:160], "reason": reason})

    # (a) AI vocabulary
    hits = {}
    for n, s in sents:
        found = [p for r, p in _vocab_res if r.search(s)] + [nm for r, nm in _pat_res if r.search(s)]
        for p in found:
            hits[p] = hits.get(p, 0) + 1
        if found:
            flag(n, s, "AI vocab: " + ", ".join(found))
    d = per100(sum(hits.values()))
    m["vocab"] = {"score": clamp(100 - 30 * d), "per_100_words": round(d, 2),
                  "hits": dict(sorted(hits.items(), key=lambda kv: -kv[1]))}

    # (b) burstiness
    lens = [len(WORD.findall(s)) for _, s in sents]
    if len(lens) >= 4:
        cv = statistics.pstdev(lens) / max(statistics.mean(lens), 1)
        m["burstiness"] = {"score": clamp((cv - 0.2) / 0.45 * 100), "cv": round(cv, 2),
                           "mean_len": round(statistics.mean(lens), 1)}
    else:
        m["burstiness"] = {"score": 70, "note": "too few sentences"}

    # (c) em dashes
    dashes = 0
    for n, s in sents:
        c = s.count("—") + s.count(" -- ") + s.count(" – ")
        if c:
            dashes += c
            flag(n, s, "em dash x%d" % c)
    d = 1000.0 * dashes / nw
    m["em_dash"] = {"score": clamp(100 - 8 * max(0, d - 2)), "per_1000_words": round(d, 1)}

    # (d) triads
    tri = 0
    for n, s in sents:
        if TRIAD.search(s):
            tri += 1
            flag(n, s, "triad list (X, Y, and Z)")
    frac = tri / max(len(sents), 1)
    m["triads"] = {"score": clamp(100 - 250 * max(0, frac - 0.08)), "sentence_share": round(frac, 2)}

    # (e) hedges / filler
    hc = sum(len(r.findall(body)) for r in _hedge_res)
    d = per100(hc)
    m["hedges"] = {"score": clamp(100 - 18 * max(0, d - 1)), "per_100_words": round(d, 2)}

    # (f) paragraph uniformity
    if len(paras) >= 3:
        cv = statistics.pstdev(paras) / max(statistics.mean(paras), 1)
        m["paragraph_uniformity"] = {"score": clamp(cv / 0.5 * 100), "cv": round(cv, 2)}
    else:
        m["paragraph_uniformity"] = {"score": 70, "note": "too few paragraphs"}

    # (g) repeated / transition openers
    firsts = [(n, s, s.split()[0].strip("\"'(").lower().rstrip(",")) for n, s in sents if s.split()]
    counts = {}
    for _, _, w in firsts:
        counts[w] = counts.get(w, 0) + 1
    trans = 0
    for i, (n, s, w) in enumerate(firsts):
        low = s.lower()
        if any(low.startswith(t) for t in TRANSITIONS):
            trans += 1
            flag(n, s, "transition opener")
        elif i and firsts[i - 1][2] == w and w not in ("i",):
            flag(n, s, "same opener as previous sentence: '%s'" % w)
    top = max(counts.values()) / len(firsts) if firsts else 0
    tf = trans / max(len(firsts), 1)
    m["openers"] = {"score": clamp(100 - 250 * max(0, top - 0.2) - 300 * tf),
                    "top_opener_share": round(top, 2), "transition_share": round(tf, 2)}

    # (h) reveal bridges
    rv = 0
    for n, s in sents:
        if any(r.search(s) for r in _reveal_res):
            rv += 1
            flag(n, s, "reveal bridge")
    m["reveal_bridges"] = {"score": clamp(100 - 30 * rv), "count": rv}

    # (i) specificity (positive signal)
    nums = len(NUMBER.findall(body))
    fp = len(FIRST_PERSON.findall(body))
    proper = sum(len(re.findall(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]+", s)) for _, s in sents)
    d = per100(nums * 1.5 + proper + fp)
    m["specificity"] = {"score": clamp(20 + 16 * d), "numbers": nums, "proper_nouns": proper,
                        "first_person": fp, "per_100_words": round(d, 2)}

    total = sum(m[k]["score"] * w for k, w in WEIGHTS.items()) / sum(WEIGHTS.values())
    flags.sort(key=lambda f: f["line"])
    return {"score": clamp(total), "words": len(words), "sentences": len(sents),
            "metrics": m, "weights": WEIGHTS, "flags": flags}


def report(r):
    out = ["# Humanize score: %d/100" % r["score"], "",
           "%d words, %d sentences. Target >= 85." % (r["words"], r["sentences"]), "",
           "| Metric | Score | Weight | Detail |", "|---|---|---|---|"]
    for k, w in WEIGHTS.items():
        d = {x: y for x, y in r["metrics"][k].items() if x != "score"}
        out.append("| %s | %d | %d | %s |" % (k, r["metrics"][k]["score"], w,
                                              json.dumps(d, ensure_ascii=False)[:120]))
    out += ["", "## Flagged sentences (%d)" % len(r["flags"]), ""]
    out += ["- L%d [%s] %s" % (f["line"], f["reason"], f["sentence"]) for f in r["flags"]]
    return "\n".join(out)


AI_SAMPLE = """In today's fast-paced digital landscape, it's important to note that content creation is not just a skill, but a crucial pillar of success. Moreover, creators must navigate an ever-evolving realm of platforms, algorithms, and audiences.

Let's dive in. Leveraging robust tools can seamlessly elevate your workflow, unlock new opportunities, and foster meaningful engagement. Furthermore, a holistic strategy serves as a testament to your commitment.

Here's the thing: consistency is pivotal. Additionally, embracing a multifaceted approach empowers creators to delve deeper into the intricate tapestry of audience needs. In conclusion, the journey is transformative, vibrant, and rewarding."""

HUMAN_SAMPLE = """I posted 41 videos on TikTok last March. Three did anything.

The one that hit 210k views was a 9-second clip of my dog stealing a bagel off the counter in our Denver apartment. No script. Shot it on a cracked iPhone 12 because Maya was laughing too hard to hold the good camera.

Everything I had planned for weeks flopped. My editing setup cost $1,400 and the bagel video beat all of it. So now I shoot first and think later, which my old boss at Hearst would hate.

Is that a strategy? Probably not. But my average views went from 800 to about 3,000 in two months, and I'm not arguing with that."""


def demo():
    ai, hu = analyze(AI_SAMPLE), analyze(HUMAN_SAMPLE)
    print("AI sample: %d  |  human sample: %d" % (ai["score"], hu["score"]))
    assert ai["score"] < hu["score"] - 30, (ai["score"], hu["score"])
    assert ai["score"] < 50 and hu["score"] >= 75, (ai["score"], hu["score"])
    assert ai["metrics"]["vocab"]["score"] < hu["metrics"]["vocab"]["score"]
    assert ai["metrics"]["specificity"]["score"] < hu["metrics"]["specificity"]["score"]
    assert any("reveal" in f["reason"] for f in ai["flags"])
    assert all(f["line"] >= 1 for f in ai["flags"])
    assert analyze("")["score"] >= 0  # empty input must not crash
    print("selftest OK")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", nargs="?", help="text/markdown file, or - for stdin")
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        return demo()
    if not a.file:
        p.error("file required (or --selftest)")
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    r = analyze(text)
    print(json.dumps(r, indent=2, ensure_ascii=False) if a.json else report(r))


if __name__ == "__main__":
    main()
