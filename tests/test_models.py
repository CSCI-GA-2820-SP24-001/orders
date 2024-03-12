"""
Test cases for Pet Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import DataValidationError, Orders, OrderItems, db
from tests.factories import OrdersFactory, OrderItemsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


class TestOrdersModel(TestCase):
    """TestOrdersModel"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Orders).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_order(self):
        """test_create_order"""
        order = OrdersFactory()
        order.create()
        self.assertIsNotNone(order.order_id)
        order = OrdersFactory(customer_id=None)
        with self.assertRaises(DataValidationError):
            order.create()

    def test_update_order(self):
        """test_update_order"""
        order = OrdersFactory(status="pending")
        order.create()
        order.status = "processing"
        order.update()
        self.assertEqual(order.status, "processing")
        order.customer_id = None
        with self.assertRaises(DataValidationError):
            order.update()

    def test_delete_order(self):
        """test_delete_order"""
        order = OrdersFactory()
        order.create()
        found = Orders.query.all()
        self.assertEqual(len(found), 1)
        order.delete()
        found = Orders.query.all()
        self.assertEqual(len(found), 0)
        order = OrdersFactory()
        order.create()
        order.order_id = None
        with self.assertRaises(DataValidationError):
            order.delete()

    def test_serialize_order(self):
        """test_serialize_order"""
        order = OrdersFactory()
        data = order.serialize()
        self.assertEqual(data["order_id"], order.order_id)

    def test_deserialize_order(self):
        """test_deserialize_order"""
        order = OrdersFactory()
        data = order.serialize()
        new_order = Orders()
        new_order.deserialize(data)
        self.assertEqual(new_order.customer_id, order.customer_id)
        data = {}  # This will cause a KeyError
        with self.assertRaises(DataValidationError):
            new_order.deserialize(data)
        data = "not a dict"  # This will cause a TypeError
        with self.assertRaises(DataValidationError):
            new_order.deserialize(data)

    def test_list_all_orders(self):
        """test_list_all_orders"""
        test_orders = OrdersFactory.create_batch(5)
        for order in test_orders:
            order.create()
        orders = Orders.list_all()
        self.assertEqual(len(orders), 5)

    def test_create_new_order(self):
        """test_create_new_order"""
        order_data = {
            "customer_id": 1,
            "order_date": "2021-12-01",
            "status": "pending",
            "tracking_number": "1234567890",
            "discount_amount": 10.0,
        }
        order = Orders.create_new(order_data)
        self.assertEqual(order.customer_id, order_data["customer_id"])

    def test_find_order(self):
        """test_find_order"""
        order = OrdersFactory()
        order.create()
        found = Orders.find(order.order_id)
        self.assertEqual(found.order_id, order.order_id)

    def test_update_order_method(self):
        """test_update_order_method"""
        order = OrdersFactory(status="pending")
        order.create()
        order_data = {"status": "processing"}
        updated_order = Orders.update_order(order.order_id, order_data)
        self.assertEqual(updated_order.status, "processing")
        order = Orders.update_order(updated_order.order_id + 1, order_data)
        assert order is None

    def test_delete_order_method(self):
        """test_delete_order_method"""
        order = OrdersFactory()
        order.create()
        found = Orders.query.all()
        self.assertEqual(len(found), 1)
        Orders.delete_order(order.order_id)
        found = Orders.query.all()
        self.assertEqual(len(found), 0)
        order = Orders.delete_order(1)
        assert order is None

    def test_order_repr(self):
        """test_order_repr"""
        order = OrdersFactory()
        order.create()
        self.assertEqual(str(order), f"<Order id=[{order.order_id}]>")


