'use strict';

var init_weight_view = function () {
	$("#location-weight").val(10);
	$("#weight-update-btn").on("click", function () {
		update_recommendation(cur_selected_duns);
	});

	$("#phase-II-button").on("click", function () {
		if (!recommend_flag) {
			recommend_flag = true;
			$("#search-container").css("display", "none");
			$("#feature-container").css("display", "block");
			$("#phase-II-button").html("phase I");
		} else {
			recommend_flag = false;
			$("#search-container").css("display", "block");
			$("#feature-container").css("display", "none");
			$("#phase-II-button").html("phase II");
		}
	})
}

var update_recommendation = function (selected_duns) {
	var hierarchy_weight = +$("#hierarchy-level-weight").val();
	var revenue_weight = +$("#revenue-weight").val();
	var employee_weight = +$("#employee-number-weight").val();
	var branches_weight = +$("#branches-weight").val();
	var subsidiaries_weight = +$("#subsidiaries-weight").val();
	var location_weight = +$("#location-weight").val();
    var message = JSON.stringify({
        selected_duns: selected_duns,
        weights: [hierarchy_weight, revenue_weight, employee_weight, branches_weight, subsidiaries_weight, location_weight],
        digits: DIGITS,
        logic: LOGIC 
    });
    $.get("/api/recommend/" + message, function (rtn_string) {
        if (rtn_string == "NO_DATA") {
            console.log("Error", "Failed in recommend data.");
        } else {
            var recommend_data = JSON.parse(rtn_string);
            cur_tornado_data = recommend_data;
            console.log(cur_tornado_data);
            draw_tornado_view(cur_tornado_data); 
        }
    }); 
}