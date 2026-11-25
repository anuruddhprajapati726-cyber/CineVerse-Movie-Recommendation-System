import ast
import pickle
import pandas as pd

print("Data preprocessing shuru ho gaya hai...")

# 1. Load Datasets
movies = pd.read_csv("tmdb_5000_movies.csv")

# 2. Merge Datasets
movies = movies.merge(credits, on="title")

# 3. Zaroori columns select karna
movies = movies[
    ["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]
]
movies.dropna(inplace=True)
movies.drop_duplicates(inplace=True)


# 4. Helper functions for parsing JSON string columns
def convert(text):
  L = []
  try:
    for i in ast.literal_eval(text):
      L.append(i["name"])
  except:
    pass
  return L


def convert_cast(text):
  L = []
  counter = 0
  try:
    for i in ast.literal_eval(text):
      if counter < 3:
        L.append(i["name"])
        counter += 1
      else:
        break
  except:
    pass
  return L


def fetch_director(text):
  L = []
  try:
    for i in ast.literal_eval(text):
      if i["job"] == "Director":
        L.append(i["name"])
        break
  except:
    pass
  return L


movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(convert_cast)
movies["crew"] = movies["crew"].apply(fetch_director)

movies["overview"] = movies["overview"].apply(lambda x: str(x).split())


def collapse(L):
  return [i.replace(" ", "") for i in L]


movies["genres"] = movies["genres"].apply(collapse)
movies["keywords"] = movies["keywords"].apply(collapse)
movies["cast"] = movies["cast"].apply(collapse)
movies["crew"] = movies["crew"].apply(collapse)

# 5. Create Tags
movies["tags"] = (
    movies["overview"]
    + movies["genres"]
    + movies["keywords"]
    + movies["cast"]
    + movies["crew"]
)
new_df = movies[["movie_id", "title", "tags"]].copy()
new_df["tags"] = new_df["tags"].apply(lambda x: " ".join(x))
new_df["tags"] = new_df["tags"].str.lower()

# 6. Save processed dataframe to pickle file
pickle.dump(new_df, open("movies.pkl", "wb"))
print("SUCCESS: movies.pkl ban gaya hai!")