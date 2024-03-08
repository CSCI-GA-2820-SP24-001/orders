"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Orders(db.Model):
    """
    Class that represents a order
    """

    ##################################################
    # Table Schema
    ##################################################
    order_id: int = db.Column(db.Integer, primary_key=True)
    customer_id: int = db.Column(db.Integer, nullable=False)
    order_date: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    status: str = db.Column(
        Enum(
            "pending",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "returned",
            "refunded",
            name="status_enum",
        ),
        default="pending",
    )
    tracking_number: str|None  = db.Column(db.String, nullable=True)
    discount_amount: float = db.Column(db.Float, default=0.0)
    # Relationship to OrderItems
    order_items = db.relationship(
        "OrderItems", backref="orders", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order id=[{self.order_id}]>"

    def create(self):
        """
        Creates a Order to the database
        """
        logger.info("Creating %s", self.order_id)
        self.order_id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Order to the database
        """
        logger.info("Saving %s", self.order_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e
        
    def delete(self):
        """Removes a Order from the data store"""
        logger.info("Deleting %s", self.order_id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Order into a dictionary"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "tracking_number": self.tracking_number,
            "discount_amount": self.discount_amount,
        }

    def deserialize(self, data):
        """
        Deserializes a Order from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id: int = data["customer_id"]
            self.order_date: datetime = datetime.fromisoformat(data.get("order_date", datetime.utcnow().isoformat()))
            self.status: str = data.get("status", "pending")
            self.tracking_number: str|None = data.get("tracking_number", None)
            self.discount_amount: float = data.get("discount_amount", 0.0)
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def list_all(cls):
        """Returns a list of all orders"""
        logger.info("Processing list_all request")
        return cls.query.all()

    @classmethod
    def create_new(cls, data):
        """Creates a new order"""
        logger.info("Processing create_new request")
        order = cls()
        order.deserialize(data)
        order.create()
        return order

    @classmethod
    def find(cls, order_id):
        """Returns a single order by its ID"""
        logger.info("Processing get_order request for id %s", order_id)
        return cls.query.get(order_id)

    @classmethod
    def update_order(cls, order_id, data):
        """Updates an order by its ID"""
        logger.info("Processing update_order request for id %s", order_id)
        order = cls.query.get(order_id)
        if not order:
            return None
        for key, value in data.items():
            setattr(order, key, value)
        order.update()
        return order

    @classmethod
    def delete_order(cls, order_id):
        """Deletes an order by its ID"""
        logger.info("Processing delete_order request for id %s", order_id)
        order = cls.query.get(order_id)
        if not order:
            return None
        order.delete()
        return order


class OrderItems(db.Model):
    """
    Class that represents an order item
    """

    ##################################################
    # Table Schema
    ##################################################
    order_item_id: int = db.Column(db.Integer, primary_key=True)
    order_id: int = db.Column(db.Integer, db.ForeignKey("orders.order_id"))
    product_id: int = db.Column(db.Integer, nullable=False)
    quantity: int = db.Column(db.Integer)
    price: float = db.Column(db.Float)

    def __repr__(self):
        return f"<OrderItem id=[{self.order_item_id}]>"

    def create(self):
        """
        Creates an OrderItem to the database
        """
        logger.info("Creating %s", self.order_item_id)
        self.order_item_id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates an OrderItem to the database
        """
        logger.info("Saving %s", self.order_item_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes an OrderItem from the data store"""
        logger.info("Deleting %s", self.order_item_id)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes an OrderItem into a dictionary"""
        return {
            "order_item_id": self.order_item_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": self.price,
        }

    def deserialize(self, data):
        """
        Deserializes an OrderItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id: int = data["product_id"]
            self.quantity: int = data["quantity"]
            self.price: float = data["price"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid OrderItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid OrderItem: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def find_by_order(cls, order_id):
        """Returns all OrderItems with the given order ID"""
        logger.info("Processing order query for %s ...", order_id)
        return cls.query.filter(cls.order_id == order_id).all()

    @classmethod
    def create_item(cls, order_id, item_data):
        """Creates a new item and adds it to an order"""
        logger.info("Creating new item for order %s ...", order_id)
        new_item = cls()
        new_item.deserialize(item_data)
        new_item.order_id = order_id
        new_item.create()
        return new_item

    @classmethod
    def find_item_in_order(cls, order_id, item_id):
        """Finds a single item in an order"""
        logger.info("Finding item %s in order %s ...", item_id, order_id)
        return cls.query.filter_by(order_id=order_id, order_item_id=item_id).first()

    @classmethod
    def update_item_in_order(cls, order_id, item_id, data):
        """Updates a single item in an order"""
        logger.info("Updating item %s in order %s ...", item_id, order_id)
        item = cls.find_item_in_order(order_id, item_id)
        if not item:
            return None
        for key, value in data.items():
            setattr(item, key, value)
        item.update()
        return item

    @classmethod
    def delete_item_from_order(cls, order_id, item_id):
        """Deletes a single item from an order"""
        logger.info("Deleting item %s from order %s ...", item_id, order_id)
        item = cls.find_item_in_order(order_id, item_id)
        if not item:
            return None
        item.delete()
        return item
