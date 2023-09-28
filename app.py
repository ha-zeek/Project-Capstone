from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

load_dotenv()


@app.route('/')
def index():
    return render_template("home.html")  # Landing on homepage


# Function for getting movie details through OMDB api.
@app.route("/movie", methods=["GET", "POST"])
def movie():
    user_input = None
    error_message = None
    movie_data = None  # as default, these variables will be None

    if request.method == 'POST':
        user_input = request.form.get('user_input')  # defining user_input

        if user_input is None or user_input == "":
            error_message = "<h1>Please type a movie!</h1>"
            # If user submit an empty input, it will return an error_message.
            return error_message
        else:  # if user input submit with a movie name >>
            try:
                title = user_input  # user input would be the title
                # every api has an apikey, api key is needed to access the data.
                key = os.getenv("OMDB_KEY")
                req = requests.get(
                    f"http://www.omdbapi.com/?t={title}&apikey={key}")  # HTTP request to OMDB api with the title & api key.
                req.raise_for_status()  # Check for HTTP request errors
                # data from the request is clean to through JSON and assigned as movie_data.
                movie_data = req.json()

                # check if movie data response from HTTP is in the API, if false, it will return an error.
                if movie_data.get("Response", '').lower() == "false":
                    return "<h1>Movie not found.</h1>"
            # handling any error in the request, if there is any it will return the error message.
            except requests.exceptions.RequestException as e:
                # Handle request-related errors here
                error_message = f"Error: {str(e)}"
                return error_message

        # rendering movie.html page. while passing data through it.
        return render_template("movie.html", movie_data=movie_data, user_input=user_input, error_message=error_message)


# Function for getting streaming availibility of the movie via stream API.
@app.route("/streaming", methods=["GET", "POST"])
def streaming():

    if request.method == 'POST':
        user_input = request.form.get('user_input')

        ra_key = os.getenv("RAPID_API_Key")

        url_stream = "https://streaming-availability.p.rapidapi.com/search/title"
        querystring = {f"title": {user_input}, "country": "us",
                       "show_type": "all", "output_language": "en"}
        headers = {
            "X-RapidAPI-Key": ra_keys,
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }  # these code block is from the API website, a suggestion on how to call the website.

        try:
            response = requests.get(
                url_stream, headers=headers, params=querystring)  # with the querystring as parameters, we can call the exact movie api.
            response.raise_for_status()  # Check for HTTP request errors
            # data from the request is clean to through JSON and assigned as movie_data.
            data = response.json()
            # cleaning the big JSON file, from dictionary to list.
            streaming_data = list(data['result'][0]['streamingInfo']['us'])
            if len(streaming_data) > 3:  # if there more than 3 sources of stream. it will only show top 3
                streaming_data = streaming_data[:3]

        except requests.exceptions.RequestException as e:
            # Handle request-related errors here
            error_message = f"Error: {str(e)}"
            return error_message

    # render streaming.html while passing through data to use in HTML.
    return render_template("streaming.html", streaming_data=streaming_data, user_input=user_input)


if __name__ == '__main__':
    app.run(debug=True)
