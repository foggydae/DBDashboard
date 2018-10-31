import pandas as pd
import pymongo
import math
import time
import datetime
from pprint import pprint

global DATEBASE_ADDRESS, DATABASE_NAME
DATEBASE_ADDRESS = '127.0.0.1:20001'
DATABASE_NAME = 'test'


# format the station and line num from csv
def format_station_ID (stationNum):
	outputID = str(stationNum)
	if len(outputID) == 3 or len(outputID) == 1:
		outputID = "0" + outputID
	return outputID


# prepare the data from the csv file into station(name as key) structure
def generate_station_dict (csvDf):
	stationDict = {}
	for index, row in csvDf.iterrows():
		# check if the station data is complete(if the longitude or latitude data is missing)
		if math.isnan(row['LONGITUDE']):
			# if it is, ignore this station
			print("ERROR:", row['STATION_NAME'], "has no longitude and latitude data.")
			continue

		if row['STATION_NAME'] not in stationDict:
			stationDict[row['STATION_NAME']] = {
				'STATION_NAME_ZH': row['STATION_NAME_CN'],
				'STATION_NAME_EN': row['STATION_NAME'],
				'LINE_NAME_ZH': row['LINE_NAME_CN'],
				'LINE_NAME': row['LINE_NAME'],
				'LINE_COLOR': [row['LINE_COLOR']],
				'STATION_ID': [format_station_ID(row['STATION_NUM'])],
				'LINE_ID': [format_station_ID(row['LINE_NUM'])],
				'ADJ_STATION': [],
				'TRANSFER': 1,
				'LONGITUDE': row['LONGITUDE'],
				'LATITUDE': row['LATITUDE']
			}
			if not math.isnan(row['ADJ_STATION']):
				stationDict[row['STATION_NAME']]['ADJ_STATION'].append(format_station_ID(int(row['ADJ_STATION'])))
			if not math.isnan(row['ADJ_STATION_2']):
				stationDict[row['STATION_NAME']]['ADJ_STATION'].append(format_station_ID(int(row['ADJ_STATION_2'])))
		else:
			stationDict[row['STATION_NAME']]['TRANSFER'] += 1
			stationDict[row['STATION_NAME']]['LONGITUDE'] += row['LONGITUDE']
			stationDict[row['STATION_NAME']]['LATITUDE']  += row['LATITUDE']
			stationDict[row['STATION_NAME']]['STATION_ID'].append(format_station_ID(row['STATION_NUM']))
			stationDict[row['STATION_NAME']]['LINE_ID'].append(format_station_ID(row['LINE_NUM']))
			stationDict[row['STATION_NAME']]['LINE_COLOR'].append(row['LINE_COLOR'])
			if not math.isnan(row['ADJ_STATION']):
				stationDict[row['STATION_NAME']]['ADJ_STATION'].append(format_station_ID(int(row['ADJ_STATION'])))
			if not math.isnan(row['ADJ_STATION_2']):
				stationDict[row['STATION_NAME']]['ADJ_STATION'].append(format_station_ID(int(row['ADJ_STATION_2'])))

	for station in stationDict:
		if stationDict[station]['TRANSFER'] > 1:
			stationDict[station]['LONGITUDE'] /= stationDict[station]['TRANSFER']
			stationDict[station]['LATITUDE'] /= stationDict[station]['TRANSFER']

	# change the dict into list in order to store them into the database
	station_list = []
	for key in stationDict:
		station_list.append(stationDict[key])

	return station_list


if __name__ == '__main__':
	# establish the database linking
	dbConnect = pymongo.MongoClient(DATEBASE_ADDRESS)
	db = dbConnect[DATABASE_NAME]

	# using the pandas package to read(decode) the csv file
	df = pd.read_csv("../SubwayData/station_info_by_id.csv")
	# extract needed data from the csv file
	station_list = generate_station_dict(df)

	# store the processed data into the database
	db['station_info_by_name'].insert_many(station_list)
