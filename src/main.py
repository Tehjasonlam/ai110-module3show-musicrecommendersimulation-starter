"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# A set of diverse taste profiles to stress-test the recommender, including an
# adversarial profile with conflicting preferences (high energy + sad mood).
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    "Adversarial: High-Energy Sad": {"genre": "classical", "mood": "sad", "energy": 0.95, "likes_acoustic": True},
}


def print_recommendations(name: str, user_prefs: dict, songs: list) -> None:
    """Run the recommender for one profile and print its top 5 results."""
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n=== {name} ===")
    print(f"User profile: {user_prefs}")
    print("\nTop recommendations:\n")
    for rank, rec in enumerate(recommendations, start=1):
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{rank}. {song['title']} - {song['artist']}  (Score: {score:.2f})")
        print(f"   Because: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs)


if __name__ == "__main__":
    main()
