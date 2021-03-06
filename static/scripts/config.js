// By default, the hierarchy view will or will not show branches.
// if HIERARCHY_IGNORE_BRANCHES = true, branches will NOT be shown;
// otherwise, branches will be shown by default.
var HIERARCHY_IGNORE_BRANCHES = true;


// By default, show virtual node in hierarchy view
var HIERARCHY_SHOW_VIRTUAL_NODE = true;


// default colors
var NODE_COLOR = {
	"virtual": "#d3d3d3", 	// lightgray
	"root": "#926757",		// brown
	"branch": "#8fbc8f",	// darkgreen
	"subsidiary": "#4682b4"	// steelblue
}


// Sibling Definition
var DIGITS = 4;				// number of SIC digits 
var LOGIC = 'OR';
var MAX_NUM = 30;			// to ensure front-end performance



