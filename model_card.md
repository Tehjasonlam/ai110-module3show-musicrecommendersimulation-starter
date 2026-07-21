# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
