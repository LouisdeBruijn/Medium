#!/usr/bin/env python3
# File name: alsrecommender.py
# Description: Analyses MovieLens Dataset and builds model from it using Implicit library
# Author: Louis de Bruijn
# Date: 07-08-2019
# Updated: 31-03-2022

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz, vstack, hstack, lil_matrix
import implicit
import pickle
from implicit.evaluation import train_test_split, precision_at_k, mean_average_precision_at_k


def load_data(movielens_file_path='files/ml-1m/ratings.dat'):
    """Loads the MovieLens 1m dataset in a Pandas dataframe.

    Args:
        movielens_file_path (str): file location for the MovieLens 1m dataset

    Returns:
        ratings (pd.DataFrame): Table with MovieLens 1m dataset, users * movies = ratings
    """
    ratings = pd.read_csv(movielens_file_path, delimiter='::', header=None,
                          names=['user_id', 'movie_id', 'rating', 'timestamp'],
                          usecols=['user_id', 'movie_id', 'rating'], engine='python')

    return ratings


def sparse_matrices(df):
    """Creates the sparse user-item and item-user matrices.

    Args:
        df (pd.DataFrame): Table with MovieLens 1m dataset, users * movies = ratings

    Returns:

        sparse_user_item (scipy.sparse.csr_matrix): sparse user * item matrix
        sparse_item_user (scipy.sparse.csr_matrix): sparse item * user matrix

    """
    # using a scalar value (40) to convert ratings from a scale (1-5) to a like/click/view (1)
    alpha = 40

    sparse_user_item = csr_matrix(([alpha] * len(df['movie_id']), (df['user_id'], df['movie_id'])))

    # transposing the item-user matrix to create a user-item matrix
    sparse_item_user = sparse_user_item.T.tocsr()
    # save the matrices for recalculating user on the fly
    save_npz('files/sparse_user_item.npz', sparse_user_item)
    save_npz('files/sparse_item_user.npz', sparse_item_user)

    return sparse_user_item, sparse_item_user


def production_model(sparse_user_item_file_path='files/sparse_user_item.npz'):
    """Fits model and saves it.

    Args:
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix
    """
    sparse_user_item = load_npz(sparse_user_item_file_path)

    model = implicit.als.AlternatingLeastSquares(factors=100,
                                                 regularization=0.1, iterations=100, calculate_training_loss=False)
    model.fit(sparse_user_item)

    with open('files/production_model.sav', 'wb') as pickle_out:
        pickle.dump(model, pickle_out)


def model(sparse_user_item_file_path='files/sparse_user_item.npz'):
    """Computes p@k and map@k evaluation mettrics and saves model.

    Args:
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix

    Returns:
        p_at_k (float): precision @ k recommendations, with k=10
        m_at_k (float): mean average precision @ k recommendations, with k=10
    """
    sparse_user_item = load_npz(sparse_user_item_file_path)

    train, test = train_test_split(sparse_user_item, train_percentage=0.8)

    model = implicit.als.AlternatingLeastSquares(factors=100,
                                                 regularization=0.1, iterations=100, calculate_training_loss=False)
    model.fit(train)

    with open('files/model.sav', 'wb') as pickle_out:
        pickle.dump(model, pickle_out)

    p_at_k = precision_at_k(model, train_user_items=train,
                            test_user_items=test, K=10)
    map_at_k = mean_average_precision_at_k(model, train, test, K=10)

    return p_at_k, map_at_k


