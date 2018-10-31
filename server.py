import pymongo
import csv
import json
import re
import math
import time
import datetime
from pprint import pprint
from flask import Flask

app = Flask(__name__)

# global variables, mainly about the database connection
global DB_CONNECT, DB
DB_CONNECT = pymongo.MongoClient("127.0.0.1:20001")
DB = DB_CONNECT['subway']


# assistant function, to make a str into a list. mainly for unifying variables' type.
def generate_ID_list (IDData):
	if type(IDData) == list:
		return IDData
	else:
		return [IDData]


# prepare the dictionary to map station ids to names accordingly
def get_name_2_id_dict ():
	global DB
	name2id_dict = {}
	# using pymongo to get access to the mongoDB(local), and get the station information list
	name2id_list = list(DB['station_info_by_name'].find({}, {'_id': 0, 'STATION_ID': 1, 'STATION_NAME_ZH': 1}))
	# transfer the list into dict
	for i in range(len(name2id_list)):
		name2id_dict[name2id_list[i]["STATION_NAME_ZH"]] = generate_ID_list(name2id_list[i]["STATION_ID"])
	return name2id_dict


# validate the input station name. make sure the name is in the database
def validate_station_name (startName, endName):
	# get the dict to make the validation easier
	name2id_dict = get_name_2_id_dict()
	# any of the input pairs is wrong will cause this function get a False return
	if startName not in name2id_dict:
		return False
	elif endName not in name2id_dict:
		return False
	else:
		return True


# get basic information of stations from the database, such as name and color
def get_basic_station_info (cityName):
	global DB
	# the GPS in the database is slightly different from that of the map using in the front end. here is a bias to make them correct
	longitudeBias = -0.006;
	latitudeBias = -0.0012;
	if cityName == "beijing":
		collection = DB['station_info_by_name']
		# get all the station info entries from database
		stationList = list(collection.find({}, {'_id': 0}))
		station_info = {}
		# update the station gps data with the bias
		for station in stationList:
			station_info[station['STATION_NAME_ZH']] = station
			station_info[station['STATION_NAME_ZH']]['LATITUDE'] += latitudeBias
			station_info[station['STATION_NAME_ZH']]['LONGITUDE'] += longitudeBias
	
		# get line info
		collection = DB['line_info']
		line_info = list(collection.find({}, {'_id': 0}))
		# again, update the gps of stations in the line dataset
		for line in line_info:
			for i in range(len(line["PATH"])):
				line['PATH'][i]["LONGITUDE"] += longitudeBias
				line['PATH'][i]["LATITUDE"] += latitudeBias

		return station_info, line_info
	else:
		print("Sorry:", cityName, " station info is unavailiable for now.")
		return "NO_DATA"


# get transfer plan(trajectory) when start and end station is given. just look it up in the database.
def get_trajectory (startStationName, endStationName):
	global DB
	print(startStationName, endStationName)
	return list(DB['transfer_dict'].find({'START_STATION': startStationName, 'END_STATION': endStationName}, {"_id": 0, "TRAJECTORY": 1}))[0]['TRAJECTORY']


@app.route("/")
def Index():
	return app.send_static_file("index.html")


@app.route("/ini_station/<message>", methods=["get", "post"])
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


@app.route("/query_trajectory/<message>", methods=["get", "post"])
def query_trajectory (message):
	messageDict = json.loads(message)
	startName = messageDict['startName']
	endName = messageDict['endName']
	# check is the input station names is valid in database
	if not validate_station_name(startName, endName):
		return "WRONG_INPUT"
	else:
		try:
			rtnData = {
				'station_list': []
			}
			rtnData['station_list'] = get_trajectory(startName, endName)
			return json.dumps(rtnData)
		except:
			return "NO_DATA"


if __name__=="__main__":
	app.run(debug=True)
