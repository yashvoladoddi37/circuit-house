import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load the dataset
def load_data(file_path):
    return pd.read_csv(file_path)

# Parse and clean the 'genres' column
def split_genres(genre_str):
    if pd.isna(genre_str):  # Handle missing values
        return []
    return [genre.strip() for genre in genre_str.split(',')]

def split_keywords(keyword_str):
    if pd.isna(keyword_str):  # Handle missing values
        return []
    return [key.strip() for key in keyword_str.split(',')]

# Extract and process features from the data
def process_data(md):
    md['tagline'] = md['tagline'].fillna('')
    md['description'] = md['description'].fillna('')
    # Don't join genres here, keep as a list
    md['keywords'] = md['keywords'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '')
    md['overview'] = md['description'] + ' ' + md['tagline'] + ' ' + md['genres'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '') + ' ' + md['keywords']
    return md

# Calculate cosine similarity
def calculate_cosine_similarity(smd):
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.0, stop_words='english')
    tfidf_matrix = tf.fit_transform(smd['overview'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

# Get movie recommendations
def improved_recommendations(title, smd, indices, cosine_sim):
    if title not in indices:
        return "Movie not in database, search for another movie."

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx].tolist()))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    movies = smd.iloc[movie_indices]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.60)
    qualified = movies[(movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    qualified['wr'] = qualified.apply(lambda x: weighted_rating(x, m, C), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(10)
    
    # Convert genres list to comma-separated string
    qualified['genres'] = qualified['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    return qualified[['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']]

# Weighted rating formula
def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

# Main function
def movie_based_movies(title: str, limit: int):
    file_path = './datasets/enriched_ch_data_new.csv'
    md = load_data(file_path)
    md['genres'] = md['genres'].fillna('').apply(split_genres)
    md['keywords'] = md['keywords'].fillna('').apply(split_keywords)

    smd = process_data(md)
    cosine_sim = calculate_cosine_similarity(smd)
    smd = smd.reset_index()
    titles = smd['title']
    indices = pd.Series(smd.index, index=smd['title'])
    recommendations = improved_recommendations(title, smd, indices, cosine_sim)
    
    if isinstance(recommendations, str):
        # If recommendations is a string, it means the movie was not found
        return recommendations
    else:
        # If recommendations is a DataFrame, return the limited results
        return recommendations.head(limit).reset_index(drop=True)
