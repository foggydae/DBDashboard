'use strict';

var init_search_view = function () {
    $.get("/api/get_LOB_list", function (rtn_string) {
        if (rtn_string == "NO_DATA") {
            console.log("Error", "Failed in LOB data.");
        } else {
            var lob_list = JSON.parse(rtn_string);
			init_LOB_box(lob_list); 
        }
    });	

    $("#search-submit-btn").on("click", function () {
    	var checkboxes = $('.search-checkbox:checked');
    	var lob = [];
    	for (var i = 0; i < checkboxes.length; i++) {
    		lob.push(checkboxes[i].value);
    	}
    	var keyword = $("#search-keyword-input").val();
	    var message = JSON.stringify({
	        keyword: keyword,
	        lob: lob
	    });
	    $.get("/api/filter/" + message, function (rtn_string) {
	        if (rtn_string == "NO_DATA") {
	            console.log("Error", "Failed in filter data.");
	        } else {
	            var filtered = JSON.parse(rtn_string);
	            filter_hierarchy_view(filtered);
	        }
	    });	
    });

    $("#search-clear-all-btn").on("click", function () {
		$('.search-checkbox').removeAttr('checked');    	
    });

}

var init_LOB_box = function (lob_list) {
	$("#form-check-container").css("max-height", $("#filter-form").height() - $("#form-keyword-container").height() - $("#form-control-container").height() - 14);
	for (var i = 0; i < lob_list.length; i++) {
		$("#form-check-container").append(
			"<div class='form-check-base'>" +
			"	<input class='search-checkbox' type='checkbox' name='lob' value='" + lob_list[i] + "'>" +
			"	<label class='form-check-label'>" + lob_list[i] + "</label>" + 
			"</div>"
		);
	}
}
