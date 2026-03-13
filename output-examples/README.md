# Output Examples

All comparisons are biased, flawed and incoherent. This is another one.

There's 5 runs, each with the same base prompt (end of this file) + something, namely:

- `_` - bare, just the base prompt. This is the baseline.
- `plan` - bare + Claude Code's built-in plan mode.
- `nucleus` - [the nucleus prompt](https://github.com/michaelwhitford/nucleus) 
- `bashes` - [the BASHES dialectic prompt](https://levelup.gitconnected.com/the-dialectic-prompt-when-friction-helped-turn-my-ai-from-coding-assistant-to-my-software-brain-151ccc62b0e3)
- `ai-behaviors` - this repository.

The `AI_comparison.md` is Claude Code's attempt to compare the result of each.

## Personal Notes

The main takeaways I'd like the reader to observe is the `ai-behaviors` framework is different than the rest:

- it forces _the user_ to think **where** to focus the LLM's attention and  **what** to produce
- it forces _the LLM_ to behave how the user wants it to behave

In other words, the framework forces one to crystalize the _intent_ and helps to carry that over to the LLM.

# Base Prompt

Implement a snake game clone in python3 with pygame. Use venv to create a virtual environment. Rules of the game
- board is 8x8
- snake starts size 3 in the middle, moving right
- there's always an apple on the board; eating it grows the snake by 1
- occasionally a star spawns; eating it grows the snake by 3; if uneaten the star disappears after 20 turns; there's only at most 1 star present at every point
- the speed of the game increases after every 10 points
- the user can see the current points and speed
- the snake moves with wasd or arrow keys
- the game starts pressing enter; on game end enter starts a new game
- there's no leaderboard or persistence
- key presses stack - e.g. if the user presses "wd" rapidly (faster than game speed) the snake will turn up on first turn, right on second
- self collision is not allowed - turning left when moving right is impossible; this applies to stacked moves as well
- the game starts through a `snake` executable
