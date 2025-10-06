import streamlit as st
import pandas as pd
import pickle
import requests
from requests.exceptions import RequestException
import time

def fetch_poster(movie_id, retries=3, delay=5):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=1f54a24f1dd67b09e2427633faefd8d2&language=en-US'
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            if 'poster_path' in data:
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                return "https://via.placeholder.com/500x750?text=No+Poster+Available"
        except RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(delay)  # Wait before retrying
    return "https://via.placeholder.com/500x750?text=Error+Fetching+Poster"


def fetch_video_url(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=1f54a24f1dd67b09e2427633faefd8d2&language=en-US'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data['results']:
            # Get the first trailer or video result
            video = next((vid for vid in data['results'] if vid['type'] == 'Trailer'), data['results'][0])
            return f"https://www.youtube.com/embed/{video['key']}?autoplay=1"  # Use embed URL for autoplay
        else:
            return None
    except RequestException as e:
        print(f"Request failed: {e}")
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_urls = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        # fetch video URL from API
        recommended_movie_urls.append(fetch_video_url(movie_id))
    return recommended_movies, recommended_movie_posters, recommended_movie_urls


movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values)

if st.button('Recommend'):
    names, posters, urls = recommend(selected_movie_name)

    # Create tabs for each recommendation
    tabs = st.tabs([names[i] for i in range(5)])

    for i in range(5):
        with tabs[i]:
            # Create a horizontal layout with columns for the poster and video
            col1, col2 = st.columns([1, 2])  # Adjust column widths as needed

            with col1:
                # Display the poster image without explicit width and height
                st.image(posters[i],width="90%", use_column_width=True)

            with col2:
                # Display the video iframe
                if urls[i]:
                    st.markdown(f'<iframe width="100%" height="337" src="{urls[i]}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                else:
                    st.text("Trailer not available")
