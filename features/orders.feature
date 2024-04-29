Feature: The order service back-end
    As a Order Owner
    I need a RESTful catalog service
    So that I can keep track of all my orders

Background:
    Given the following orders
        | customer_id | order_date | status     | tracking_number | discount_amount |
        | 1001        | 2022-01-01 | pending    | TRK12345        | 0.0             |
        | 1002        | 2022-01-02 | processing | TRK12346        | 5.0             |
        | 1003        | 2022-01-03 | shipped    | TRK12347        | 10.0            |
        | 1004        | 2022-01-04 | delivered  | TRK12348        | 15.0            |
        | 1005        | 2022-01-05 | returned   | TRK12349        | 20.0            |
Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Orders RESTful Service" in the title
    And I should not see "404 Not Found"


# CREATE A ORDER
Scenario: Create a order
    When I visit the "Home Page"
    And I set the "Order User ID" to "10"
    And I press the "Create order" button
    Then I should see the message "Success"

# DELETE ORDERS
Scenario: Delete orders
When I visit the "Home Page"
And I set the "Order User ID" to "1"
And I press the "Search Order" button
Then I should see the message "Success"
And I should see "1" under the row "User ID 1" in the table
When I press the "Delete Order" button
Then I should see the message "Success"
When I press the "Search Order" button
Then I should see the message "Success"
And I should not see "User ID 1" in the results

