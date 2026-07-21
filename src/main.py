"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs

Stretch challenges demonstrated here:
- Challenge 2: switchable scoring modes (Strategy pattern)
- Challenge 3: diversity penalty across artists/genres
- Challenge 4: formatted table output including the reasons per song
"""

import textwrap

from src.recommender import load_songs, recommend_songs, STRATEGIES

# Challenge 4: use tabulate for a clean table, with an ASCII fallback so the
# script still runs if the library isn't installed.
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# A rich profile that exercises the Challenge 1 advanced features
# (decade, mood tags, popularity, instrumental preference, language).
USER_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "likes_acoustic": False,
    "decade": 2020,
    "mood_tags": ["euphoric", "upbeat"],
    "target_popularity": 85,
    "likes_instrumental": False,
    "language": "en",
}


def print_table(title: str, recommendations: list) -> None:
    """Print recommendations as a formatted table including the reasons."""
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = "\n".join(textwrap.wrap(explanation, width=48))
        rows.append([rank, song["title"], song["artist"], f"{score:.2f}", reasons])

    headers = ["#", "Title", "Artist", "Score", "Reasons"]
    print(f"\n=== {title} ===")
    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        # Simple ASCII fallback.
        print(" | ".join(headers))
        print("-" * 80)
        for r in rows:
            print(f"{r[0]}. {r[1]} - {r[2]}  (Score: {r[3]})")
            for line in r[4].splitlines():
                print(f"     {line}")


def main() -> None:
    songs = load_songs("data/songs.csv")

    print(f"\nUser profile: {USER_PREFS}")

    # Challenge 2: run the same profile through each scoring mode.
    for strategy in STRATEGIES.values():
        recs = recommend_songs(USER_PREFS, songs, k=5, strategy=strategy)
        print_table(f"Mode: {strategy.name}", recs)

    # Challenge 3: compare balanced ranking with and without the diversity penalty.
    balanced = STRATEGIES["balanced"]
    print_table(
        "Balanced + Diversity Penalty",
        recommend_songs(USER_PREFS, songs, k=5, strategy=balanced, diversity=True),
    )


if __name__ == "__main__":
    main()
