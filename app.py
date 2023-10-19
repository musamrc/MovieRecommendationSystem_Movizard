# This file is responsible for creating the Flask application and handling the routing.
from flask import Flask, render_template, request
from movie_recommender import MovieRecommender

# Creating the Flask app instance.
app = Flask(__name__)
# Creating an instance of the MovieRecommender class.
movie_recommender = MovieRecommender()

# Defining the route for the home page, which accepts both GET and POST requests.
@app.route('/', methods=['GET', 'POST'])
def movie_recommendation():
    # If the request method is POST, it means that the user has submitted the form.
    if request.method == 'POST':
        # Retrieving the user's preferences from the form.
        movie_recommender.get_preferences(request.form)
        # Getting the movie recommendations based on the user's preferences.
        recommendations = movie_recommender.recommend_movies()

        # If there are no recommendations, return a message to the user.
        if not recommendations:
            return "No movies found with the given preferences. Please try again with different preferences."
        else:
            # If there are recommendations, render the 'results.html' template with the recommendations.
            return render_template('results.html', movies=recommendations)
    else:
        # If the request method is GET, render the form for the user to fill out.
        return render_template('form.html')
