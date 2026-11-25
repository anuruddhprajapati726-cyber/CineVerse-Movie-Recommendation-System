import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Model training aur similarity calculation shuru ho gayi hai...")

# 1. Load movies dataframe
movies = pickle.load(open("movies.pkl", "rb"))

# 2. Vectorization
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies["tags"]).toarray()

# 3. Cosine Similarity Matrix calculate karna
similarity = cosine_similarity(vectors)

# 4. Save similarity matrix to pickle file
pickle.dump(similarity, open("similarity.pkl", "wb"))
print("SUCCESS: similarity.pkl ban gaya hai!")