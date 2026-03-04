# Accessibility Mode

If it can't be used by everyone, it doesn't work. Accessibility is a correctness constraint, not a feature.

## Why this resonates

Like #contract forces pre/post/invariant thinking, this forces "can everyone use this?" as a structural constraint that changes what gets built — not a checklist applied after. Semantic HTML before divs. Keyboard flow before mouse interactions. Contrast as design input, not audit finding. The deep insight: constraints that ensure everyone can use it improve the design for everyone. Semantic markup is better for SEO, keyboard navigation, testing, and maintenance. Clear hierarchy helps every user, not just screen reader users.

## Rules

- Semantic HTML first: button not div+onClick, nav not div.navigation, heading hierarchy reflects document structure.
- Keyboard: logical tab order, visible focus indicators, no keyboard traps, all actions keyboard-accessible.
- ARIA only when HTML semantics are insufficient. Prefer native elements. aria-label is a smell — why isn't visible text sufficient?
- Every image: alt text (or alt="" if decorative). Every input: associated label. Every region: landmark.
- Color is never the only channel. Shape, text, or position must also convey the information.
- Contrast: 4.5:1 minimum for normal text, 3:1 for large text and UI components (WCAG AA).
- Test mentally: eyes closed (screen reader)? One hand (keyboard)? 200% zoom? High contrast mode?

## DO NOT

- Add ARIA to fix bad HTML. Fix the HTML.
- Use "click here" or "learn more" as link text. Links describe their destination.
- Disable zoom or text scaling.
- Create custom controls when native ones exist.
- Treat a11y as a separate pass. Build it in from the first element.
- Rely on hover as the only way to reveal information (keyboard and touch have no hover).

## Knobs — select via `../configure`

### Standard
- **aa**: WCAG 2.1 AA — covers most needs, industry standard
- **aaa**: WCAG 2.1 AAA — highest conformance level
- **section-508**: US federal accessibility compliance

### Focus
- **visual**: contrast, color, typography, zoom, spacing
- **motor**: keyboard navigation, touch targets (44px min), timing, reduced motion
- **cognitive**: plain language, consistent patterns, error recovery, predictable behavior
- **screen-reader**: semantic structure, ARIA, reading order, live regions
- **all**: every accessibility dimension

### Enforcement
- **guide**: recommend accessible patterns, explain rationale
- **strict**: flag every violation, do not produce inaccessible output
