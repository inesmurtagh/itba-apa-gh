# -*- coding: utf-8 -*-
"""app_completa.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Hqz8R7BXyXFSdGH-d2xgocsP7k-Xmhet
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from scipy.spatial.distance import cdist
import plotly.express as px

# Load your data
data = pd.read_csv("dataset.csv")

number_cols = ['valence', 'year', 'decade', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit', 'key',
               'mode', 'instrumentalness', 'liveness', 'loudness', 'popularity', 'speechiness', 'tempo', 'cluster']

# Function to retrieve song data for a given song name
def get_song_data(name, data):
    try:
        return data[data['name'].str.lower() == name].iloc[0]
    except IndexError:
        return None

# Function to calculate the mean vector of a list of songs
def get_mean_vector(song_list, data):
    song_vectors = []
    for song in song_list:
        song_data = get_song_data(song['name'], data)
        if song_data is None:
            print(f"Warning: {song['name']} no existe en el dataset")
            return None
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

# Function to recommend songs based on a list of seed songs
def recommend_songs(seed_songs, data, n_recommendations=10):
    metadata_cols = ['name', 'artists', 'year']
    song_center = get_mean_vector(seed_songs, data)

    # Return an empty list if song_center is missing
    if song_center is None:
        return []

    # Normalize the song center
    normalized_song_center = min_max_scaler.transform([song_center])

    # Standardize the normalized song center
    scaled_normalized_song_center = standard_scaler.transform(normalized_song_center)

    # Calculate Euclidean distances and get recommendations
    distances = cdist(scaled_normalized_song_center, scaled_normalized_data, 'euclidean')
    index = np.argsort(distances)[0]

    # Filter out seed songs and duplicates, then get the top n_recommendations
    rec_songs = []
    for i in index:
        song_name = data.iloc[i]['name']
        if song_name not in [song['name'] for song in seed_songs] and song_name not in [song['name'] for song in rec_songs]:
            rec_songs.append(data.iloc[i])
            if len(rec_songs) == n_recommendations:
                break

    # Remove the seed song from recommendations if it's present
    rec_songs = [song for song in rec_songs if song['name'].lower() != seed_songs[0]['name']]

    return pd.DataFrame(rec_songs)[metadata_cols].to_dict(orient='records')

# Normalize the song data using Min-Max Scaler
min_max_scaler = MinMaxScaler()
normalized_data = min_max_scaler.fit_transform(data[number_cols])

# Standardize the normalized data using Standard Scaler
standard_scaler = StandardScaler()
scaled_normalized_data = standard_scaler.fit_transform(normalized_data)

# Streamlit app
st.set_page_config(layout='wide')

st.title('Sistema de recomendación de Música')
st.subheader('Recomendaciones personalizadas de canciones')

# Subheader
# st.subheader('| Sobre ')

"""
El modelo ofrece a los usuarios una lista seleccionada de canciones que son similares a las canciones elegidas.

El sistema de recomendación funciona calculando la similitud entre canciones mediante diversas características numéricas como valencia, acústica, capacidad de baile y más.
Los usuarios pueden ingresar los nombres de sus canciones favoritas, y el sistema generará una lista de canciones recomendadas que es probable que les gusten según las similitudes en estas características.

