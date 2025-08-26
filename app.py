import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
from requests.exceptions import RequestException

# Page config
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Load data with caching
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open("movie_list.pkl", "rb"))
        similarity = pickle.load(open("similarity.pkl", "rb"))
        return movies, similarity
    except FileNotFoundError:
        st.error("Model files not found! Need movie_list.pkl and similarity.pkl")
        return None, None

# Fetch movie poster URL from TMDB API with caching
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w300{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except RequestException:
        return "https://via.placeholder.com/300x450?text=Unavailable"

# Generate recommendations (top N similar movies)
def get_recommendations(movie_title, movies, similarity, n=10):
    if movie_title not in movies['title'].values:
        return None
    
    idx = movies[movies['title'] == movie_title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]  # exclude self
    
    return [{
        "title": movies.iloc[i]['title'],
        "score": score,
        "movie_id": movies.iloc[i]['movie_id']
    } for i, score in scores]

# Create a movie card using Streamlit's native components
def create_movie_card(title, score=None, poster_url=None):
    # Display poster image
    if poster_url:
        st.image(poster_url, width=200)
    
    # Display title
    st.markdown(f"**{title}**")
    
    # Display score if provided
    if score:
        st.success(f"Similarity: {score:.3f}")

# Alternative HTML card (properly formatted)
def movie_html_card(title, score=None, poster_url=None):
    score_badge = ""
    if score:
        score_badge = f'''
        <div style="
            position: absolute; 
            top: 10px; 
            right: 10px; 
            background: #4CAF50; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 12px; 
            font-weight: bold; 
            font-size: 0.8rem;
            z-index: 10;
        ">{score:.3f}</div>'''
    
    # Escape HTML in title to prevent issues
    escaped_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    
    card_html = f"""
    <div style="
        position: relative;
        width: 100%;
        max-width: 200px;
        margin: 10px auto;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
        background: #1e1e1e;
        color: white;
        font-family: Arial, sans-serif;
    ">
        <img src="{poster_url}" alt="{escaped_title}" style="
            width: 100%; 
            height: 300px; 
            object-fit: cover; 
            display: block;
        ">
        {score_badge}
        <div style="
            padding: 12px;
            text-align: center;
            font-weight: bold;
            font-size: 0.9rem;
            background: #2a2a2a;
            min-height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <span title="{escaped_title}">{escaped_title}</span>
        </div>
    </div>
    """
    return card_html

# Main app function
def main():
    st.title("🎬 Movie Recommendation System")
    st.caption("Find movies similar to your favorites with AI-powered recommendations")
    st.markdown("**Coded by:** Anup Shrestha", unsafe_allow_html=True)

    movies, similarity = load_data()
    if movies is None:
        return

    movie_titles = movies['title'].tolist()

    # Sidebar UI
    with st.sidebar:
        st.header("🎯 Find Movies")
        search = st.text_input("🔍 Search movies:", placeholder="Type to filter...")
        filtered_movies = [m for m in movie_titles if search.lower() in m.lower()] if search else movie_titles

        if not filtered_movies:
            st.warning("No matches found")
            filtered_movies = movie_titles[:10]

        selected = st.selectbox("Select a movie:", filtered_movies)
        count = st.slider("Number of recommendations:", 5, 20, 10)
        
        # Style options
        display_style = st.radio("Display style:", ["Cards"])
        
        get_recs = st.button("🚀 Get Recommendations", type="primary", use_container_width=True)

        with st.expander("📊 App Info"):
            st.metric("Total Movies", f"{len(movies):,}")
            st.write("**Algorithm:** Content-based filtering with cosine similarity")

    # Main content area
    if selected:
        st.subheader("🎥 Selected Movie")
        
        # Get selected movie details
        try:
            selected_movie_id = movies[movies['title'] == selected].movie_id.values[0]
            selected_poster = fetch_poster(selected_movie_id)
        except:
            selected_poster = "https://via.placeholder.com/300x450?text=No+Poster"
        
        # Display selected movie
        col1, col2, col3 = st.columns([1, 1, 2])
        with col2:
            if display_style == "HTML Grid":
                st.markdown(movie_html_card(selected, poster_url=selected_poster), unsafe_allow_html=True)
            else:
                create_movie_card(selected, poster_url=selected_poster)

        if get_recs:
            with st.spinner("🔄 Finding similar movies..."):
                recs = get_recommendations(selected, movies, similarity, count)
                if not recs:
                    st.error("❌ No recommendations found!")
                    return

                st.subheader("🎯 Recommended Movies")

                if display_style == "HTML Grid":
                    # HTML Grid display
                    cols_per_row = 4
                    for i in range(0, len(recs), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, rec in enumerate(recs[i:i + cols_per_row]):
                            if j < len(cols):
                                poster_url = fetch_poster(rec['movie_id'])
                                with cols[j]:
                                    st.markdown(
                                        movie_html_card(rec['title'], rec['score'], poster_url), 
                                        unsafe_allow_html=True
                                    )
                else:
                    # Native Streamlit cards
                    cols_per_row = 3
                    for i in range(0, len(recs), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, rec in enumerate(recs[i:i + cols_per_row]):
                            if j < len(cols):
                                poster_url = fetch_poster(rec['movie_id'])
                                with cols[j]:
                                    create_movie_card(rec['title'], rec['score'], poster_url)

                # Analytics section
                st.subheader("📈 Recommendation Analytics")
                col1, col2, col3 = st.columns(3)
                
                scores = [r['score'] for r in recs]
                with col1:
                    st.metric("Average Similarity", f"{np.mean(scores):.3f}")
                with col2:
                    st.metric("Highest Similarity", f"{max(scores):.3f}")
                with col3:
                    st.metric("Lowest Similarity", f"{min(scores):.3f}")

                # Results table
                st.subheader("📋 Detailed Results")
                df = pd.DataFrame(recs)
                df = df.reset_index()
                df['index'] = df['index'] + 1
                df = df.rename(columns={
                    'index': 'Rank',
                    'title': 'Movie Title',
                    'score': 'Similarity Score'
                })
                df = df[['Rank', 'Movie Title', 'Similarity Score']]
                df['Similarity Score'] = df['Similarity Score'].round(4)
                
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Download section
                st.subheader("💾 Export Results")
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download as CSV",
                    csv,
                    f"movie_recommendations_{selected.replace(' ', '_').replace('/', '_')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        else:
            st.info("👆 Click 'Get Recommendations' in the sidebar to find similar movies!")
    else:
        st.info("🎬 Select a movie from the sidebar to get started!")
        st.markdown("---")
        st.markdown("### How it works:")
        st.markdown("""
        1. **Select a movie** from the dropdown in the sidebar
        2. **Choose the number** of recommendations you want
        3. **Pick your display style** (Cards or HTML Grid)
        4. **Click 'Get Recommendations'** to see similar movies
        5. **Download results** as CSV for later reference
        """)


        # namee
    st.markdown("""
    <hr style="margin-top: 3em;">
    <div style='text-align: center; color: gray; font-size: 0.85rem;'>
        Coded by: <a href="https://github.com/anupstha01" target="_blank" style="color: #bbb;">Anup Shrestha</a> 🎬
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()