from flask import Flask, request, render_template
from Utils.EntityModel import EntityModel
import json
from datetime import datetime

app = Flask(__name__)
entity_model = EntityModel(verbose=False)

@app.route("/", methods=['GET'])
def Index():
    return render_template("upload.html")


@app.route("/api/load_file", methods=["POST", "GET"])
def load_file():
    if request.method == 'POST':
        global entity_model
        entity_model = EntityModel(verbose=False)
        file = request.files["myfile"]
        entity_model.upload(file)
    return render_template("dashboard.html", filename=file.filename)


@app.route("/api/get_hierarchy_data", methods=["GET"])
def get_hierarchy_data():
    try:
        return json.dumps(entity_model.get_json_tree(ignore_branches=True))
    except:
        return "NO_DATA"


@app.route("/api/get_map_data/<message>", methods=["GET"])
def get_map_data(message):
    pass


if __name__ == "__main__":
    app.run(debug=True)
