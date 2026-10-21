# Encore — a live-event group planning UX project

A standalone UX project site with an overview, a case-study entry page and a working prototype. Built for a UX New Grad application: user/task hypotheses, information architecture, self-review iterations, interaction design, accessibility choices, engineering handoff and a research plan.

## Open

- Project overview: `https://chaturyaganne.github.io/portfolio/encore/`
- Original portfolio (restored): `https://chaturyaganne.github.io/portfolio/`
- Case study: `https://chaturyaganne.github.io/portfolio/encore/case-study.html`
- Prototype: `https://chaturyaganne.github.io/portfolio/encore/prototype.html`

These are intended publication paths. Consult the delivery note for whether publication was verified.

## Try the core flow

Open Midnight Echo. Set four people, a $100 all-in per-person budget, step-free route and clear view. Compare sections 102 and 104. Review one option, inspect the price breakdown and copy the sample plan. Try a $40 budget to exercise recovery. No purchase, reservation or real event is involved.

The case-study research task starts a local session record. It is not a completed study. Output records contain no participant identity and are never sent to a server.

## Files

`catalog.js`: fictional events and inventory. `domain.js`: pure pricing and eligibility rules. `app.js`: interaction state, routing, dialogs, comparison, review and local task instrumentation. `modular.css`: standalone project layout and component styling. `site.css`: responsive visual system. `design-spec.md`: component/data/state handoff. `research-kit.md`: consent/recruiting guidance, neutral tasks, observation sheet and analysis plan. `design-handoff.svg`: editable vector sheet, importable into Figma. `tests.mjs`: automated DOM behavior checks. No native Figma file or completed Figma work is claimed.

The main portfolio homepage is restored byte-for-byte from its pre-Encore revision. This project lives only at the separate /portfolio/encore/ URL, with its own identity and navigation.

## Development

The live application is plain HTML/CSS/JavaScript and has no runtime packages. To run the behavior tests from this directory, install the declared dev dependency with `npm install`, then `npm test`. The authoring checkout additionally contains `build.mjs`, `case-study.html` and the preserved original portfolio source. `node build-modular.mjs` generates `dist/`; the output contains the unchanged original portfolio index and the separate project under `encore/`. Publishing updates the project directory while preserving the restored root homepage.

## Evidence boundaries

Self-initiated concept, not affiliated with SeatGeek. Synthetic inventory, assumed user needs, no interviews, no participant usability study, no conversion claims. Automated tests verify behavior; they do not certify usability, accessibility or business impact. Native dialog/clipboard/device behavior requires browser testing. AI assistance supported design exploration and implementation; review and understand the work before presenting it as a portfolio project.

## Foundations

[SeatGeek all-in pricing](https://seatgeek.com/blog/seatgeek-all-in-pricing-explained-how-to-avoid-hidden-ticket-fees) and [accessible filter guidance](https://support.seatgeek.com/hc/en-us/articles/11181317039891-What-should-I-expect-when-buying-tickets-for-prominent-events) establish existing features. The project explores group constraints and explicit comparisons rather than claiming those features are missing from SeatGeek. Accessibility choices reference [WAI labels](https://www.w3.org/WAI/tutorials/forms/labels/) and [visible focus](https://www.w3.org/WAI/WCAG21/Understanding/focus-visible.html).
