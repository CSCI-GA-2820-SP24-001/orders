$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.order_id);
        $("#customer_id").val(res.customer_id);
        $("#status").val(res.status);
        let order_date = new Date(res.order_date);
        let formatted_date = order_date.toISOString().split("T")[0];
        $("#order_date").val(formatted_date);
        $("#discount_amount").val(res.discount_amount);
        $("#tracking_number").val(res.tracking_number);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#status").val("");
        $("#order_date").val("");
        $("#discount_amount").val("");
        $("#tracking_number").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Order
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let status = $("#status").val();
        let order_date = $("#order_date").val();
        let discount_amount = $("#discount_amount").val();
        let tracking_number = $("#tracking_number").val();

        let data = {
            "customer_id": customer_id,
            "status": status,
            "order_date": order_date,
            "discount_amount": discount_amount,
            "tracking_number": tracking_number
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let customer_id = $("#customer_id").val();
        let status = $("#status").val();
        let order_date = $("#order_date").val();
        let discount_amount = $("#discount_amount").val();
        let tracking_number = $("#tracking_number").val();

        let data = {
            "customer_id": customer_id,
            "status": status,
            "order_date": order_date,
            "discount_amount": discount_amount,
            "tracking_number": tracking_number
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/orders/${order_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Order
    // ****************************************

    $("#search-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let status = $("#status").val();
        let order_date = $("#order_date").val();
        let discount_amount = $("#discount_amount").val();
        let tracking_number = $("#tracking_number").val();

        let queryString = ""

        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }
        if (order_date) {
            if (queryString.length > 0) {
                queryString += '&order_date=' + order_date
            } else {
                queryString += 'order_date=' + order_date
            }
        }
        if (discount_amount) {
            if (queryString.length > 0) {
                queryString += '&discount_amount=' + discount_amount
            } else {
                queryString += 'discount_amount=' + discount_amount
            }
        }
        if (tracking_number) {
            if (queryString.length > 0) {
                queryString += '&tracking_number=' + tracking_number
            } else {
                queryString += 'tracking_number=' + tracking_number
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Order ID</th>'
            table += '<th class="col-md-1">Customer ID</th>'
            table += '<th class="col-md-2">Order Date</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-3">Tracking Number</th>'
            table += '<th class="col-md-2">Discount Amount</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                table +=  `<tr id="row_${i}"><td>${order.order_id}</td><td>${order.customer_id}</td><td>${order.order_date}</td><td>${order.status}</td><td>${order.tracking_number}</td><td>${order.discount_amount}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
