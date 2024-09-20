import pandas as pd
import numpy as np
from app.utils import load_data

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


# Main function to run the analysis
def genre_based_content(genre: str, limit: int, content_type: str = None):
    bucket_name = 'enriched-dataset'  # Replace with your S3 bucket name
    file_key = 'enriched_ch_data_shows.csv'  # Replace with your S3 file key
    content_data = load_data(file_key, bucket_name)
    
    # Apply content type filtering if provided
    if content_type:
        content_data = content_data[content_data['content_type'] == content_type]
    
    # Parse and clean genres
    content_data['genres'] = content_data['genres'].fillna('').apply(split_genres)
    
    # Build the top content chart
    top_content = build_chart(content_data, genre)
    top_content['id'] = top_content['id'].astype(str)
    
    return top_content.head(limit).reset_index(drop=True)
