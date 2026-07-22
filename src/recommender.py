import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Scoring weights for the Algorithm Recipe (see README "Finalized Algorithm Recipe").
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

# Columns in songs.csv parsed as floats / ints rather than left as strings.
NUMERIC_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness"}
INT_FIELDS = {"id", "popularity", "release_decade"}

# --- Challenge 2: Strategy pattern ---------------------------------------
# Each scoring "mode" is just a named bundle of weights. score_song() is the
# single algorithm; swapping the ScoringStrategy swaps how much each feature
# counts, so we get modular ranking modes without duplicating the scoring code.
@dataclass
class ScoringStrategy:
    """A named set of feature weights that controls how songs are scored."""
    name: str
    weights: Dict[str, float]

# Baseline weights (the finalized Phase 2 recipe, plus the Challenge 1 features).
DEFAULT_WEIGHTS: Dict[str, float] = {
    "genre": GENRE_WEIGHT,
    "mood": MOOD_WEIGHT,
    "energy": ENERGY_WEIGHT,
    "acoustic": ACOUSTIC_WEIGHT,
    "decade": 0.5,          # exact release-decade match
    "mood_tags": 0.25,      # per overlapping detailed mood tag
    "popularity": 0.5,      # closeness to a target popularity (0-100)
    "instrumental": 0.5,    # instrumental vs vocal preference match
    "language": 0.5,        # language match
}

def _weights(**overrides: float) -> Dict[str, float]:
    """Return a copy of DEFAULT_WEIGHTS with the given keys overridden."""
    merged = dict(DEFAULT_WEIGHTS)
    merged.update(overrides)
    return merged

