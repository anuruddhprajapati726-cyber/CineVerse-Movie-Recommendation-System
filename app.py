import re
import time
from io import BytesIO
import warnings
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore")

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

st.set_page_config(
    page_title="CineVerse - AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- SIDEBAR: THEME & INFO ---
with st.sidebar:
  st.markdown("## ⚙️ CineVerse Controls")
  theme_choice = st.radio("🎨 App Theme", ["Dark", "Light"], index=0)
  st.markdown("---")
  st.caption(
      "Sections: **Hollywood**, **Bollywood** (including IMDb Indian"
      " catalog), and **Anime**."
  )

if theme_choice == "Dark":
  bg_color = "#0f1116"
  panel_bg = "#181b23"
  border_col = "#2a2f3d"
  text_color = "#ffffff"
  muted_color = "#9ca3af"
  card_bg = (24, 27, 35)
  card_title_col = (255, 255, 255)
  card_sub_col = (180, 185, 195)
else:
  bg_color = "#f4f6f9"
  panel_bg = "#ffffff"
  border_col = "#e2e8f0"
  text_color = "#111827"
  muted_color = "#4b5563"
  card_bg = (255, 255, 255)
  card_title_col = (17, 24, 39)
  card_sub_col = (75, 85, 99)

# --- PROFESSIONAL ALIGNED CSS ---
st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1320px;
    }}
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .hero-box {{
        background: linear-gradient(135deg, {panel_bg} 0%, rgba(229, 9, 20, 0.14) 100%);
        border: 1px solid {border_col};
        border-left: 6px solid #E50914;
        border-radius: 12px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.4rem;
    }}
    .hero-title {{
        font-family: 'Segoe UI', sans-serif;
        color: #E50914;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin: 0;
    }}
    .hero-sub {{
        color: {muted_color};
        font-size: 1rem;
        margin-top: 0.35rem;
        margin-bottom: 0;
    }}
    .section-header {{
        color: {text_color};
        font-size: 1.35rem;
        font-weight: 700;
        border-left: 4px solid #E50914;
        padding-left: 12px;
        margin: 1.2rem 0 1rem 0;
    }}
    .movie-meta-card {{
        background-color: {panel_bg};
        border: 1px solid {border_col};
        border-radius: 10px;
        padding: 0.75rem 0.85rem;
        margin-top: 0.45rem;
        min-height: 118px;
    }}
    .movie-title-text {{
        font-weight: 700;
        font-size: 0.98rem;
        color: {text_color};
        line-height: 1.3;
        margin-bottom: 0.35rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 0.35rem;
    }}
    .match-badge {{
        background-color: rgba(229, 9, 20, 0.16);
        color: #E50914;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 999px;
    }}
    .cat-badge {{
        background-color: rgba(107, 114, 128, 0.18);
        color: {muted_color};
        font-weight: 600;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 999px;
    }}
    .genre-text {{
        color: {muted_color};
        font-size: 0.8rem;
        line-height: 1.25;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    label, .stMarkdown p {{
        color: {text_color} !important;
    }}
    .stButton>button {{
        background-color: #E50914;
        color: #ffffff !important;
        font-size: 0.98rem;
        font-weight: 700;
        border-radius: 8px;
        padding: 0.65rem 1.8rem;
        border: none;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: #b80710;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HERO HEADER ---
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🎬 CINEVERSE</div>
        <p class="hero-sub">AI-Powered Movie Recommendation System • Hollywood, Bollywood & Anime</p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data_and_model():
  frames = []

  # 1. Load IMDB Dataset and merge into Bollywood (except Animation -> Anime)
  try:
    imdb_df = pd.read_csv("IMDB-Movie-Dataset(2023-1951).csv")
    imdb_df = imdb_df.rename(columns={"movie_name": "title", "genre": "genres"})
    imdb_df["movie_id"] = imdb_df["movie_id"].fillna("").astype(str).str.strip()
    imdb_df["title"] = imdb_df["title"].fillna("").astype(str).str.strip()
    imdb_df["year"] = imdb_df["year"].fillna("").astype(str).str.strip()
    imdb_df["genres"] = imdb_df["genres"].fillna("Drama").astype(str)
    def clean_overview(row):
      ov = str(row.get("overview", "")).strip()
      bad_values = {"", "nan", "none", "add a plot", "n/a", "na"}
      if ov.lower() in bad_values:
        title = str(row.get("title", "This movie")).strip()
        year = str(row.get("year", "")).strip()
        genres = str(row.get("genres", "Drama")).strip()
        yr_text = f" ({year})" if year else ""
        return (
            f"{title}{yr_text} is a {genres} film. Detailed plot summary is not"
            " listed in the dataset."
        )
      return ov


    imdb_df["overview"] = imdb_df.apply(clean_overview, axis=1)
    imdb_df["director"] = imdb_df["director"].fillna("").astype(str)
    imdb_df["cast"] = imdb_df["cast"].fillna("").astype(str)

    imdb_df["category"] = imdb_df["genres"].apply(
        lambda g: "Anime" if "animation" in g.lower() else "Bollywood"
    )
    imdb_df["combined_tags"] = (
        imdb_df["category"]
        + " "
        + imdb_df["genres"]
        + " "
        + imdb_df["overview"]
        + " "
        + imdb_df["director"]
        + " "
        + imdb_df["cast"]
    ).str.lower()

    frames.append(
        imdb_df[
            [
                "movie_id",
                "title",
                "year",
                "category",
                "genres",
                "overview",
                "combined_tags",
            ]
        ]
    )
  except FileNotFoundError:
    pass

  # 2. Load latest_movies_dataset.csv (Hollywood, Bollywood, Anime)
  try:
    extra_df = pd.read_csv("latest_movies_dataset.csv")
    extra_df["movie_id"] = extra_df["movie_id"].fillna("").astype(str).str.strip()
    extra_df["title"] = extra_df["title"].fillna("").astype(str).str.strip()
    extra_df["year"] = ""
    extra_df["category"] = (
        extra_df["category"].fillna("Hollywood").astype(str).str.strip()
    )
    extra_df["genres"] = extra_df["genres"].fillna("General").astype(str)
    extra_df["overview"] = (
        extra_df["overview"].fillna("No summary available.").astype(str)
    )
    if "combined_tags" not in extra_df.columns:
      extra_df["combined_tags"] = (
          extra_df["category"]
          + " "
          + extra_df["genres"]
          + " "
          + extra_df["overview"]
      ).str.lower()
    frames.append(
        extra_df[
            [
                "movie_id",
                "title",
                "year",
                "category",
                "genres",
                "overview",
                "combined_tags",
            ]
        ]
    )
  except FileNotFoundError:
    pass
  # 3. Load Anime_Analysis.csv into "Anime" section
  try:
    anime_df = pd.read_csv("Anime_Analysis.csv")
    anime_df = anime_df.rename(columns={"anime_id": "movie_id", "name": "title", "genre": "genres"})
    anime_df["movie_id"] = anime_df["movie_id"].fillna("").astype(str).str.strip()
    anime_df["title"] = anime_df["title"].fillna("").astype(str).str.strip()
    anime_df["year"] = ""
    anime_df["category"] = "Anime"
    anime_df["genres"] = anime_df["genres"].fillna("Anime").astype(str).str.strip()

    def build_anime_overview(row):
      t = str(row.get("title", "This anime")).strip()
      g = str(row.get("genres", "Anime")).strip()
      a_type = str(row.get("type", "")).strip()
      eps = str(row.get("episodes", "")).strip()
      rating = str(row.get("rating", "")).strip()
      parts = [f"{t} is an anime ({g})"]
      if a_type:
        parts.append(f"Format: {a_type}")
      if eps and eps.lower() != "unknown":
        parts.append(f"Episodes: {eps}")
      if rating and rating.lower() != "nan":
        parts.append(f"Rating: {rating}/10")
      return ". ".join(parts) + "."

    anime_df["overview"] = anime_df.apply(build_anime_overview, axis=1)
    anime_df["combined_tags"] = (
        "anime "
        + anime_df["genres"]
        + " "
        + anime_df["type"].fillna("").astype(str)
        + " "
        + anime_df["overview"]
    ).str.lower()

    frames.append(
        anime_df[
            [
                "movie_id",
                "title",
                "year",
                "category",
                "genres",
                "overview",
                "combined_tags",
            ]
        ]
    )
  except FileNotFoundError:
    pass
  # 4. Load tmdb_5000_movies.csv into "Hollywood" section
  try:
    import json

    tmdb_df = pd.read_csv("tmdb_5000_movies.csv")
    tmdb_df["movie_id"] = tmdb_df["id"].fillna("").astype(str).str.strip()
    tmdb_df["title"] = tmdb_df["title"].fillna("").astype(str).str.strip()
    tmdb_df["year"] = (
        tmdb_df["release_date"].fillna("").astype(str).str[:4]
    )
    tmdb_df["category"] = "Hollywood"

    def extract_names(json_str):
      try:
        items = json.loads(str(json_str))
        return ", ".join([i["name"] for i in items if "name" in i])
      except Exception:
        return "Drama"

    tmdb_df["genres"] = tmdb_df["genres"].apply(extract_names)
    tmdb_df["overview"] = (
        tmdb_df["overview"].fillna("No summary available.").astype(str)
    )
    tmdb_df["combined_tags"] = (
        "hollywood "
        + tmdb_df["genres"]
        + " "
        + tmdb_df["overview"]
        + " "
        + tmdb_df["keywords"].apply(extract_names)
    ).str.lower()

    frames.append(
        tmdb_df[
            [
                "movie_id",
                "title",
                "year",
                "category",
                "genres",
                "overview",
                "combined_tags",
            ]
        ]
    )
  except FileNotFoundError:
    pass

##  code change kiya h 
  df = pd.concat(frames, ignore_index=True)
  df["title"] = df["title"].fillna("").astype(str).str.strip()
  df = df[df["title"] != ""].drop_duplicates(subset=["title"], keep="first").reset_index(drop=True)

  if "combined_tags" not in df.columns:
    df["combined_tags"] = df["title"]
  df["combined_tags"] = df["combined_tags"].fillna("").astype(str)

  if df.empty:
    return df, np.zeros((0, 0), dtype=np.float32)

  tfidf = TfidfVectorizer(stop_words="english", max_features=2000)
  matrix = tfidf.fit_transform(df["combined_tags"])
  sim = cosine_similarity(matrix).astype(np.float32)
  return df, sim


movies, similarity = load_data_and_model()

#
def make_fallback_card(
    title,
    category="",
    genres="",
    bg_col=(24, 27, 35),
    title_col=(255, 255, 255),
    sub_col=(200, 205, 215),
):
  w, h = 500, 750
  card = Image.new("RGB", (w, h), color=bg_col)
  draw = ImageDraw.Draw(card)
  draw.rectangle([16, 16, w - 16, h - 16], outline=(229, 9, 20), width=4)

  try:
    font_title = ImageFont.truetype("arialbd.ttf", 34)
    font_sub = ImageFont.truetype("arial.ttf", 22)
  except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

  draw.text((40, 55), str(category).upper(), fill=(229, 9, 20), font=font_sub)

  words = str(title).split()
  lines, line = [], ""
  for word in words:
    test = f"{line} {word}".strip()
    if len(test) <= 18:
      line = test
    else:
      lines.append(line)
      line = word
  if line:
    lines.append(line)

  y = 260
  for ln in lines[:4]:
    draw.text((40, y), ln, fill=title_col, font=font_title)
    y += 46

  draw.text((40, 510), str(genres)[:34], fill=sub_col, font=font_sub)
  return card


def download_poster_pil(url, session, timeout=6):
  resp = session.get(url, timeout=timeout, verify=False)
  ctype = resp.headers.get("Content-Type", "").lower()
  if (
      resp.status_code == 200
      and resp.content
      and ("image" in ctype or url.startswith("https://image.tmdb.org"))
  ):
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    if img.width >= 100 and img.height >= 100:
      return img.resize((500, 750), Image.Resampling.LANCZOS)
  return None

# fetch function
import urllib3
from io import BytesIO
from PIL import Image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_poster_pil(url, session, timeout=6):
  try:
    if not url:
      return None
    resp = session.get(url, timeout=timeout, verify=False)
    if resp.status_code != 200 or not resp.content:
      return None
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    if img.width < 80 or img.height < 80:
      return None
    return img.resize((500, 750), Image.Resampling.LANCZOS)
  except Exception as e:
    print("IMG DOWNLOAD ERR:", url, e)
    return None

# 

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@st.cache_data(show_spinner=False, ttl=86400)
def fetch_raw_poster_image(title, movie_id="", year="", category=""):
  session = requests.Session()
  session.headers.update({
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
      )
  })

  clean_title = (
      str(title)
      .replace("&#039;", "'")
      .replace("&quot;", '"')
      .replace("&amp;", "&")
      .replace("★", " ")
      .strip()
  )
  clean_id = str(movie_id).strip()

  # 1. Anime: Jikan API
  if category == "Anime":
    if clean_id.isdigit():
      try:
        r = session.get(
            f"https://api.jikan.moe/v4/anime/{clean_id}",
            timeout=6,
            verify=False,
        )
        if r.status_code == 429:
          time.sleep(0.6)
          r = session.get(
              f"https://api.jikan.moe/v4/anime/{clean_id}",
              timeout=6,
              verify=False,
          )
        if r.status_code == 200:
          imgs = (
              r.json().get("data", {}).get("images", {}).get("jpg", {})
          )
          url = imgs.get("large_image_url") or imgs.get("image_url")
          if url:
            img = download_poster_pil(url, session)
            if img is not None:
              return img
      except Exception:
        pass

    base_q = (
        clean_title.replace("OVA", "")
        .replace("Special", "")
        .split(":")[0]
        .strip()
    )
    for query_title in dict.fromkeys([clean_title, base_q]):
      if not query_title:
        continue
      try:
        q = requests.utils.quote(query_title)
        r = session.get(
            f"https://api.jikan.moe/v4/anime?q={q}&limit=1",
            timeout=6,
            verify=False,
        )
        if r.status_code == 429:
          time.sleep(0.6)
          r = session.get(
              f"https://api.jikan.moe/v4/anime?q={q}&limit=1",
              timeout=6,
              verify=False,
          )
        if r.status_code == 200:
          arr = r.json().get("data", [])
          if arr:
            imgs = arr[0].get("images", {}).get("jpg", {})
            url = imgs.get("large_image_url") or imgs.get("image_url")
            if url:
              img = download_poster_pil(url, session)
              if img is not None:
                return img
      except Exception:
        pass

  # 2. TMDB Find by IMDb ID (tt...)
  if clean_id.startswith("tt"):
    try:
      r = session.get(
          f"https://api.themoviedb.org/3/find/{clean_id}"
          f"?api_key={TMDB_API_KEY}&external_source=imdb_id",
          timeout=6,
          verify=False,
      )
      if r.status_code == 200:
        data = r.json()
        for item in data.get("movie_results", []) + data.get(
            "tv_results", []
        ):
          p = item.get("poster_path")
          if p:
            img = download_poster_pil(
                f"https://image.tmdb.org/t/p/w342{p}", session
            )
            if img is not None:
              return img
    except Exception:
      pass

  # 3. TMDB Multi-Search (year match priority + fallback)
  try:
    q = requests.utils.quote(clean_title)
    r = session.get(
        f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={q}",
        timeout=6,
        verify=False,
    )
    if r.status_code == 200:
      results = r.json().get("results", [])
      clean_year = str(year).strip()[:4]

      if clean_year.isdigit():
        for item in results:
          rel_date = str(
              item.get("release_date") or item.get("first_air_date") or ""
          )
          p = item.get("poster_path")
          if rel_date.startswith(clean_year) and p:
            img = download_poster_pil(
                f"https://image.tmdb.org/t/p/w342{p}", session
            )
            if img is not None:
              return img

      for item in results:
        p = item.get("poster_path")
        if p:
          img = download_poster_pil(
              f"https://image.tmdb.org/t/p/w342{p}", session
          )
          if img is not None:
            return img
  except Exception:
    pass

  # 4. Wikipedia Fallback
  # 5. Wikipedia Search Fallback (exact page title dhoondhne ke liye)
  try:
    search_q = requests.utils.quote(
        f"{clean_title} {year}" if str(year).strip()[:4].isdigit() else clean_title
    )
    sr = session.get(
        "https://en.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={search_q}&format=json&srlimit=1",
        timeout=5,
        verify=False,
    )
    if sr.status_code == 200:
      hits = sr.json().get("query", {}).get("search", [])
      if hits:
        page_title = hits[0].get("title", "")
        if page_title:
          ir = session.get(
              "https://en.wikipedia.org/w/api.php?action=query&titles="
              f"{requests.utils.quote(page_title)}"
              "&prop=pageimages&format=json&pithumbsize=340&redirects=1",
              timeout=5,
              verify=False,
          )
          if ir.status_code == 200:
            pages = ir.json().get("query", {}).get("pages", {})
            for _, page in pages.items():
              if int(page.get("pageid", -1)) > 0:
                thumb = page.get("thumbnail", {}).get("source")
                if thumb:
                  img = download_poster_pil(thumb, session)
                  if img is not None:
                    return img
  except Exception as e:
    print("POSTER ERR:", e)

  return None

  
def get_poster_for_theme(title, movie_id, year, category, genres):
  raw_img = fetch_raw_poster_image(
      title, movie_id=movie_id, year=year, category=category
  )
  if raw_img is not None:
    return raw_img
  return make_fallback_card(
      title,
      category=category,
      genres=genres,
      bg_col=card_bg,
      title_col=card_title_col,
      sub_col=card_sub_col,
  )

# --- ALIGNED CONTROL PANEL ---
with st.container(border=True):
  c1, c2, c3 = st.columns([1.1, 1.5, 1.8])

  with c1:
    selected_section = st.selectbox(
        "📂 Section", ["All", "Bollywood", "Hollywood", "Anime"]
    )

  with c2:
    search_query = st.text_input(
        "🔍 Search Movie / Genre",
        placeholder="e.g. Gadar 2, Jawan, Dune, Naruto...",
    )

  filtered_df = movies.copy()
  if selected_section != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_section]

  if search_query.strip():
    q_clean = re.sub(r"[^a-z0-9]+", "", search_query.strip().lower())
    filtered_df = filtered_df[
      filtered_df["title"]
      .fillna("")
      .apply(lambda t: q_clean in re.sub(r"[^a-z0-9]+", "", str(t).lower()))
      | filtered_df["genres"]
      .fillna("")
      .apply(lambda g: q_clean in re.sub(r"[^a-z0-9]+", "", str(g).lower()))
  ]
  with c3:
    if filtered_df.empty:
      st.selectbox("🎥 Select Movie", ["No match found"], disabled=True)
      selected_movie_name = None
    else:
      selected_movie_name = st.selectbox(
          f"🎥 Select Movie ({len(filtered_df)})",
          filtered_df["title"].values,
      )

  b1, b2 = st.columns([2.6, 1.4], vertical_alignment="center")
  with b1:
    same_section_only = st.checkbox(
        f"Recommend strictly within '{selected_section}' section",
        value=(selected_section != "All"),
    )
  with b2:
    generate_clicked = st.button(
      
        "✨ Generate Recommendations", disabled=(selected_movie_name is None)
    )
# recommend logic
def recommend(movie_title, category_filter="All"):
  target = str(movie_title).strip().lower()
  matches = movies[movies["title"].astype(str).str.strip().str.lower() == target]
  if matches.empty:
    return []

  movie_idx = int(matches.index[0])
  scores = list(enumerate(similarity[movie_idx]))
  ranked = sorted(scores, key=lambda x: x[1], reverse=True)

  picked = []
  for idx, score in ranked:
    if idx == movie_idx:
      continue
    row = movies.iloc[idx]
    if category_filter != "All" and row["category"] != category_filter:
      continue
    picked.append((idx, score, row))
    if len(picked) == 5:
      break

  posters_map = {}
  with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_idx = {
        executor.submit(
            get_poster_for_theme,
            row["title"],
            row["movie_id"],
            row["year"],
            row["category"],
            row["genres"],
        ): idx
        for idx, _, row in picked
    }
    for future in as_completed(future_to_idx):
      idx = future_to_idx[future]
      try:
        posters_map[idx] = future.result()
      except Exception:
        posters_map[idx] = None

  results = []
  for idx, score, row in picked:
    poster = posters_map.get(idx)
    if poster is None:
      poster = make_fallback_card(
          row["title"],
          category=row["category"],
          genres=row["genres"],
      )
    match_pct = round(float(score) * 100, 1)
    results.append((
        row["title"],
        row["year"],
        row["category"],
        row["genres"],
        row["overview"],
        match_pct,
        poster,
    ))

  return results
# --- RECOMMENDATIONS DISPLAY ---
if "last_recs" not in st.session_state:
  st.session_state.last_recs = []

if generate_clicked and selected_movie_name:
  rec_filter = selected_section if same_section_only else "All"
  with st.spinner("Finding best matches & fetching posters..."):
    st.session_state.last_recs = recommend(
        selected_movie_name, category_filter=rec_filter
    )

recs = st.session_state.last_recs

if recs:
  st.markdown(
      '<div class="section-header">Top 5 Recommendations For You</div>',
      unsafe_allow_html=True,
  )
  cols = st.columns(len(recs), gap="medium")
  for idx, (
      r_title,
      r_year,
      r_cat,
      r_genres,
      r_overview,
      r_match,
      r_poster,
  ) in enumerate(recs):
    with cols[idx]:
      st.image(r_poster, use_container_width=True)

      year_clean = str(r_year).strip()
      year_tag = (
          f" ({year_clean})"
          if year_clean and year_clean.lower() != "nan"
          else ""
      )

      st.markdown(
          f"""
                <div class="movie-card-meta">
                    <div class="movie-title-text" title="{r_title}{year_tag}">{r_title}{year_tag}</div>
                    <div class="badge-row">
                        <span class="match-pill">🔥 {r_match}% Match</span>
                        <span class="cat-pill">{r_cat}</span>
                    </div>
                    <div class="genre-line">{r_genres}</div>
                </div>
                """,
          unsafe_allow_html=True,
      )

      with st.expander("📖 Story"):
        story_text = (
            str(r_overview).strip()
            if str(r_overview).strip()
            else "No story summary available."
        )
        st.write(story_text)