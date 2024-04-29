"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status

from service.models import Orders, OrderItems, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods,R0801
class TestRoutesService(TestCase):
    """TestRoutesService"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(OrderItems).delete()  # clean up the last tests
        db.session.query(Orders).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """test_index"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """test_create_order"""
        # Create a order
        resp = self.client.post("/orders", json={"customer_id": 1})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["customer_id"], 1)
        # Create a order with status
        resp = self.client.post("/orders", json={"customer_id": 2, "status": "shipped"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["status"], "shipped")
        self.assertEqual(resp.json["customer_id"], 2)
        # Create a order with tracking number
        resp = self.client.post(
            "/orders", json={"customer_id": 3, "tracking_number": "1234"}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["tracking_number"], "1234")
        self.assertEqual(resp.json["customer_id"], 3)
        # Create a order with discount amount
        resp = self.client.post(
            "/orders", json={"customer_id": 4, "discount_amount": 10.00}
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["discount_amount"], 10.00)
        self.assertEqual(resp.json["customer_id"], 4)
        # Create a order with all fields
        resp = self.client.post(
            "/orders",
            json={
                "customer_id": 5,
                "status": "processing",
                "tracking_number": "123456",
                "discount_amount": 100.00,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["status"], "processing")
        self.assertEqual(resp.json["tracking_number"], "123456")
        self.assertEqual(resp.json["discount_amount"], 100.00)
        self.assertEqual(resp.json["customer_id"], 5)
        # Create a order with no customer_id
        resp = self.client.post("/orders", json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Create a order with invalid status
        resp = self.client.post("/orders", json={"customer_id": 6, "status": "invalid"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Create a order with invalid discount amount
        resp = self.client.post(
            "/orders", json={"customer_id": 7, "discount_amount": "invalid"}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Create a order with invalid customer_id
        resp = self.client.post("/orders", json={"customer_id": "invalid"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Create a order with invalid json
        resp = self.client.post("/orders", data="invalid")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_to_order(self):
        """test_add_item_to_order"""
        resp = self.client.post(
            "/orders",
            json={
                "customer_id": 5,
                "status": "processing",
                "tracking_number": "123456",
                "discount_amount": 100.00,
            },
        )
        order_id = resp.json["order_id"]
        # Add an item to the order
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json["product_id"], 1)
        self.assertEqual(resp.json["quantity"], 1)
        self.assertEqual(resp.json["price"], 10.00)
        # Add an item to the order with no product_id
        resp = self.client.post(
            f"/orders/{order_id}/items", json={"quantity": 1, "price": 10.00}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with no quantity
        resp = self.client.post(
            f"/orders/{order_id}/items", json={"product_id": 1, "price": 10.00}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with no price
        resp = self.client.post(
            f"/orders/{order_id}/items", json={"product_id": 1, "quantity": 1}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with invalid product_id
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": "invalid", "quantity": 1, "price": 10.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with invalid quantity
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": "invalid", "price": 10.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with invalid price
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": "invalid"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with invalid json
        resp = self.client.post(f"/orders/{order_id}/items", data="invalid")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # Add an item to the order with non-existent order_id
        resp = self.client.post(
            "/orders/9999999/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_item_in_order(self):
        """test_get_single_item_in_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["order_id"]

        # Add an item to the order
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.json["order_item_id"]

        # Get the item from the order
        resp = self.client.get(f"/orders/{order_id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["order_item_id"], item_id)
        self.assertEqual(resp.json["product_id"], 1)
        self.assertEqual(resp.json["quantity"], 1)
        self.assertEqual(resp.json["price"], 10.00)

        # Try to get a non-existent item from the order
        resp = self.client.get(f"/orders/{order_id}/items/9999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Try to get an item from a non-existent order
        resp = self.client.get(f"/orders/9999999/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_items_in_order(self):
        """test_get_items_in_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["order_id"]

        # Add some items to the order
        self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 2, "quantity": 2, "price": 20.00},
        )

        # Get the items from the order
        resp = self.client.get(f"/orders/{order_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json), 2)
        self.assertEqual(resp.json[0]["product_id"], 1)
        self.assertEqual(resp.json[0]["quantity"], 1)
        self.assertEqual(resp.json[0]["price"], 10.00)
        self.assertEqual(resp.json[1]["product_id"], 2)
        self.assertEqual(resp.json[1]["quantity"], 2)
        self.assertEqual(resp.json[1]["price"], 20.00)

        # Try to get items from a non-existent order
        resp = self.client.get("/orders/9999999/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order(self):
        """test_get_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.json["order_id"]

        # Get the order
        resp = self.client.get(f"/orders/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["order_id"], order_id)
        self.assertEqual(resp.json["customer_id"], 1)

        # Try to get a non-existent order
        resp = self.client.get("/orders/9999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders(self):
        """test_list_orders"""
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json), 0)

        # Create some orders
        self.client.post("/orders", json={"customer_id": 1})
        self.client.post("/orders", json={"customer_id": 2})
        self.client.post("/orders", json={"customer_id": 3})

        # Get all orders
        resp = self.client.get("/orders")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json), 3)
        self.assertEqual(resp.json[0]["customer_id"], 1)
        self.assertEqual(resp.json[1]["customer_id"], 2)
        self.assertEqual(resp.json[2]["customer_id"], 3)

    def test_update_order(self):
        """test_update_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        order_id = resp.json["order_id"]

        # Update the order
        resp = self.client.put(f"/orders/{order_id}", json={"customer_id": 2})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["order_id"], order_id)
        self.assertEqual(resp.json["customer_id"], 2)

        # Try to update a non-existent order
        resp = self.client.put("/orders/9999999", json={"customer_id": 3})
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        """test_delete_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        order_id = resp.json["order_id"]

        # Delete the order
        resp = self.client.delete(f"/orders/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["message"], "Order successfully deleted")

        # Try to delete a non-existent order
        resp = self.client.delete("/orders/9999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 2})
        order_id = resp.json["order_id"]

        # Add an item to the order
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 2, "quantity": 1, "price": 100.00},
        )

        # Delete the order
        resp = self.client.delete(f"/orders/{order_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["message"], "Order successfully deleted")

    def test_update_item_in_order(self):
        """test_update_item_in_order"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        order_id = resp.json["order_id"]

        # Add an item to the order
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        item_id = resp.json["order_item_id"]

        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 2, "quantity": 1, "price": 100.00},
        )

        # Update the item in the order
        resp = self.client.put(
            f"/orders/{order_id}/items/{item_id}",
            json={"product_id": 2, "quantity": 2, "price": 20.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["order_item_id"], item_id)
        self.assertEqual(resp.json["product_id"], 2)
        self.assertEqual(resp.json["quantity"], 2)
        self.assertEqual(resp.json["price"], 20.00)

        # Try to update a non-existent item in the order
        resp = self.client.put(
            f"/orders/{order_id}/items/9999999",
            json={"product_id": 3, "quantity": 3, "price": 30.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Try to update an item in a non-existent order
        resp = self.client.put(
            f"/orders/9999999/items/{item_id}",
            json={"product_id": 4, "quantity": 4, "price": 40.00},
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST ACTIONS
    # ----------------------------------------------------------
    def test_like_an_item(self):
        """It should Like an Item"""
        items = self._create_items(10)
        response = self.client.put(f"{BASE_URL}/{item.id}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{item.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["available"], False)


    def test_delete_order_item(self):
        """test_delete_order_item"""
        # Create a new order
        resp = self.client.post("/orders", json={"customer_id": 1})
        order_id = resp.json["order_id"]

        # Add an item to the order
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 1, "quantity": 1, "price": 10.00},
        )
        item_id = resp.json["order_item_id"]
        resp = self.client.post(
            f"/orders/{order_id}/items",
            json={"product_id": 2, "quantity": 1, "price": 100.00},
        )

        # Get the items from the order
        resp = self.client.get(f"/orders/{order_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json), 2)

        # Delete the item from the order
        resp = self.client.delete(f"/orders/{order_id}/items/{item_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json["message"], "Item successfully deleted")

        # Get the new list of items from the order
        resp = self.client.get(f"/orders/{order_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]["product_id"], 2)
        self.assertEqual(resp.json[0]["quantity"], 1)
        self.assertEqual(resp.json[0]["price"], 100.00)

        # Try to delete a non-existent item from the order
        resp = self.client.delete(f"/orders/{order_id}/items/9999999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Try to delete an item from a non-existent order
        resp = self.client.delete(f"/orders/9999999/items/{item_id}")

    def test_health(self):
        """test_health"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_order_id(self):
        """It should Query orders by order_id"""
        orders = self._create_orders(5)
        test_order_id = orders[0].order_id
        order_id_count = len([order for order in orders if order.order_id == test_order_id])
        response = self.client.get(
            BASE_URL, query_string=f"order_id={quote_plus(test_order_id)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), order_id_count)
         # check the data just to be sure
        for order in data:
            self.assertEqual(order["order_id"], test_order_id)

    def test_query_by_customer_id(self):
        """It should Query orders by customer_id"""
        orders = self._create_orders(5)
        test_customer_id = orders[0].customer_id
        customer_id_count = len([order for order in orders if order.customer_id == test_customer_id])
        response = self.client.get(
            BASE_URL, query_string=f"customer_id={quote_plus(test_customer_id)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), customer_id_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["customer_id"], test_customer_id)

    
    def test_query_by_order_date(self):
        """It should Query orders by order_date"""
        orders = self._create_orders(5)
        test_order_date = orders[0].order_date
        order_date_count = len([order for order in orders if order.order_date == test_order_date])
        response = self.client.get(
            BASE_URL, query_string=f"order_date={quote_plus(test_order_date)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), order_date_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["order_date"], test_order_date)

    def test_query_by_status(self):
        """It should Query orders by status"""
        orders = self._create_orders(10)
        pending_orders = [order for order in orders if order.status == status.pending]
        processing_orders = [order for order in orders if order.status == status.processing]
        shipped_orders = [order for order in orders if order.status == status.shipped]
        delivered_orders = [order for order in orders if order.status == status.delivered]
        cancelled_orders = [order for order in orders if order.status == status.cencelled]
        returned_orders = [order for order in orders if order.status == status.returned]
        refunded_orders = [order for order in orders if order.status == status.refunded]
        pending_count = len(pending_orders)
        processing_count = len(processing_orders)
        shipped_count = len(shipped_orders)
        delivered_count = len(delivered_orders)
        cancelled_count = len(cancelled_orders)
        returned_count = len(returned_orders)
        refunded_count = len(refunded_orders)
        logging.debug("Pending orders [%d] %s", pending_count, pending_orders)
        logging.debug("Processing orders [%d] %s", processing_count, processing_orders)
        logging.debug("Shipped orders [%d] %s", shipped_count, shipped_orders)
        logging.debug("Delivered orders [%d] %s", delivered_count, delivered_orders)
        logging.debug("Cancelled orders [%d] %s", cancelled_count, cancelled_orders)
        logging.debug("Returned orders [%d] %s", returned_count, returned_orders)
        logging.debug("Refunded orders [%d] %s", refunded_count, refunded_orders)

        # test for pending
        response = self.client.get(BASE_URL, query_string="status=pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), pending_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.pending.name)

        # test for processing
        response = self.client.get(BASE_URL, query_string="status=processing")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), processing_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.processing.name)

        # test for shipped
        response = self.client.get(BASE_URL, query_string="status=shipped")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), shipped_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.shipped.name)

        # test for delivered
        response = self.client.get(BASE_URL, query_string="status=delivered")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), delivered_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.delivered.name)

        # test for cancelled
        response = self.client.get(BASE_URL, query_string="status=cancelled")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), cancelled_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.cancelled.name)

        # test for returned
        response = self.client.get(BASE_URL, query_string="status=returned")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), returned_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.returned.name)

        # test for refunded
        response = self.client.get(BASE_URL, query_string="status=refunded")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), refunded_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["status"], status.refunded.name)

    def test_query_by_tracking_number(self):
        """It should Query orders by tracking_number"""
        orders = self._create_orders(5)
        test_tracking_number = orders[0].tracking_number
        tracking_number_count = len([order for order in orders if order.tracking_number == test_tracking_number])
        response = self.client.get(
            BASE_URL, query_string=f"tracking_number={quote_plus(test_tracking_number)}"
        )
        self.assertEqual(response.tracking_number_code, tracking_number.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), tracking_number_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["tracking_number"], test_tracking_number)

    def test_query_by_discount_amount(self):
        """It should Query orders by discount_amount"""
        orders = self._create_orders(5)
        test_discount_amount = orders[0].discount_amount
        discount_amount_count = len([order for order in orders if order.discount_amount == test_discount_amount])
        response = self.client.get(
            BASE_URL, query_string=f"discount_amount={quote_plus(test_discount_amount)}"
        )
        self.assertEqual(response.discount_amount_code, discount_amount.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), discount_amount_count)
        # check the data just to be sure
        for order in data:
            self.assertEqual(order["discount_amount"], test_discount_amount)