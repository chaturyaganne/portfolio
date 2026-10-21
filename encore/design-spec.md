# Encore — design and engineering handoff

Independent UX exploration by Chaturya Ganne, created with Codex assistance. Fictional content; no affiliation with SeatGeek. No backend, payment collection, inventory holds or live collaboration.

## Core decisions

- Persist group requirements throughout the current tab's prototype session. Do not require sign-in or ask for disability details.
- Show price per person and total for the group. All sample mandatory charges are included. Do not show fake discounts, popularity scores, countdowns or scarcity.
- Compare up to three options using facts: section, row, route, view, adjacent-seat count and prices. No opaque “best deal” score is fabricated.
- Explain the distinction between step-free travel and accessible seating/wheelchair spaces. Venue data is illustrative; no real accommodation guarantee is offered.
- Copying a group plan shares text only. The copy states that no reservation or purchase exists. Clipboard failure exposes selectable text rather than pretending a copy succeeded.

## Data contract

Event: id, name, category, sample date, fictional venue/location, artwork theme and base-price offset. Listing: id, section, row, base price in cents, fee in cents, adjacent availability, stepFree, clearView, route/view labels and seatType. No user identity or medical data is stored.

All arithmetic uses integer cents. `each = base + fee`, `total = each * quantity`, `baseSubtotal = base * quantity`, `feesSubtotal = fee * quantity`. All sample prices are whole-dollar amounts. A real product needs currency-aware formatting, rounding, tax treatment, inventory refresh and binding-price rules.

Matching requires: enough adjacent seats, each <= budget in cents, and any requested step-free/clear-view flag. Changing group requirements clears comparisons and selection. Choosing a map section filters the list, but does not change group needs. Zero results preserve context and offer distinct recovery actions. Invalid budgets cannot open a review.

## Component inventory and states

| Component | States / behavior |
| --- | --- |
| Group requirements | 1–6 people; budget $40–$250 in whole dollars; visible validation error; independent step-free and clear-view controls. |
| Category chip | All/Music/Sports/Comedy; pressed state exposed with aria-pressed. |
| Event card | Matching all-in starting price; explicit no-match state; still allows exploring filters. |
| Seat map section | Normal, focused, selected; Enter/Space activation; label includes section number; list alternative present. |
| Listing | Clear/partial view, stairs/step-free route; all-in amount, group total; compare checkbox and review button. |
| Compare dock | Hidden at zero; one selected with disabled compare action; 2–3 enables comparison; fourth selection rejected with status text. |
| Dialog | Named heading, close action, Escape, focus containment, focus return; native dialog when supported. |
| Review | Exact price breakdown; access caveat; copy action and explicit finish-prototype action. |
| Clipboard fallback | Read-only selectable text and manual-copy acknowledgment. Acknowledgment is not clipboard verification. |
| Task record | Local elapsed time/actions and separate selection/comparison/copy checks; no server transmission or claimed study result. |

## Visual system

Paper #F7F7F2, ink #17263F, muted text #566174, line #D9DDE3, signal #DCE8FF, accent #B83C2A, white #FFFFFF. DM Serif Display for display headings, DM Sans for controls/body, local Georgia/Arial fallbacks. Avoid color-only state meaning. Buttons have minimum-height targets, explicit labels and visible keyboard outlines.

Breakpoints: 1000 px, 700 px and 380 px. Desktop uses 3 event columns and a map/list split; smaller screens use 2 and then 1 column. Case-study navigation becomes a wrapping row. Table wrappers allow horizontal scrolling rather than clipping. Reduced-motion media query removes transitions and smooth scrolling. Print styles remove navigation and emphasize case-study content.

The editable SVG sheet is an importable vector handoff, not a native Figma document. Open Figma → new design file → drag in `design-handoff.svg`; optionally recreate its frames/components and variables using this specification. No Figma usage or proficiency is claimed by providing this export.

## Content and research

All events and seats are seeded examples. Proto-personas, pain points and expected benefits are labeled hypotheses. The V1/V2 comparison documents self-review, not participant feedback or an experiment. Existing ML projects, degree facts and outbound links are retained from the original portfolio. No UX employment or completed study is invented.

## Launch constraints

This is a static GitHub Pages project, using relative asset paths under `encore/` and hash navigation so direct case-study/prototype URLs work without server rewrites. A production marketplace would require authoritative inventory, accommodation metadata, authentication, permission-aware collaboration, payments, taxes, privacy review, error handling and monitored analytics.

Manual visual, keyboard, screen-reader, browser-compatibility and device tests are distinct from DOM checks. See validation evidence for what was actually executed; do not describe the site as WCAG-certified or user-validated.

## Standalone delivery and modules

The original portfolio homepage is restored unchanged. This project has its own `/portfolio/encore/` directory, with `index.html` for the project overview, `case-study.html` for the narrative and `prototype.html` for the interactive flow. Shared templates generate all three entry pages. `catalog.js` owns fictional sample content; `domain.js` owns integer-cent arithmetic and eligibility predicates; `app.js` owns interaction state and rendering. `site.css` supplies shared components and `modular.css` supplies the standalone project layout and visual overrides.