class TestOrderItemsModel(TestCase):
    """TestOrderItemsModel"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(OrderItems).delete()  # clean up the last tests
        db.session.query(Orders).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_item(self):
        """test_create_item"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        self.assertIsNotNone(item.order_item_id)
        item = OrderItemsFactory(order_id=order.order_id, product_id=None)
        with self.assertRaises(DataValidationError):
            item.create()

    def test_update_item(self):
        """test_update_item"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(price=999.0, order_id=order.order_id)
        item.create()
        item.price = 10.0
        item.update()
        self.assertEqual(item.price, 10.0)
        item.product_id = None
        with self.assertRaises(DataValidationError):
            item.update()

    def test_delete_item(self):
        """test_delete_item"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        found = OrderItems.query.all()
        self.assertEqual(len(found), 1)
        item.delete()
        found = OrderItems.query.all()
        self.assertEqual(len(found), 0)
        item = OrderItemsFactory(order_id=order.order_id)
        with self.assertRaises(DataValidationError):
            item.delete()

    def test_serialize_item(self):
        """test_serialize_item"""
        item = OrderItemsFactory()
        data = item.serialize()
        self.assertEqual(data["order_item_id"], item.order_item_id)

    def test_deserialize_item(self):
        """test_deserialize_item"""
        item = OrderItemsFactory()
        data = item.serialize()
        new_item = OrderItems()
        new_item.deserialize(data)
        self.assertEqual(new_item.product_id, item.product_id)
        data = {}  # This will cause a KeyError
        with self.assertRaises(DataValidationError):
            new_item.deserialize(data)
        data = "not a dict"  # This will cause a TypeError
        with self.assertRaises(DataValidationError):
            new_item.deserialize(data)

    def test_find_by_order(self):
        """test_find_by_order"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        found = OrderItems.find_by_order(item.order_id)
        self.assertEqual(found[0].order_id, item.order_id)

    def test_create_item_in_order(self):
        """test_create_item_in_order"""
        order = OrdersFactory()
        order.create()
        item_data = {
            "product_id": 1,
            "quantity": 1,
            "price": 10.0,
        }
        item = OrderItems.create_item(order.order_id, item_data)
        self.assertEqual(item.product_id, item_data["product_id"])
        self.assertEqual(item.order_id, order.order_id)

    def test_find_item_in_order(self):
        """test_find_item_in_order"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        item2 = OrderItemsFactory(order_id=order.order_id)
        item2.create()
        found = OrderItems.find_item_in_order(item.order_id, item.order_item_id)
        self.assertEqual(found.order_item_id, item.order_item_id)

    def test_update_item_in_order(self):
        """test_update_item_in_order"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(quantity=1, order_id=order.order_id)
        item.create()
        item_data = {"quantity": 2}
        updated_item = OrderItems.update_item_in_order(
            item.order_id, item.order_item_id, item_data
        )
        self.assertEqual(updated_item.quantity, 2)
        item = OrderItems.update_item_in_order(
            updated_item.order_id + 1, updated_item.order_item_id, item_data
        )
        assert item is None
        item = OrderItems.update_item_in_order(
            updated_item.order_id, updated_item.order_item_id + 1, item_data
        )
        assert item is None
        item = OrderItems.update_item_in_order(
            updated_item.order_id + 1, updated_item.order_item_id + 1, item_data
        )
        assert item is None

    def test_delete_item_from_order(self):
        """test_delete_item_from_order"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        found = OrderItems.query.all()
        self.assertEqual(len(found), 1)
        OrderItems.delete_item_from_order(item.order_id, item.order_item_id)
        found = OrderItems.query.all()
        self.assertEqual(len(found), 0)
        item_test = OrderItems.delete_item_from_order(item.order_id, item.order_item_id)
        assert item_test is None
        item_test = OrderItems.delete_item_from_order(
            item.order_id + 1, item.order_item_id
        )
        assert item_test is None
        item_test = OrderItems.delete_item_from_order(
            item.order_id, item.order_item_id + 1
        )
        assert item_test is None
        item_test = OrderItems.delete_item_from_order(
            item.order_id + 1, item.order_item_id + 1
        )
        assert item_test is None

    def test_item_repr(self):
        """test_item_repr"""
        order = OrdersFactory()
        order.create()
        item = OrderItemsFactory(order_id=order.order_id)
        item.create()
        self.assertEqual(str(item), f"<OrderItem id=[{item.order_item_id}]>")
