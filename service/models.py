"""
Models for Recommendation

All of the models are stored in this module
"""

import logging
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PrimaryKeyNotSetError(Exception):
    """Used when tried to set primary key to None"""


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    product_id = db.Column(db.Integer, nullable=False)
    recommended_product_id = db.Column(db.Integer, nullable=False)
    recommendation_type = db.Column(db.String(63), nullable=False)

    def __repr__(self):
        return f"<Recommendation {self.name} id=[{self.id}]>"

    def create(self):
        """create a record"""
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """update a record"""
        logger.info("Updating %s", self.name)
        try:
            if self.id is None:
                raise PrimaryKeyNotSetError()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """delete a record"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """serialize a record"""
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product_id,
            "recommended_product_id": self.recommended_product_id,
            "recommendation_type": self.recommendation_type,
        }

    def deserialize(self, data):
        """Function that deserialize a record"""
        try:
            self.name = data["name"]
            self.product_id = int(data["product_id"])
            self.recommended_product_id = int(data["recommended_product_id"])
            self.recommendation_type = data["recommendation_type"]
        except ValueError as error:
            raise DataValidationError(
                "Invalid data type for product_id or recommended_product_id"
            ) from error
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    # @classmethod
    # def find_by_name(cls, name):
    #     """Returns all Recommendations with the given name

    #     Args:
    #         name (string): the name of the Recommendations you want to match
    #     """
    #     logger.info("Processing name query for %s ...", name)
    #     return cls.query.filter(cls.name == name)

    # @classmethod
    # def query_filter(cls, filters):
    #     """Return filtered list of recommendations"""
    #     query = cls.query
    #     if "recommended_product_id" in filters:
    #         query = query.filter_by(
    #             recommended_product_id=filters["recommended_product_id"]
    #         )
    #     if "recommendation_type" in filters:
    #         query = query.filter_by(recommendation_type=filters["recommendation_type"])
    #     return query.all()
