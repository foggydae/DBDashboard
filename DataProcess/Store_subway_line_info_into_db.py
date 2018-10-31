import pandas as pd
import pymongo
import math
import time
import datetime
from pprint import pprint

global DATEBASE_ADDRESS, DATABASE_NAME
DATEBASE_ADDRESS = '127.0.0.1:20001'
DATABASE_NAME = 'test'


# format the station and line num from csv(if the num is XXX, change it into the formatted XXXX)
def format_station_ID (stationNum):
	outputID = str(stationNum)
	if len(outputID) == 3 or len(outputID) == 1:
		outputID = "0" + outputID
	return outputID


# prepare the data from the csv file into line structure
def generate_line_dict (csvDf):
	lineDict = {}
	for index, row in csvDf.iterrows():
		# check if the station data is complete(if the longitude or latitude data is missing)
		if math.isnan(row['LONGITUDE']):
			# if it is, ignore this station
			print("ERROR:", row['STATION_NAME'], "has no longitude and latitude data.")
			continue

		# if the line that the current station belongs to appears for the first time, add it to the line dict
		if row['LINE_NAME_CN'] not in lineDict:
			# the line item contains it's color\name in chinese\id, and a list to store its stations (ordered)
			lineDict[row['LINE_NAME_CN']] = {
				'COLOR': row['LINE_COLOR'],
				'LINE_NAME_ZH': row['LINE_NAME_CN'],
				'LINE_ID': format_station_ID(row['LINE_NUM']),
				'PATH': [{
					'LONGITUDE': row['LONGITUDE'],
					'LATITUDE': row['LATITUDE'],
					'STATION_ID': format_station_ID(row['STATION_NUM']),
					'STATION_NAME': row['STATION_NAME_CN']
				}] # current station is the first station of this line
			} # because the station order in the file is actually in accordance with the actual order, station info in the list will be good.
		else: # if the line already exists, add current station into the list directly
			lineDict[row['LINE_NAME_CN']]['PATH'].append({
				'LONGITUDE': row['LONGITUDE'],
				'LATITUDE': row['LATITUDE'],
				'STATION_ID': format_station_ID(row['STATION_NUM']),
				'STATION_NAME': row['STATION_NAME_CN']
			})

	# change the dict into list in order to store them into the database
	line_list = []
	for key in lineDict:
		line_list.append(lineDict[key])

	return line_list


if __name__ == '__main__':
	# establish the database linking
	dbConnect = pymongo.MongoClient(DATEBASE_ADDRESS)
	db = dbConnect[DATABASE_NAME]

	# using the pandas package to read(decode) the csv file
	df = pd.read_csv("../SubwayData/station_info_by_id.csv")
	# extract needed data from the csv file
	line_list = generate_line_dict(df)

	# store the processed data into the database
	db['line_info'].insert_many(line_list)
