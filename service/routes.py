######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore Rofrano jsonify restx dbname

"""
Recommendation Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations from the inventory of pets in the PetShop
"""

import secrets
from functools import wraps
from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.models import Recommendation
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Recommendation",
    {
        "name": fields.String(
            required=True, description="The name associated with the recommendation"
        ),
        "product_id": fields.Integer(
            required=True, description="The ID of the product"
        ),
        "recommended_product_id": fields.Integer(
            required=True, description="The ID of the recommended product"
        ),
        "recommendation_type": fields.String(
            required=True,
            description="The type of recommendation (e.g., similar, complementary, etc.)",
        ),
    },
)


recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {
        "_id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# Query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="Filter recommendations by name",
)
recommendation_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="Filter recommendations by product ID",
)
recommendation_args.add_argument(
    "recommended_product_id",
    type=int,
    location="args",
    required=False,
    help="Filter recommendations by recommended product ID",
)
recommendation_args.add_argument(
    "recommendation_type",
    type=str,
    location="args",
    required=False,
    help="Filter recommendations by type",
)


######################################################################
# Authorization Decorator
######################################################################
def token_required(func):
    """Decorator to require a token for this endpoint"""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if "X-Api-Key" in request.headers:
            token = request.headers["X-Api-Key"]

        if app.config.get("API_KEY") and app.config["API_KEY"] == token:
            return func(*args, **kwargs)

        return {"message": "Invalid or missing token"}, 401

    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route("/recommendations/<int:id>")
@api.param("id", "The Product Recommendation identifier")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Product Recommendation
    GET /recommendations/{id} - Returns a Product Recommendation with the given id
    PUT /recommendations/{id} - Updates a Product Recommendation with the given id
    DELETE /recommendations/{id} - Deletes a Product Recommendation with the given id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("get_recommendation")
    @api.response(404, "Product Recommendation not found")
    @api.marshal_with(recommendation_model)
    def get(self, id):
        """
        Retrieve a single Product Recommendation

        This endpoint will return a Product Recommendation based on its id
        """
        app.logger.info("Request to retrieve a product recommendation with id [%s]", id)
        recommendation = Recommendation.find(id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product Recommendation with id '{id}' was not found.",
            )
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("update_recommendation", security="apikey")
    @api.response(404, "Product Recommendation not found")
    @api.response(400, "The posted Product Recommendation data was not valid")
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, id):
        """
        Update a Product Recommendation

        This endpoint will update a Product Recommendation based on the body that is posted
        """
        app.logger.info("Request to update a product recommendation with id [%s]", id)
        recommendation = Recommendation.find(id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product Recommendation with id '{id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        recommendation.deserialize(data)
        recommendation.id = id
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("delete_recommendation", security="apikey")
    @api.response(204, "Product Recommendation deleted")
    def delete(self, id):
        """
        Delete a Product Recommendation

        This endpoint will delete a Product Recommendation based on the id specified in the path
        """
        app.logger.info("Request to delete a product recommendation with id [%s]", id)
        recommendation = Recommendation.find(id)
        if recommendation:
            recommendation.delete()
            app.logger.info("Product Recommendation with id [%s] was deleted", id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations
######################################################################
@api.route("/recommendations", strict_slashes=False)
class RecommendationCollection(Resource):
    """Handles all interactions with collections of Product Recommendations"""

    # ------------------------------------------------------------------
    # LIST ALL PRODUCT RECOMMENDATIONS
    # ------------------------------------------------------------------
    @api.doc("list_recommendations")
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """Returns all of the Product Recommendations"""
        app.logger.info("Request to list Product Recommendations...")
        recommendations = []
        app.logger.info("Returning unfiltered list.")
        recommendations = Recommendation.all()

        app.logger.info("[%s] Product Recommendations returned", len(recommendations))
        results = [recommendation.serialize() for recommendation in recommendations]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("create_recommendation", security="apikey")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Product Recommendation

        This endpoint will create a Product Recommendation based on the data in the body that is posted
        """
        app.logger.info("Request to create a Product Recommendation")
        recommendation = Recommendation()
        app.logger.debug("Payload = %s", api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        app.logger.info(
            "Product Recommendation with new id [%s] created!", recommendation.id
        )
        location_url = api.url_for(
            RecommendationResource, id=recommendation.id, _external=True
        )
        return (
            recommendation.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)
