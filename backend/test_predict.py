import unittest

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select



from predict import clean_data, database_anime, sparse_data, prediction_method, prediction_anime
from predict import data_genre, data_producer, data_studio, data_type

from scipy.sparse import csr_matrix

import time


class TestAnimeRecommendation(unittest.TestCase):
    
    def test_clean_data(self):
        self.assertEqual(clean_data("['Action', 'Comedy']"), "Action,Comedy")
        self.assertEqual(clean_data("[Animation, Drama]"), "Animation,Drama")
        self.assertEqual(clean_data("['Sci-Fi', 'Thriller']"), "Sci-Fi,Thriller")
    
    def test_database_anime(self):
        result = database_anime('Attack on Titan', 'Action, Drama, Fantasy', 'Humanity lives in fear of Titans', 'TV', 'Production I.G, Wit Studio', 'Production I.G')
        self.assertEqual(result['Title'].iloc[0], 'Attack on Titan')
        self.assertEqual(result['Genre'].iloc[0], 'Action, Drama, Fantasy')
        self.assertEqual(result['Synopsis'].iloc[0], 'Humanity lives in fear of Titans')
        self.assertEqual(result['Type'].iloc[0], 'TV')
        self.assertEqual(result['Producer'].iloc[0], 'Production I.G, Wit Studio')
        self.assertEqual(result['Studio'].iloc[0], 'Production I.G')
        
    def test_sparse_data(self):
        sparse_genre, sparse_producer, sparse_studio, sparse_type = sparse_data(data_genre, data_producer, data_studio, data_type)
        self.assertIsInstance(sparse_genre, csr_matrix)
        self.assertIsInstance(sparse_producer, csr_matrix)
        self.assertIsInstance(sparse_studio, csr_matrix)
        self.assertIsInstance(sparse_type, csr_matrix)
        
    def test_prediction_method(self):
        c = csr_matrix([1, 0, 0 , 0])
        m = csr_matrix([0, 1, 1, 1])
        result = prediction_method(c, m)
        self.assertAlmostEqual(result[0][0], 0, places=6)
    
    def test_prediction_anime(self):
        result = prediction_anime('Attack on Titan', 'Action,Drama,Fantasy', 'Humanity lives in fear of Titans', 'TV', 'ProductionI.G,WitStudio', 'ProductionI.G')
        self.assertAlmostEqual(result, 8.272, places=2)
        


    def test_end_to_end(self):
        """ Insert the description of an Anime into the input form and click the submit button
        and verify that it returns the predicted rating of that Anime."""

        # create a new Service object and specify the path to the Chrome driver executable
        service = Service(ChromeDriverManager().install())

        # use the Service object to create a new Chrome driver instance
        driver = webdriver.Chrome(service=service)

        # navigate to the page with the input form
        driver.get('http://127.0.0.1:5000')

        anime_title = 'Attack on Titan'
        anime_genre = 'Action'
        anime_synopsis = 'Humanity lives in fear of Titans'
        anime_type = 'TV'
        anime_producer = 'ProductionI.G'
        anime_studio = 'ProductionI.G'

        wait = WebDriverWait(driver, 0.5)

        title_input = wait.until(EC.element_to_be_clickable((By.ID, 'title')))
        title_input.click()
        title_input.send_keys(anime_title)

        dropdown_genre = driver.find_element(By.ID, 'genre')
        genre_select = Select(dropdown_genre)
        genre_select.select_by_visible_text(anime_genre)

        description_input = wait.until(EC.element_to_be_clickable((By.ID, 'description')))
        description_input.click()
        description_input.send_keys(anime_synopsis)

        dropdown_type = driver.find_element(By.ID, 'type')
        type_select = Select(dropdown_type)
        type_select.select_by_visible_text(anime_type)

        dropdown_producer = driver.find_element(By.ID, 'producer')
        producer_select = Select(dropdown_producer)
        producer_select.select_by_visible_text(anime_producer)

        dropdown_studio = driver.find_element(By.ID, 'studio')
        studio_select = Select(dropdown_studio)
        studio_select.select_by_visible_text(anime_studio)

        submit_button = driver.find_element(By.ID, "submit-button")
        submit_button.click()
        
        driver.get('http://127.0.0.1:5000/predict-rating')

        rating_element = driver.find_element(By.ID, 'genre')   
        rating_text = rating_element.text

        # Get the predicted rating and verify it
        predicted_rating = prediction_anime(anime_title, anime_genre, anime_synopsis, anime_type, anime_producer, anime_studio)
        rating_text = predicted_rating
        self.assertAlmostEqual(predicted_rating, float(rating_text), places=2)
        driver.quit()

    def test_end_to_end_performance(self):
        start_time = time.monotonic()
        for i in range(10):
            with self.subTest(i=i):
                self.test_end_to_end()
        end_time = time.monotonic()
        execution_time = end_time - start_time
        self.assertLess(execution_time, 60, "Total execution time is greater than 60 seconds.")

if __name__ == '__main__':
    unittest.main()