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
Pet Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Pets from the inventory of pets in the PetShop
"""

from datetime import datetime
from flask import jsonify, request, url_for
from flask import current_app as app  # Import Flask application
from service.models import OrderItems, Orders
from service.common import status, error_handlers  # HTTP Status Codes

# pylint: disable="broad-exception-caught


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Orders Service REST API",
            version="1.0",
            paths=[
                url_for("health", _external=True),
                url_for("list_orders", _external=True),
            ],
        ),
        status.HTTP_200_OK,
    )


@app.route("/health")
def health():
    """Tries to query the database to check if service is up"""
    try:
        amount = Orders.get_all_orders_amount()
        return (
            {"status": "healthy", "order_amount": amount},
            status.HTTP_200_OK,
        )
    except Exception as e:
        return (
            {"status": "unhealthy", "error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.route("/ui")
def admin_ui():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/orders", methods=["POST"])
def create_order():
    """Create a new order.

    This function creates a new order based on the JSON data provided in the request.

    Returns:
        A JSON response containing the serialized representation of the newly created order.

    Raises:
        Exception: If there is an error while creating the order.

    """

    try:
        new_order = Orders.create_new(request.json)
        response = jsonify(new_order.serialize())
        response.status_code = 201
        return response
    except Exception as e:
        return error_handlers.bad_request(e)


@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_item_to_order(order_id: int):
    """Add an item to an order.

    This function adds a new item to the order with the specified ID.

    Args:
        id (int): The ID of the order.

    Returns:
        dict: A dictionary containing the serialized representation of the newly created item.

    Raises:
        Exception: If there is an error while adding the item to the order.
    """
    try:
        new_item = OrderItems.create_item(order_id, request.json)
        response = jsonify(new_item.serialize())
        response.status_code = 201
        return response
    except Exception as e:
        return error_handlers.bad_request(e)


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_item_in_order(order_id, item_id):
    """
    Retrieve a specific item in an order.

    Args:
        order_id (int): The ID of the order.
        item_id (int): The ID of the item.

    Returns:
        dict: A dictionary containing the serialized item if found, or an error message if not found.

    """
    item = OrderItems.find_item_in_order(order_id, item_id)
    if not item:
        return error_handlers.not_found("Item not found")
    response = jsonify(item.serialize())
    response.status_code = 200
    return response


@app.route("/orders/<int:order_id>/items", methods=["GET"])
def get_items_in_order(order_id):
    """
    Retrieve all items in an order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        dict: A dictionary containing the serialized items if found, or an error message if not found.

    """
    items = OrderItems.find_by_order(order_id)
    if not items:
        return error_handlers.not_found("No items found for this order")
    response = jsonify([item.serialize() for item in items])
    response.status_code = 200
    return response


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Retrieve a single order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        dict: A dictionary containing the serialized order if found, or an error message if not found.

    """
    order = Orders.find(order_id)
    if not order:
        return error_handlers.not_found("Order not found")
    response = jsonify(order.serialize())
    response.status_code = 200
    return response


@app.route("/orders", methods=["GET"])
def list_orders():
    """Returns all of the Orders"""
    app.logger.info("Request to list Orders...")

    orders = []

    # Parse any arguments from the query string
    customer_id = request.args.get("customer_id",type=int)
    order_date = request.args.get("order_date")
    order_status = request.args.get("status")
    tracking_number = request.args.get("tracking_number")
    discount_amount = request.args.get("discount_amount", type=float)

    if customer_id is not None:
        app.logger.info("Find by customer_id: %s", customer_id)
        orders = Orders.find_by_customer_id(customer_id)
    elif order_date is not None:
        app.logger.info("Find by order_date: %s", order_date)
        order_date: datetime = datetime.fromisoformat(order_date)
        orders = Orders.find_by_order_date(order_date)
    elif order_status is not None:
        app.logger.info("Find by status %s", order_status)
        orders = Orders.find_by_status(order_status.lower())
    elif tracking_number is not None:
        app.logger.info("Find by tracking_number: %s", tracking_number)
        orders = Orders.find_by_tracking_number(tracking_number)
    elif discount_amount is not None:
        app.logger.info("Find by discount_amount: %s", discount_amount)
        orders = Orders.find_by_discount_amount(discount_amount)
    else:
        app.logger.info("Find all")
        orders = Orders.list_all()

    results = [order.serialize() for order in orders]
    app.logger.info("[%s] Orders returned", len(results))
    response = jsonify(results)
    response.status_code =  status.HTTP_200_OK
    return response


@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Update an order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        dict: A dictionary containing the serialized order if updated, or an error message if not found.

    """
    order = Orders.update_order(order_id, request.json)
    if not order:
        return error_handlers.not_found("Order not found")
    response = jsonify(order.serialize())
    response.status_code = 200
    return response


@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete an order.
    Args:
        order_id (int): The ID of the order.
    Returns:
        dict: A dictionary containing a success message if deleted, or an error message if not found.
    """
    order = Orders.delete_order(order_id)
    if not order:
        return error_handlers.not_found("Order not found")
    response = jsonify({"message": "Order successfully deleted"})
    response.status_code = 200
    return response


@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PUT"])
def update_item_in_order(order_id, item_id):
    """
    Update a single item in an order.

    Args:
        order_id (int): The ID of the order.
        item_id (int): The ID of the item.

    Returns:
        dict: A dictionary containing the serialized item if updated, or an error message if not found.

    """
    item = OrderItems.update_item_in_order(order_id, item_id, request.json)
    if not item:
        return error_handlers.not_found("Item not found in order")
    response = jsonify(item.serialize())
    response.status_code = 200
    return response

@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item_from_order(order_id, item_id):
    """
    Delete a single item from an order.

    Args:
        order_id (int): The ID of the order.
        item_id (int): The ID of the item.

    Returns:
        dict: A dictionary containing a success message if deleted, or an error message if not found.

    """
    item = OrderItems.delete_item_from_order(order_id, item_id)
    if not item:
        return error_handlers.not_found("Item not found in order")
    response = jsonify({"message": "Item successfully deleted"})
    response.status_code = 200
    return response

@app.route("/orders/<int:order_id>/ship", methods=["PUT"])
def ship_order(order_id):
    """
    Ship an order.

    Args:
        order_id (int): The ID of the order.

    Returns:
        dict: A dictionary containing the serialized order if updated, or an error message if not found.

    """
    order = Orders.find(order_id)
    if not order:
        return error_handlers.not_found("Order not found")
    tracking_number = request.json.get("tracking_number", None)
    if tracking_number is None:
        return error_handlers.bad_request("Tracking number is required to ship an order")
    order.status = "shipped"
    order.tracking_number = tracking_number
    updated_json = order.serialize()
    order = Orders.update_order(order_id, updated_json)
    response = jsonify(order.serialize())
    response.status_code = 200
    return response
