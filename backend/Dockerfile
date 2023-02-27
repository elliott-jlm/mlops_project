FROM python:3.9

# Copy the necessary files to the container
COPY app.py requirements.txt anime_data.csv data_genre.csv data_producer.csv data_studio.csv data_type.csv predict.py embeddings.npy  /app/
COPY . /app/backend

# Set the working directory to the parent of the backend folder
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port that the app is running on
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]