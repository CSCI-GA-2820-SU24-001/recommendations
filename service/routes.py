######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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

"""
Recommendation Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations from the inventory of pets in the PetShop
"""
from flask import jsonify, request, make_response
from flask import current_app as app  # Import Flask application
from sqlalchemy.exc import SQLAlchemyError
from service.models import Recommendation
from service.common import status  # HTTP Status Codes


# from sqlalchemy import text  # Import the text function
# from service.models import db  # for check endpoints


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "This is the home page",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a recommendation
    This endpoint will create a recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    # check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    message = recommendation.serialize()
    # location_url = url_for("get_recommendations", id=recommendation.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": 250})


######################################################################
# LIST RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    """List all recommendations"""
    try:
        recommendations = Recommendation.query.all()
        return jsonify([rec.serialize() for rec in recommendations]), 200
    except SQLAlchemyError as e:
        return {"message": str(e)}, 500


#####################################################################
# DELETE RECOMMENDATIONs
#####################################################################
# @app.route("/recommendations/<int:int_id>", methods=["DELETE"])
# def delete_recommendation(int_id):
#     """delete a record"""
#     recommendation = Recommendation.query.get(int_id)
#     if recommendation:
#         try:
#             recommendation.delete()
#             return "", 204
#         except SQLAlchemyError as e:
#             return {"message": str(e)}, 500
#     else:
#         return {"message": "Recommendation not found"}, 404
# @app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
# def delete_recommendation(recommendation_id):
#     """
#     Delete a Recommendation
#     """
#     # Retrieve the recommendation to delete and delete it if it exists
#     recommendation = Recommendation.find(recommendation_id)
#     if not recommendation:
#         return "", status.HTTP_204_NO_CONTENT

#     try:
#         recommendation.delete()
#     except SQLAlchemyError as e:
#         return jsonify({"error": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR

#     return "", status.HTTP_204_NO_CONTENT


######################################################################
# Liveness Health Checkpoint
######################################################################


# @app.route("/health/liveness", methods=["GET"])
# def liveness():
#     """Endpoint to check if the application is alive"""
#     app.logger.info("Liveness check performed")
#     return jsonify(status="OK"), 200


######################################################################
# Readiness Health Checkpoints
######################################################################


# @app.route("/health/readiness", methods=["GET"])
# def readiness():
#     """Endpoint to check if the application is ready to serve"""
#     try:
#         # Attempt to make a simple query to ensure database connectivity
#         sql = text("select 1")
#         db.session.execute(sql)
#         app.logger.info("Readiness check performed")
#         return jsonify(status="OK"), 200
#     except Exception as e:
#         app.logger.error(f"Readiness check failed: {e}")
#         return jsonify(status="ERROR", message=str(e)), 500
