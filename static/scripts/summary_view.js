'use strict';

var init_summary_view = function () {
	$("#summary-button").on("click", function () {
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

    $.get("/api/get_summary_data", function (rtnString) {
        if (rtnString == "NO_DATA") {
            console.log("Error", "Failed in summary data.");
        } else {
            var summaryDict = JSON.parse(rtnString);
			generate_table(summaryDict["global_ultimate_list"], $("#global-parents-table"));
			generate_table(summaryDict["pnid_list"], $("#pnid-entities-table"));
			generate_table(summaryDict["metadata_list"], $("#metadata-table"));
			update_count(summaryDict["count_dict"]);
			$("#company-name").html(summaryDict["filename"]);
        }
    });
}

var generate_table = function (dataset, table) {
	var thead_content = "<tr>";
	var tbody_content = "";
	var init_flag = true;
	for (var i = 0; i < dataset.length; i++) {
		tbody_content += "<tr>";
		for (var key in dataset[i]) {
			if (dataset[i][key]["status"] == "yes") {
				tbody_content += "<td class='error-in-table'>" + dataset[i][key]["value"] + "</td>";
			} else {
				tbody_content += "<td>" + dataset[i][key]["value"] + "</td>";
			}
		}
		tbody_content += "</tr>";
		if (init_flag) {
			for (var key in dataset[i]) {
			    thead_content += "<th>" + key + "</th>";
			}
			thead_content += "</tr>";
			init_flag = false;
		}
	}
	table.children("thead").empty().html(thead_content);
	table.children("tbody").empty().html(tbody_content);
}

var update_count = function (count_dict) {
	$("#company-source-count").html(count_dict.total);
	$("#non-branch-count").html(count_dict.non_branch);
	$("#branch-count").html(count_dict.branch);
	$("#total-count").html(count_dict.total);
	$("#root-count").html(count_dict.root);
	$("#in-tree-count").html(count_dict.in_tree);
	$("#pnid-count").html(count_dict.pnid);
	$("#out-tree-count").html(count_dict.out_tree);
}
