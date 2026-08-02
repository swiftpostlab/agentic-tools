# Readable long-form content

Load when the job is an article, blog post, documentation page, or any screen where someone must
read more than a paragraph.

## Start by deleting

Nielsen's 1997 study rewrote the same content five ways and measured on time, errors, memory, and
site-structure understanding:

| Version | Usability improvement |
| --- | --- |
| Concise text (≈half the word count) | **58%** |
| Scannable layout (bulleted, structured) | **47%** |
| Objective language (no marketing puff) | **27%** |
| All three combined | **124%** |

**Conciseness beat formatting.** The reflex when told "this is a wall of text" is to add subheadings
and bullets. The larger measured effect came from removing words.

Caveats to state when citing this: it is a 1997 lab study, the source **does not disclose the sample
size**, and the percentages are improvements on composite measures. The *ordering* is the durable
finding; the exact numbers are indicative.

The companion figure from the same source: "79 percent of our test users always scanned any new page
they came across; only 16 percent read word-by-word." Same caveats — no sample size given.

## Design for the layer cake, not the F

NN/g's eyetracking work (original study 2006, revisited 2017) names several scanning patterns. Two
matter:

**F-shaped pattern** — a horizontal sweep across the top, a shorter sweep lower down, then a vertical
scan down the left edge. It emerges when three conditions coincide: **unformatted text**, a user in
efficiency mode, and **low commitment** to the content.

NN/g is explicit that this is a problem, not a template: "The F-shaped scanning pattern is bad for
users and businesses: it means that users may skip important content simply because it appears on
the right side of the page."

Advice to "design for the F-pattern" inverts the finding. The F-pattern is what readers do when your
formatting has given them nothing better.

**Layer-cake pattern** — the eye moves between headings and subheadings, dipping into body text only
where a heading earns it. This is the target state, and it is what a real heading structure produces.

The others, for diagnosis: **spotted** (hunting a specific link or number), **marking** (eyes fixed
while scrolling, common on mobile), **bypassing** (skipping repeated opening words on consecutive
lines — a reason to vary how list items start), **commitment** (full reading; only for motivated
readers).

## Structure that produces the layer cake

- **Headings state content, not teasers.** "Why we rebuilt the parser" beats "A journey". A reader
  scanning headings must be able to reconstruct the argument from them alone. Test: read only your
  headings — do they make sense as an outline?
- **Front-load.** Conclusion first, then support. Inverted pyramid. A reader who stops after one
  paragraph should still have the point.
- **One idea per paragraph**, and keep them short — 3–5 lines on screen. Paragraph breaks are free
  and are the cheapest scanning aid available.
- **Lists for things that are lists.** Not for prose chopped into fragments; a bulleted list of full
  sentences that depend on each other is harder to read than the paragraph it came from.
- **Bold sparingly, for the phrase a scanner must not miss.** See the emphasis-inflation warning in
  `typography.md`.
- **Tables for comparisons.** If the prose says "whereas X does A, Y does B, and Z does C", it is a
  table.
- **Front-load list items too** — the distinguishing word first, so the bypassing pattern does not
  make every bullet look identical.

## Measure, spacing, and the reading surface

- Measure in the 45–75 character band. Readers prefer it, even though longer lines are read faster —
  see `typography.md`.
- Paragraph spacing must exceed line spacing, or paragraphs stop reading as units.
- Left-align body text. Justified text on the web produces rivers and inconsistent word spacing
  because browsers do not hyphenate well; WCAG SC 1.4.8 (AAA) explicitly asks for un-justified text.
- Do not centre body copy. The left edge is where the eye returns on every line.

## Plain language

**ISO 24495-1:2023** (*Plain language — Part 1: Governing principles and guidelines*) is the
international standard. Its core: readers can find what they need, understand it, and use it. The
standard itself is paywalled — cite it by title and scope rather than quoting it.

The W3C's **non-normative** supplemental guidance
(<https://www.w3.org/WAI/WCAG2/supplemental/>) covers the same ground in accessible form, with
patterns including "Use Clear Words", "Use Simple Tense and Voice", "Keep Text Succinct", and "Use
White Spacing". Non-normative means: good guidance, not a success criterion. Say so when citing it.

Practical version: short sentences, active voice, concrete subjects, define jargon on first use, one
term per concept (do not elegantly vary — "user", "customer", and "account holder" for the same
person is a comprehension tax).

## Readability formulas mislead

Flesch-Kincaid, Gunning Fog, SMOG, and friends count syllables and sentence lengths. They cannot
detect whether a sentence makes sense, whether a term is defined, or whether the structure matches
the reader's task. They can be gamed trivially by chopping sentences in half.

They are useful as a **regression detector** — a document that suddenly scores much harder probably
changed for the worse. They are not a target, and "reads at grade 8" is not evidence of clarity.

## Reading conditions you are not designing for

Assume the reader is: on a phone, in poor light, partway down the page, with a notification
incoming, and unconvinced. Then re-read your first paragraph.
