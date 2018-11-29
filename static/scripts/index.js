'use strict';

/********************
 * Global Variables *
 ********************/
// hierarchy view's root dataset
var root;

init_hierarchy_view();
init_map_view();
init_summary_view();

$(window).resize(function () { // additional listener for size-responsiblility of certain views
	// update hierarchy view
    update_hierarchy_view(root);
});

