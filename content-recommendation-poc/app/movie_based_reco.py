import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from app.utils import load_data
from enum import Enum

# Define an Enum for content providers
class ProviderEnum(str, Enum):
    zee5 = "Zee5"
    magellan = "Magellan TV"
    both = "Both"

# Parse and clean the 'genres' column
def split_genres(genre_str):
    genres = []
    for part in genre_str.split(','):
        genres.extend(part.split('&'))
    return [genre.strip() for genre in genres]

# Extract and process features from the data
def process_data(md):
    md['genres'] = md['genres'].apply(lambda x: ' '.join(x))
    md['tagline'] = md['tagline'].fillna('')
    md['description'] = md['description'].fillna('')
    md['overview'] =  md['description'] + md['tagline'] + md['genres']

    return md

# Calculate cosine similarity
def calculate_cosine_similarity(smd):
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.0, stop_words='english')
    tfidf_matrix = tf.fit_transform(smd['description'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

# Get movie recommendations
def improved_recommendations(title, smd, indices, cosine_sim, providers=None):
    if title not in indices:
        return "Movie not in database, search for another movie."

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx].tolist()))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    movies = smd.iloc[movie_indices]
    
    # Filter by provider if specified
    if providers:
        if providers == "Both":
            # Include both providers
            movies = movies[movies['provider'].isin(["Zee5", "Magellan TV"])]
        else:
            movies = movies[movies['provider'] == providers]

    movies['vote_count'] = pd.to_numeric(movies['vote_count'], errors='coerce')
    movies['vote_average'] = pd.to_numeric(movies['vote_average'], errors='coerce')
    movies = movies.dropna(subset=['vote_count', 'vote_average'])
    vote_counts = movies['vote_count'].astype('int')
    vote_averages = movies['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.60)
    qualified = movies[(movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    qualified['wr'] = qualified.apply(lambda x: weighted_rating(x, m, C), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(30)
    qualified['genres'] = qualified['genres'].apply(lambda x: ', '.join(x.split()))

    return qualified[['id', 'title', 'content_type', 'genres', 'backdrop_path','poster_path', 'provider']]

# Weighted rating formula
def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

# Main function
def movie_based_movies(title: str, limit: int, providers: str = None):  # Changed providers to str
    bucket_name = 'enriched-dataset'  # Replace with your S3 bucket name
    file_key = 'enriched_ch_data_shows.csv'  # Replace with your S3 file key
    md = load_data(bucket_name, file_key)
    md = md[md['content_type']=='movie']
    md['genres'] = md['genres'].fillna('').apply(split_genres)
    smd = process_data(md)
    cosine_sim = calculate_cosine_similarity(smd)
    smd = smd.reset_index()
    titles = smd['title']
    indices = pd.Series(smd.index, index=smd['title'])
    recommendations = improved_recommendations(title, smd, indices, cosine_sim, providers)  # Pass providers to the recommendations function
    recommendations['genres'] = recommendations['genres'].fillna('').apply(split_genres)
    return recommendations.head(limit).reset_index(drop=True)