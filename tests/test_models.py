# pylint: disable=R0801
"""
Test cases for Pet Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from wsgi import app
from service.models import Recommendation, DataValidationError, db
from .factories import RecommendationFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendation(TestCase):
    """Test Cases for Recommendation Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_create_recommendation(self):
        """It should Create a Recommendation and assert that it exists"""
        recommendation = Recommendation(
            name="t-shirt",
            product_id=101,
            recommended_product_id=202,
            recommendation_type="cross-sell",
        )
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.name, "t-shirt")
        self.assertEqual(recommendation.product_id, 101)
        self.assertEqual(recommendation.recommended_product_id, 202)
        self.assertEqual(recommendation.recommendation_type, "cross-sell")

    def test_add_recommendation(self):
        """It should Create a Recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(
            name="shoes",
            product_id=123,
            recommended_product_id=456,
            recommendation_type="up-sell",
        )
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].name, "shoes")
        self.assertEqual(recommendations[0].product_id, 123)
        self.assertEqual(recommendations[0].recommended_product_id, 456)
        self.assertEqual(recommendations[0].recommendation_type, "up-sell")

    def test_read_recommendation(self):
        """It should Read a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        found_recommendation = Recommendation.find(recommendation.id)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(found_recommendation.name, recommendation.name)
        self.assertEqual(found_recommendation.product_id, recommendation.product_id)
        self.assertEqual(
            found_recommendation.recommended_product_id,
            recommendation.recommended_product_id,
        )

    def test_update_recommendation(self):
        """It should update a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        recommendation.name = "Updated Recommendation"
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.name, "Updated Recommendation")
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].name, "Updated Recommendation")

    def test_update_no_id(self):
        """It should not Update Recommendation with no id"""
        recommendation = RecommendationFactory()
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_list_all_recommendations(self):
        """It should List all Recommendations"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 5)

    def test_serialize_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertIsNotNone(data)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], recommendation.name)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], recommendation.product_id)
        self.assertIn("recommended_product_id", data)
        self.assertEqual(
            data["recommended_product_id"], recommendation.recommended_product_id
        )
        self.assertIn("recommendation_type", data)
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type
        )

        def test_find_by_attribute(self):
            """It should find Recommendations by product_id, recommended_product_id, and recommendation_type"""
            recommendation1 = Recommendation(
                name="t-shirt",
                product_id=101,
                recommended_product_id=404,
                recommendation_type="cross-sell",
            )
            recommendation1.create()

            recommendation2 = Recommendation(
                name="shoes",
                product_id=202,
                recommended_product_id=404,
                recommendation_type="up-sell",
            )
            recommendation2.create()

            recommendation3 = Recommendation(
                name="hat",
                product_id=303,
                recommended_product_id=505,
                recommendation_type="cross-sell",
            )
            recommendation3.create()

            # Test with all attributes
            results = Recommendation.find_by_attribute(101, 202, "cross-sell")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "t-shirt")

            # Test with only product_id
            results = Recommendation.find_by_attribute(None, 404, None)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].name, "t-shirt")
            self.assertEqual(results[1].name, "shoes")

            # Test with only recommended_product_id
            results = Recommendation.find_by_attribute(None, None, "cross-sell")
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].name, "t-shirt")
            self.assertEqual(results[1].name, "hat")

            # Test with only recommendation_type
            results = Recommendation.find_by_attribute(None, None, "cross-sell")
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].name, "t-shirt")
            self.assertEqual(results[1].name, "hat")

            # Test with no matching attributes
            results = Recommendation.find_by_attribute(999, 999, "unknown")
            self.assertEqual(len(results), 0)

    def test_deserialize_recommendation(self):
        """It should de-serialize a recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertIsNotNone(recommendation)
        self.assertIsNone(recommendation.id)
        self.assertEqual(recommendation.name, data["name"])
        self.assertEqual(recommendation.product_id, data["product_id"])
        self.assertEqual(
            recommendation.recommended_product_id, data["recommended_product_id"]
        )
        self.assertEqual(
            recommendation.recommendation_type, data["recommendation_type"]
        )

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"name": "Sample Recommendation"}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    ######################################################################
    #  T E S T   E X C E P T I O N   H A N D L E R S
    ######################################################################
    def test_create_with_database_error(self):
        """It should handle database errors during creation"""
        with patch(
            "service.models.db.session.add", side_effect=Exception("Mocked exception")
        ):
            recommendation = RecommendationFactory()
            with self.assertRaises(DataValidationError):
                recommendation.create()

    # def test_delete_recommendation_with_database_error(self):
    #     """It should handle database errors during deletion"""
    #     recommendation = RecommendationFactory()
    #     recommendation.create()
    #     with patch(
    #         "service.models.db.session.delete",
    #         side_effect=Exception("Mocked exception"),
    #     ):
    #         with self.assertRaises(DataValidationError):
    #             recommendation.delete()
    #         self.assertTrue(
    #             db.session.rollback.called, "Database rollback should be called"
    #         )

    def test_handle_database_errors_during_deletion(self):
        """It should handle database errors during deletion"""
        recommendation = RecommendationFactory()
        recommendation.create()
        with patch(
            "service.models.db.session.delete",
            side_effect=SQLAlchemyError("Mocked exception"),
        ) as mock_delete:
            with self.assertRaises(DataValidationError) as context:
                recommendation.delete()
            self.assertTrue(mock_delete.called)
            self.assertIn("Mocked exception", str(context.exception))
