import pandas as pd
import datetime
import numpy as np
from typing import List
from ast import literal_eval
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.utils import load_data, encode_cursor, decode_cursor

# Importing functions from other files
from app.genre_based_shows import genre_based_shows
from app.genre_based_movies import genre_based_movies
from app.genre_based_weight_movies import genre_based_movies_weight
from app.genre_based_weight_shows import genre_based_shows_weight
from app.movie_based_reco import movie_based_movies
from app.show_based_reco import show_based_shows
from app.multiple_genre_based_movies import multiple_genre_based_movies
from app.multiple_genre_based_shows import multiple_genre_based_shows
from app.top_movies import top_n_movies
from app.top_shows import top_n_shows
from app.toptrending_movies_global import get_trending_movies_global
from app.toptrending_movies_week import get_trending_movies_week
from app.user_based_movies_reco import users_rating_based_movies
from app.preview import search_id_in_csv


app = FastAPI()

from typing import Optional

@app.get("/recommendation/genrebasedmovies")
async def get_genre_based_movies(
    genre: str = Query(..., description="The genre of the movie to filter by", example="Drama"),
    limit: int = Query(20, description="The number of results to return", example=10),
    cursor: Optional[str] = Query(None, description="Cursor for pagination")
):
    try:
        result = genre_based_movies(genre, limit, cursor)
        
        # Replace NaN, inf, and -inf values
        result['data'] = pd.DataFrame(result['data']).replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict(orient='records')
        
        return result
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

# @app.get("/recommendation/genrebasedmovies")
# async def get_genre_based_movies(
#     genre: str = Query(..., description="The genre of the movie to filter by", example="Drama"),
#     limit: int = Query(20, description="The number of results to return", example=10),
#     cursor: Optional[str] = Query(None, description="Cursor for pagination"),
#     providers: Optional[List[str]] = Query(None, description="List of content providers to filter by"),
#     max_limit: int = 100
# ):
#     try:
#         # Enforce maximum limit
#         limit = min(limit, max_limit)
        
#         # Load data from S3
#         bucket_name = 'your-s3-bucket-name'
#         file_key = 'movies_data.csv'
#         movies_df = load_data_from_s3(bucket_name, file_key)
        
#         # Filter by genre
#         top_movies = genre_based_movies(movies_df, genre)
        
#         # Filter by content providers if specified
#         if providers:
#             top_movies = top_movies[top_movies['provider'].isin(providers)]
        
#         # Apply cursor-based pagination
#         if cursor:
#             last_id, last_score = decode_cursor(cursor)
#             top_movies = top_movies[
#                 (top_movies['score'] < last_score) |
#                 ((top_movies['score'] == last_score) & (top_movies['id'] > last_id))
#             ]
        
#         # Get the next page of results
#         result = top_movies.head(limit + 1)
        
#         # Prepare the response
#         has_more = len(result) > limit
#         top_movies = result[:limit]
        
#         next_cursor = None
#         if has_more:
#             last_item = top_movies.iloc[-1]
#             next_cursor = encode_cursor(last_item['id'], last_item['score'])
        
#         top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
#         top_movies_json = top_movies.to_dict(orient='records')
        
#         return {
#             "results": top_movies_json,
#             "next_cursor": next_cursor
#         }
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=str(error)) from error
    
@app.get("/recommendation/genreweightbasedmovies")
async def get_genre_based_movies_weight(genre: str = Query(..., description="The genre of the movie to filter by", example="Action,Drama")):
    try:
        genre_list = genre.split(',')
        top_movies = genre_based_movies_weight(genre_list)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')  # Convert DataFrame to list of dicts
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
# @app.get("/recommendation/genreweightbasedshows")
# async def get_genre_based_shows_weight(genre: str = Query(..., description="The genre of the TV shows to filter by", example="Action,Drama")):
#     try:
#         genre_list = genre.split(',')
#         top_shows = genre_based_shows_weight(genre_list)
#         top_shows = top_shows.replace({np.nan: None, np.inf: None, -np.inf: None})
#         top_shows_json = top_shows.to_dict(orient='records')  # Convert DataFrame to list of dicts
#         return top_shows_json
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=str(error)) from error

