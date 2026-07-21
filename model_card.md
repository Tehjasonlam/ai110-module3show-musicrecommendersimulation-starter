# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**VibeFinder 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

VibeFinder suggests songs from a small catalog that match a user's stated taste.
It generates a ranked top-5 list with a plain-language reason for each pick. It
assumes the user can describe their taste as a favorite genre, a favorite mood,
a target energy level, and whether they like acoustic music. This is a classroom
project for learning how recommenders work — not a production system for real
listeners.

### Non-Intended Use

VibeFinder should **not** be used to make real product recommendations, to judge
the quality of any song or artist, or to draw conclusions about a genre. The
catalog is tiny (18 songs) and the "mood" and "energy" values are made up for
the exercise, so its output is illustrative only.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

VibeFinder gives every song a score and then lines them up from highest to
lowest. A song earns points for matching what the user asked for. Matching the
favorite genre is worth the most points, matching the mood is worth a bit less,
and the song also earns points for having an energy level close to what the user
wants — the closer it is, the more points it gets. There's a small bonus if the
song's "acoustic" feel matches the user's preference. Add it all up, sort the
list, and the top few songs become the recommendations. Compared to the starter
code (which just returned the first few songs), I added the real scoring, the
closeness math for energy, the reasons behind each pick, and the sorting step.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog has 18 songs. Each song has a genre, a mood, and five numeric
features on a 0.0–1.0 scale: energy, valence, danceability, acousticness, plus
tempo in BPM. I started with 10 songs and added 8 to widen the variety, bringing
in genres like hip-hop, edm, classical, country, r&b, metal, folk, and reggae,
and moods like energetic, romantic, melancholy, and aggressive. Even so, a lot
of real musical taste is missing: there are no lyrics or language, no era/decade,
no live-vs-studio feel, and only one song per most genres — so the dataset is far
too small to represent how people actually listen.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

VibeFinder works best for users whose preferences agree with each other. The
Chill Lofi profile is the clearest win: it surfaced *Library Rain* and *Midnight
Coding* — quiet, acoustic, low-energy tracks — exactly what I'd expect. The
energy-closeness rule works well too, correctly separating slow songs from fast
ones and keeping high-energy picks together for the Pop and Rock profiles. When
a user's genre, mood, and energy all point the same direction, the top result
almost always feels right, and the "reasons" list makes it easy to see why.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

### Findings

The clearest weakness I found is that **genre dominates the ranking**. Because a
genre match is worth +2.0 — more than a mood match (+1.5) and up to twice the
energy score — a song can rank highly on genre alone even when it doesn't match
the user's mood at all. For the "Happy Pop" profile, *Gym Hero* (a pop song
tagged `intense`, not `happy`) ranks second, ahead of *Rooftop Lights*, which
actually matches both the happy mood and the target energy but is tagged
`indie pop` instead of `pop`. In plain terms: the system keeps showing "Gym
Hero" to someone who asked for happy pop simply because it shares the exact
genre label, ignoring that its *vibe* is wrong. A second limitation is the
**energy-gap being a weak tiebreaker**: since energy only contributes 0.0–1.0,
even a huge mismatch (the adversarial `energy=0.95` + `classical` profile) can't
overcome a genre match, so a slow classical piece still wins for a user asking
for high energy. Finally, the score ignores tempo, valence, and danceability
entirely, so two songs that feel very different can tie.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

### Profiles Tested

I stress-tested four profiles defined in `src/main.py`: **High-Energy Pop**,
**Chill Lofi**, **Deep Intense Rock**, and an **adversarial** profile with
conflicting preferences (`classical` genre, `sad` mood, but `energy=0.95`). I
looked at whether the top 5 matched the intended vibe and whether any single
song dominated every list.