"""

# Streamlit app
st.sidebar.subheader('Recomendador')
song_names = st.sidebar.text_area("Escribir los nombres de las canciones (una por línea):")

# Slider to select the number of recommendations
n_recommendations = st.sidebar.slider("Cantidad de recomendaciones:", 1, 10, 5)

input_song_names = song_names.strip().split('\n') if song_names else []

# boton
if st.sidebar.button('Recomendar'):
    # Convert input to list of seed songs
    seed_songs = [{'name': name.lower()} for name in input_song_names]

    # Filter out empty names
    seed_songs = [song for song in seed_songs if song['name']]

    if not seed_songs:
        st.sidebar.warning("Porfavor, ingresar por lo menos una canción.")
    else:
        # Call the recommend_songs function
        recommended_songs = recommend_songs(seed_songs, data, n_recommendations)

        if not recommended_songs:
            st.sidebar.warning("No hay recomendaciones disponibles para las canciones elegidas.")
        else:
            # Convert the recommended songs to a DataFrame
            recommended_df = pd.DataFrame(recommended_songs)

            # Excluir la cancion ingresada por el usuario
            excluded_songs = [song['name'].lower() for song in seed_songs]

            # Verificar si la canción ingresada está en las recomendaciones
            if recommended_df['name'].str.lower().isin(excluded_songs).any():
                st.sidebar.warning("La canción esta incluida en las recomendaciones. Proba otra.")
            else :
                # Create a bar plot of recommended songs by name
                for index, row in recommended_df.iterrows():
                    st.sidebar.markdown(f"{index + 1}. {row['name']} by {row['artists']} ({row['year']})")

# About Me
st.sidebar.markdown('---')
st.sidebar.markdown('')
st.sidebar.markdown('App creada por:')
st.sidebar.text('Sofía Weintraub, Inés Murtagh')
st.sidebar.text('y Josefina Soto Acebal')
st.sidebar.markdown('[Link a la presentación](https://docs.google.com/presentation/d/1PrRhQbjNpI2GGjTz00z8F9oMch-MF1_hfVNl2CzEQqc/edit#slide=id.g1ec463fc7f2_0_15)')
st.sidebar.markdown('[Link al código de python](https://colab.research.google.com/drive/1H19o93nqGndW4-2oZ-PbWG0Ky3Kso_A8#scrollTo=4ICNZ9KsxV6a)')
st.sidebar.markdown('[Link al GitHub](https://github.com/inesmurtagh/itba-apa-gh)')

st.markdown('---')
st.subheader('| Datos interesantes del dataset utilizado')
st.markdown('')

st.subheader('Canciones más populares por año')

year = st.selectbox('Seleccionar año:', options=data['year'].unique())
data_year = data[data['year'] == year]

top_songs = data_year.nlargest(3, 'popularity')
fig_popularity = px.pie(top_songs, values='popularity', names='name', color='name')
fig_popularity.update_layout(height=500)
st.plotly_chart(fig_popularity, use_container_width=True)

data['decade'] = (data['year'] // 10) * 10

# Count the number of songs per decade
decade_counts = data['decade'].value_counts().sort_index()

# Canciones por decada
st.subheader('Cantidad de canciones por década')
fig_decades = px.bar(x=decade_counts.index, y=decade_counts.values,
                     labels={'x': 'Decade', 'y': 'Number of Songs'},
                     color=decade_counts.values)
fig_decades.update_layout(xaxis_type='category', height=500)
st.plotly_chart(fig_decades, use_container_width=True)

lista = ['valence', 'year', 'decade', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'duration_ms']

# Histograma
st.subheader('Distribución de las características de las canciones')
attribute_to_plot = st.selectbox('Seleccionar una característica:', lista)
fig_histogram = px.histogram(data, x=attribute_to_plot, nbins=30,
                              title=f'Distribución de {attribute_to_plot}')
fig_histogram.update_layout(height=500)
st.plotly_chart(fig_histogram, use_container_width=True)

# Display a bar plot of artists with the most songs in the dataset
st.subheader('Artistas con más canciones')
top_artists = data['artists'].str.replace("[", "").str.replace("]", "").str.replace("'", "").value_counts().head(10)
fig_top_artists = px.bar(top_artists, x=top_artists.index, y=top_artists.values, color=top_artists.index,
                         labels={'x': 'Artista', 'y': 'Número of Canciones'})
fig_top_artists.update_xaxes(categoryorder='total descending')
fig_top_artists.update_layout(height=500, showlegend=False)
st.plotly_chart(fig_top_artists, use_container_width=True)