@app.get("/recommendation/moviebased")
async def get_movie_based_movies(title: str = Query(..., description="The title of the movie to base recommendations on", example="Inception"), limit: int = Query(20, description="The number of results to return", example=10)):
    try:
        top_movies = movie_based_movies(title, limit)
        if isinstance(top_movies, str):
            # If top_movies is a string, it means the movie was not found
            raise HTTPException(status_code=404, detail=top_movies)
        else:
            # If top_movies is a DataFrame, process it as before
            top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
            top_movies_json = top_movies.to_dict(orient='records')
            return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
# @app.get("/recommendation/showbased")
# async def get_show_based_shows(title: str = Query(..., description="The title of the TV shows to base recommendations on", example="Game of Thrones"), limit: int = Query(20, description="The number of results to return", example=10)):
#     try:
#         top_shows = show_based_shows(title, limit)
#         top_shows = top_shows.replace({np.nan: None, np.inf: None, -np.inf: None})
#         top_shows_json = top_shows.to_dict(orient='records')  # Convert DataFrame to list of dicts
#         return top_shows_json
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=str(error)) from error
    
# @app.get("/recommendation/genremultipleshows")
# async def get_multiple_genre_based_shows(genre: str = Query(..., description="The genre of the TV shows to filter by", example="Action,Drama")):
#     try:
#         genre_list = genre.split(',')
#         top_shows = multiple_genre_based_shows(genre_list)
#         top_shows = top_shows.replace({np.nan: None, np.inf: None, -np.inf: None})
#         top_shows_json = top_shows.to_dict(orient='records')  # Convert DataFrame to list of dicts
#         return top_shows_json
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=str(error)) from error

@app.get("/recommendation/genremultiplemovies")
async def get_multipule_genre_based_movies(genre: str = Query(..., description="The genre of the movies to filter by", example="Action,Drama")):
    try:
        genre_list = genre.split(',')
        top_movies = multiple_genre_based_movies(genre_list)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
@app.get("/recommendation/movies")
async def get_top_movies(limit: int = Query(20, description="The number of results to return", example=10)):
    try:
        top_movies = top_n_movies(limit)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')  # Convert DataFrame to list of dicts
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
# @app.get("/recommendation/shows")
# async def get_top_shows(limit: int = Query(20, description="The number of results to return", example=10)):
#     try:
#         top_shows = top_n_shows(limit)
#         top_shows = top_shows.replace({np.nan: None, np.inf: None, -np.inf: None})
#         top_shows_json = top_shows.to_dict(orient='records')  # Convert DataFrame to list of dicts
#         return top_shows_json
#     except Exception as error:
#         raise HTTPException(status_code=500, detail=str(error)) from error
    
@app.get("/recommendation/toptrendingGlobalmovies")
async def get_top_movies(week: int = Query(..., description="The week number to filter the trending movies (e.g., '32' for the 32nd week of the year)", example=32) , limit: int = Query(20, description="The number of results to return", example=10)):
    try:
        top_movies = get_trending_movies_global(week, limit)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')  # Convert DataFrame to list of dicts
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
@app.get("/recommendation/toptrendingWeekmovies")
async def get_top_movies(country: str = Query(..., description="The country code to filter the trending movies (e.g., 'US', 'IN')", example="US"), week: int = Query(..., description="The week number to filter the trending movies (e.g., '32' for the 32nd week of the year)", example=32) , limit: int = Query(20, description="The number of results to return", example=10)):
    try:
        top_movies = get_trending_movies_week(country, week, limit)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')  # Convert DataFrame to list of dicts
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

@app.get("/recommendation/usersratingbased")
async def get_users_rating_based_movies(userid: int = Query(..., description="The unique ID of the user whose ratings are to be used for recommendations", example=123) , limit: int = Query(20, description="The number of results to return", example=10)):
    try:
        top_movies = users_rating_based_movies(userid, limit)
        top_movies = top_movies.replace({np.nan: None, np.inf: None, -np.inf: None})
        top_movies_json = top_movies.to_dict(orient='records')  # Convert DataFrame to list of dicts
        return top_movies_json
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    
@app.get("/preview")
async def search_movie(id: str = Query(..., description="The unique ID of the movie or show to preview", example="98"), content_type: str = Query(..., description="The type of content: 'movie' or 'tv_show'", example="movie")):
    result = search_id_in_csv(id, content_type)
    if result.empty:
        raise HTTPException(status_code=404, detail="ID not found")
    else:
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return result.to_dict(orient='records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)