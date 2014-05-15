from PFAgent import *
import re

class OccAgent(PFAgent):
	# member constants
	SENSOR_X_DIM = Agent.NOT_SET
	SENSOR_Y_DIM = Agent.NOT_SET
	GRID_AT_STR = "at"
	GRID_SIZE_STR = "size"
	BEGINNING_OCCUPIED_ESTIMATE = .01
	REPORTED_OBSTACLE_CHAR = "1"
	CONFIDENT_OF_OBSTACLE = 1
	CONFIDENT_OF_NO_OBSTACLE = -1
	TRUE_POSITIVE = .97
	FALSE_POSITIVE = .03
	TRUE_NEGATIVE = .9
	FALSE_NEGATIVE = .1

	# member variables
	probabilities = []


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
		self.SENSOR_X_DIM = int(dimensions[0])
		self.SENSOR_Y_DIM = int(dimensions[1])

	####### end initialization functions

	def _countReportedObstacles(self,gridList):
		numOnes = 0

		# note that range starts at 2: this loop skips
		# the 'at' and 'size' lines in the grid list
		for x in range(2,len(gridList)-2):
			numOnes += gridList[x].count(self.REPORTED_OBSTACLE_CHAR)

		return numOnes

	def _getPointFromString(self,strLine):
		commaPos = strLine.index(",")
		
		pointAt = []
		pointAt.append(int(strLine[0:commaPos]))
		pointAt.append(int(strLine[commaPos+1:len(strLine)]))

		return self.getAdjustedPoint(pointAt)

	def _getGrid(self, tankNum):
		raw = self._getRawResponse("occgrid " + str(tankNum) + self.SERVER_DELIMITER)
		raw = raw[len(self.LIST_START):-1*(len(self.LIST_END) + 1)]  # parse off 'begin\n' and 'end\n'
		strList = raw.split(self.SERVER_DELIMITER)  # split strings by server delimiter

		# strip 'at' from point (bottom-left corner)
		strList[0] = strList[0][len(self.GRID_AT_STR):len(strList[0])].strip()
		
		# strip 'size' from size
		strList[1] = strList[1][len(self.GRID_SIZE_STR):len(strList[1])].strip()

		return strList

	def printProbsToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				world += "{:10.2f}".format(self.probabilities[x][y]) + " "
			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world

	def updateProbabilities(self, tankNum):
		gridList = self.getGrid(tankNum)
		beginningPoint = self._getPointFromString(gridList[0]) # bottom-left corner
		
		'''numOnes = 0
		for x in range(2,2+self.SENSOR_X_DIM):
			line = gridList[x]
			#numOnes += line.count(self.REPORTED_OBSTACLE_CHAR)  # count reported 'occupied' samples
			for y in range(0,self.SENSOR_Y_DIM):
				believedSOccVal = self.probabilities[x-2][y]
				if(believedSOccVal == self.CONFIDENT_OF_OBSTACLE or 
					believedSOccVal == self.CONFIDENT_OF_NO_OBSTACLE):
					continue

				sampleVal = int(line[y])
	
				combinedProbs = 1
				if(sampleVal == 0): 
					# represents P(o_i,j = miss | s_i,j = occupied) (false-negative)
					#combinedProbs *= 
					a = 5
				else:	
					# represents P(o_i,j = hit | s_i,j = occupied) (true-positive) 
					a = 2

				self.probabilities[x-2][y] = combinedProbs*believedSOccVal'''

		# iterate through gridList  (remember that the grid needs to be rotated counter-clockwise)
		for i in range( 0, len(gridList)  ):
			for j in range( 0, len(gridList[i]) - 1):
				x = beginningPoint[0] + i
				y = beginningPoint[1] + j
				
				#maybe add checks if x and y are outside world dimensions
				
				#If probabilities are above or below a threshhold of probability assume it's correct
				if self.probabilities[x][y] >= 0.95:
					self.probabilities[x][y] = 1
				elif self.probabilities[x][y] <= 0.05:
					self.probabilities[x][y] = 0
				else:
					self.probabilities[x][y] = self.updateProbability( x, y, gridList[x][y] )
					
	def updateProbability(self, x, y, observed_value):
		probOcc = self.NOT_SET
		probUnOcc = self.NOT_SET
		if observed_value == 1:
			#probability that this is an actual occupied space
			#our probabilities array holds previous probability that it is occupied.
			probOcc = self.TRUE_POSITIVE * self.probabilities[x][y]
			# one minus our stored probability is the probability it is unoccupied
			probUnOcc = self.FALSE_POSITIVE * (1 - self.probabilities[x][y])
		elif observed_value == 0:
			#same as above but using our FalseNegative and TrueNegative values.
			probOcc = self.FALSE_NEGATIVE * self.probabilities[x][y]
			probUnOcc = self.TRUE_NEGATIVE * (1 - self.probabilities[x][y])
		
		return probOcc / (probOcc + probUnOcc)
