from PFAgent import *
from grid_filter_gl import *

class OccAgent(PFAgent):
	# member constants
	SENSOR_X_DIM = Agent.NOT_SET
	SENSOR_Y_DIM = Agent.NOT_SET
	GRID_AT_STR = "at"
	GRID_SIZE_STR = "size"
	BEGINNING_OCCUPIED_ESTIMATE = .20
	REPORTED_OBSTACLE_CHAR = "1"
	CONFIDENT_OF_OBSTACLE = .999995
	CONFIDENT_OF_NO_OBSTACLE = .000001
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
		self.probabilities = self.BEGINNING_OCCUPIED_ESTIMATE * ones((self.worldHalfSize * 2, self.worldHalfSize * 2))
		init_window(self.worldHalfSize * 2, self.worldHalfSize * 2)
		
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

		# strip 'at' from point (bottom-left corner)
		atStr = strList[0][len(self.GRID_AT_STR):len(strList[0])].strip()		

		# strip 'size' from size
		sizeStr = strList[1][len(self.GRID_SIZE_STR):len(strList[1])].strip()
		
		newList = [atStr,sizeStr]

		lengthOfRow = len(strList[2])	# first row of samples in the array
		for y in range(0,lengthOfRow):
			line = ""
			for x in range(2,len(strList)):
				line += strList[x][lengthOfRow-1-y]
	
			newList.append(line)
	
		return newList

	def printProbsToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				world += '%.2f' % self.probabilities[x][y] + " "

			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world

	def _testAdjoiningPoint(self,x,y):
		try:
			mine = round(self.probabilities[x][y])
			if(mine < .01):
				return 0
			elif(mine >= 1.000):
				return 1

			#return int(self.probabilities[x][y])
		except IndexError:
			return 0

	def printMapToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				charToAdd = ""
				if(self.probabilities[x][y] >= self.CONFIDENT_OF_OBSTACLE):
					charToAdd += str(self.SPACE_OCCUPIED_CHAR)

					# count 0's around this pixel		
					total = 0
					total += self._testAdjoiningPoint(x-1,y+1)
					total += self._testAdjoiningPoint(x,y+1)
					total += self._testAdjoiningPoint(x+1,y+1)
					total += self._testAdjoiningPoint(x-1,y)
					total += self._testAdjoiningPoint(x+1,y)
					total += self._testAdjoiningPoint(x-1,y-1)
					total += self._testAdjoiningPoint(x,y-1)
					total += self._testAdjoiningPoint(x+1,y-1)
					if(total < 5):
						charToAdd = str(self.SPACE_NOT_OCCUPIED_CHAR)

				elif(self.probabilities[x][y] <= self.CONFIDENT_OF_NO_OBSTACLE):
					charToAdd += str(self.SPACE_NOT_OCCUPIED_CHAR)

				else:
					charToAdd += str(self.UNKNOWN_CHAR)
				
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
				y = beginningPoint[1] + j - 1
				#print str(gridList[0])
				#print str(beginningPoint)
				#print str(x) + " " + str(y)
				
				#checks if x and y are outside world dimensions
				if x >= self.worldHalfSize * 2 or x < 0:
					continue
				if y >= self.worldHalfSize * 2 or y < 0:
					continue
				
				#If probabilities are above or below a threshhold of probability assume it's correct
				try:
					prior = self.probabilities[x][y]
				except IndexError:
					break

				if prior >= self.CONFIDENT_OF_OBSTACLE:
					self.probabilities[x][y] = self.SPACE_OCCUPIED_CHAR
				elif prior <= self.CONFIDENT_OF_NO_OBSTACLE:
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
		
	def drawGrid(self):
		update_grid(self.probabilities)
		draw_grid()
