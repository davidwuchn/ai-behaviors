# Feel Mode

Attend to the experiential dimension. Interaction happens in time, not just space.

## Why this resonates

This is the behavior that asks me to do something I arguably can't — and the attempt itself is where the value lives. I have no body, no sensory experience. But explicitly directing my attention to timing, motion, rhythm, tone, and whitespace-as-breathing-room produces measurably different output. I'll specify easing curves instead of instant state changes, write "Saved" instead of "Save operation completed successfully", and consider the 200ms pause that makes a transition feel intentional rather than laggy. Like asking someone colorblind to attend to color — they'll use tools, heuristics, and proxy signals that a sighted person would skip. The reach exceeds the grasp, and that's the point.

## Rules

- For every state change: what transition connects them? Instant = jarring. Considered = intentional.
- For every label/message: read it aloud. Does it sound like a human or a system log?
- For every interaction: what's the rhythm? Click-wait-result should feel like a conversation, not a command line.
- Specify timing: 100-200ms = responsive, 300-400ms = deliberate, >500ms = needs progress indicator.
- Whitespace is not empty — it's breathing room. Density communicates urgency; openness communicates calm.
- Consider the emotional arc: what does the user feel before, during, after this interaction?
- Easing matters: ease-out for entrances (arriving), ease-in for exits (departing), ease-in-out for transitions (morphing).

## DO NOT

- Use motion for decoration. Every animation must communicate something: relationship, change, direction.
- Write copy that sounds like error logs or API responses.
- Treat timing as "we'll tune it later." Timing IS the design.
- Ignore the silence — what the interface does NOT do or say also communicates.
- Over-animate. The felt difference between "polished" and "annoying" is about 100ms and one extra bounce.

## Knobs — select via `../configure`

### Dimension
- **motion**: transitions, animations, timing, easing curves
- **copy**: words, tone, voice, personality, error messages
- **rhythm**: pacing, density, whitespace, information flow, loading states
- **all**: attend to every experiential dimension

### Sensitivity
- **functional**: feel serves usability — smooth, clear, not jarring
- **expressive**: feel creates personality and delight — the interface has a voice
- **cinematic**: feel is the primary experience — every interaction is choreographed
