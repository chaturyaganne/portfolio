# Encore — a live-event group planning UX project

Featured case study and working static prototype in Chaturya Ganne's portfolio. Built for a UX New Grad application: user/task hypotheses, information architecture, self-review iterations, interaction design, accessibility choices, engineering handoff and a research plan.

## Open

- Portfolio: `https://chaturyaganne.github.io/portfolio/`
- Case study: `https://chaturyaganne.github.io/portfolio/#encore`
- Prototype: `https://chaturyaganne.github.io/portfolio/#encore-prototype`

These are intended publication paths. Consult the delivery note for whether publication was verified.

## Try the core flow

Open Midnight Echo. Set four people, a $100 all-in per-person budget, step-free route and clear view. Compare sections 102 and 104. Review one option, inspect the price breakdown and copy the sample plan. Try a $40 budget to exercise recovery. No purchase, reservation or real event is involved.

The case-study research task starts a local session record. It is not a completed study. Output records contain no participant identity and are never sent to a server.

## Files

`app.js`: data, filtering, pricing, routing, dialogs, comparison, review and local task instrumentation. `site.css`: responsive visual system. `design-spec.md`: component/data/state handoff. `research-kit.md`: consent/recruiting guidance, neutral tasks, observation sheet and analysis plan. `design-handoff.svg`: editable vector sheet, importable into Figma. `tests.mjs`: automated DOM behavior checks. No native Figma file or completed Figma work is claimed.

The portfolio retains the original engineering projects, research, education, experience and external links. Its new design introduces UX exploration without inventing UX employment or changing the degree timeline.

## Development

The live application is plain HTML/CSS/JavaScript and has no runtime packages. To run the behavior tests from this directory, install the declared dev dependency with `npm install`, then `npm test`. The authoring checkout additionally contains `build.mjs`, `case-study.html` and the preserved original portfolio source. `node build.mjs` generates `dist/`; publishing copies the generated index and `encore/` assets into the existing Pages repository.

## Evidence boundaries

Self-initiated concept, not affiliated with SeatGeek. Synthetic inventory, assumed user needs, no interviews, no participant usability study, no conversion claims. Automated tests verify behavior; they do not certify usability, accessibility or business impact. Native dialog/clipboard/device behavior requires browser testing. AI assistance supported design exploration and implementation; review and understand the work before presenting it as a portfolio project.

## Foundations

[SeatGeek all-in pricing](https://seatgeek.com/blog/seatgeek-all-in-pricing-explained-how-to-avoid-hidden-ticket-fees) and [accessible filter guidance](https://support.seatgeek.com/hc/en-us/articles/11181317039891-What-should-I-expect-when-buying-tickets-for-prominent-events) establish existing features. The project explores group constraints and explicit comparisons rather than claiming those features are missing from SeatGeek. Accessibility choices reference [WAI labels](https://www.w3.org/WAI/tutorials/forms/labels/) and [visible focus](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html).
