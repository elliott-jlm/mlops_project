from flask import Flask, render_template, request, send_file
import joblib
import os
import pandas as pd

from predict import prediction_anime

app = Flask(__name__)

# Construct the absolute path to the static directory
static_dir = '../frontend/static'
app.static_folder = static_dir

# Construct the absolute path to the templates directory
template_dir = '../frontend/templates'
app.template_folder = template_dir


@app.route('/')
def index():
    return send_file(template_dir+'/page.html')

@app.route('/predict-rating', methods=['GET', 'POST'])
def predict_rating():

    if request.method == 'POST':
        # Get the form data
        title = request.form['title']
        genre = request.form.getlist('genre')
        description = request.form['description']
        anime_type = request.form['type']
        producer = request.form['producer']
        studio = request.form.getlist('studio')
        
        # preprocess 
        genre, producer, studio = ','.join(genre), ','.join(producer), ','.join(studio)

        rating = prediction_anime(title, genre, description, anime_type, producer, studio)

        # Render the result template
        return render_template('result.html', title=title, genre=genre, description=description, type=anime_type, producer=producer, studio=studio, rating=rating)
    else:
        return render_template('page.html')

if __name__ == '__main__':
    app.run(debug=True)