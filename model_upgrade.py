import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading big dataset...")

# ⚠️ adjust filename if needed
movies = pd.read_csv("TMDB_all_movies.csv", low_memory=False)

# ================= BASIC CLEAN =================
needed_cols = [col for col in ['title', 'overview', 'original_language'] if col in movies.columns]
movies = movies[needed_cols]

movies.dropna(subset=['title', 'overview'], inplace=True)

# Remove very short overviews
movies = movies[movies['overview'].str.len() > 50]

print("Total movies after cleaning:", len(movies))

# ================= BOLLYWOOD BOOST =================
# Keep more Hindi movies deliberately (examiner likes this)
if 'original_language' in movies.columns:
    hindi_movies = movies[movies['original_language'] == 'hi']
    other_movies = movies[movies['original_language'] != 'hi']

    hindi_sample = hindi_movies.sample(min(4000, len(hindi_movies)), random_state=42)
    other_sample = other_movies.sample(min(11000, len(other_movies)), random_state=42)

    # ================= SMART SAMPLING =================

# Always keep popular movies
priority_keywords = [
    "avengers", "spider", "batman", "iron man",
    "thor", "hulk", "superman", "shah rukh",
    "salman", "aamir", "ranbir", "deepika"
]

priority_mask = movies['title'].str.lower().str.contains('|'.join(priority_keywords), na=False)
priority_movies = movies[priority_mask]

# Hindi boost
if 'original_language' in movies.columns:
    hindi_movies = movies[movies['original_language'] == 'hi']
    other_movies = movies[~priority_mask & (movies['original_language'] != 'hi')]

    hindi_sample = hindi_movies.sample(min(4000, len(hindi_movies)), random_state=42)
    other_sample = other_movies.sample(min(9000, len(other_movies)), random_state=42)

    movies = pd.concat([priority_movies, hindi_sample, other_sample]).drop_duplicates()
else:
    remaining = movies[~priority_mask].sample(12000, random_state=42)
    movies = pd.concat([priority_movies, remaining]).drop_duplicates()

# Reset the index so it stays aligned with the similarity matrix's row positions
movies.reset_index(drop=True, inplace=True)

print("Final movies used for ML:", len(movies))

# ================= TFIDF =================
print("Vectorizing...")

tfidf = TfidfVectorizer(
    stop_words='english',
    max_features=6000
)

vectors = tfidf.fit_transform(movies['overview']).toarray()

print("Computing similarity...")

similarity = cosine_similarity(vectors)

# ================= SAVE =================
pickle.dump(movies.to_dict(), open('movies.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Upgraded pickle files created successfully!")