STRATEGIES: Dict[str, ScoringStrategy] = {
    "balanced": ScoringStrategy("Balanced", _weights()),
    "genre-first": ScoringStrategy("Genre-First", _weights(genre=3.0, mood=1.0, energy=0.5)),
    "mood-first": ScoringStrategy("Mood-First", _weights(mood=3.0, mood_tags=0.5, genre=1.0)),
    "energy-focused": ScoringStrategy("Energy-Focused", _weights(energy=3.0, genre=1.0, mood=0.5)),
}

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Challenge 1 advanced features (defaulted so older constructors still work).
    popularity: int = 0
    release_decade: int = 0
    mood_tags: str = ""
    instrumentalness: float = 0.0
    language: str = ""

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Optional preferences for the Challenge 1 advanced features.
    decade: Optional[int] = None
    mood_tags: Optional[List[str]] = None
    target_popularity: Optional[float] = None
    likes_instrumental: Optional[bool] = None
    language: Optional[str] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(
        self, user: UserProfile, song: Song, strategy: Optional[ScoringStrategy] = None
    ) -> Tuple[float, List[str]]:
        """Score a Song against a UserProfile by delegating to score_song().

        score_song() is the single source of truth for the scoring formula; this
        method just translates the dataclasses into the dict shape it expects, so
        the OOP and functional paths can never drift apart.
        """
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "decade": user.decade,
            "mood_tags": user.mood_tags,
            "target_popularity": user.target_popularity,
            "likes_instrumental": user.likes_instrumental,
            "language": user.language,
        }
        weights = strategy.weights if strategy is not None else DEFAULT_WEIGHTS
        return score_song(user_prefs, vars(song), weights)

    def recommend(self, user: UserProfile, k: int = 5, strategy: Optional[ScoringStrategy] = None) -> List[Song]:
        """Return the top k songs ranked highest-to-lowest by their score."""
        # Judge every song, then rank: sorted() returns a new list without mutating self.songs.
        ranked = sorted(self.songs, key=lambda s: self._score(user, s, strategy)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string of why this song was recommended."""
        score, reasons = self._score(user, song)
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # Read every row into a dict, converting numeric columns so we can do math later.
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for field in NUMERIC_FIELDS:
                if field in row and row[field] != "":
                    row[field] = float(row[field])
            for field in INT_FIELDS:
                if field in row and row[field] != "":
                    row[field] = int(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # Algorithm Recipe: weighted genre + mood matches, energy closeness, and the
    # Challenge 1 advanced features. `weights` comes from the active ScoringStrategy
    # (Challenge 2); each preference is optional so profiles can omit any feature.
    w = weights if weights is not None else DEFAULT_WEIGHTS
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") is not None and song.get("genre") == user_prefs["genre"]:
        score += w["genre"]
        reasons.append(f"genre match ({song['genre']}) (+{w['genre']})")

    if user_prefs.get("mood") is not None and song.get("mood") == user_prefs["mood"]:
        score += w["mood"]
        reasons.append(f"mood match ({song['mood']}) (+{w['mood']})")

    if user_prefs.get("energy") is not None:
        energy_points = w["energy"] * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += energy_points
        reasons.append(f"energy close to {user_prefs['energy']} (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") is not None:
        is_acoustic = song.get("acousticness", 0) >= 0.5
        if is_acoustic == user_prefs["likes_acoustic"]:
            score += w["acoustic"]
            reasons.append(f"acoustic preference match (+{w['acoustic']})")

    # --- Challenge 1: advanced features ----------------------------------
    if user_prefs.get("decade") is not None and song.get("release_decade") == user_prefs["decade"]:
        score += w["decade"]
        reasons.append(f"decade match ({song['release_decade']}s) (+{w['decade']})")

    if user_prefs.get("mood_tags"):
        song_tags = set(str(song.get("mood_tags", "")).split(";"))
        overlap = song_tags & set(user_prefs["mood_tags"])
        if overlap:
            tag_points = w["mood_tags"] * len(overlap)
            score += tag_points
            reasons.append(f"mood tags {sorted(overlap)} (+{tag_points:.2f})")

    if user_prefs.get("target_popularity") is not None and song.get("popularity") is not None:
        closeness = 1 - abs(song["popularity"] - user_prefs["target_popularity"]) / 100
        pop_points = w["popularity"] * closeness
        score += pop_points
        reasons.append(f"popularity near {user_prefs['target_popularity']} (+{pop_points:.2f})")

    if user_prefs.get("likes_instrumental") is not None and song.get("instrumentalness") is not None:
        is_instrumental = song["instrumentalness"] >= 0.5
        if is_instrumental == user_prefs["likes_instrumental"]:
            score += w["instrumental"]
            reasons.append(f"instrumental preference match (+{w['instrumental']})")

    if user_prefs.get("language") is not None and song.get("language") == user_prefs["language"]:
        score += w["language"]
        reasons.append(f"language match ({song['language']}) (+{w['language']})")

    return score, reasons

def _select_diverse(
    scored: List[Tuple[Dict, float, List[str]]],
    k: int,
    artist_penalty: float,
    genre_penalty: float,
) -> List[Tuple[Dict, float, List[str]]]:
    """
    Greedily pick k songs, penalizing a candidate each time its artist or genre
    already appears in the chosen list (Challenge 3). This spreads the top
    results across more artists/genres instead of stacking one of each.
    """
    remaining = list(scored)
    selected: List[Tuple[Dict, float, List[str]]] = []

    while remaining and len(selected) < k:
        best_i, best_eff, best_reasons = None, None, None
        for i, (song, base, reasons) in enumerate(remaining):
            artist_hits = sum(1 for s, _, _ in selected if s.get("artist") == song.get("artist"))
            genre_hits = sum(1 for s, _, _ in selected if s.get("genre") == song.get("genre"))
            penalty = artist_penalty * artist_hits + genre_penalty * genre_hits
            eff = base - penalty
            if best_eff is None or eff > best_eff:
                eff_reasons = list(reasons)
                if penalty:
                    eff_reasons.append(f"diversity penalty (-{penalty:.2f})")
                best_i, best_eff, best_reasons = i, eff, eff_reasons

        song, _, _ = remaining.pop(best_i)
        selected.append((song, best_eff, best_reasons))

    return selected


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: Optional[ScoringStrategy] = None,
    diversity: bool = False,
    artist_penalty: float = 1.0,
    genre_penalty: float = 0.5,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Judge every song with score_song using the chosen strategy's weights (Challenge 2).
    weights = strategy.weights if strategy is not None else DEFAULT_WEIGHTS
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, reasons))

    if diversity:
        # Challenge 3: re-rank greedily with an artist/genre penalty.
        ranked = _select_diverse(scored, k, artist_penalty, genre_penalty)
    else:
        # Plain ranking: sort highest-to-lowest and keep the top k.
        scored.sort(key=lambda item: item[1], reverse=True)
        ranked = scored[:k]

    results = []
    for song, score, reasons in ranked:
        explanation = "; ".join(reasons) if reasons else "no matching features"
        results.append((song, score, explanation))
    return results
