from PFAgent import *
import re

class OccAgent(PFAgent):
	# member constants
	SENSOR_X = Agent.NOT_SET
	SENSOR_Y = Agent.NOT_SET
	GRID_AT_STR = "at"
	GRID_SIZE_STR = "size"
	BEGINNING_OCCUPIED_ESTIMATE = .01

	# member variables
	probabilities = []
	probOfObstacles = .5

	####### initialization functions
	def __init__(self, ip, port):
		Agent.__init__(self, ip, port)
		self._initializePF()
		self._initializeOcc()

	def _initializeOcc(self):
		# initialize the probabilities 
		for x in range(0,self.worldHalfSize*2):
			col = []
			for y in range(0,self.worldHalfSize*2):
				col.append(self.BEGINNING_OCCUPIED_ESTIMATE)
			self.probabilities.append(col)

		# set sensor x,y
		self._setSensorDimensions()

	def _setSensorDimensions(self):
		strList = self.getGrid(0)
		
		dimensions = strList[1].split("x")
		SENSOR_X = int(dimensions[0])
		SENSOR_Y = int(dimensions[1])

	####### end initialization functions

	def _countReportedObstacles(self,gridList):
		numOnes = 0

		# note that range starts at 2: this loop skips
		# the 'at' and 'size' lines in the grid list
		for x in range(2,len(gridList)-2):
			numOnes += gridList[x].count("1")

		return numOnes

	def _getPointFromString(self,strLine):
		commaPos = strLine.index(",")
		
		pointAt = []
		pointAt.append(int(strLine[0:commaPos]))
		pointAt.append(int(strLine[commaPos+1:len(strLine)]))

		return self.getAdjustedPoint(pointAt)

	def getGrid(self, tankNum):
		raw = self._getRawResponse("occgrid " + str(tankNum) + self.SERVER_DELIMITER)
		raw = raw[len(self.LIST_START):-1*(len(self.LIST_END) + 1)]  # parse off 'begin\n' and 'end\n'
		strList = raw.split(self.SERVER_DELIMITER)  # split strings by server delimiter

		# strip 'at' from point (bottom-left corner)
		strList[0] = strList[0][len(self.GRID_AT_STR):len(strList[0])].strip()
		
		# strip 'size' from size
		strList[1] = strList[1][len(self.GRID_SIZE_STR):len(strList[1])].strip()

		return strList

	def calculateProbabilities(self, tankNum):
		gridList = self._getGrid(tankNum)
		beginningPoint = self._getPointFromString(gridList[0]) # bottom-left corner
