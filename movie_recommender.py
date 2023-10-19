# This code is used to build a movie recommendation system.
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

class MovieRecommender:
    # Initializing the class with the movie data loaded from a JSON file.
    def __init__(self):
        # Reading the JSON file into a DataFrame.
        self.df = pd.read_json('movies.json')
        # Creating a combined feature from genres, cast, keywords, vote_count and vote_average.
        self.df['combined_features'] = self.df['genres']*3 + self.df['cast']*2 + self.df['keywords'].apply(lambda x: x.split()) + self.df['vote_count'].apply(lambda x: [str(x)]) + self.df['vote_average'].apply(lambda x: [str(x)])
        # Joining the features together into a single string.
        self.df['combined_features'] = self.df['combined_features'].apply(lambda x: ' '.join(x))
        # Initializing an empty dictionary to store user preferences.
        self.preferences = {}

    # This function finds the closest string to the user's input in the 'title' column. This is used because there is only one title for each movie.
    def find_closest_string_movie(self, user_input):
        closest_string = None
        similarity_score = 0
        for string in self.df['title']:
            current_score = fuzz.token_set_ratio(user_input, string.lower())
            if current_score > similarity_score:
                closest_string = string
                similarity_score = current_score
        return closest_string

    # This function finds the closest string to the user's input in the 'genres' and 'cast' columns. String lists are used because there are multiple genres and actors for each movie.
    def find_closest_string_genre_actor(self, user_input, column_name):
        closest_string = None
        similarity_score = 0
        for string_list in self.df[column_name]:
            for string in string_list:
                current_score = fuzz.token_set_ratio(user_input, string.lower())
                if current_score > similarity_score:
                    closest_string = string
                    similarity_score = current_score
        return closest_string


    # This function collects the user's preferences from a given form.
    def get_preferences(self, form):
        # Checking if the user has a preferred movie and storing it.
        self.preferences['has_preferred_movie'] = form['has_preferred_movie'] == 'Yes'
        # Storing the user's preferred movie, genre, actor, and year.
        closest_movie = self.find_closest_string_movie(form['movie']) if self.preferences['has_preferred_movie'] else None
        closest_genre = self.find_closest_string_genre_actor(form['genre'], 'genres')
        closest_actor = self.find_closest_string_genre_actor(form['actor'], 'cast')

        self.preferences['movie'] = closest_movie
        self.preferences['genre'] = closest_genre
        self.preferences['actor'] = closest_actor
        self.preferences['year'] = form['year']

        if closest_movie is not None and form['movie'] == closest_movie:
            print("Girilen film adı bulundu: ", closest_movie)
        if closest_movie is not None and form['movie'] != closest_movie:
            print("Girilen film adı bulunamadı. En yakın eşleşme: ", closest_movie)

        if form['genre'] == closest_genre:
            print("Girilen tür bulundu: ", closest_genre)
        if form['genre'] != closest_genre:
            print("Girilen tür bulunamadı. En yakın eşleşme: ", closest_genre)

        if form['actor'] == closest_actor:
            print("Girilen aktör bulundu: ", closest_actor)
        if form['actor'] != closest_actor:
            print("Girilen aktör bulunamadı. En yakın eşleşme: ", closest_actor)


    # This function uses the user's preferences to recommend movies.
    def recommend_movies(self):
        # Resetting the DataFrame's index.
        self.df.reset_index(inplace=True, drop=True)

        # Check if user selected 'Yes' for having a preferred movie but did not specify which movie
        if self.preferences['has_preferred_movie'] and not self.preferences['movie']:
            return ["Since you answered 'Yes I do!' to the question 'Do you have a favorite movie in mind?', you should specify your favorite movie or select 'Not really' for the question."]

        # Check if user didn't provide any preference at all
        if not any([self.preferences['has_preferred_movie'], self.preferences['genre'], self.preferences['actor'], self.preferences['year']]):
            return ["You haven't made any selections. Please answer at least one question."]

        # If the user specified a preferred movie:
        if self.preferences['has_preferred_movie']:
            # If the preferred movie isn't in the dataset, return an empty list.
            if self.preferences['movie'] not in self.df['title'].values:
                return []
            else:
                # Creating a CountVectorizer object.
                cv = CountVectorizer()
                # Generating the count matrix from the combined features.
                count_matrix = cv.fit_transform(self.df['combined_features'])
                # Computing the cosine similarity matrix.
                cosine_sim = cosine_similarity(count_matrix)
                # Getting the index of the user's preferred movie.
                movie_index = self.df[self.df.title == self.preferences['movie']].index[0]
                # Getting a list of similar movies by cosine similarity.
                similar_movies = list(enumerate(cosine_sim[movie_index]))
                # Sorting the movies by similarity.
                sorted_similar_movies = sorted(similar_movies, key=lambda x:x[1], reverse=True)

                # Creating a filtered DataFrame that doesn't include the preferred movie.
                filtered_df = self.df.copy()
                filtered_df = filtered_df.loc[[index for index, similarity in sorted_similar_movies if index != movie_index]]

                # Applying additional filters based on the user's preferences.
                if self.preferences['year']:
                    year = int(self.preferences['year'])
                    filtered_df = filtered_df[filtered_df['year'] > year]
                filtered_df = filtered_df[
                    (filtered_df['genres'].apply(lambda x: self.preferences['genre'] in x if self.preferences['genre'] else True)) & 
                    (filtered_df['cast'].apply(lambda x: self.preferences['actor'] in x if self.preferences['actor'] else True))
                ]

                # If there are no movies that match the user's preferences, return an empty list.
                if filtered_df.empty:
                    return []
                
                # Return the top 5 movies.
                return [{'title': movie, 'thumbnail': self.df[self.df['title'] == movie]['thumbnail'].values[0]} for movie in filtered_df['title'].tolist()[:5]]
        else:
            # If the user didn't specify a preferred movie, filter the movies based on the other preferences.
            filtered_df = self.df.copy()

            if self.preferences['year']:
                year = int(self.preferences['year'])
                filtered_df = filtered_df[filtered_df['year'] > year]

            filtered_df = filtered_df[
                (filtered_df['genres'].apply(lambda x: self.preferences['genre'] in x if self.preferences['genre'] else True)) & 
                (filtered_df['cast'].apply(lambda x: self.preferences['actor'] in x if self.preferences['actor'] else True))
            ]

            # If there are no movies that match the user's preferences, return an empty list.
            if filtered_df.empty:
                return []
            
            # Sort by vote_count and vote_average
            filtered_df = filtered_df.sort_values(by=['vote_count', 'vote_average'], ascending=False)
            
            # Return the top 5 movies.
            return [{'title': movie, 'thumbnail': self.df[self.df['title'] == movie]['thumbnail'].values[0]} for movie in filtered_df['title'].tolist()[:5]]
