import csv
import json
import re
import math
import time
import datetime
from flask import Flask

app = Flask(__name__)


@app.route("/")
def Index():
	return app.send_static_file("index.html")


@app.route("/api/get_hierarchy_data/<message>", methods=["get", "post"])
# get stations' both basic info(name\ID\color\...)
def ini_station (message):
	messageDict = json.loads(message)
	curCity = messageDict['city']
	try:
		rtnData = {
			'basic_info': {},
			'line_info': []
		}
		rtnData['basic_info'], rtnData['line_info'] = get_basic_station_info(curCity)
		return json.dumps(rtnData)
	except:
		return "NO_DATA"


if __name__=="__main__":
	app.run(debug=True)
