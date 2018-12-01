'use strict';

/********************
 * Global Variables *
 ********************/
// hierarchy view's root dataset
var root;
// tornado view's current dataset
var cur_tornado_data;

init_hierarchy_view();
init_map_view();
init_summary_view();
init_tornado_view();

// additional listener for size-responsiblility of certain views
$(window).resize(function () { 
	// update hierarchy view
    update_hierarchy_view(root);
	draw_tornado_view(cur_tornado_data); 
});

