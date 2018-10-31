import json
import pymongo
import re
import datetime
from pprint import pprint

global DATEBASE_ADDRESS, DATABASE_NAME
DATEBASE_ADDRESS = '127.0.0.1:20001'
DATABASE_NAME = 'test'
FILE_PATH = '../SubwayData/'


# generate a transfer trajectory matrix and a transfer distance matrix
def ini_transfer_map ():


	# initialize the transfer matrix, the station list(an according table between a matrix index and a station name)
	def ini_transfer_matrix (stationLinkJson, stationTransJson):
		outputStationList = list(stationLinkJson.keys())
		outputStationList.sort()
		stationNum = len(outputStationList)
		outputDistanceMatrix = [[999 for col in range(stationNum)] for row in range(stationNum)]
		outputTransferMatrix = [[-1 for col in range(stationNum)] for row in range(stationNum)]
		outputTransFlgMatrix = [[-1 for col in range(stationNum)] for row in range(stationNum)]

		# initialize the starting graph by reading transfer information from files
		for i in range(stationNum):
			outputDistanceMatrix[i][i] = 0
			station = outputStationList[i]
			for adjStation in stationLinkJson[station]:
				j = outputStationList.index(adjStation)
				distance = stationLinkJson[station][adjStation]
				if outputDistanceMatrix[i][j] == 999 or outputDistanceMatrix[i][j] == distance:
					outputDistanceMatrix[i][j] = distance
					outputDistanceMatrix[j][i] = distance
				else:
					print("conflict in station link graph, between", station, "and", adjStation)

		for stationA in stationTransJson:
			for stationB in stationTransJson[stationA]:
				i = outputStationList.index(stationA)
				j = outputStationList.index(stationB)
				outputTransFlgMatrix[i][j] = 1

		return outputStationList, outputDistanceMatrix, outputTransferMatrix, outputTransFlgMatrix


	# import transfer graph, stored in json format
	with open(FILE_PATH + "station_linking_graph.json") as jsonLinkFile:
		with open(FILE_PATH + "station_transfer_graph.json") as jsonTransFile:
			stationLinkGraph = json.load(jsonLinkFile)
			stationTransGraph = json.load(jsonTransFile)
			# ini matrix
			stationList, distanceMatrix, transferMatrix, transflgMatrix = ini_transfer_matrix(stationLinkGraph, stationTransGraph)

			# Floyd algorithm
			for k in range(len(stationList)):
				for i in range(len(stationList)):
					for j in range(len(stationList)):
						if distanceMatrix[i][k] < 999 and distanceMatrix[k][j] < 999 and distanceMatrix[i][j] > distanceMatrix[i][k] + distanceMatrix[k][j]:
							distanceMatrix[i][j] = distanceMatrix[i][k] + distanceMatrix[k][j]
							transferMatrix[i][j] = k

	return stationList, distanceMatrix, transferMatrix, transflgMatrix


# restore the path between a OD pair from the transfer trajectory matrix
def get_trajectory (transferMap, stationList, origin, destination):


	# check if each pair of adjacent stations can be reached from each other DIRECTLY
	def check_transfer_station (curTrajectory, transferMap):
		for i in range(len(curTrajectory) - 1):
			if not transferMap[curTrajectory[i]][curTrajectory[i + 1]] == -1:
				return i + 1
		return -1


	if origin not in stationList:
		print("ERROR:" ,origin, "is not in the list.")
		return [origin, destination]
	if destination not in stationList:
		print("ERROR:" ,destination, "is not in the list.")
		return [origin, destination]

	originIndex = stationList.index(origin)
	destinationIndex = stationList.index(destination)
	# ini the trajectory between the OD pairs
	tmpTrajectory = [originIndex, destinationIndex]

	# iteratively check if the current trajectory is smooth(each pair can be linked without pass another station)
	insertIndex = check_transfer_station(tmpTrajectory, transferMap)
	while not insertIndex == -1:
		tmpTrajectory.insert(insertIndex, transferMap[tmpTrajectory[insertIndex - 1]][tmpTrajectory[insertIndex]])
		insertIndex = check_transfer_station(tmpTrajectory, transferMap)
	
	# transform the index of station into the station ID
	outputTrajectory = []
	for stationIndex in tmpTrajectory:
		outputTrajectory.append(stationList[stationIndex])

	return outputTrajectory


# get distance bwtween a OD pair
def get_distance (distanceMatrix, stationList, origin, destination):

	if origin not in stationList:
		print("ERROR:" ,origin, "is not in the list.")
		return -1
	if destination not in stationList:
		print("ERROR:" ,destination, "is not in the list.")
		return -1

	originIndex = stationList.index(origin)
	destinationIndex = stationList.index(destination)

	return distanceMatrix[originIndex][destinationIndex]


