from KalmanFilter import *
from grid_filter_gl import *
from PFAgent import *
from KalmanFinalAgent import *
from PIL import Image
from random import randint

class FinalAgent(KalmanFinalAgent):
	# member constants
	SENSOR_X_DIM = Agent.NOT_SET
	SENSOR_Y_DIM = Agent.NOT_SET
	GRID_AT_STR = "at"
	GRID_SIZE_STR = "size"
	BEGINNING_OCCUPIED_ESTIMATE = .05
	REPORTED_OBSTACLE_CHAR = "1"
	CONFIDENT_OF_OBSTACLE = .90
	CONFIDENT_OF_NO_OBSTACLE = .01
	SPACE_OCCUPIED_CHAR = 1
	SPACE_NOT_OCCUPIED_CHAR = 0
	UNKNOWN_CHAR = "."
	TRUE_POSITIVE = .97
	FALSE_POSITIVE = .03
	TRUE_NEGATIVE = .9
	FALSE_NEGATIVE = .1

	KALMAN_TANK_1 = 0
	KALMAN_TANK_2 = 1
	EXPLORING_TANK = 2
	
	# member variables
	probabilities = []
	openGlWindowInitialized = False
	visitedNodes = []
	currNodeToVisit = [(0,0)]
	visitNodeTime = 0


	####### initialization functions
	def __init__(self, ip, port):
		KalmanFinalAgent.__init__(self,ip,port)

		self._initializePF()
		self._initializeOcc()

		self.kalmanFilter1 = KalmanFilter(self.NOISE)
		self.kalmanFilter2 = KalmanFilter(self.NOISE)

	def _initializeOcc(self):
		# initialize the probabilities 
		self.probabilities = self.BEGINNING_OCCUPIED_ESTIMATE * ones((self.worldHalfSize * 2, self.worldHalfSize * 2))
		#initialize visitedNodes
		for i in range(0,15):
			row = []
			for j in range(0,15):
				row.append(0)
			self.visitedNodes.append(row)
		
		# set sensor x,y
		self._setSensorDimensions()
		

	def _setSensorDimensions(self):
		strList = self._getGrid(self.EXPLORING_TANK)
		
		dimensions = strList[1]
		self.SENSOR_X_DIM = int(dimensions[0])
		self.SENSOR_Y_DIM = int(dimensions[1])

	####### end initialization functions

	def _getPointFromString(self,strLine):
		commaPos = strLine.index(",")
		
		pointAt = []
		pointAt.append(int(strLine[0:commaPos]))
		pointAt.append(int(strLine[commaPos+1:len(strLine)]))

		return self.getAdjustedPoint(pointAt)

	def _getSizeFromString(self,strLine):
		xPos = strLine.index("x")

		sizes = []
		sizes.append(int(strLine[0:xPos]))
		sizes.append(int(strLine[xPos+1:len(strLine)]))

		return sizes

	def _getGrid(self, tankNum):
		raw = self._getRawResponse("occgrid " + str(tankNum) + self.SERVER_DELIMITER)
		raw = raw[len(self.LIST_START):-1*(len(self.LIST_END) + 1)]  # parse off 'begin\n' and 'end\n'
		strList = raw.split(self.SERVER_DELIMITER)  # split strings by server delimiter

		# strip 'at' from point (bottom-left corner)
		atStr = strList[0][len(self.GRID_AT_STR):len(strList[0])].strip()
		strList[0] = self._getPointFromString(atStr)  # translate to x,y coordinates
		
		# strip 'size' from size
		sizeStr = strList[1][len(self.GRID_SIZE_STR):len(strList[1])].strip()
		strList[1] = self._getSizeFromString(sizeStr)
		
		newList = [strList[0],strList[1]]
		lengthOfRow = len(strList[2])	# first row of samples in the array
		for y in range(0,lengthOfRow):
			line = ""
			for x in range(2,len(strList)):
				line += strList[x][lengthOfRow-1-y]
	
			newList.append(line)

		newList2 = [newList[0],newList[1]]
		for x in range(0,len(newList)-2):
			newList2.append(newList[len(newList)-1-x])
		
		return newList2

	def printProbsToFile(self, filename):
		world = ""
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				world += '%.2f' % self.probabilities[x][y] + " "

			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world

	def printMapToGrayscale(self, filename):
		imgArray = []
		for y in range(0,self.worldHalfSize*2):
			yCoord = (self.worldHalfSize*2)-1-y
			for x in range(0,self.worldHalfSize*2):
				intToAdd = 0
		
				# start from top-left of screen: x = 0, y = 800
				probability = self.probabilities[x][yCoord]
				if(probability >= self.CONFIDENT_OF_OBSTACLE):
					intToAdd = (self.SPACE_OCCUPIED_CHAR*255)

				elif(probability <= self.CONFIDENT_OF_NO_OBSTACLE):
					intToAdd = 01

				else:
					intToAdd = probability*255
				
				imgArray.append(intToAdd)

		im = Image.new('L',(800,800))
		im.putdata(imgArray)
		im.save(filename,"PNG")

	def printMapToFile(self, filename):
		world = ""

		# start with y so we go across the screen instead of up and down
		for y in range(0,self.worldHalfSize*2):
			yCoord = (self.worldHalfSize*2)-1-y
			for x in range(0,self.worldHalfSize*2):
				charToAdd = ""
		
				# start from top-left of screen: x = 0, y = 800
				probability = self.probabilities[x][yCoord]
				if(probability >= self.CONFIDENT_OF_OBSTACLE):
					charToAdd += str(self.SPACE_OCCUPIED_CHAR)

				elif(probability <= self.CONFIDENT_OF_NO_OBSTACLE):
					charToAdd += str(self.SPACE_NOT_OCCUPIED_CHAR)

				else:
					charToAdd += str(self.UNKNOWN_CHAR)
				
				world += charToAdd
				
			world += "\n"

		outfile = open(filename,'w')
		print >>outfile, world

	def senseTerrain(self,tankNum):
		for x in range(0,20):
			self.updateProbabilities(tankNum)
		self.printMapToGrayscale("tankmap5.png")

	def _checkNeighbors(self,x,y):	
		tolerance = .1
		topLeft = tolerance
		try:
			topLeft = self.probabilities[x-1,y+1]
		except IndexError:
			pass
	
		topMiddle = tolerance
		try:
			topMiddle = self.probabilities[x,y+1]
		except IndexError:
			pass

		topRight = tolerance
		try:
			topRight = self.probabilities[x+1,y+1]
		except IndexError:
			pass

		middleLeft = tolerance
		try:
			middleLeft = self.probabilities[x-1,y]
		except IndexError:
			pass

		middleRight = tolerance
		try:
			middleRight = self.probabilities[x+1,y]
		except IndexError:
			pass

		bottomLeft = tolerance
		try:
			bottomLeft = self.probabilities[x-1,y-1]
		except IndexError:
			pass

		bottomMiddle = tolerance
		try:
			bottomMiddle = self.probabilities[x,y-1]
		except IndexError:
			pass

		bottomRight = tolerance
		try:
			bottomRight = self.probabilities[x+1,y-1]
		except IndexError:
			pass

		arr = [topLeft,topMiddle,topRight,middleLeft,middleRight,bottomLeft,bottomMiddle,bottomRight]

		# count 1's and 0's (not probabilities in between)
		onesCounter = 0
		zerosCounter = 0
		for x in range(0,len(arr)):
			if(arr[x] >= self.CONFIDENT_OF_OBSTACLE):
				onesCounter += 1
			if(arr[x] < self.CONFIDENT_OF_NO_OBSTACLE):
				zerosCounter += 1

		if(onesCounter > 4):
			return 1
		if(zerosCounter > 4):
			return 0

		# neither ones nor zeros are a majority--return -1 to
		# signify no majority
		return -1

	def randomWander(self):
		currTime = time.time()
		rotating = False
		tolerance = 30
		self.commandAgent("speed " + str(self.EXPLORING_TANK) + " 1")
		while 1:
			self.commandAgent("shoot " + str(self.EXPLORING_TANK))
			negative = False
			self.senseTerrain(self.EXPLORING_TANK)
			if(time.time() - currTime > tolerance):
				self.commandAgent("speed " + str(self.EXPLORING_TANK) + " 0")
				randomAngVel = random.random() 
				if(randomAngVel < .5):
					randomAngVel += .5
				if(negative == True):
					randomAngVel *= -1
					negative = (not negative)

				self.commandAgent("angvel " + str(self.EXPLORING_TANK) + " " + str(randomAngVel))
				time.sleep(5)
				self.commandAgent("angvel " + str(self.EXPLORING_TANK) + " 0")
				self.commandAgent("speed " + str(self.EXPLORING_TANK) + " 1")
				currTime = time.time()
				
	
	def updateProbabilities(self, tankNum):
		gridList = self._getGrid(tankNum)
		beginningPoint = gridList[0] # bottom-left corner

		# iterate through gridList
		for i in range( 2, len(gridList)  ):
			for j in range( 0, len(gridList[i]) ):
				x = beginningPoint[0] + j
				y = beginningPoint[1] + (i-2)
				
				#checks if x and y are outside world dimensions
				if x >= self.worldHalfSize * 2 or x < 0:
					continue
				if y >= self.worldHalfSize * 2 or y < 0:
					continue
				
				# get the prior probability value for this pixel
				try:
					prior = self.probabilities[x][y]
				except IndexError:
					continue

				# if 5+ neighboring values are known, make this
				# pixel match the neighboring values
				checkNeighborsVal = self._checkNeighbors(x,y)
				if(checkNeighborsVal == 1):
					prior = 1
				if(checkNeighborsVal == 0):
					prior = 0

				# If probabilities are above or below a certain  
				# threshold, assume it's correct
				if prior >= self.CONFIDENT_OF_OBSTACLE:
					self.probabilities[x][y] = self.SPACE_OCCUPIED_CHAR
				elif prior <= self.CONFIDENT_OF_NO_OBSTACLE:
					self.probabilities[x][y] = self.SPACE_NOT_OCCUPIED_CHAR
				else:
					self.probabilities[x][y] = self.updateProbability( x, y, gridList[i][j] )
				
				#update visited nodes
				if x % 100 == 0 and y % 100 == 0:
					if self.visitedNodes[(x/100)-1][(y/100)-1] == 0:
						self.visitedNodes[(x/100)-1][(y/100)-1] = 1
						self.currNodeToVisit == [(-1,-1)]
						self.setNextUnvisitedNode()
						self.visitNodeTime = time.time()
						#print self.currNodeToVisit
					
									
	def updateProbability(self, x, y, observed_value):
		probOcc = self.NOT_SET
		probUnOcc = self.NOT_SET

		if observed_value == "1":
			# probability that this is an actual occupied space
			# our probabilities array holds previous probability that it is occupied.
			probOcc = self.TRUE_POSITIVE * self.probabilities[x][y]
			
			# one minus our stored probability is the probability it is unoccupied
			probUnOcc = self.FALSE_POSITIVE * (1 - self.probabilities[x][y])
		
		elif observed_value == "0":
			# same as above but using our FalseNegative and TrueNegative values.
			probOcc = self.FALSE_NEGATIVE * self.probabilities[x][y]
			probUnOcc = self.TRUE_NEGATIVE * (1 - self.probabilities[x][y])

		return probOcc / (probOcc + probUnOcc)
		
	def drawGrid(self):
		if False == self.openGlWindowInitialized:
			init_window(self.worldHalfSize * 2, self.worldHalfSize * 2)
			self.openGlWindowInitialized = True
		update_grid(self.probabilities)
		draw_grid()
		
	def setNextUnvisitedNode(self):
		for x in range(0, 6):
			returnRandom = False
			for y in range(6, 0,-1):
				if self.visitedNodes[x][y] == 0:
					if (x+1)*100-self.worldHalfSize == self.currNodeToVisit[0][0] and (y+1)*100-self.worldHalfSize == self.currNodeToVisit[0][1]:
						returnRandom = True
						break
					self.currNodeToVisit = [self.getAdjustedPoint(((x+1)*100-self.worldHalfSize,(y+1)*100-self.worldHalfSize))]
					return self.currNodeToVisit
			if returnRandom == True:
				break
		
		x = random.randint(1,7)
		y = random.randint(1,7)
		self.currNodeToVisit = [self.getAdjustedPoint(((x*100)-self.worldHalfSize,(y*100)-self.worldHalfSize))]
		print "tovisit: " + str(self.currNodeToVisit)
		return self.currNodeToVisit
	
	def getClosestEnemy(self,tankNum):
		enemyData = self._query("othertanks")
		target = False
		shortestDistance = 999999999999
		closestTankIndex = -1
		myTankPos = self._getCurrentPositionOfTank(tankNum)
		for key, entry in enumerate(enemyData):
			enemyPoint = self.getAdjustedPoint((float(entry[4]),float(entry[5])))
			distance = self.distance(enemyPoint,myTankPos)
			if(distance < shortestDistance):
				shortestDistance = distance
				closestTankIndex = key
		#print "closest: " + str(enemyData[closestTankIndex])
		return enemyData[closestTankIndex]
		
	def play(self):
		### POTENTIAL FIELDS###
		firstTankNum = 3

		# assign shooting tolerance (tolerance is a measure of time)
		shootTolerance = self.getRandomShotTolerance()
		shootTime = time.time()


		### KALMAN ###
		prev_time = time.time()
		counter = 0
		threshold = 150
		
		### OCCGRID ###		
		captureTank = self.EXPLORING_TANK

		updateNodeTolerance = 20
		self.visitNodeTime = time.time()
		tanksInfo = self._query("mytanks")
		occPos = self._getCurrentPositionOfTank(self.EXPLORING_TANK)
		occXPos = int(occPos[0])
		occYPos = int(occPos[1])
		self.setNextUnvisitedNode()
		self.calculateAttractiveFieldAtPoint(int(occXPos),int(occYPos),self.currNodeToVisit,self.occFieldX,self.occFieldY)
		#print self.currNodeToVisit'''

		while True:
			### PFAgent ###		
			currTime = time.time()	
			for tankNum in range(firstTankNum,len(tanksInfo)):
				tanksInfo = self._query("mytanks")
				tankPos = self._getCurrentPositionOfTank(tankNum)
				tankXPos = int(tankPos[0])
				tankYPos = int(tankPos[1])
				self.calculateAttractiveFieldAtPoint(tankXPos,tankYPos,self._getAttractiveGoalParam(), self.fieldX, self.fieldY)

				# check to see if the tank should shoot
				#if(shootTolerance < (currTime - shootTime))):
				self.commandAgent("shoot " + str(tankNum))
				#	shootTime = currTime
				#	shootTolerance = self.getRandomShotTolerance()

				# check to see if the tank should rotate.
				# Once pointed the right way crank up the speed! (v1!)
				tankHeading = self.getAdjustedAngle(float(tanksInfo[tankNum][8]))
				if tankHeading > self.desiredHeading + self.HEADING_TOLERANCE:
					self.commandAgent("angvel " + str(tankNum) + " -0.75")
				elif tankHeading < self.desiredHeading - self.HEADING_TOLERANCE:
					self.commandAgent("angvel " + str(tankNum) + " 0.75")
				else:
					self.commandAgent("angvel " + str(tankNum) + " 0")

					magnitude = (self.fieldX[tankXPos][tankYPos]**2+self.fieldY[tankXPos][tankYPos]**2)**.5
					if(magnitude > 1):
						magnitude = 1
					if(magnitude < -1):
						magnitude = -1
					if(magnitude == 0):
						magnitude = .3
					self.commandAgent("speed " + str(tankNum) + " " + str(magnitude))

			### KALMAN ###
			now = time.time()
			time_diff = now - prev_time
			prev_time = now
		
			self.delta += time_diff
		
			queryRes = self._query("mytanks")
			kalman1 = queryRes[self.KALMAN_TANK_1]
			kalman2 = queryRes[self.KALMAN_TANK_2]

			target1 = self.getClosestEnemy(self.KALMAN_TANK_1)
			target2 = self.getClosestEnemy(self.KALMAN_TANK_2)
			if self.delta >= self.WAIT:
			
				self.get_new_target(target1, self.KALMAN_TANK_1, self.kalmanFilter1, 1)
				self.get_new_target(target2, self.KALMAN_TANK_2, self.kalmanFilter2, 2)
				self.delta = 0.0
			
			self.tank_controller(counter, threshold, self.KALMAN_TANK_1, self.target1)
			self.tank_controller(counter, threshold, self.KALMAN_TANK_2, self.target2) 

			counter += 1
			if(counter > threshold):
				counter = 0

			### OCC ### 
			currTime = time.time()
			tanksInfo = self._query("mytanks")
			if(updateNodeTolerance < (currTime - self.visitNodeTime)):
				self.visitNodeTime = time.time()	
				self.setNextUnvisitedNode()
				self.calculateAttractiveFieldAtPoint(occXPos,occYPos,self.currNodeToVisit, self.occFieldX, self.occFieldY)
				#print self.currNodeToVisit
			
			tanksInfo = self._query("mytanks")
			occPos = self._getCurrentPositionOfTank(captureTank)
			occXPos = int(occPos[0])
			occYPos = int(occPos[1])
			self.calculateAttractiveFieldAtPoint(int(occXPos),int(occYPos),self.currNodeToVisit,self.occFieldX,self.occFieldY)
			self.updateProbabilities(captureTank)
			self.drawGrid()
			
			# check to see if the tank should rotate.
			# Once pointed the right way crank up the speed! (v2!)
			tankHeading = self.getAdjustedAngle(float(tanksInfo[captureTank][8]))
			if tankHeading > self.desiredHeading + self.HEADING_TOLERANCE:
				self.commandAgent("angvel " + str(captureTank) + " -0.75")
			elif tankHeading < self.desiredHeading - self.HEADING_TOLERANCE:
				self.commandAgent("angvel " + str(captureTank) + " 0.75")
			else:
				self.commandAgent("angvel " + str(captureTank) + " 0")

				magnitude = (self.fieldX[occXPos][occYPos]**2+self.fieldY[occXPos][occYPos]**2)**.5
				if(magnitude > 1):
					magnitude = 1
				if(magnitude < -1):
					magnitude = -1
				self.commandAgent("speed " + str(captureTank) + " " + str(magnitude))
	
