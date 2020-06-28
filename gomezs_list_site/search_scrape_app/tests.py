from django.test import TestCase
import search_scrape_app.webScraper as webScraper
# Create your tests here.

class WebscrapTestCase(TestCase):

    def test_american_locations(self):
        self.assertEqual(webScraper.getNearestCitySubdomain("oakland pittsburgh"), 
        "https://pittsburgh.craigslist.org/")

        self.assertEqual(webScraper.getNearestCitySubdomain("montepelier va"),
        "https://richmond.craigslist.org/")

        self.assertIsNotNone(webScraper.getNearestCitySubdomain("vermont"))
        
        self.assertEqual(webScraper.getNearestCitySubdomain("museum of sex"),
        "https://newyork.craigslist.org/")

    def test_canadian_locations(self):
        try:
            self.assertEqual(webScraper.getNearestCitySubdomain("Elliot Lake ON"),
            "https://sudbury.craigslist.org/")
        except:
            self.assertEqual(webScraper.getNearestCitySubdomain("Elliot Lake ON"),
            "https://soo.craigslist.org/")