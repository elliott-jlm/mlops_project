import pandas as pd

import numpy as np
from scipy.sparse import csr_matrix
import scipy.sparse as sp
import statistics
from sklearn.metrics.pairwise import cosine_similarity

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('distilbert-base-nli-mean-tokens')

data = pd.read_csv("./backend/anime_data.csv")

data_genre = pd.read_csv('./backend/data_genre.csv', sep=";")
data_producer = pd.read_csv('./backend/data_producer.csv', sep=";")
data_studio = pd.read_csv('./backend/data_studio.csv', sep=";")
data_type = pd.read_csv('./backend/data_type.csv', sep=";")
embeddings = np.load('./backend/embeddings.npy')



def clean_data(x):
    for character in "['] ":
        x = x.replace(character, '')
    
    return x



data.dropna(subset=['Rating','Producer','Studio'], inplace=True)
data.reset_index(drop=True, inplace=True)



def database_anime(title, genre, synopsis, types, producer, studio):
    data = {
        'Title': title,
        'Genre': genre,
        'Synopsis': synopsis,
        'Type': types,
        'Producer': producer,
        'Studio': studio,
    }
    return pd.DataFrame(data, index=[0])



def sparse_data(data_genre, data_producer, data_studio, data_type):

    sparse_genre = csr_matrix(data_genre.values.tolist())
    sparse_producer = csr_matrix(data_producer.values.tolist())
    sparse_studio = csr_matrix(data_studio.values.tolist())
    sparse_type = csr_matrix(data_type.values.tolist())
    
    return sparse_genre, sparse_producer, sparse_studio, sparse_type



def prediction_method(c, m):
    similarity_matrix = cosine_similarity(c, m)
    return(similarity_matrix)



def prediction_anime(title, genre, synopsis, types, producer, studio):
    idx_Cos_sim = []
    
    anime = database_anime(title, genre, synopsis, types, producer, studio)
    
    #sparse matrix of data
    sparse_genre, sparse_producer, sparse_studio, sparse_type = sparse_data(data_genre, data_producer, data_studio, data_type)
    
    anime['Genre'] = anime['Genre'].apply(lambda x: clean_data(x) if type(x)==str else 'No genre')
    anime_genre = anime['Genre'].str.get_dummies(sep=',').reindex(columns=data_genre.columns, fill_value=0)
    anime_genre_csr = csr_matrix(anime_genre)
    
    anime['Producer'] = anime['Producer'].apply(lambda x: clean_data(x) if type(x)==str else 'No producer')
    anime_producer = anime['Producer'].str.get_dummies(sep=',').reindex(columns=data_producer.columns, fill_value=0)
    anime_producer_csr = csr_matrix(anime_producer)
    
    anime['Studio'] = anime['Studio'].apply(lambda x: clean_data(x) if type(x)==str else 'No studio')
    anime_studio = anime['Studio'].str.get_dummies(sep=',').reindex(columns=data_studio.columns, fill_value=0)
    anime_studio_csr = csr_matrix(anime_studio)
    
    anime['Type'] = anime['Type'].apply(lambda x: clean_data(x) if type(x)==str else 'No genre')
    anime_type = anime['Type'].str.get_dummies(sep=',').reindex(columns=data_type.columns, fill_value=0)
    anime_type_csr = csr_matrix(anime_type)
    
    anime_matrix = sp.hstack([anime_genre_csr, anime_producer_csr, anime_studio_csr, anime_type_csr])
    synopsis_title = anime['Synopsis'] + ' ' + anime['Title']
    new_embedding = model.encode(synopsis_title)
    similarity_scores = cosine_similarity(new_embedding.reshape(1, -1), embeddings)
    
    for idx, row in data.iterrows():
        cos_sim = prediction_method(anime_matrix,sp.hstack([sparse_genre[idx], sparse_producer[idx], sparse_studio[idx], sparse_type[idx]]))
        cos_sim_final = cos_sim*4/6 + similarity_scores[0][idx]*2/6
        idx_Cos_sim.append((cos_sim_final, row['Rating']))
    idx_Cos_sim.sort(reverse=True, key=lambda tup: tup[0])
    
    # Extract the second element from each tuple using a list comprehension
    second_elements = [t[1] for t in idx_Cos_sim[0:5]]

    # Calculate the mean of the second elements using the mean method from the statistics module
    mean_rating = statistics.mean(second_elements)

    return mean_rating