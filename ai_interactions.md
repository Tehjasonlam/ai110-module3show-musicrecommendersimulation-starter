# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

I asked the agent to complete Challenge 1: add five or more advanced attributes
to the dataset and update the scoring logic to use them. The goal was to make the
recommender consider more than genre/mood/energy.

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

- "Add 5 new columns to `data/songs.csv`: popularity (0-100), release_decade,
  mood_tags (semicolon-separated detailed tags like 'euphoric;upbeat'),
  instrumentalness (0.0-1.0), and language. Fill sensible values for all 18
  songs and keep the CSV valid."
- "Update `score_song` in `src/recommender.py` so it also scores these new
  features: exact decade match, overlap of mood_tags, closeness to a target
  popularity, an instrumental-preference match, and a language match. Keep every
  new preference optional so profiles that don't set them still work, and keep
  returning the (score, reasons) tuple. Verify the math stays in range."

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

- Rewrote `data/songs.csv` with the 5 new columns and values for all 18 songs.
- Added `INT_FIELDS` and extended `NUMERIC_FIELDS`/`load_songs` to parse the new
  numeric columns (`popularity`, `release_decade`, `instrumentalness`).
- Extended `score_song` with five new optional scoring blocks and reason strings.
- Ran `python -m src.main` and `python -m pytest` to confirm behavior.

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

I checked the CSV had exactly 15 comma-separated values per row (no stray commas
inside `mood_tags`, which is why I used `;` as the tag separator). I confirmed
the popularity closeness formula `1 - abs(song - target)/100` stays within 0-1,
and I verified the new features only activate when the profile sets the matching
key so the earlier Phase 4 profiles still run unchanged.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

The **Strategy pattern**, used for Challenge 2 (multiple scoring modes).

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

I attached `recommender.py` and asked how to support several ranking modes
("Genre-First", "Mood-First", "Energy-Focused") without copy-pasting the scoring
function four times. The AI compared a few options — `if/elif` branches, separate
functions, and the Strategy pattern — and recommended Strategy because the
*algorithm* (add up weighted feature matches) never changes; only the *weights*
do. It suggested representing each mode as a small object holding a weights
dictionary, so adding a new mode is just one more entry, and `score_song` stays a
single function that reads whichever weights it's handed.

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->

- `ScoringStrategy` (dataclass) in `src/recommender.py` holds a `name` and a
  `weights` dict — this is the interchangeable "strategy" object.
- `STRATEGIES` is a registry of the four modes (`balanced`, `genre-first`,
  `mood-first`, `energy-focused`), each built from `DEFAULT_WEIGHTS` via
  `_weights(...)` overrides.
- `score_song(user_prefs, song, weights)` is the context that applies whichever
  strategy's weights it receives, and `recommend_songs(..., strategy=...)` lets
  `src/main.py` swap modes by passing a different `ScoringStrategy`.
