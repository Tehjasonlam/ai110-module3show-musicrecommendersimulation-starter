import pytest

from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    score_song,
    recommend_songs,
    DEFAULT_WEIGHTS,
    STRATEGIES,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Targeted scoring tests (pin exact numeric behavior) ------------------

def test_perfect_match_score_equals_sum_of_weights():
    # Genre + mood match, exact energy, and acoustic preference satisfied.
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.1}

    score, reasons = score_song(user_prefs, song)
    expected = (
        DEFAULT_WEIGHTS["genre"]
        + DEFAULT_WEIGHTS["mood"]
        + DEFAULT_WEIGHTS["energy"] * 1.0  # energy exactly on target -> closeness 1.0
        + DEFAULT_WEIGHTS["acoustic"]
    )
    assert score == pytest.approx(expected)


def test_explanation_contains_specific_reasons():
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.1}

    _, reasons = score_song(user_prefs, song)
    joined = "; ".join(reasons)
    assert "genre match" in joined
    assert "mood match" in joined


def test_no_matching_features_scores_only_energy_component():
    # Different genre and mood; acoustic preference NOT satisfied -> only energy counts.
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    song = {"genre": "rock", "mood": "sad", "energy": 0.8, "acousticness": 0.9}

    score, reasons = score_song(user_prefs, song)
    assert score == pytest.approx(DEFAULT_WEIGHTS["energy"] * 1.0)
    assert all("genre match" not in r and "mood match" not in r for r in reasons)


def test_missing_optional_keys_does_not_crash():
    # Profile with only a genre key: no energy/mood/acoustic terms should apply.
    user_prefs = {"genre": "pop"}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.1}

    score, reasons = score_song(user_prefs, song)
    assert score == pytest.approx(DEFAULT_WEIGHTS["genre"])


def test_oop_and_functional_paths_agree():
    # The delegating _score must produce the same number as score_song directly.
    rec = make_small_recommender()
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    song = rec.songs[0]
    oop_score, _ = rec._score(user, song)
    func_score, _ = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        vars(song),
    )
    assert oop_score == pytest.approx(func_score)


def test_strategy_changes_the_score():
    # Energy-Focused weights the energy term higher than Balanced for the same song.
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.5}
    song = {"genre": "rock", "mood": "sad", "energy": 0.5, "acousticness": 0.1}

    balanced, _ = score_song(user_prefs, song, STRATEGIES["balanced"].weights)
    energy_focused, _ = score_song(user_prefs, song, STRATEGIES["energy-focused"].weights)
    # Only the energy term applies here, and energy-focused weights it more.
    assert energy_focused > balanced


def test_diversity_penalty_spreads_genres():
    # Two same-genre songs would both rank high; the penalty should demote the second.
    songs = [
        {"id": 1, "title": "A", "artist": "X", "genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.1},
        {"id": 2, "title": "B", "artist": "Y", "genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.1},
        {"id": 3, "title": "C", "artist": "Z", "genre": "rock", "mood": "happy", "energy": 0.8, "acousticness": 0.1},
    ]
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    plain = recommend_songs(user_prefs, songs, k=3)
    diverse = recommend_songs(user_prefs, songs, k=3, diversity=True, genre_penalty=5.0)

    # Without diversity the two pop songs occupy the top two slots.
    assert [s["genre"] for s, _, _ in plain[:2]] == ["pop", "pop"]
    # With a strong genre penalty, the rock song is lifted above the second pop song.
    assert diverse[1][0]["genre"] == "rock"
