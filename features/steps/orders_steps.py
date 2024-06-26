######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Order Steps

Steps file for Order.feature
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following orders')
def step_impl(context):
    """ Delete all Orders and load new ones """

    # List all of the orders and delete them one by one
    rest_endpoint = f"{context.base_url}/orders"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for order in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{order['order_id']}")
        assert(context.resp.status_code == HTTP_200_OK)

    # load the database with new orders
    for row in context.table:
        payload = {
            "customer_id": row['customer_id'],
            "order_date": row['order_date'],
            "status": row['status'],
            "tracking_number": row['tracking_number'],
            "discount_amount": row['discount_amount']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert(context.resp.status_code == HTTP_201_CREATED)