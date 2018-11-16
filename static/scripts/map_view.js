var map;
var marker_dict, maxValue;
var entities, branches, controller, baseMaps;

var init_map_view = function () {
	var baseMapLayer_light = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
		id: "light",
		attribution: ""
	});
	var baseMapLayer_standard = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		id: "standard",
		attribution: ""
	});
	baseMaps = {
	    "light": baseMapLayer_light,
	    "standard": baseMapLayer_standard
	};

	// put map to map-canvas
	map = L.map("map-canvas").setView([39.8283, -98.5795], 4);
	// load the map
	baseMapLayer_light.addTo(map);

	// init map with data
	var message = JSON.stringify({
		select_entity: "ALL"
	});
	$.get("/api/get_map_data/" + message, function (rtn_string) {
		if (rtn_string == "NO_DATA") {
			console.log("Error", "Failed in map data.");
		} else {
			var map_data = JSON.parse(rtn_string);
			marker_dict = {};
			maxValue = 0;
			for (var key in map_data) {
			    maxValue = Math.max(Math.log(+map_data[key]["revenue"] + 1), maxValue);
			}
			init_marker_dict(map_data);
			var new_layers = get_entity_group(map_data);
			entities = new_layers[0];
			branches = new_layers[1];
			entities.addTo(map);
			branches.addTo(map);

			var overlayMaps = {
			    "entities": entities,
			    "branches": branches
			};
			controller = L.control.layers(baseMaps, overlayMaps);
			controller.addTo(map);
		}
	});
}

var init_marker_dict = function (map_data) {
	for (var key in map_data) {
		marker_dict[key] = L.circleMarker(
				[
					+map_data[key]["latitude"], 
					+map_data[key]["longitude"]
				], 
				{
					id: key,
					weight: 1,
					fill: true,
					radius: _get_radius(+map_data[key]["size"]),
					color: _get_colors(map_data[key]["type"]),
					fillColor: _get_colors(map_data[key]["type"]),
					fillOpacity: _get_opacity(map_data[key]["revenue"])
				}
			)
			.bindPopup(
				"<span class='info-header'>Name: </span><span>" + map_data[key]["name"] + "</span>"
			)
			.on("mouseover", function(d) {
				this.openPopup();
			})
			.on("mouseout", function(d) {
				this.closePopup();
			})
			.on("click", function(d) {
				center_node(d.target.options.id);
			});
	}
}

var get_entity_group = function (map_data) {
	var new_entities = L.layerGroup(), 
		new_branches = L.layerGroup();
	for (var key in map_data) {
		if (map_data[key]["type"] == "branch") {
			new_branches.addLayer(marker_dict[key]);
		} else {
			new_entities.addLayer(marker_dict[key]);
		}
	}
	return [new_entities, new_branches];
}

var update_map_view = function (duns) {
	// init map with data
	var message = JSON.stringify({
		select_entity: duns
	});
	$.get("/api/get_map_data/" + message, function (rtn_string) {
		if (rtn_string == "NO_DATA") {
			console.log("Error", "Failed in map data.");
		} else {
			var map_data = JSON.parse(rtn_string);
			var new_layers = get_entity_group(map_data);
			entities.remove();
			branches.remove();
			controller.remove();

			entities = new_layers[0];
			branches = new_layers[1];
			entities.addTo(map);
			branches.addTo(map);

			var overlayMaps = {
			    "entities": entities,
			    "branches": branches
			};
			controller = L.control.layers(baseMaps, overlayMaps);
			controller.addTo(map);
		}
	});

}

var _get_colors = function (type) {
    return NODE_COLOR[type];
}

var _get_radius = function (size) {
    return Math.sqrt(Math.sqrt(size)) * 2 + 4;
}

var _get_opacity = function (revenue) {
    return Math.log(+revenue + 1) / maxValue * 0.9 + 0.1;
}
