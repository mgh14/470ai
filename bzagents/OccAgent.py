from PFAgent import *

class OccAgent(PFAgent):
	# member constants
	SENSOR_X_DIM = Agent.NOT_SET
	SENSOR_Y_DIM = Agent.NOT_SET
	GRID_AT_STR = "at"
	GRID_SIZE_STR = "size"
	BEGINNING_OCCUPIED_ESTIMATE = .1
	REPORTED_OBSTACLE_CHAR = "1"
	CONFIDENT_OF_OBSTACLE = .95
	CONFIDENT_OF_NO_OBSTACLE = (1-CONFIDENT_OF_OBSTACLE)
	SPACE_OCCUPIED_CHAR = 1
	SPACE_NOT_OCCUPIED_CHAR = 0
	UNKNOWN_CHAR = "."
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
		strList = self._getGrid(0)
		
		dimensions = strList[1].split("x")
		self.SENSOR_X_DIM = int(dimensions[0])
		self.SENSOR_Y_DIM = int(dimensions[1])

	####### end initialization functions

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

		rotatedList = []
		#rotatedList.append(strList[0])
		#rotatedList.append(strList[1])
		#for x in range(0,len(strList)-2):
		#	rotatedList.append(strList[len(strList)-1-x])
		rotatedList = strList
		# strip 'at' from point (bottom-left corner)
		rotatedList[0] = rotatedList[0][len(self.GRID_AT_STR):len(rotatedList[0])].strip()
		#strList[0] = strList[0][len(self.GRID_AT_STR):len(strList[0])].strip()
		
		# strip 'size' from size
		rotatedList[1] = rotatedList[1][len(self.GRID_SIZE_STR):len(rotatedList[1])].strip()
		#strList[1] = strList[1][len(self.GRID_SIZE_STR):len(strList[1])].strip()

		#for x in range(2,len(strList)):
		#	strList[x] = strList[x][::-1]

		return rotatedList
		#return strList

	def printProbsToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				world += "{:10.2f}".format(self.probabilities[x][y]) + " "
			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world
	#def _testAdjoiningPoint(x,y):
		

	def printMapToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				charToAdd = ""
				if(self.probabilities[x][y] >= self.CONFIDENT_OF_OBSTACLE):
					charToAdd += str(self.SPACE_OCCUPIED_CHAR)
				elif(self.probabilities[x][y] <= self.CONFIDENT_OF_NO_OBSTACLE):
					charToAdd += str(self.SPACE_NOT_OCCUPIED_CHAR)
				else:
					charToAdd += self.UNKNOWN_CHAR

				# count 1's around this pixel		
				#total = 0
				#total += int(self.probabilities[x-1][y+1])
				#total += int(self.probabilities[x][y+1])
				#total += int(self.probabilities[x+1][y+1])
				#total += int(self.probabilities[x-1][y])
				#total += int(self.probabilities[x+1][y])
				#total += int(self.probabilities[x-1][y-1])
				#total += int(self.probabilities[x][y-1])
				#total += int(self.probabilities[x+1][y-1])
				#if(total > 4):
				#	charToAdd = CONFIDENT_OF_OBSTACLE
				
				world += charToAdd
				
			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world

	def updateProbabilities(self, tankNum):
		gridList = self._getGrid(tankNum)
		#print str(gridList)		
		#print str(len(gridList))
		#print str(gridList[0]) + " " + str(gridList[1])
		#print str(gridList[101])
		beginningPoint = self._getPointFromString(gridList[0]) # bottom-left corner

		# iterate through gridList
		for i in range( 2, len(gridList)  ):
			for j in range( 0, len(gridList[i]) ):
				x = beginningPoint[0] + (i-2)
				y = beginningPoint[1] + j
				#print str(gridList[0])
				#print str(beginningPoint)
				#print str(x) + " " + str(y)
				
				#maybe add checks if x and y are outside world dimensions
				
				#If probabilities are above or below a threshhold of probability assume it's correct
				if self.probabilities[x][y] >= self.CONFIDENT_OF_OBSTACLE:
					self.probabilities[x][y] = self.SPACE_OCCUPIED_CHAR
				elif self.probabilities[x][y] <= self.CONFIDENT_OF_NO_OBSTACLE:
					#print "B"
					self.probabilities[x][y] = self.SPACE_NOT_OCCUPIED_CHAR
				else:
					#print "c"
					self.probabilities[x][y] = self.updateProbability( x, y, gridList[i][j] )
				#sys.exit(0)

		#print "help: " + str(self.probabilities[beginningPoint[0]][beginningPoint[1]])
					
	def updateProbability(self, x, y, observed_value):
		probOcc = self.NOT_SET
		probUnOcc = self.NOT_SET
		if observed_value == "1":
			#probability that this is an actual occupied space
			#our probabilities array holds previous probability that it is occupied.
			probOcc = self.TRUE_POSITIVE * self.probabilities[x][y]
			# one minus our stored probability is the probability it is unoccupied
			probUnOcc = self.FALSE_POSITIVE * (1 - self.probabilities[x][y])
		elif observed_value == "0":
			#same as above but using our FalseNegative and TrueNegative values.
			probOcc = self.FALSE_NEGATIVE * self.probabilities[x][y]
			probUnOcc = self.TRUE_NEGATIVE * (1 - self.probabilities[x][y])

		return probOcc / (probOcc + probUnOcc)