```
=== High-Energy Pop ===
User profile: {'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'likes_acoustic': False}
1. Sunrise City - Neon Echo  (Score: 4.92)  genre + mood + energy + acoustic
2. Gym Hero - Max Pulse  (Score: 3.47)      genre + energy + acoustic
3. Rooftop Lights - Indigo Parade  (Score: 2.86)  mood + energy + acoustic
4. Storm Runner - Voltline  (Score: 1.49)   energy + acoustic
5. Neon Overdrive - Pulse Theory  (Score: 1.45)  energy + acoustic

=== Chill Lofi ===
User profile: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
1. Library Rain - Paper Lanterns  (Score: 5.00)  genre + mood + energy + acoustic
2. Midnight Coding - LoRoom  (Score: 4.93)  genre + mood + energy + acoustic
3. Focus Flow - LoRoom  (Score: 3.45)       genre + energy + acoustic
4. Spacewalk Thoughts - Orbit Bloom  (Score: 2.93)  mood + energy + acoustic
5. Coffee Shop Stories - Slow Stereo  (Score: 1.48)  energy + acoustic

=== Deep Intense Rock ===
User profile: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}
1. Storm Runner - Voltline  (Score: 4.99)   genre + mood + energy + acoustic
2. Gym Hero - Max Pulse  (Score: 2.97)      mood + energy + acoustic
3. Neon Overdrive - Pulse Theory  (Score: 1.45)  energy + acoustic
4. Sunrise City - Neon Echo  (Score: 1.42)  energy + acoustic
5. Iron Verdict - Ashfall  (Score: 1.42)    energy + acoustic

=== Adversarial: High-Energy Sad ===
User profile: {'genre': 'classical', 'mood': 'sad', 'energy': 0.95, 'likes_acoustic': True}
1. Winter Nocturne - Amelie Rousseau  (Score: 2.77)  genre + energy(0.27) + acoustic
2. Paper Boats - Wren Hollow  (Score: 2.35)  mood + energy(0.35) + acoustic
3. Backroad Sunset - Cassidy Lane  (Score: 1.10)  energy + acoustic
4. Neon Overdrive - Pulse Theory  (Score: 1.00)  energy(1.00)
5. Gym Hero - Max Pulse  (Score: 0.98)      energy(0.98)
```

### Profile Comparisons

- **High-Energy Pop vs Chill Lofi:** These are near-opposites and the outputs
  reflect it. Pop pulls bright, fast tracks (*Sunrise City*, energy ~0.82),
  while Lofi pulls quiet, acoustic tracks (*Library Rain*, energy 0.35). The
  energy-closeness score flips which end of the catalog rises, which is exactly
  what those preferences are meant to test — and it works.
- **High-Energy Pop vs Deep Intense Rock:** Both want high energy, so several
  songs (*Gym Hero*, *Neon Overdrive*, *Storm Runner*) appear on both lists. The
  difference is the genre/mood anchor: pop crowns *Sunrise City*, rock crowns
  *Storm Runner*. This shows the genre weight is doing the steering while energy
  sets the shared "loud and fast" background.
- **Deep Intense Rock vs Adversarial:** The adversarial profile deliberately
  fights itself (wants energy 0.95 but genre `classical`, which is low-energy).
  The result proves the bias from Section 6: *Winter Nocturne* wins on the genre
  point despite a 0.68 energy penalty, so the user asking for "high energy" gets
  a slow classical piece first. The rock profile has no such conflict, so its
  #1 (*Storm Runner*) satisfies genre, mood, and energy all at once.

### Experiment: Weight Shift

I doubled the energy weight (1.0 → 2.0) and halved the genre weight (2.0 → 1.0),
then reran. The results became **different, not clearly more accurate**: for
Happy Pop, *Rooftop Lights* (matches mood + energy) rose above *Gym Hero*
(matches genre only), which feels more correct; but in the adversarial profile,
pure high-energy songs like *Neon Overdrive* and *Gym Hero* climbed into the top
5 even though they match neither the genre nor the mood. This confirmed that
genre weight is what keeps recommendations on-theme, and that over-weighting
energy trades relevance for raw intensity.

### What Surprised Me

I expected genre to matter, but not to *override* a perfect mood-and-energy
match. Watching *Gym Hero* outrank *Rooftop Lights* for a "happy" user made the
"filter bubble" idea concrete: the system rewards the label the user named and
is blind to songs that would actually fit the mood better under a different tag.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

1. **Use more features in the score.** Fold in valence, danceability, and tempo
   so the "vibe" is captured by more than genre, mood, and energy.
2. **Soften the genre weight / add diversity.** Lower genre dominance or add a
   rule that avoids filling the top 5 with one genre, so great mood-and-energy
   matches in other genres aren't buried.
3. **Support richer profiles.** Let users list several favorite genres or moods,
   or weight their own preferences, so the system can handle taste that isn't a
   single label.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

My biggest learning moment was seeing that a "recommendation" is really just a
score and a sort — there's no magic, just weights I chose. Watching *Gym Hero*
outrank a better mood match for a "happy pop" user showed me how much power the
weights hold, and how easily a small choice creates a filter bubble. AI tools
helped me move fast: they drafted the CSV loader, suggested the energy-closeness
formula, and explained `.sort()` vs `sorted()`. But I had to double-check them —
for example, the starter import would have crashed under `python -m src.main`,
and I needed to make sure the scoring weights matched the recipe I actually
designed rather than whatever default was suggested. What surprised me most is
how convincing simple math can feel: with just four features and clear reasons,
the output really does read like a thoughtful recommendation. If I kept going,
I'd add more features to the score and a diversity rule so the top 5 doesn't
collapse onto one genre. This project made me realize the recommendation apps I
use every day are the same idea scaled up — and that the weights behind them
quietly shape what I get to discover.
