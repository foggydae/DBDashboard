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
	print('[LOG] init dashboard')
	return app.send_static_file("index.html")


@app.route("/api/get_hierarchy_data", methods=["get"])
# get stations' both basic info(name\ID\color\...)
def get_hierarchy_data ():
	print('[LOG] get hierarchy data request')
	try:
		with open("./dataset/gen_data/parental_tree_wo_branches.json", "r") as f:
			json_tree = f.read()
		return json_tree
	except:
		return "NO_DATA"


@app.route("/api/get_map_data/<message>", methods=["get"])
def get_map_data(message):
	print('[LOG] get map data request')
	pass

if __name__=="__main__":
	app.run(debug=True)
