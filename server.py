from flask import Flask, request, render_template
import json
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=['GET'])
def Index():
	return render_template("upload.html")


@app.route("/api/load_file", methods=["POST", "GET"])
def load_file():
	if request.method == 'POST':
		file = request.files["myfile"]
		print(file)
	return render_template("dashboard.html", filename=file.filename)


@app.route("/api/get_hierarchy_data", methods=["GET"])
def get_hierarchy_data():
	try:
		with open("./dataset/gen_data/parental_tree_wo_branches.json", "r") as f:
			json_tree = f.read()
		return json_tree
	except:
		return "NO_DATA"


@app.route("/api/get_map_data/<message>", methods=["GET"])
def get_map_data(message):
	pass


if __name__=="__main__":
	app.run(debug=True)
