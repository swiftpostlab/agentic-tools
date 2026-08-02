# Foundations: grouping, hierarchy, attention, and the "laws"

Load when a design argument needs a mechanism rather than a preference, or when someone invokes a
named law.

## The grouping principles

From Wagemans et al. (2012), *A century of Gestalt psychology in visual perception I*,
**Psychological Bulletin 138(6), 1172–1217** — the authoritative modern review.

**Wertheimer's classical set (1923):** proximity, similarity, common fate, good continuation,
closure, symmetry, parallelism.

**Later additions:**

| Principle | Credited to | What it means in an interface |
| --- | --- | --- |
| Common region | Palmer, 1992 | A shared background or enclosure groups items, even against proximity — this is what a card *is* |
| Element connectedness | Palmer & Rock, 1994 | Things joined by a line read as one unit — breadcrumbs, steppers, tree views |
| Uniform connectedness | Palmer & Rock, 1994 | A connected region of uniform properties is one unit |
| Synchrony | Alais, Blake & Lee, 1998 | Things changing at the same moment group — loading states, multi-select |
| Generalized common fate | Sekuler & Bennett, 2001 | Things changing together in *any* property, not just motion |

**Prägnanz**, the most general principle, quoted from the review: "the perceptual field and objects
within it will take on the simplest and most encompassing ('ausgezeichnet') structure permitted by
the given conditions."

### Use them honestly

The review calls these **principles, not laws**, and records the criticism that they were formulated
"with little precision" and proliferated. So:

- Correct: "these two are 4 px apart and the group below is 24 px away, so they read as one unit."
- Incorrect: "the law of proximity requires 8 px here."

Also: common fate and synchrony are motion-dependent and mostly irrelevant to static layout. Do not
pad an argument with the ones that do not apply.

### The practical ordering

When principles conflict, in interfaces they usually resolve in roughly this order:

1. **Common region** (an enclosure) beats proximity — a card boundary wins over a small gap.
2. **Proximity** beats similarity — near-but-different groups more strongly than far-but-matching.
3. **Similarity** beats alignment for grouping, but alignment beats similarity for *scanning*.

This ordering is a working heuristic drawn from how the principles interact in practice, **not** a
finding from the review. Labelled tier 4. It is useful for diagnosing a conflict, not for winning an
argument.

## Visual hierarchy

Hierarchy is contrast in a dimension the eye ranks pre-attentively. The dimensions available, roughly
in order of strength:

1. **Size** — largest single lever, and the most abused.
2. **Weight** — strong and cheap; see the bold caveat in `typography.md`.
3. **Colour and contrast** — strong, but the first thing to fail for colour-vision deficiency and in
   dark mode.
4. **Position** — top and leading edge read first, in reading order. Apple's HIG: "People often
   start by viewing items in reading order… from top to bottom and from the leading to trailing
   side." Note *leading*, not *left* — RTL languages invert it.
5. **Space** — isolation makes a thing important without changing the thing at all.

**One primary per view.** If three things are competing to be most important, none of them is. The
common failure is not too little hierarchy but too much: five levels where two would do.

## Cognitive load

The useful distinction:

- **Intrinsic** — the task's own difficulty. You cannot design it away; you can chunk it.
- **Extraneous** — load your interface adds. This is your entire job.
- **Germane** — effort spent building a mental model. Worth preserving.

Concretely: recognition beats recall (Nielsen's heuristic 6); progressive disclosure keeps the
extraneous load proportional to what the user is actually doing; consistency means a pattern learned
once is not re-learned.

## Nielsen's 10 usability heuristics

Nielsen & Molich, 1990; refined 1994 from a factor analysis of 249 usability problems; language
updated 2020 with the heuristics unchanged. NN/g's own framing: they are "broad rules of thumb and
not specific usability guidelines."

1. Visibility of system status
2. Match between the system and the real world
3. User control and freedom — "a clearly marked 'emergency exit'"
4. Consistency and standards
5. Error prevention — "the best designs carefully prevent problems from occurring in the first place"
6. Recognition rather than recall
7. Flexibility and efficiency of use
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, and recover from errors — "plain language (no error codes)"
10. Help and documentation

Best used as an *inspection checklist* by two or three reviewers independently, then merged. A single
reviewer's heuristic evaluation finds a fraction of what a group finds.

## The "laws" — what they actually say

Aggregator sites present these as physics. Each has a scope, and the scope is where design writing
goes wrong.

### Fitts's law (Fitts, 1954, *J. Exp. Psychol.* 47(6), 381–391)

Predicts **time to acquire a target** as a function of distance and target width. Genuinely robust.

Its scope: a **known** target the user is already moving toward. It does not say "bigger is always
better", it does not model visual search, and it does not tell you where to put things you have not
been asked to point at. Legitimate uses: screen edges and corners are effectively infinite-width
targets; small controls far from the pointer cost real time; separating a destructive action from a
common one has a measurable safety value.

### Hick–Hyman law (Hick, 1952; Hyman, 1953)

Decision time rises logarithmically with the number of **known, ordered** alternatives.

Its scope is the part that gets dropped. Landauer & Nachbar (1985) and later work show it models
choice among familiar, well-organised options — not visual search through an unfamiliar menu, which
is what designers usually invoke it for. "Hick's law says cut the nav to five items" is a misuse:
searching an unfamiliar list of 20 is a search problem, not a choice-reaction problem.

### Miller (1956), "The Magical Number Seven, Plus or Minus Two"

**The most abused citation in interface writing.** Miller's paper is about the span of immediate
memory for unrelated items. It is not about menu length, navigation, or chunking a form, and Miller
proposed no UI rule. Cowan (2001) puts the working-memory limit closer to **4 ± 1** anyway.

If you want to argue for a shorter menu, argue from scanning cost or decision cost. Do not cite
Miller.

### Aesthetic-usability effect (Kurosu & Kashimura, 1995; Tractinsky, Katz & Ikar, 2000)

Attractive interfaces are *rated* more usable, and the effect is real. Read it as a **measurement
hazard** first: it means your usability test results are biased by visual polish, and that
attractiveness can mask real problems in evaluation. It is not a licence to prioritise looks over
function.

## Research methods, briefly

- **ISO 9241-11:2018** defines usability as effectiveness, efficiency, and satisfaction **in a
  specified context of use**. The context clause is the part people drop; "usable" with no stated
  user and task is not a claim.
- **The "5 users" claim.** Nielsen & Landauer (1993) give an expected value. Faulkner (2003,
  *Behavior Research Methods, Instruments, & Computers* 35(3), 379–383) resampled from a pool of 60
  and found that sets of 5 users caught anywhere from **55% to 99%** of known problems; 10 users
  raised the worst case to **80%**, and 20 users to **95%**. Five users is a statement about the
  average run. Any single run can miss nearly half. Quote the variance, not the mean.
- **Heuristic evaluation finds different defects than user testing.** Run both, or say which you did
  not run.
