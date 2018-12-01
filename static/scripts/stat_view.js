'use strict';

var init_stat_view = function () {
    $.get("/api/get_stat_data", function (rtn_string) {
        if (rtn_string == "NO_DATA") {
            console.log("Error", "Failed in stat data.");
        } else {
            var stat_data = JSON.parse(rtn_string);
			draw_stat_view(stat_data);
        }
    });	

	$("#summary-button-2").on("click", function () {
		if ($("#summary-container").css("display") == "none") {
			$("#main-container").css("display", "none");
			$("#summary-container").css("display", "block");
			$("#summary-button").html("Dashboard");
		} else {
			$("#main-container").css("display", "flex");
			$("#summary-container").css("display", "none");
			$("#summary-button").html("Summary");
		}
	})
}


var draw_stat_view = function (stat_data) {
	$("#stat-company-name").html(stat_data["filename"]);
	$("#stat-total-count").html(stat_data["total"]);
	$("#stat-root-subs-count").html(stat_data["non_branch"]);
	$("#stat-branch-count").html(stat_data["branch"]);
	$("#stat-root-count").html(stat_data["root"]);
	$("#stat-in-tree-count").html(stat_data["in_tree"]);
	$("#stat-pnid-count").html(stat_data["pnid"]);
	$("#stat-out-tree-count").html(stat_data["out_tree"]);
	$("#stat-max-hierarchy").html(stat_data["max_hierarchy"]);
	$("#stat-global-ultimate-count").html(stat_data["global_ultimates"]);
	$("#stat-missing-global-count").html(stat_data["missing_ultimates"]);
	$("#stat-total-revenue").html("$" + stat_data["root_revenue"].toLocaleString());
	$("#stat-total-emp").html(stat_data["root_emp"].toLocaleString());
}
