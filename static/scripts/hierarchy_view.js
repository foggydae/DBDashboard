/* implemented based on Rob Schmuecker's DNDTree Demo */

// global variables for hierarchy view
var maxLabelLength, maxValue, duration, root;
var diagonal, treeLayout;
var zoomListener, baseSvg, svgGroup;

var init_hierarchy_view = function () {
    maxLabelLength = 0; 
    maxValue = 0;
    duration = 750;

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

    load_hierarchy_view(ignore_branches=HIERARCHY_IGNORE_BRANCHES);
}

var load_hierarchy_view = function (ignore_branches=true) {
    var message = JSON.stringify({
        ignore_branches: ignore_branches
    });
    $.get("/api/get_hierarchy_data/" + message, function (rtnString) {
        if (rtnString == "NO_DATA") {
            console.log("Error", "Failed in hierarchy data.");
        }
        else {
            var treeData = JSON.parse(rtnString);
            console.log(treeData);
        
            // Call _visit function to establish maxLabelLength
            _visit(treeData, 
                function(d) {
                    maxLabelLength = Math.max(d.name.length, maxLabelLength);
                    maxValue = Math.max(Math.log(+d.revenue + 1), maxValue);
                }, 
                function(d) {
                    return d.children && d.children.length > 0 ? d.children : null;
                });

            // Define the root
            root = treeData;

            update_hierarchy_view(root);
            // Layout the tree initially and center on the root node.
            center_node(root["children"][0]);
        }
    });

}

var update_hierarchy_view = function (source) {

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
    tree = treeLayout.size([newHeight, viewerWidth]);

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
    node = svgGroup.selectAll("g.node")
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
        .attr("r", 0)
        .style("stroke", function(d) {
            return d.type == "3" ? "steelblue" : "darkseagreen";
        })
        .style("fill", function(d) {
            return d._children ? "orange" : d.type == "3" ? "steelblue" : "darkseagreen";
        })
        .style("fill-opacity", _getOpacity)
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
        .attr("r", function(d) { return Math.sqrt(Math.sqrt(+d.size)) * 2 + 4; })
        .style("fill", function(d) {
            return d._children ? "orange" : d.type == "3" ? "steelblue" : "darkseagreen";
        })
        .style("fill-opacity", _getOpacity);

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
var center_node = function (source) {
    scale = zoomListener.scale();
    x = -source.y0;
    y = -source.x0;
    x = x * scale + 10;
    y = y * scale + baseSvg.attr("height") / 2;
    d3.select('g').transition()
        .duration(duration)
        .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
    zoomListener.scale(scale);
    zoomListener.translate([x, y]);
}

// A recursive helper function for performing some setup by walking through all nodes
var _visit = function (parent, visitFn, childrenFn) {
    if (!parent) return;
    visitFn(parent);
    var children = childrenFn(parent);
    if (children) {
        var count = children.length;
        for (var i = 0; i < count; i++) {
            _visit(children[i], visitFn, childrenFn);
        }
    }
}

var _getOpacity = function (d) {
    return Math.log(+d.revenue + 1) / maxValue * 0.9 + 0.1;
}

var _mouseover = function (d) {
    $("#hierarchy-info-name").html(d.name);
    $("#hierarchy-info-location").html(d.location);
    $("#hierarchy-info-address").html(d.address);
    $("#hierarchy-info-SIC").html(d.SIC);
    $("#hierarchy-info-lastUpdate").html(d.lastUpdate);
    $("#hierarchy-info-completeness").html(d.Completeness);
    $("#hierarchy-info-hierarchy").html(d.level);
    $("#hierarchy-info").css("display", "unset");
}

var _mouseout = function (d) {

}

// Toggle children on click.
var _click_node = function (d) {
    if (d3.event.defaultPrevented) return; // click suppressed
    d = _toggleChildren(d);
    update_hierarchy_view(d);
    center_node(d);
}

// Toggle children function
var _toggleChildren = function (d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    return d;
}

var _click_name = function (d) {
    console.log("click on " + d.name);
    $(".selectedText").removeClass('selectedText');
    $(this).addClass('selectedText');
}

var _hide_virtual_node = function (d) {
    if (HIERARCHY_SHOW_VIRTUAL_NODE && d.PARENT_DUNS.startsWith("Virtual")) {
        return "none";
    }
    return "unset";
}

var _hide_virtual_link = function (d) {
    if (HIERARCHY_SHOW_VIRTUAL_NODE && (d.source.PARENT_DUNS.startsWith("Virtual") || d.target.PARENT_DUNS.startsWith("Virtual"))) {
        return "none";
    }
    return "unset";
}


