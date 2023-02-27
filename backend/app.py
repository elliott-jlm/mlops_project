import psutil
from flask import Flask, render_template, request, send_file
import time
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CollectorRegistry, start_http_server
from predict import prediction_anime

app = Flask(__name__)

# Define the Prometheus metrics
anime_rating_predictions = Counter('anime_rating_predictions', 'Number of anime rating predictions')
cpu_usage = Gauge('cpu_usage', 'Current CPU usage')
response_time = Histogram('response_time_seconds', 'Response time in seconds', buckets=[0.1, 0.5, 1, 5, 10])
request_count = Counter('request_count', 'Number of requests processed')
exception_count = Counter('exception_count', 'Number of exceptions occurred')

# Create a CollectorRegistry and register the Prometheus metrics with the registry
registry = CollectorRegistry()
registry.register(anime_rating_predictions)
registry.register(cpu_usage)
registry.register(response_time)
registry.register(request_count)
registry.register(exception_count)

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

    # Increment the request count metric
    request_count.inc()

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

        # Record the start time of the prediction
        start_time = time.time()

        # Predict the rating
        rating = prediction_anime(title, genre, description, anime_type, producer, studio)

        # Record the end time of the prediction
        end_time = time.time()

        # Calculate the response time in seconds and record it in the response time histogram
        response_time.observe(end_time - start_time)

        # Increment the anime rating predictions metric
        anime_rating_predictions.inc()

        # Render the result template
        return render_template('result.html', title=title, genre=genre, description=description, type=anime_type, producer=producer, studio=studio, rating=rating)
    else:
        return render_template('page.html')

@app.route('/metrics')
def metrics():
    # Increment the request count metric
    request_count.inc()

    # Record the current CPU usage in the CPU usage gauge
    cpu_usage.set(psutil.cpu_percent())

    # Generate the latest metrics in the text-based exposition format
    data = generate_latest(registry)

    # Return the metrics in the text-based exposition format
    return data.decode('utf-8')

start_http_server(5000)
if __name__ == '__main__':
    app.run(debug=True)
