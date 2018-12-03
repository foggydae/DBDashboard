'use strict';
/* implemented based on Rob Schmuecker's DNDTree Demo */

// global variables for hierarchy view
var maxLabelLength, maxValue, duration, idNodeDict;
var diagonal, treeLayout;
var zoomListener, baseSvg, svgGroup;
var defaultCenter = null;

var init_hierarchy_view = function () {
    maxLabelLength = 0; 
    maxValue = 0;
    duration = 750;
    idNodeDict = {};

    // define a d3 diagonal projection for use by the node paths later on.
    diagonal = d3.svg.diagonal()
        .projection(function(d) {
            return [d.y, d.x];
        });
    treeLayout = d3.layout.tree()
        .sort(function(a, b) {
            return b.name.toLowerCase() <= a.name.toLowerCase() ? 1 : -1;
        });

    // define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleExtents
    zoomListener = d3.behavior.zoom().scaleExtent([0.1, 3]).on("zoom", function () {
        svgGroup.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    });
    // define the baseSvg, attaching a class for styling and the zoomListener
    baseSvg = d3.select("#hierarchy-container").append("svg")
        .attr("class", "overlay")
        .call(zoomListener);
    // Append a group which holds all nodes and which the zoom Listener can act upon.
    svgGroup = baseSvg.append("g");

    _init_hierarchy_control();
    _load_hierarchy_view(cur_ignore_branch_flag, true);
}

var _load_hierarchy_view = function (ignore_branches=true, centering=false) {
    var message = JSON.stringify({
        ignore_branches: ignore_branches
    });
    $.get("/api/get_hierarchy_data/" + message, function (rtnString) {
        if (rtnString == "NO_DATA") {
            console.log("Error", "Failed in hierarchy data.");
        } else {
            var treeData = JSON.parse(rtnString);

            // Call _visit function to establish maxLabelLength
            _visit(treeData);
            // Define the root
            root = treeData;
            if (defaultCenter == null || typeof defaultCenter != "string") {
                defaultCenter = root["children"][0];
            }
            update_hierarchy_view(root);
            if (centering) {
                center_node(defaultCenter, false);
            }
        }
    });
}

var update_hierarchy_view = function (source) {

    if (typeof source == "string") {
        source = idNodeDict[source];
    }

    // size of the diagram
    var viewerWidth = $("#hierarchy-container").width();
    var viewerHeight = $("#hierarchy-container").height();
    root.x0 = viewerHeight / 2;
    root.y0 = 0;
    baseSvg.attr("width", viewerWidth)
        .attr("height", viewerHeight);

    // Compute the new height, function counts total children of root node and sets tree height accordingly.
    // This prevents the layout looking squashed when new nodes are made visible or looking sparse when nodes are removed
    // This makes the layout more consistent.
    var levelWidth = [1];
    var childCount = function(level, n) {
        if (n.children && n.children.length > 0) {
            if (levelWidth.length <= level + 1) levelWidth.push(0);
            levelWidth[level + 1] += n.children.length;
            n.children.forEach(function(d) {
                childCount(level + 1, d);
            });
        }
    };

    childCount(0, root);
    var newHeight = d3.max(levelWidth) * 35; // 25 pixels per line  
    var tree = treeLayout.size([newHeight, viewerWidth]);

    // Compute the new tree layout.
    var nodes = tree.nodes(root).reverse(),
        links = tree.links(nodes);

    // Set widths between levels based on maxLabelLength.
    nodes.forEach(function(d) {
        d.y = (d.depth * (maxLabelLength * 4)); //maxLabelLength * 10px
        // alternatively to keep a fixed scale one can set a fixed depth per level
        // Normalize for fixed-depth by commenting out below line
        // d.y = (d.depth * 500); //500px per level.
    });

    // Update the nodes…
    var node = svgGroup.selectAll("g.node")
        .data(nodes, function(d) {
            return d.id || (d.id = ++i);
        });

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("g")
        // .call(dragListener)
        .attr("class", "node")
        .attr("transform", function(d) {
            return "translate(" + source.y0 + "," + source.x0 + ")";
        })
        .style("display", _hide_virtual_node);

    nodeEnter.append("circle")
        .attr('class', 'nodeCircle')
        .attr("id", function(d) {
            return "circle" + d.id;
        })
        .attr("r", 0)
        .style("stroke", _get_node_color)
        .style("fill", _get_node_color)
        .style("fill-opacity", _get_node_opacity)
        .on("mouseover", _mouseover)
        .on("mouseout", _mouseout)
        .on('click', _click_node);

    nodeEnter.append("text")
        .attr("x", function(d) {
            return 14;
            // return d.children || d._children ? -10 : 10;
        })
        .attr("dy", ".35em")
        .attr('class', 'nodeText')
        .attr("id", function(d) {
            return "text" + d.id;
        })
        .attr("text-anchor", function(d) {
            return "start";
            // return d.children || d._children ? "end" : "start";
        })
        .text(function(d) {
            return d.name;
        })
        .style("fill-opacity", 0)
        .on("mouseover", _mouseover)
        .on("mouseout", _mouseout)
        .on("click", _click_name);

    // Update the text to reflect whether node has children or not.
    node.select('text')
        .attr("x", function(d) {
            return 14;
            // return d.children || d._children ? -10 : 10;
        })
        .attr("text-anchor", function(d) {
            return "start";
            // return d.children || d._children ? "end" : "start";
        })
        .text(function(d) {
            return d.name;
        });

    // Change the circle fill depending on whether it has children and is collapsed
    node.select("circle.nodeCircle")
        .attr("r", _get_node_size)
        .style("fill", _get_node_color)
        .style("fill-opacity", _get_node_opacity);

    // Transition nodes to their new position.
    var nodeUpdate = node.transition()
        .duration(duration)
        .attr("transform", function(d) {
            return "translate(" + d.y + "," + d.x + ")";
        });

    // Fade the text in
    nodeUpdate.select("text")
        .style("fill-opacity", 1);

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) {
            return "translate(" + source.y + "," + source.x + ")";
        })
        .remove();

    nodeExit.select("circle")
        .attr("r", 0);

    nodeExit.select("text")
        .style("fill-opacity", 0);

    // Update the links…
    var link = svgGroup.selectAll("path.link")
        .data(links, function(d) {
            return d.target.id;
        });

    // Enter any new links at the parent's previous position.
    link.enter().insert("path", "g")
        .attr("class", "link")
        .attr("d", function(d) {
            var o = {
                x: source.x0,
                y: source.y0
            };
            return diagonal({
                source: o,
                target: o
            });
        })
        .style("display", _hide_virtual_link);

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function(d) {
            var o = {
                x: source.x,
                y: source.y
            };
            return diagonal({
                source: o,
                target: o
            });
        })
        .remove();

    // Stash the old positions for transition.
    nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

