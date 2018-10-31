// 这一文件主要是操作栏（输入输出、下面显示线路）的逻辑，实际上只是给查询按钮设定相应的逻辑
function draw_action_window () {

	// 为操作栏下方的div设定固定的高度，使其在显示路径时，如果条数过多，不会溢出，而是使用滚轮上下滑（css中设置的）
	$("#table-container").height($("#action-window").height() - $("#form-container").height() - 81)

	// 当button被点击的时候发生的事儿
	$(".log-btn").on("click", function(){
		// 获得输入
		var startStationName = $("#form-start-station").val();
		var endStationName = $("#form-end-station").val();
		// 检查输入内容是否为空
		if (startStationName == "" || endStationName == "") {
			$("#input-instruction")
				.css("display", "block")
				.text("起止站点不得为空");
			$("#traj-table>tbody").empty();
		}
		else { // 不为空的情况
			// 开始查询，先改变输入提示，以防查询时间太长（虽然理论上不会发生）
			$("#input-instruction")
				.css("display", "block")
				.text("查询中……");

			// 传回后端的查询参数
			var message = JSON.stringify({
				startName: startStationName,
				endName: endStationName
			});
			// 向后端请求与输入的起止站点名称对应的换乘路径
			$.ajax({
				type: "POST",
				url: "/query_trajectory/" + message,
				// 当成功收到后端返回的数据时
				success: function (rtnString) {
					// 后端返回报错（约定报错字段为“NO_DATA”）
					if (rtnString == "NO_DATA") {
						console.log("Error", "Failed in requesting station information.");
					}
					// 后端返回说明，输入的站点有问题，在数据库中找不到这个名字
					else if (rtnString == 'WRONG_INPUT') {
						// 相应地更改输入指南
						$("#input-instruction")
							.css("display", "block")
							.text("起止站点填写有误，请修改后重新查询");
						$("#traj-table>tbody").empty();
					}
					else { // 后端正常返回
						// 从后端返回值中获得路径数据，后端返回的本来是一个字符串化的json
						var rtnDict = JSON.parse(rtnString);
						traj_list = rtnDict['station_list'];
						// 因为要开始在输入栏下面显示路径信息了，所以把输入指南隐藏掉
						$("#input-instruction")
							.css("display", "none");
						$("#traj-table>tbody").empty();
						tuqiaoCellR = d3.select("#station9713").attr("r");
						ciquCellR = d3.select("#station9645").attr("r");
						suzhuangCellR = d3.select("#station9541").attr("r");
						// 还原地图上的所有站点的圆的大小
						curCellR = Math.min(tuqiaoCellR, suzhuangCellR, ciquCellR);
						d3.selectAll(".circle")
							.attr("r", curCellR)
							.style("stroke-width", "0px")
							.style("stroke", "none");
						console.log(curCellR)

						// 对于返回的路径信息中的每个站，在显示栏中显示（table加一行）
						for (var i = 0; i < traj_list.length; i++) {
							// 因为jQuery的append是直接加html代码，所以这里先用字符串的形式准备好要加的代码
							var stationItem = "<tr><td class='color-rect'><div style='background-color:";
							// 这是每一排中的第一个色块，代表地铁线路的颜色，返回的数据中有颜色信息
							stationItem += traj_list[i][2];
							stationItem += ";'></div></td><td class='station-name'><span>";
							// 如果返回的数据中显示这是换乘站，那么加粗，否则不加粗
							if (traj_list[i][1] != 1)
								stationItem += traj_list[i][0];
							else
								stationItem += "<strong>" + traj_list[i][0] + "</strong>";
							stationItem += "</span></td></tr>";
							// 用jquery append这一个站的信息
							$("#traj-table>tbody")
								.append(stationItem);
							
							// 在地图上将这些站台的圈圈变大
							d3.select("#station" + traj_list[i][3])
								.attr("r", 5 * curCellR)
								.style("stroke-width", "2px")
								.style("stroke", traj_list[i][2]);
						};
					}
				}
			});
		}
	})
}
