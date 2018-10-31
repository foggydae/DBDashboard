// 这一文件主要是地图部分在地图上画线路图的逻辑
var stationList = [];
var lineList = [];

// 在地图上画线路图的函数
function draw_station_layer (curMap) {

	// 利用d3SvgOverlay库来在leaflet的地图上画东西
	var station_layer = L.d3SvgOverlay(function (selection, projection) {

		selection.attr("id", "station_layer");

		// 具体执行画线路的函数，用于在异步请求站台数据之后调用。画线使用了d3.js库，专门用来画可视化，比较方便
		function draw_station (stationList, lineList) {

			// 定义线的画法，cardinal插值保证了线路看起来比较正常，比折线好
			var line = d3.svg.line()
				.x(function(d) { return projection.latLngToLayerPoint(L.latLng(+d.LATITUDE, +d.LONGITUDE)).x; })
				.y(function(d) { return projection.latLngToLayerPoint(L.latLng(+d.LATITUDE, +d.LONGITUDE)).y; })
				.interpolate("cardinal");

			// 因为地图可能被缩放，所以动态调整线的宽度和地铁站小圆圈的半径大小
			var strokeWidth = 20 / projection.scale;
			if(strokeWidth > 2)
				strokeWidth = 2;
			if(strokeWidth < 0.5)
				strokeWidth = 0.5;
			var cellR = 5 / projection.scale;
			if(strokeWidth == 2)
				cellR = 1;
			if(cellR < 0.2)
				cellR = 0.2;

			// 开始画。首先画线路。首先移除所有可能已经画好的线路
			selection.selectAll(".subwayline").remove();
			// 将线路的数据绑定在一个一个g（group）上，便于之后在每个g内画图
			var lineGs = selection.selectAll(".subwayline")
				.data(lineList).enter()
				.append("g")
				.attr("class", "subwayline");

			// 在每个组（g）内画线，线的数据来自之前绑定的数据，每个g都对应这一个线路，每个线路是一个数组，里面包括各个站点，站点数据中包含gps
			lineGs.append("path")
				.style("stroke", function(d) { return d['COLOR']; })
				.datum(function(d) { return d['PATH']; })
				.style("fill", "none")
				.style("opacity", 0.8)
				.style("stroke-width", strokeWidth)
				.attr("d", line);

			// 在线的基础上画小白圈，表示站点
			lineGs.selectAll('.circle')
				.data(function(d) { return d['PATH']; })
				.enter()
				.append("circle")
				.attr('class', 'circle')
				.attr('id', function(d) {
					return "station" + d['STATION_ID'];
				})
				.attr('cx', function(d) { 
					return projection.latLngToLayerPoint(L.latLng(+d.LATITUDE, +d.LONGITUDE)).x; })
				.attr('cy', function(d) { return projection.latLngToLayerPoint(L.latLng(+d.LATITUDE, +d.LONGITUDE)).y; })
				.attr('r', cellR)
				.attr('fill', "#FFFFFF")
				.attr("stroke", "none");

		}

		// 向后端请求数据
		function get_info_and_draw () {
			// stationList和linelist如果不为空，说明已经请求过数据了，不需要再请求。否则用ajax请求数据：
			if(stationList.length == 0 || lineList.length == 0){
				// 向后端请求数据的参数，其实没啥用
				var message = JSON.stringify({
					city: globalCurCity
				})
				// 请求数据
				$.post("/ini_station/" + message, function (rtnString) {
					if(rtnString == "NO_DATA"){
						console.log("Error", "Failed in requesting station information.");
					}
					else{
						// 获得数据之后，从中提取出站点信息和线路信息，最后其实只用到了线路信息
						var rtnDict = JSON.parse(rtnString);
						var basicStationInfoDict = rtnDict["basic_info"];
						// 将站点信息存入数组（请求到的是一个字典）
						for (var stationName in basicStationInfoDict) {
							var idList = basicStationInfoDict[stationName]['STATION_ID'];
							for (var i = idList.length - 1; i >= 0; i--) {
								var curID = idList[i];
							};
							stationList.push(basicStationInfoDict[stationName]);
						}
						// 线路信息本来就是数组，直接给变量
						lineList = rtnDict['line_info'];
					}
					// 在请求数据成功之后，调用画图的函数
					draw_station(stationList, lineList);
				});
			}
			else{
				draw_station(stationList, lineList);
			}

		}

		get_info_and_draw();
	});

	// d3SvgOverlay语法，将上面定义的画图过程绑定在地图上
	station_layer.addTo(curMap);
}
