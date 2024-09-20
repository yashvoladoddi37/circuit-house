import pandas as pd
import datetime
import numpy as np

# Load data from CSV files
def load_data():
    users_df = pd.read_csv('./datasets/users.csv', on_bad_lines='skip', engine='python') 
    ratings_df = pd.read_csv('./datasets/ratings_with_timestamps.csv', on_bad_lines='skip', engine='python')
    movies_df = pd.read_csv('./datasets/movies_data.csv', on_bad_lines='skip', engine='python')
    
    return users_df, ratings_df, movies_df

# Merge users and ratings dataframes on 'userId'
def merge_data(users_df, ratings_df):
    merged_df = pd.merge(users_df, ratings_df, on='userId')
    return merged_df[['userId', 'Country', 'movieId', 'timestamp']]

# Filter dataframe based on selected country ISO code
def filter_by_country(df, country):
    if country.lower() == 'all':
        return df
    else:
        return df[df['Country'] == country]

# Convert timestamps to datetime and calculate weighted score
def calculate_weighted_score(timestamps, days):
    now = datetime.datetime.now()
    weights = timestamps.apply(lambda x: (now - x).days).apply(lambda x: np.exp(-x / days))
    return weights

# Get top trending movies based on weighted scores
def get_top_trending_movies(df, weeks):
    days = (weeks * 7) + 7
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['weighted_score'] = calculate_weighted_score(df['timestamp'], days)
    movie_trend_scores = df.groupby('movieId')['weighted_score'].sum().reset_index()
    return movie_trend_scores.sort_values(by='weighted_score', ascending=False).head(30)

# Merge with movie titles
def merge_with_movie_titles(trending_movies_df, movies_df):
    trending_movies_df['movieId'] = trending_movies_df['movieId'].astype(str)
    movies_df['id'] = movies_df['id'].astype(str)
    return pd.merge(trending_movies_df, movies_df, left_on='movieId', right_on='id')

#Enter the country ISO code you want to filter by (e.g., IN for India, US for United States, CA for Canada, CN for China, UK for United Kingdom) or type 'All' to select all countries
#Enter the number of weeks ago for trending movies (0 for this week, 1 for last week, and so on, up to 104 for the last two years)
def get_trending_movies_global(country: str, week: int, limit: int):
    users_df, ratings_df, movies_df = load_data()
    merged_df = merge_data(users_df, ratings_df)
    filtered_df = filter_by_country(merged_df, country)
    top_trending_movies = get_top_trending_movies(filtered_df, week)
    top_trending_movies_with_titles = merge_with_movie_titles(top_trending_movies, movies_df)
    output_columns = ['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']
    top_trending_movies_with_titles = top_trending_movies_with_titles[output_columns].head(limit).reset_index(drop=True)
    return top_trending_movies_with_titles
