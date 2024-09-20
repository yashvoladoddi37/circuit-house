import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from surprise import Reader, Dataset, SVD
import warnings
warnings.simplefilter('ignore')
import boto3

s3 = boto3.client
bucket_name = 'enriched-dataset'


# Load datasets
def load_data():
    md = pd.read_csv('./datasets/movies_data.csv', on_bad_lines='skip', engine='python')
    ratings = pd.read_csv('./datasets/ratings_with_timestamps.csv', on_bad_lines='skip', engine='python')
    links = pd.read_csv('./datasets/links_small.csv', on_bad_lines='skip', engine='python')
    return md, ratings, links

# Extract and process features from the data
def process_data(md, links):
    md = md[md['id'].isin(links['tmdbId'])]
    md['principal_cast'] = md['principal_cast'].apply(literal_eval).apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
    md['director'] = md['directors'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
    md['directors'] = md['directors'].apply(lambda x: [x, x, x])

    s = md.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'keyword'
    s = s.value_counts()
    s = s[s > 1]

    stemmer = SnowballStemmer('english')
    md['keywords'] = md['keywords'].apply(literal_eval).apply(lambda x: filter_keywords(x, s, stemmer))
    md['genres'] = md['genres'].apply(literal_eval)
    md['soup'] = md.apply(lambda x: x['keywords'] + x['principal_cast'] + x['directors'] + x['genres'], axis=1)
    md['soup'] = md['soup'].apply(lambda x: ' '.join(map(str, x)))

    return md

# Function to filter keywords
def filter_keywords(keywords, s, stemmer):
    words = [stemmer.stem(i) for i in keywords if i in s]
    return [str.lower(i.replace(" ", "")) for i in words]

# Build the count matrix and cosine similarity matrix
def build_cosine_sim(smd):
    count = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.0, stop_words='english')
    count_matrix = count.fit_transform(smd['soup'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return cosine_sim

# Train the SVD model
def train_svd_model(ratings):
    reader = Reader()
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    algo = SVD()
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    return algo

# Convert id to int
def convert_int(x):
    try:
        return int(x)
    except:
        return np.nan

# Build the ID map
def build_id_map(smd):
    id_map = pd.read_csv('./datasets/links_small.csv', on_bad_lines='skip', engine='python')[['movieId', 'tmdbId']]
    id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
    id_map.columns = ['movieId', 'id']
    id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')
    indices_map = id_map.set_index('id')
    return id_map, indices_map

# Hybrid recommendation function
def hybrid(userId, title, cosine_sim, algo, id_map, indices_map, smd, indices):
    try:
        idx = indices[title]
        sim_scores = list(enumerate(cosine_sim[int(idx)]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:26]
        movie_indices = [i[0] for i in sim_scores]

        # Include additional fields in the output
        movies = smd.iloc[movie_indices]
        movies['est'] = movies['id'].apply(lambda x: algo.predict(userId, indices_map.loc[x]['movieId']).est)
        
        # Convert numpy.int64 to standard Python types
        movies['vote_count'] = movies['vote_count'].astype(int)
        movies['vote_average'] = movies['vote_average'].astype(float)
        movies['id'] = movies['id'].astype(int)
        movies['est'] = movies['est'].astype(float)

        movies = movies.sort_values('est', ascending=False).head(30)
        movies = movies.drop(columns=['est'])
        return movies.reset_index(drop=True)  # Reset index and remove old index

    except KeyError as e:
        print(f"KeyError: {e}. Check if '{title}' exists in the data.")
        return pd.DataFrame()

    except IndexError:
        print(f"IndexError: Index out of bounds. Failed to generate recommendations for '{title}'.")
        return pd.DataFrame()

# Main function to run the analysis
def users_rating_based_movies(userId: int, limit: int):
    md, ratings, links = load_data()
    smd = process_data(md,links)
    cosine_sim = build_cosine_sim(smd)
    algo = train_svd_model(ratings)
    id_map, indices_map = build_id_map(smd)
    smd = smd.reset_index()
    indices = pd.Series(smd.index, index=smd['title'])

    user_ratings = ratings[ratings['userId'] == userId]

    if user_ratings.empty:
        print(f"No ratings found for user {userId}.")
        return pd.DataFrame()

    # Find the highest rated movie by the user
    rated_movies = user_ratings.sort_values(by='rating', ascending=False)
    for idx, rating_row in rated_movies.iterrows():
        movie_id = rating_row['movieId']
        if movie_id in smd['id'].values:
            highest_rated_movie_title = smd.loc[smd['id'] == movie_id, 'title'].iloc[0]
            break
    else:
        print(f"No valid rated movies found in movies metadata for user {userId}.")
        return []
    recommendations = hybrid(userId, highest_rated_movie_title, cosine_sim, algo, id_map, indices_map, smd, indices)
    output_columns = ['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']
    recommendations = recommendations[output_columns].head(limit).reset_index(drop=True)
    return recommendations