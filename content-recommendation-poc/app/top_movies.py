# import pandas as pd
# import numpy as np

# def load_data(file_path):
#     return pd.read_csv(file_path)

# def calculate_vote_statistics(df):
#     vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype(int)
#     vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype(int)
#     C = vote_averages.mean()
#     m = vote_counts.quantile(0.95)
#     return C, m

# def filter_qualified_movies(df, m):
#     qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())]
#     qualified['vote_count'] = qualified['vote_count'].astype(int)
#     qualified['vote_average'] = qualified['vote_average'].astype(int)
#     return qualified

# def weighted_rating(x, m, C):
#     v = x['vote_count']
#     R = x['vote_average']
#     return (v / (v + m) * R) + (m / (m + v) * C)

# def compute_and_sort_movies(df, m, C):
#     df['wr'] = df.apply(lambda x: weighted_rating(x, m, C), axis=1)
#     df = df.sort_values('wr', ascending=False).head(30)
    
#     # Convert numpy types to native Python types
#     df = df.applymap(lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x)
#     df = df.applymap(lambda x: float(x) if isinstance(x, (np.float64, np.float32)) else x)
    
#     return df

# def top_n_movies(limit : int):
#     file_path = './datasets/movies_data.csv'
#     md = load_data(file_path)
#     C, m = calculate_vote_statistics(md)
#     qualified = filter_qualified_movies(md, m)
#     top_movies = compute_and_sort_movies(qualified, m, C)
#     output_columns = ['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']
#     sorted_movies = top_movies[output_columns].head(limit).reset_index(drop=True)
#     return sorted_movies.reset_index(drop=True)


import pandas as pd
import numpy as np

# Load the dataset
def load_data(file_path):
    return pd.read_csv(file_path)

# Parse and clean the 'genres' column
def split_genres(genre_str):
    genres = []
    for part in genre_str.split(','):
        genres.extend(part.split('&'))
    return [genre.strip() for genre in genres]

def calculate_vote_statistics(df):
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype(int)
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype(int)
    C = vote_averages.mean()
    m = vote_counts.quantile(0.95)
    return C, m

def filter_qualified_shows(df, m):
    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype(int)
    qualified['vote_average'] = qualified['vote_average'].astype(int)
    return qualified

def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

def compute_and_sort_shows(df, m, C):
    df['wr'] = df.apply(lambda x: weighted_rating(x, m, C), axis=1)
    df = df.sort_values('wr', ascending=False).head(30)
    
    # Convert numpy types to native Python types
    df = df.applymap(lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x)
    df = df.applymap(lambda x: float(x) if isinstance(x, (np.float64, np.float32)) else x)
    
    return df

def top_n_movies(limit: int):
    file_path = './datasets/enriched_ch_data_new.csv'
    md = load_data(file_path)
    md['genres'] = md['genres'].fillna('').apply(split_genres)
    
    C, m = calculate_vote_statistics(md)
    qualified = filter_qualified_shows(md, m)
    top_shows = compute_and_sort_shows(qualified, m, C)
    output_columns = ['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']
    sorted_shows = top_shows[output_columns].head(limit).reset_index(drop=True)
    return sorted_shows.reset_index(drop=True)