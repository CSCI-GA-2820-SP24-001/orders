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
    And I set the "Customer ID" to "10"
    And I set the "Order Date" to "04/29/2024"
    And I set the "Discount Amount" to "0"
    And I press the "Create" button
    Then I should see the message "Success"

# LIST ALL ORDERS
Scenario: List orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1001" in the results
    And I should see "1002" in the results
    And I should see "1003" in the results
    And I should see "1004" in the results
    And I should see "1005" in the results

# UPDATE ORDERS
Scenario: Update Orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1001" in the "Customer ID" field
    When I set the "Customer ID" to "10"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "10" in the "Customer ID" field


# DELETE ORDERS
Scenario: Delete Orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "1001" in the results
    And I should see "1001" in the "Customer ID" field
    When I press the "Delete" button
    Then I should see the message "Order has been Deleted!"
    When I press the "Search" button
    Then I should see the message "Success"
    And I should not see "1001" in the results


