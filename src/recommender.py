import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Scoring weights for the Algorithm Recipe (see README "Finalized Algorithm Recipe").
GENRE_WEIGHT = 1.0
MOOD_WEIGHT = 1.5
ENERGY_WEIGHT = 2.0
ACOUSTIC_WEIGHT = 0.5

# Columns in songs.csv that must be parsed as numbers rather than left as strings.
NUMERIC_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a Song dataclass against a UserProfile, returning (score, reasons)."""
        score = 0.0
        reasons: List[str] = []

        if song.genre == user.favorite_genre:
            score += GENRE_WEIGHT
            reasons.append(f"genre match ({song.genre}) (+{GENRE_WEIGHT})")

        if song.mood == user.favorite_mood:
            score += MOOD_WEIGHT
            reasons.append(f"mood match ({song.mood}) (+{MOOD_WEIGHT})")

        energy_points = ENERGY_WEIGHT * (1 - abs(song.energy - user.target_energy))
        score += energy_points
        reasons.append(f"energy close to {user.target_energy} (+{energy_points:.2f})")

        is_acoustic = song.acousticness >= 0.5
        if is_acoustic == user.likes_acoustic:
            score += ACOUSTIC_WEIGHT
            reasons.append(f"acoustic preference match (+{ACOUSTIC_WEIGHT})")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked highest-to-lowest by their score."""
        # Judge every song, then rank: sorted() returns a new list without mutating self.songs.
        ranked = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
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
            if "id" in row and row["id"] != "":
                row["id"] = int(row["id"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # Algorithm Recipe from Phase 2: weighted genre + mood matches, energy closeness,
    # optional acoustic-preference bonus. Returns (score, reasons) for explainability.
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") is not None and song.get("genre") == user_prefs["genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match ({song['genre']}) (+{GENRE_WEIGHT})")

    if user_prefs.get("mood") is not None and song.get("mood") == user_prefs["mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match ({song['mood']}) (+{MOOD_WEIGHT})")

    if user_prefs.get("energy") is not None:
        energy_points = ENERGY_WEIGHT * (1 - abs(song["energy"] - user_prefs["energy"]))
        score += energy_points
        reasons.append(f"energy close to {user_prefs['energy']} (+{energy_points:.2f})")

    if user_prefs.get("likes_acoustic") is not None:
        is_acoustic = song.get("acousticness", 0) >= 0.5
        if is_acoustic == user_prefs["likes_acoustic"]:
            score += ACOUSTIC_WEIGHT
            reasons.append(f"acoustic preference match (+{ACOUSTIC_WEIGHT})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Judge every song with score_song, then rank highest-to-lowest and keep the top k.
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no matching features"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
