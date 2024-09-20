import pandas as pd
import numpy as np
from app.utils import load_data
from typing import Optional
from botocore.exceptions import ClientError
from fastapi import HTTPException

# Parse and clean the 'genres' column
def split_genres(genre_str):
    genres = []
    for part in genre_str.split(','):
        genres.extend(part.split('&'))
    return [genre.strip() for genre in genres]

# Build chart based on genre
def build_chart(df, genre, percentile=0.85):
    # Filter rows where genre is in the genres list
    df = df[df['genres'].apply(lambda x: genre in x)]

    # Ensure 'vote_count' and 'vote_average' are numeric, coerce errors to NaN
    df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df = df.dropna(subset=['vote_count', 'vote_average'])
    vote_counts = df['vote_count'].astype('int')
    vote_averages = df['vote_average'].astype('int')

    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)

    qualified = df[(df['vote_count'] >= m)]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    qualified['wr'] = qualified.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) +
                  (m / (m + x['vote_count']) * C), axis=1
    )
    qualified = qualified.sort_values('wr', ascending=False).head(30)
    
    qualified = qualified.drop(columns=['wr'])
    
    return qualified[['id', 'title', 'content_type', 'genres', 'backdrop_path', 'poster_path']]


# Main function to run the analysis with cursor-based pagination
def genre_based_movies(genre: str, limit: int, cursor: Optional[str] = None):
    bucket_name = 'enriched-dataset'
    file_key = 'enriched_ch_data_shows.csv'
    
    try:
        md = load_data(file_key, bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            raise HTTPException(status_code=500, detail=f"S3 bucket '{bucket_name}' does not exist or is not accessible")
        else:
            raise HTTPException(status_code=500, detail=f"An error occurred while accessing S3: {str(e)}")
    
    md = md[md['content_type'] == 'movie']
    md['genres'] = md['genres'].fillna('').apply(split_genres)
    
    top_movies = build_chart(md, genre)
    top_movies['id'] = top_movies['id'].astype(str)
    
    # Implement cursor-based pagination
    if cursor:
        cursor_index = top_movies.index[top_movies['id'] == cursor].tolist()
        if cursor_index:
            start_index = cursor_index[0] + 1
            paginated_movies = top_movies.iloc[start_index:start_index + limit]
        else:
            paginated_movies = pd.DataFrame()
    else:
        paginated_movies = top_movies.head(limit)
    
    # Prepare pagination metadata
    next_cursor = None
    if len(paginated_movies) == limit and len(top_movies) > (start_index + limit if cursor else limit):
        next_cursor = paginated_movies.iloc[-1]['id']
    
    result = {
        'data': paginated_movies.reset_index(drop=True).to_dict('records'),
        'pagination': {
            'next_cursor': next_cursor,
        }
    }
    
    return result