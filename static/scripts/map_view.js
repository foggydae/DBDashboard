
var init_map_view = function () {
	// global variables for hierarchy view
	var latlng = {
		United_State: [39.8283, -98.5795],
	};
	var zoom = {
		United_State: 4,
	};
	var globalCurCity = "United_State";

	// put map to map-canvas
	var map = L.map("map-canvas").setView(latlng[globalCurCity], zoom[globalCurCity]);
	var baseMapLayer_light = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
		attribution: ''
	});
	// another version of the map
	var baseMapLayer_standard = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		attribution: ''
	});
	// load the map
	baseMapLayer_light.addTo(map);
	// baseMapLayer_standard.addTo(map);	
}

var draw_map_view = function () {
	
}