# get transfer station list
def get_transfer_station_list (transflgMatrix, stationList, trajectory):

	outputTransStationList = []
	for i in range(len(trajectory) - 1):
		stationA = trajectory[i]
		stationB = trajectory[i + 1]
		if stationA not in stationList:
			print("ERROR:" ,stationA, "is not in the list.")
			return []
		if stationB not in stationList:
			print("ERROR:" ,stationB, "is not in the list.")
			return []
		stationAIndex = stationList.index(stationA)
		stationBIndex = stationList.index(stationB)

		if (not stationA[0:2] == stationB[0:2]) and (transflgMatrix[stationAIndex][stationBIndex] == 1):
			outputTransStationList.append(stationA)
			outputTransStationList.append(stationB)

	outputTransStationList = list(set(outputTransStationList))
	return outputTransStationList


# format the station and line num from database
def format_station_ID (stationNum):
	outputID = str(stationNum)
	if len(outputID) == 1:
		outputID = "0" + outputID
	return outputID


# prepare the dictionary to map station names to ids accordingly
def get_name_2_id_dict ():
	global DATEBASE_ADDRESS, DATABASE_NAME
	name2id_dict = {}
	dbConnect = pymongo.MongoClient(DATEBASE_ADDRESS)
	db = dbConnect[DATABASE_NAME]
	name2id_list = list(db['station_info_by_name'].find({}, {'_id': 0, 'STATION_ID': 1, 'STATION_NAME_ZH': 1}))
	for i in range(len(name2id_list)):
		name2id_dict[name2id_list[i]["STATION_NAME_ZH"]] = generate_ID_list(name2id_list[i]["STATION_ID"])
	return name2id_dict


# prepare the dictionary to map station ids to names accordingly
def get_id_2_name_dict ():
	global DATEBASE_ADDRESS, DATABASE_NAME
	id2name_dict = {}
	dbConnect = pymongo.MongoClient(DATEBASE_ADDRESS)
	db = dbConnect[DATABASE_NAME]
	id2name_list = list(db['station_info_by_id'].find({}, {'_id': 0, 'STATION_ID': 1, 'STATION_NAME_ZH': 1, 'LINE_COLOR': 1}))
	for i in range(len(id2name_list)):
		for curID in generate_ID_list(id2name_list[i]["STATION_ID"]):
			id2name_dict[curID] = (id2name_list[i]["STATION_NAME_ZH"], id2name_list[i]["LINE_COLOR"])
	return id2name_dict


# if the STATION_ID value is a string, transfer it to a list
def generate_ID_list (IDData):
	if type(IDData) == list:
		return IDData
	else:
		return [IDData]


if __name__ == '__main__':
	stationList, distanceMatrix, transferMatrix, transflgMatrix = ini_transfer_map()
	timeCostBias = 20

	# establish the database linking
	dbConnect = pymongo.MongoClient(DATEBASE_ADDRESS)
	db = dbConnect[DATABASE_NAME]
	name2id_dict = get_name_2_id_dict()
	id2name_dict = get_id_2_name_dict()

	# calculate the path between every pair of stations
	trajsSet = []
	for stationAName in name2id_dict:
		for stationBName in name2id_dict:
			# transfer the name into id
			minDistance = 999
			trajInID = []
			transInID = []
			# base on the help of generated matrix, get the shortest trajectory
			for stationAid in name2id_dict[stationAName]:
				for stationBid in name2id_dict[stationBName]:
					curDistance = get_distance(distanceMatrix, stationList, stationAid, stationBid)
					if curDistance < minDistance:
						minDistance = curDistance
						trajInID = get_trajectory(transferMatrix, stationList, stationAid, stationBid)
						transInID = get_transfer_station_list(transflgMatrix, stationList, trajInID)
			trajInName = []
			trajInDetail = []
			for i in range(len(trajInID)):
				curStationName = id2name_dict[trajInID[i]][0]
				if not curStationName in trajInName:
					if trajInID[i] in transInID:
						trajInName.append(curStationName)
						trajInDetail.append((curStationName, 1, id2name_dict[trajInID[i]][1], trajInID[i]))
					else:
						trajInName.append(curStationName)
						trajInDetail.append((curStationName, 0, id2name_dict[trajInID[i]][1], trajInID[i]))
			# print(stationAName, stationBName, trajInDetail)
			trajsSet.append({
				'START_STATION': stationAName,
				'END_STATION': stationBName,
				'TRAJECTORY': trajInDetail
			})
	db['transfer_dict'].insert_many(trajsSet)


