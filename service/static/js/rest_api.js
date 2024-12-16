$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
function update_form_data(res) {
    $("#rec_id").val(res.id);
    $("#rec_name").val(res.name);
    $("#product_id").val(res.product_id);
    $("#recommended_product_id").val(res.recommended_product_id);
    $("#rec_type").val(res.recommendation_type);
}

// Clears all form fields
function clear_form_data() {
    $("#rec_id").val("");
    $("#rec_name").val("");
    $("#product_id").val("");
    $("#recommended_product_id").val("");
    $("#rec_type").val("");
}

// Updates the flash message area
function flash_message(message) {
    $("#flash_message").empty();
    $("#flash_message").append(message);
}



    // ****************************************
    // Create a Pet
    // ****************************************

    // Create a Recommendation
$("#create-btn").click(function () {

    let name = $("#rec_name").val();
    let product_id = $("#product_id").val();
    let recommended_product_id = $("#recommended_product_id").val();
    let rec_type = $("#rec_type").val();

    console.log("Name:", name);
    console.log("Product ID:", product_id);
    console.log("Recommended Product ID:", recommended_product_id);
    console.log("Recommendation Type:", rec_type);

    let data = {
        "name": name,
        "product_id": parseInt(product_id),
        "recommended_product_id": parseInt(recommended_product_id),
        "recommendation_type": rec_type
    };

    $("#flash_message").empty();
    
    let ajax = $.ajax({
        type: "POST",
        url: "/recommendations",
        contentType: "application/json",
        data: JSON.stringify(data),
    });

    ajax.done(function(res){
        update_form_data(res);
        flash_message("Success");
    });

    ajax.fail(function(res){
        flash_message(res.responseJSON.message);
    });
});




    // ****************************************
    // Update a Pet
    // ****************************************

    // Update a Recommendation
$("#update-btn").click(function () {

    let rec_id = $("#rec_id").val();
    let name = $("#rec_name").val();
    let product_id = $("#product_id").val();
    let recommended_product_id = $("#recommended_product_id").val();
    let rec_type = $("#rec_type").val();

    let data = {
        "name": name,
        "product_id": parseInt(product_id),
        "recommended_product_id": parseInt(recommended_product_id),
        "recommendation_type": rec_type
    };

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "PUT",
        url: `/recommendations/${rec_id}`,
        contentType: "application/json",
        data: JSON.stringify(data)
    });

    ajax.done(function(res){
        update_form_data(res);
        flash_message("Success");
    });

    ajax.fail(function(res){
        flash_message(res.responseJSON.message);
    });

});



    // ****************************************
    // Retrieve a Pet
    // ****************************************

 // Retrieve a Recommendation
$("#retrieve-btn").click(function () {

    let rec_id = $("#rec_id").val();

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "GET",
        url: `/recommendations/${rec_id}`,
        contentType: "application/json",
        data: ''
    });

    ajax.done(function(res){
        update_form_data(res);
        flash_message("Success");
    });

    ajax.fail(function(res){
        clear_form_data();
        flash_message(res.responseJSON.message);
    });

});



    // ****************************************
    // Delete a Pet
    // ****************************************

 // Delete a Recommendation
$("#delete-btn").click(function () {

    let rec_id = $("#rec_id").val();

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "DELETE",
        url: `/recommendations/${rec_id}`,
        contentType: "application/json",
        data: '',
    });

    ajax.done(function(res){
        clear_form_data();
        flash_message("Recommendation has been Deleted!");
    });

    ajax.fail(function(res){
        flash_message("Server error!");
    });

});



    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#rec_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });


    // ****************************************
    // Search for a Pet
    // ****************************************
// Search for Recommendations
$("#search-btn").click(function () {

    let name = $("#rec_name").val();
    let product_id = $("#product_id").val();
    let recommended_product_id = $("#recommended_product_id").val();
    let rec_type = $("#rec_type").val();

    let queryString = "";

    if (name) {
        queryString += `name=${name}`;
    }
    if (product_id) {
        if (queryString.length > 0) {
            queryString += `&product_id=${product_id}`;
        } else {
            queryString += `product_id=${product_id}`;
        }
    }
    if (recommended_product_id) {
        if (queryString.length > 0) {
            queryString += `&recommended_product_id=${recommended_product_id}`;
        } else {
            queryString += `recommended_product_id=${recommended_product_id}`;
        }
    }
    if (rec_type) {
        if (queryString.length > 0) {
            queryString += `&recommendation_type=${rec_type}`;
        } else {
            queryString += `recommendation_type=${rec_type}`;
        }
    }

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "GET",
        url: `/recommendations?${queryString}`,
        contentType: "application/json",
        data: ''
    });

    ajax.done(function(res){
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-1">ID</th>';
        table += '<th class="col-md-2">Name</th>';
        table += '<th class="col-md-1">Product ID</th>';
        table += '<th class="col-md-1">Recommended Product ID</th>';
        table += '<th class="col-md-2">Recommendation Type</th>';
        table += '<th class="col-md-2">Created Time</th>';
        table += '<th class="col-md-2">Updated Time</th>';
        table += '</tr></thead><tbody>';
        let firstRec = "";
        for (let i = 0; i < res.length; i++) {
            let rec = res[i];
            table += `<tr id="row_${i}"><td>${rec.id}</td><td>${rec.name}</td><td>${rec.product_id}</td><td>${rec.recommended_product_id}</td><td>${rec.recommendation_type}</td><td>${rec.created_at}</td><td>${rec.updated_at}</td></tr>`;
            if (i == 0) {
                firstRec = rec;
            }
        }
        table += '</tbody></table>';
        $("#search_results").append(table);

        // copy the first result to the form
        if (firstRec != "") {
            update_form_data(firstRec);
        }

        flash_message("Success");
    });

    ajax.fail(function(res){
        flash_message(res.responseJSON.message);
    });

});



})
