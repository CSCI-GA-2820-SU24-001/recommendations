"""
TestRecommendation API Service Test Suite
"""

import os
import logging
from unittest import TestCase


from wsgi import app
from service.common import status
from service.models import db, Recommendation
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


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
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            b"This is the home page",
            response.data,
        )

    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        recommendation = RecommendationFactory()
        response = self.client.post(
            "/recommendations",
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
        response = self.client.get("/recommendations")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], recommendation.name)

    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        response = self.client.delete(f"/recommendations/{recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Recommendation.find(recommendation.id))


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
        response = self.client.put("/recommendations")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post("/recommendations", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post("/recommendations")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(
            "/recommendations", data="hello", content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_bad_product_id(self):
        """It should not Create a Recommendation with bad product_id data"""
        test_recommendation = RecommendationFactory()
        # change product_id to a string
        test_recommendation.product_id = "bad_id"
        response = self.client.post(
            "/recommendations", json=test_recommendation.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_missing_recommendation_type(self):
        """It should not Create a Recommendation with missing recommendation_type"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        del data["recommendation_type"]
        response = self.client.post("/recommendations", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_404_not_found(self):
        """It should return 404 for non-existent endpoints"""
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
