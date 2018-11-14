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


@app.route("/api/get_hierarchy_data/<message>", methods=["GET"])
def get_hierarchy_data(message):
    message_dict = json.loads(message)
    ignore_branches = message_dict["ignore_branches"]
    try:
        return json.dumps(entity_model.get_json_tree(ignore_branches=ignore_branches))
    except:
        return "NO_DATA"


@app.route("/api/get_map_data/<message>", methods=["GET"])
def get_map_data(message):
    message_dict = json.loads(message)
    duns = message_dict['id']
    try:
        return json.dumps(entity_model.get_gps(duns))
    except:
        return "NO_DATA"


if __name__ == "__main__":
    app.run(debug=True)
