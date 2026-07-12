import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
movies = pd.read_csv('tmdb_5000_movies.csv')

# Keep needed columns
movies = movies[['title', 'overview']]
movies.dropna(inplace=True)

# Convert overview into vectors
tfidf = TfidfVectorizer(stop_words='english')
vectors = tfidf.fit_transform(movies['overview']).toarray()

# Similarity matrix
similarity = cosine_similarity(vectors)

# Save files
pickle.dump(movies.to_dict(), open('movies.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("✅ Pickle files created successfully!")