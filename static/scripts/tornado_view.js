'use strict';

var HEAD_HEIGHT = 50;
var BODY_HEIGHT = 36;
var y_scale, rev_scale, emp_scale;


var init_tornado_view = function() {
    $("#tornado-logic-input").val(LOGIC);
    $("#tornado-digit-input").val(DIGITS);
    update_tornado_view("INIT");
    $("#tornado-update-button").on("click", function () {
        var tmp_logic = $("#tornado-logic-input").val();
        var tmp_digit = +$("#tornado-digit-input").val();
        if (tmp_logic != "OR" && tmp_logic != "AND") {
            $("#tornado-logic-input").css("color", "red");
        } else if (tmp_digit > 6 || tmp_digit < 0) {
            $("#tornado-digit-input").css("color", "red");
        } else {
            $("#tornado-logic-input").css("color", "black");
            $("#tornado-digit-input").css("color", "black");
            LOGIC = tmp_logic;
            DIGITS = tmp_digit;
            if (recommend_flag) {
                update_recommendation(cur_selected_duns);
            } else {
                update_tornado_view(cur_selected_duns);
            }
        }
    })
}


var update_tornado_view = function(duns_id) {
    var message = JSON.stringify({
        selected_duns: duns_id,
        digits: DIGITS,
        logic: LOGIC,
        max_num: MAX_NUM 
    });
    $.get("/api/get_SIC_sibling/" + message, function (rtn_string) {
        if (rtn_string == "NO_DATA") {
            console.log("Error", "Failed in tornado data.");
        } else {
            var init_data = JSON.parse(rtn_string);
            cur_tornado_data = init_data;
            draw_tornado_view(cur_tornado_data); 
        }
    }); 
}


var draw_tornado_view = function(data) {
    var max_revenue = 0, 
        max_num_emp = 0,
        min_revenue = Number.MAX_SAFE_INTEGER,
        min_num_emp = Number.MAX_SAFE_INTEGER;
    data.forEach(function (element) {
        element["revenue"] = +element["revenue"];
        element["empNum"] = +element["empNum"];
        max_revenue = Math.max(max_revenue, element["revenue"]);
        max_num_emp = Math.max(max_num_emp, element["empNum"]);
        min_revenue = Math.min(min_revenue, element["revenue"]);
        min_num_emp = Math.min(min_num_emp, element["empNum"]);
        element["color"] = NODE_COLOR[element["type"]];
    });

    y_scale = d3.scale.ordinal()
        .domain([0]);
    rev_scale = d3.scale.log()
        .base(Math.E)
        .domain([min_revenue+1, max_revenue+1]);
    emp_scale = d3.scale.linear()
        .domain([min_num_emp, max_num_emp]);

    // update the head (the selected entity)
    draw_tornado_name(data[0], 0);
    draw_tornado_chart("#tornado-head-chart-div", data[0], y_scale, rev_scale, emp_scale, true);

    $("#tornado-body-container").empty();
    $("#tornado-body-container").css("max-height", $("#tornado-container").height() - $("#tornado-head-container").height() - $("#tornado-control").height() - 13);
    for (var i = 1; i < data.length; i++) {
        var cur_data = data[i];
        var new_element = "<div class='tornado-base-container tornado-siblings'>" +
            "<div id='tornado-" + i + "-name-div' class='col-sm-5 tornado-name'>" + 
            "<span id='tornado-" + i + "-name'></span>" +
            "</div>" + 
            "<div id='tornado-" + i + "-chart-div' class='col-sm-7'></div>"
            "</div>";
        $("#tornado-body-container").append(new_element);
        draw_tornado_name(data[i], i);
        draw_tornado_chart("#tornado-" + i + "-chart-div", data[i], y_scale, rev_scale, emp_scale);
    }
}


var draw_tornado_name = function (data, index) {
    var selector = "#tornado-" + index + "-name";
    if (index == 0) {
        selector = "#tornado-head-name";
    }
    $(selector).off("click");
    $(selector).html(data["location"] + "</br><strong>" + data["name"] + "</strong>")
        .css("cursor", "click");
    $(selector + "-div")
        .removeClass("tornado-branch tornado-root tornado-subsidiary")
        .addClass("tornado-" + data["type"])
        .on("click", function () {
            center_node(data["id"], true);
            // console.log(data["id"]);
        });
}


var draw_tornado_chart = function (divID, data, y_scale, rev_scale, emp_scale, head=false) {
    // get current size of the svg
    var cur_width, cur_height;
    cur_width = $(divID).width();
    if (head) {
        cur_height = HEAD_HEIGHT;
    } else {
        cur_height = BODY_HEIGHT;
    }

    var trans_data = [
        {"value": data["revenue"], "type": "revenue", "id": data["id"]},
        {"value": data["empNum"], "type": "empNum",  "id": data["id"]}
    ]

    // update the scale
    y_scale.rangeRoundBands([0, cur_height]);
    rev_scale.range([3, cur_width/2-5]);
    emp_scale.range([3, cur_width/2-5]);

    // generate the svg
    $(divID).empty();
    var tornado_svg = d3.select(divID).append("svg")
        .attr("id", "tornado-head-svg")
        .attr("width", cur_width)
        .attr("height", cur_height)
        .append("g")
        .selectAll(".bar")
        .data(trans_data);

    tornado_svg.enter()
        .append("rect")
        .attr("class", function (d) {
            return "bar tornado-bar tornado-bar-" + d.type;
        })
        .attr("x", function (d) {
            if (d.type == "revenue") {
                return cur_width / 2 - rev_scale(d.value + 1) - 1;
            } else {
                return cur_width / 2;
            }
        })
        .attr("y", cur_height / 2 - 15)
        .attr("width", function(d) {
            if (d.type == "revenue") {
                return rev_scale(d.value + 1);
            } else {
                return emp_scale(d.value);
            }
        })
        .attr("height", 30)
        .on("click", function (d) {
            center_node(data["id"], true);
        });

    tornado_svg.enter()
        .append("text")
        .attr("class", "tornado-chart-text")
        .attr("text-anchor", function (d) {
            if (d.type == "revenue") {
                return "end";
            } else {
                return "start";
            }
        })
        .attr("x", cur_width / 2)
        .attr("y", cur_height / 2 - 15)
        .attr("dx", function (d) {
            if (d.type == "revenue") {
                return -4;
            } else {
                return 3;
            }
        })
        .attr("dy", 20)
        .text(function (d) {
            var number = +d.value;
            if (d.type == "revenue") {
                return "$" + number.toLocaleString();
            } else {
                return number.toLocaleString();
            }
        })
        .on("click", function (d) {
            center_node(data["id"], true);
        });
}
