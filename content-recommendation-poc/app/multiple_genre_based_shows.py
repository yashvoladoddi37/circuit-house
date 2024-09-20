import pandas as pd
import numpy as np
import math
from ast import literal_eval

# Load the dataset
def load_data(file_path):
    return pd.read_csv(file_path)

# Parse and clean the 'genres' column
def split_genres(genre_str):
    genres = []
    for part in genre_str.split(','):
        genres.extend(part.split('&'))
    return [genre.strip() for genre in genres]

# Build chart based on genre
def build_chart(df, genre, top_n, percentile=0.85):
    # Filter rows where genre is in the genres list
    df = df[df['genres'].apply(lambda x: genre in x)]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)

    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(top_n * 2)
    
    qualified = qualified.drop(columns=['wr'])
    
    return qualified[['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']]

# Main function to run the analysis
def multiple_genre_based_shows(genres: list):
    file_path = './datasets/shows_data.csv'
    md = load_data(file_path)
    md['genres'] = md['genres'].fillna('').apply(split_genres)
    
    top_shows = pd.DataFrame()
    seen_shows = set()
    num = math.ceil(10 / len(genres))
    for genre in genres:
        top_shows_genre = build_chart(md, genre, num)
        top_shows_genre = top_shows_genre[~top_shows_genre['id'].isin(seen_shows)]
        seen_shows.update(top_shows_genre['id'].values)
        
        top_shows = pd.concat([top_shows, top_shows_genre.head(num)])
    
    return top_shows.reset_index(drop=True)