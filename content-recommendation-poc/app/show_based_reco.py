import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load the dataset
def load_data(file_path):
    return pd.read_csv(file_path)

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

    return qualified[['id', 'title', 'content_type', 'genres', 'backdrop_path','poster_path']]

# Weighted rating formula
def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

# Main function
def show_based_shows(title: str, limit : int):
    file_path = './datasets/shows_data_small.csv'
    md = load_data(file_path)
    md['genres'] = md['genres'].fillna('').apply(split_genres)

    smd = process_data(md)
    cosine_sim = calculate_cosine_similarity(smd)
    smd = smd.reset_index()
    titles = smd['title']
    indices = pd.Series(smd.index, index=smd['title'])
    recommendations = improved_recommendations(title, smd, indices, cosine_sim)
    return recommendations.reset_index(drop=True)