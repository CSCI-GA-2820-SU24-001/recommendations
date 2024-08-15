# pylint: disable=C0411
"""
TestRecommendation API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service import routes
from service.common import status
from service.models import db, Recommendation
from .factories import RecommendationFactory
from urllib.parse import quote_plus

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/api/recommendations"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        # api_key = routes.generate_apikey()
        # app.config["API_KEY"] = api_key
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    def setUp(self):
        """Runs before each test"""
        self.app = app.test_client()
        # self.headers = {"X-Api-Key": app.config["API_KEY"]}
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def tearDown(self):
        """Clear the database"""
        resp = self.app.delete(BASE_URL, headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should serve the index.html file"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Recommendation Demo RESTful Service", response.data)
        self.assertIn(
            b"Create, Retrieve, Update, and Delete a Recommendation", response.data
        )

        # Check for the footer content
        self.assertIn(b"&copy; NYU DevOps Company 2023", response.data)

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        recommendation = RecommendationFactory()
        response = self.client.post(
            BASE_URL,
            json=recommendation.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json["name"], recommendation.name)
        self.assertEqual(response.json["product_id"], recommendation.product_id)
        self.assertEqual(
            response.json["recommended_product_id"],
            recommendation.recommended_product_id,
        )
        self.assertEqual(
            response.json["recommendation_type"], recommendation.recommendation_type
        )

    def test_list_recommendations(self):
        """It should List all Recommendations"""
        recommendation = RecommendationFactory()
        recommendation.create()
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], recommendation.name)

    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        response = self.client.delete(f"{BASE_URL}/{recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Recommendation.find(recommendation.id))

    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            recommendation = RecommendationFactory()
            recommendation.create()
            recommendations.append(recommendation)
        return recommendations

    def test_query_by_recommended_product_id(self):
        """It should Query Recommendations by recommended_product_id"""
        recommendations = self._create_recommendations(1)
        test_recommended_product_id = recommendations[0].recommended_product_id
        recommended_product_id_count = len(
            [
                recommendation
                for recommendation in recommendations
                if recommendation.recommended_product_id == test_recommended_product_id
            ]
        )
        response = self.client.get(
            BASE_URL,
            query_string=f"recommended_product_id={quote_plus(str(test_recommended_product_id))}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), recommended_product_id_count)
        for recommendation in data:
            self.assertEqual(
                recommendation["recommended_product_id"], test_recommended_product_id
            )

    def test_invalid_query_parameters(self):
        """It should return error for invalid query parameters"""
        response = self.client.get(BASE_URL, query_string="invalid_param=value")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid query parameter")


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a recommendation id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_bad_product_id(self):
        """It should not Create a Recommendation with bad product_id data"""
        test_recommendation = RecommendationFactory()
        # change product_id to a string
        test_recommendation.product_id = "bad_id"
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_missing_recommendation_type(self):
        """It should not Create a Recommendation with missing recommendation_type"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        del data["recommendation_type"]
        response = self.client.post(BASE_URL, json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_404_not_found(self):
        """It should return 404 for non-existent endpoints"""
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