// Function to center node when clicked/dropped so node doesn't get lost when collapsing/moving with large amount of children.
var center_node = function (source, with_highlight) {
    if (typeof source == "string") {
        source = idNodeDict[source];
    }
    var scale = zoomListener.scale();
    var x = -source.y0;
    var y = -source.x0;
    if (with_highlight) {
        x = x * scale + baseSvg.attr("width") / 2;
        highlight_node(source.id);
    } else {
        x = x * scale + 20;
    }
    y = y * scale + baseSvg.attr("height") / 2;
    d3.select('g').transition()
        .duration(duration)
        .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
    zoomListener.scale(scale);
    zoomListener.translate([x, y]);
}

var highlight_node = function (duns_id) {
    $(".highlight-text").removeClass("highlight-text");
    $("#text" + duns_id).addClass("highlight-text");
    update_hierarchy_info(idNodeDict[duns_id]);
}

var update_hierarchy_info = function (d) {
    $("#hierarchy-info-name").html(d.name);
    $("#hierarchy-info-location").html(d.location);
    $("#hierarchy-info-address").html(d.address);
    $("#hierarchy-info-SIC").html(d.SIC);
    $("#hierarchy-info-lastUpdate").html(d.lastUpdate);
    $("#hierarchy-info-completeness").html(d.Completeness);
    $("#hierarchy-info-hierarchy").html(d.level);
    $("#hierarchy-info-revenue").html(d.revenue);
    $("#hierarchy-info").css("display", "inline-block");
}

var _init_hierarchy_control = function () {
    if (cur_ignore_branch_flag) {
        $("#hierarchy-branch-btn").html("Branches");
    } else {
        $("#hierarchy-branch-btn").html("NoBranch");
    }

    $("#hierarchy-unselect-btn").on("click", function () {
        defaultCenter = root["children"][0];
        $(".highlight-text").removeClass("highlight-text");
        $(".selected-text").removeClass("selected-text");
        update_map_view("ALL");
        center_node(defaultCenter, false);
        $("#hierarchy-info").css("display", "none");                
    });
    $("#hierarchy-branch-btn").on("click", function () {
        // current status is ignoring branches
        if (cur_ignore_branch_flag) {
            $("#hierarchy-branch-btn").html("NoBranch");
            _load_hierarchy_view(false, true);
            cur_ignore_branch_flag = false;
        } else {
            $("#hierarchy-branch-btn").html("Branches");
            _load_hierarchy_view(true, true);
            cur_ignore_branch_flag = true;
        }
    });
}

// A recursive helper function for performing some setup by walking through all nodes
var _visit = function (node) {
    if (!node) return;

    maxLabelLength = Math.max(node.name.length, maxLabelLength);
    maxValue = Math.max(Math.log(+node.revenue + 1), maxValue);
    idNodeDict[node.id] = node;

    var children = node.children && node.children.length > 0 ? node.children : null;
    if (children) {
        var count = children.length;
        for (var i = 0; i < count; i++) {
            _visit(children[i]);
        }
    }
}

var _mouseover = function (d) {
    update_hierarchy_info(d);
}

var _mouseout = function (d) {
    // $("#hierarchy-info").css("display", "none");
}

// Toggle children on click.
var _click_node = function (d) {
    if (d3.event.defaultPrevented) return; // click suppressed
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    update_hierarchy_view(d);
    // center_node(d);
}

var _click_name = function (d) {
    $(".highlight-text").removeClass("highlight-text");
    $(".selected-text").removeClass('selected-text');
    $(this).addClass('selected-text');
    defaultCenter = d.id;
    update_map_view(d.id);
    update_tornado_view(d.id);
    center_node(defaultCenter, false);
}

var _get_node_opacity = function (d) {
    return Math.log(+d.revenue + 1) / maxValue * 0.9 + 0.1;
}

var _get_node_color = function (d) {
    return d._children ? "orange" : NODE_COLOR[d.type];
}

var _get_node_size = function (d) {
    // return Math.sqrt(Math.sqrt(+d.size)) * 2 + 4;
    return +d.size;
}

var _hide_virtual_node = function (d) {
    if (d.type == "virtual_root") {
        return "none";
    }
    if (!HIERARCHY_SHOW_VIRTUAL_NODE && d.type == "virtual") {
        return "none";
    }

    return "unset";
}

var _hide_virtual_link = function (d) {
    if (d.source.type == "virtual_root" || d.target.type == "virtual_root") {
        return "none";
    }
    if (!HIERARCHY_SHOW_VIRTUAL_NODE && (d.source.type == "virtual" || d.target.type == "virtual")) {
        return "none";
    }
    return "unset";
}
