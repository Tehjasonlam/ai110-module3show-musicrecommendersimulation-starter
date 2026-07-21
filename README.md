# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

### My Design

Real platforms like Spotify predict what you'll enjoy by combining two ideas:
*collaborative filtering*, which recommends songs based on what similar
listeners enjoyed, and *content-based filtering*, which matches songs to you
using their own attributes like tempo, genre, and energy. At scale these run on
millions of implicit signals — plays, skips, and saves — that my small
simulation doesn't have. So my version is purely **content-based**: it compares
each song's measured features against a stored taste profile and prioritizes
closeness of vibe over raw popularity.

- **Song features used:** `genre`, `mood`, `energy`, `valence`, `acousticness`.
- **UserProfile stores:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.
- **Scoring rule (one song):** each song earns weighted points for matching
  genre (highest weight) and mood, plus a closeness score for how near its
  energy is to the user's target (`1 - |song.energy - target_energy|`), plus a
  bonus if its acousticness matches the user's acoustic preference.
- **Ranking rule (list of songs):** every song is scored, the list is sorted
  from highest to lowest score, and the top *k* songs are returned as
  recommendations.

Starting weight recipe: `genre = 2.0`, `mood = 1.5`, `energy closeness = 1.0`,
`acoustic match = 0.5` — genre is weighted highest because it's the most
reliable boundary of musical taste.

### Example User Profile

The recommender compares every song against a single taste profile like this:

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.4,
    "likes_acoustic": True,
}
```

This profile is specific enough to tell "chill lofi" apart from "intense rock":
a low `target_energy` (0.4) and the `lofi`/`chill` matches reward mellow tracks,
while a high-energy rock song loses the genre point, the mood point, and most of
the energy-closeness score — so the two land far apart in the ranking.

### Finalized Algorithm Recipe

For each song, add up:

| Rule | Points |
|---|---|
| Genre matches `favorite_genre` | +2.0 |
| Mood matches `favorite_mood` | +1.5 |
| Energy closeness: `1 - abs(song.energy - target_energy)` | +0.0 to +1.0 |
| Acousticness matches `likes_acoustic` preference | +0.5 |

Then **rank**: sort all songs by total score (highest first) and return the top *k*.

### Data Flow

```
Input                 Process (the loop)              Output
-----                 ------------------              ------
user_prefs  ─▶  for each song in songs.csv:   ─▶  ranked list
              score_song(user_prefs, song)        top K songs
              collect (song, score, reasons)      + explanations
                        │
                        ▼
                 sort by score desc
```

### Potential Biases

- **Genre over-prioritization:** with genre worth +2.0, a great mood-and-energy
  match in a *different* genre can be buried beneath a weak same-genre song.
- **Popularity blind spot / filter bubble:** the system only recommends more of
  what the profile already likes, so it never surprises the user with something
  new.
- **Feature coverage:** it ignores tempo, valence, and danceability in the core
  score, so two songs that "feel" very different can score identically.
- **Single-profile assumption:** one static taste profile can't capture that
  real listeners want different vibes at different times (focus vs workout).

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



