'use strict';

/********************
 * Global Variables *
 ********************/

// hierarchy view's root dataset
var root;
// tornado view's current dataset
var cur_tornado_data;
// branch flag for hierarchy and map
var cur_ignore_branch_flag = HIERARCHY_IGNORE_BRANCHES;
// current selected node
var cur_selected_duns;

/********************
 ** Initiate Views **
 ********************/

init_hierarchy_view();
init_map_view();
init_tornado_view();
init_search_view();
init_stat_view();
init_summary_view();

/*********************
 * Manual Responsive *
 *********************/

// additional listener for size-responsiblility of certain views
$(window).resize(function () { 
	// update hierarchy view
    update_hierarchy_view(root);
	draw_tornado_view(cur_tornado_data);
	$("#form-check-container").css("max-height", $("#filter-form").height() - $("#form-keyword-container").height() - $("#form-control-container").height() - 14);
});