def most_similar_items(item_id, model_file_path='files/model.sav', n_similar=10):
    """Computes the most similar items.

    Args:
        item_id (int): identifier for movie item
        model_file_path (str): file path for the ALS model
        n_similar (int): number of similar neighbours to return

    Returns:
        map_movies(similar) ([dic()]): similar movies with ID, title, genre and year
    """
    with open(model_file_path, 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    similar, _ = model.similar_items(item_id, n_similar)
    similar = similar[1:] # the first most similar movie == item_id

    return map_movies(similar)


def most_similar_users(user_id, sparse_user_item_file_path='files/sparse_user_item.npz', model_file_path='files/model.sav', n_similar=10):
    """computes the most similar users.

    Args:
        user_id (int): identifier for user
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix
        model_file_path (str): file path for the ALS model
        n_similar (int): number of similar neighbours to return

    Returns:
        similar_users_info [dict()]: user information for each similar user to user_id with ID, gender, agerange, occupation

    """
    sparse_user_item = load_npz(sparse_user_item_file_path)

    with open(model_file_path, 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    # similar users gives back [(users, scores)]
    # we want just the users and not the first one, because that is the same as the original user
    similar, _ = model.similar_users(user_id, n_similar)
    similar = similar[1:] # the first most similar user == user_id

    # orginal users items
    original_user_items = list(sparse_user_item[user_id].indices)

    # # this maps back user_ids to their information, which is useful for visualisation
    similar_users_info = map_users(similar)
    # # now we want to add the items that a similar used has rated
    for user_info in similar_users_info:
        # we create a list of items that correspond to the simillar user ids
        # then compare that in a set operation to the original user items
        # as a last step we add it as a key to the user information dictionary
        user_info['items'] = set(list(sparse_user_item[user_info['user_id']].indices)) & set(original_user_items)

    return similar_users_info


def recommend(user_id, model_file_path='files/model.sav', sparse_user_item_file_path='files/sparse_user_item.npz'):
    """recommend N items to user.

    Args:
        user_id (int): user identifier to recommend items for
        model_file_path (str): file path for the ALS model
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix

    Returns:
        recommended ([int]): the recommended movie IDs
        map_movies(recommended) ([dic()]): recommended movies with ID, title, genre and year
    """
    sparse_user_item = load_npz(sparse_user_item_file_path)

    with open(model_file_path, 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    recommended, _ = model.recommend(user_id, sparse_user_item[user_id])

    return recommended, map_movies(recommended)


def recommend_all_users(model_file_path='files/model.sav', sparse_user_item_file_path='files/sparse_user_item.npz'):
    """Recommend N items to all users.

    Args:
        model_file_path (str): file path for the ALS model
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix

    Returns:
        df (pd.DataFrame): matrix with user_id * N recommendations
    """
    sparse_user_item = load_npz(sparse_user_item_file_path)

    with open(model_file_path, 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    # numpy array with N recommendations for each user
    # remove first array, because those are the columns
    all_recommended = model.recommend_all(user_items=sparse_user_item, N=10,
                                          recalculate_user=False, filter_already_liked_items=True)[1:]

    # create a new Pandas Dataframe with user_id, 10 recommendations, for all users
    df = pd.read_csv('files/ml-1m/users.dat', delimiter='::', header=None,
                     names=['user_id', 'gender', 'agerange', 'occupation', 'timestamp'], engine='python')
    df = df.drop(['gender', 'agerange', 'occupation', 'timestamp'], axis=1)
    df[['rec1', 'rec2', 'rec3', 'rec4', 'rec5', 'rec6', 'rec7', 'rec8', 'rec9', 'rec10']] = pd.DataFrame(
        all_recommended)
    df.to_pickle('all_recommended.pkl')

    # melt dataframe into SQL format for Django model
    melted = df.melt(id_vars=['user_id'], var_name='order', value_name='recommendations',
        value_vars=['rec1', 'rec2', 'rec3', 'rec4', 'rec5', 'rec6', 'rec7', 'rec8', 'rec9', 'rec10'])
    melted['order'] = melted.order.str[3:]
    melted.to_pickle('all_recommended_melted.pkl')

    return df


def map_movies(movie_ids, movielens_file_path='files/ml-1m/movies.dat'):
    """Takes a list of movie_ids and returns a list of dictionaries with movies information.

    Args:
        movie_ids ([int]): a list of identifiers for movies
        movielens_file_path (str): file location for the MovieLens 1m dataset

    Returns:
        mapped_movies ([dic]): movies dictionary with ID, title, genre and year
    """
    df = pd.read_csv(movielens_file_path, delimiter='::', header=None, encoding='iso-8859-1',
                     names=['movie_id', 'title', 'genre'], engine='python')

    # add years to a new column 'year' and remove them from the movie title
    df['year'] = df['title'].str[-5:-1]
    df['title'] = df['title'].str[:-6]

    # creates an ordered list of dictionaries with the movie information for all movie_ids
    mapped_movies = [df[df['movie_id'] == i].to_dict('records')[0] for i in movie_ids]

    return mapped_movies


def map_users(user_ids, movielens_file_path='files/ml-1m/users.dat'):
    """Takes a list of user_ids and returns a list of dictionaries with user information.

    Args:
        user_ids ([int]): a list of identifiers for users
        movielens_file_path (str): file location for the MovieLens 1m dataset

    Returns:
        mapped_users ([dic]): movies dictionary with ID, gender, agerange and occupation
    """
    df = pd.read_csv(movielens_file_path, delimiter='::', header=None,
                     names=['user_id', 'gender', 'agerange', 'occupation', 'timestamp'], engine='python')
    df = df.drop(['timestamp'], axis=1)

    mapped_users = [df[df['user_id'] == i].to_dict('records')[0] for i in user_ids]

    return mapped_users


def visualize_movies():
    """Adds poster image links and imdb url to movies data based on Movielens 100k dataset."""
    urls = pd.read_csv('posters/movie_url.csv', delimiter=',',
                       header=None, names=['movie_id', 'url'], engine='python')
    posters = pd.read_csv('posters/movie_poster.csv', delimiter=',',
                          header=None, names=['movie_id', 'poster'], engine='python')
    movies = pd.read_csv('files/ml-1m/movies.dat', delimiter='::', header=None, encoding='iso-8859-1',
                         names=['movie_id', 'title', 'genre'], engine='python')

    visuals = pd.merge(urls, posters, on='movie_id', how='left')

    # merge url, posters and movies 1m dataset on their ids
    df = pd.merge(movies, visuals, on='movie_id', how='left')
    df['year'] = df['title'].str[-5:-1]
    df['title'] = df['title'].str[:-6]

    # import ratings document
    ratings = pd.read_csv('files/ml-1m/ratings.dat', delimiter='::', header=None,
                          names=['user_id', 'movie_id', 'rating', 'timestamp'],
                          usecols=['user_id', 'movie_id', 'rating'], engine='python')
    # add rating count to movies dataframe
    counts = pd.DataFrame(ratings['movie_id'].value_counts())
    counts.columns = ['counts']

    merged = pd.merge(df, counts, left_on='movie_id', right_index=True)
    merged.to_pickle('movies.pkl')

    return df


def recalculate_user(user_ratings, model_file_path='files/model.sav', sparse_user_item_file_path='files/sparse_user_item.npz'):
    """Adds new user and its liked items to sparse matrix and returns recalculated recommendations.

    Args:
        user_ratings ([int]): movie ratings for new user
        model_file_path (str): file path for the ALS model
        sparse_user_item_file_path (str): file location for a scipy.sparse.csr_matrix sparse user * item matrix

    Returns:
        recommended ([int]): the recommended movie IDs
        map_movies(recommended) ([dic()]): recommended movies with ID, title, genre and year
    """
    alpha = 40
    m = load_npz(sparse_user_item_file_path)
    n_users, n_movies = m.shape

    ratings = [alpha for i in range(len(user_ratings))]

    m.data = np.hstack((m.data, ratings))
    m.indices = np.hstack((m.indices, user_ratings))
    m.indptr = np.hstack((m.indptr, len(m.data)))
    m._shape = (n_users + 1, n_movies)

    with open(model_file_path, 'rb') as pickle_in:
        model = pickle.load(pickle_in)

    recommended, _ = model.recommend(n_users, m[n_users], recalculate_user=True)

    return recommended, map_movies(recommended)


if __name__ == '__main__':

    p_at_k, map_at_k = model()
    print(f'P@K: {p_at_k}, MAP@K: {map_at_k}\n')

    user_id = 2
    recommended, mapped_movies = recommend(user_id)
    print(f'Recommended movies for user {user_id}: {recommended}\n {mapped_movies}\n')

    movie_list = [2031, 999, 2731]
    recommended, mapped_movies = recalculate_user(movie_list)
    print(f'Recommended movies for user with these liked movies {movie_list}: {recommended}\n {mapped_movies}\n')
