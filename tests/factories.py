"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Orders, OrderItems


class OrdersFactory(factory.Factory):
    """
    Factory class for creating Orders instances.
    """

    class Meta:
        """
        Meta class for defining metadata options for the Orders factory.
        """

        model = Orders

    order_id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    order_date = factory.Faker("date_time")
    status = factory.Iterator(
        [
            "pending",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "returned",
            "refunded",
        ]
    )
    tracking_number = factory.Faker("random_number", digits=10)
    discount_amount = factory.Faker("random_number", digits=2)


class OrderItemsFactory(factory.Factory):
    """
    Factory class for creating instances of OrderItems model.
    """

    class Meta:
        """
        Meta class for defining metadata options for the OrderItems factory.
        """

        model = OrderItems

    order_item_id = factory.Sequence(lambda n: n)
    order_id = factory.SubFactory(OrdersFactory)
    product_id = factory.Sequence(lambda n: n)
    quantity = factory.Faker("random_number", digits=2)
    price = factory.Faker("random_number", digits=2)
