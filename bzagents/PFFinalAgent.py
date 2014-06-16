from Agent import *

class PFFinalAgent(Agent):
	# constants
	CLOSE_TO_ENEMY = 30 	# within a radius of 30 pixels of the enemy
	SEMI_CLOSE_TO_ENEMY = 2*CLOSE_TO_ENEMY
	HEADING_TOLERANCE = 0.1 # tolerance of finding desired heading

	# member variables
	fieldX = []
	fieldY = []
	occFieldX = []
	occFieldY = []
	desiredHeading = 0 #angle of desired travel

	def __init__(self, ip, port):
		Agent.__init__(self, ip, port)
		self._initializePF()

	def _initializePF(self):
		for x in range(0,self.worldHalfSize*2):
			colX = []
			colY = []
			for y in range(0,self.worldHalfSize*2):
				colX.append(0)
				colY.append(0)
			self.fieldX.append(colX)
			self.fieldY.append(colY)
			self.occFieldX.append(colX)
			self.occFieldY.append(colY)

	### aggregated field methods
	def calculatePF(self):
		otherTanks = self._query("othertanks")
	
		attractiveGoalParam = self._getAttractiveGoalParam()
		myFlagCaptured = self._isMyFlagCaptured()
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				self.calculateAttractiveFieldAtPoint(x,y,attractiveGoalParam)

				for tank in otherTanks:
					self.calculateRepulsiveFieldAtPoint(x,y,tank)

				if(not myFlagCaptured):
					self.calculateTangentialFieldAtPoint(x,y,self.myFlagStand)

	### attractive field methods
	def calculateAttractivePF(self):
		attractiveGoalParam = self._getAttractiveGoalParam()		
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				self.calculateAttractiveFieldAtPoint(x,y,attractiveGoalParam)
	
	def calculateAttractiveFieldAtPoint(self, x, y, goals, fieldX, fieldY):
		x = int(x)
		y = int(y)

		if(fieldX == self.fieldX and fieldY == self.fieldY):
			print "goals: " + str(goals)		
		fieldStrength = 1
		
		innerRadius = 25
		outerRadius = 2*innerRadius
	
		deltaX = 0
		deltaY = 0
		distance = 99999999999
		goalX = self.NOT_SET
		goalY = self.NOT_SET
	
		# find closest goal
		for goal in goals:
			gX = goal[0]
			gY = goal[1]
			currDistance = math.sqrt((gX - x)**2 + (gY - y)**2)
			if distance > currDistance:
				goalX = gX
				goalY = gY
				distance = currDistance
				theta = math.atan2((goalY-y),(goalX-x))

		#if(fieldX == self.fieldX):
		#	print str(x) + "," + str(y) + "; " + str(goalX) + "," + str(goalY)
		if(distance == 99999999999):
			theta = 0

		const = fieldStrength * (distance-innerRadius)
		if distance < innerRadius:
			deltaX = 0
			deltaY = 0
		elif innerRadius <= distance and distance <= innerRadius+outerRadius:
			deltaX = const * math.cos(theta)
			deltaY = const * math.sin(theta)
		elif distance > outerRadius:
			deltaX = const * math.cos(theta)
			deltaY = const * math.sin(theta)
	
		# assign deltas to delta x, delta y fields
		if(x >= 2*self.worldHalfSize):
			x = 2*self.worldHalfSize - 1
		if(y >= 2*self.worldHalfSize):
			y = 2*self.worldHalfSize - 1
		if(x < 0 ):
			x = 0;
		if(y < 0):
			y = 0;	
		fieldX[x][y] += deltaX
		fieldY[x][y] += deltaY
		self.desiredHeading = self.getAdjustedAngle(theta)

	def _getAttractiveGoalParam(self):
		param = self._getEnemyFlagPositions()
		if(self._iHaveEnemyFlag()):
			print "mybasecoords: " + str(self.myBaseCoords[0])
			param = [self.myBaseCoords[0]]

		return param
		

	### repulsive field methods
	def calculateRepulsivePF(self):
		otherTanks = self._query("othertanks")

		fieldStrength = .50
		
		# check distance from point to each enemy tank
		for tank in otherTanks:
			for x in range(0,self.worldHalfSize*2):
				for y in range(0,self.worldHalfSize*2):
					self.calculateRepulsiveFieldAtPoint(x,y,tank)

	def calculateRepulsiveFieldAtPoint(self, x, y, tank):
		x = int(x)
		y = int(y)

		distance = self.getDistanceToEnemyTank(x,y,tank)
		if(distance > self.SEMI_CLOSE_TO_ENEMY):
			return

		#print "distance: " + str(distance)

		fieldStrength = .50

		angle = (self.getAngleToEnemyTank(x,y,tank))
		#print "angle: " + str(angle)

		deltaX = 0
		deltaY = 0
		outerRadius = self.CLOSE_TO_ENEMY + self.SEMI_CLOSE_TO_ENEMY
		if(distance < self.CLOSE_TO_ENEMY):
			deltaX = -1 * math.cos(angle)
			deltaY = -1 * math.sin(angle)
		elif(distance <= outerRadius):
			const = -1 * fieldStrength * (outerRadius - distance)
			deltaX = const * math.cos(angle)
			deltaY = const * math.sin(angle)

		if(deltaX == 0 and deltaY == 0):
			return

		if(x >= 2*self.worldHalfSize):
			x = 2*self.worldHalfSize - 1
		if(y >= 2*self.worldHalfSize):
			y = 2*self.worldHalfSize - 1
		if(x < 0 ):
			x = 0;
		if(y < 0):
			y = 0;
		self.fieldX[x][y] += deltaX
		self.fieldY[x][y] += deltaY

	def getDistanceToEnemyTank(self,x,y,tankInfo):
		tankXPos = int(float(tankInfo[4]))
		tankYPos = int(float(tankInfo[5]))

		return self.getDistanceToPoint(x,y,tankXPos,tankYPos)
		
	def getDistanceToPoint(self,x,y,px,py):
		return math.sqrt((px-x)**2 + (py - y)**2)

	def getAngleToEnemyTank(self,x,y,tankInfo):
		tankXPos = int(float(tankInfo[4]))
		tankYPos = int(float(tankInfo[5]))

		return self.getAngleToPoint(x,y,tankXPos,tankYPos)   
	
	def getAngleToPoint(self,x,y,px,py):
		if(py == y):
			return 0
		angle = math.atan2((py-y),(px-x))
		return (angle);
	
	### tangential field methods
	def calculateTangentialPF(self):
		# check distance from point to each enemy tank
		for x in range(0,self.worldHalfSize*2):
			for y in range(0,self.worldHalfSize*2):
				self.calculateTangentialFieldAtPoint(x,y,self.myFlagStand)
	
	def calculateTangentialFieldAtPoint(self,x,y,flagStand):
		distance = self.getDistanceToPoint(x,y,flagStand[0],flagStand[1])
		if(distance > self.SEMI_CLOSE_TO_ENEMY):
			return

		fieldStrength = .50

		angle = (self.getAngleToPoint(x,y,flagStand[0],flagStand[1]))
		angle += 1.5708 #add 90 degrees (in radians)

		deltaX = 0
		deltaY = 0
		outerRadius = self.CLOSE_TO_ENEMY + self.SEMI_CLOSE_TO_ENEMY
		if(distance < self.CLOSE_TO_ENEMY):
			deltaX = -1 * math.cos(angle)
			deltaY = -1 * math.sin(angle)
		elif(distance <= outerRadius):
			const = -1 * fieldStrength * (outerRadius - distance)
			deltaX = const * math.cos(angle)
			deltaY = const * math.sin(angle)

		if(deltaX == 0 and deltaY == 0):
			return

		if(x >= self.worldHalfSize*2):
			x = self.worldHalfSize*2 - 1
		if(y >= self.worldHalfSize*2):
			y = self.worldHalfSize*2 - 1
		if(x < 0 ):
			x = 0;
		if(y < 0):
			y = 0;
		self.fieldX[x][y] += deltaX
		self.fieldY[x][y] += deltaY
		return
	
	def getRandomShotTolerance(self):
		return (1.5 + random.random())	# between 1.5 and 2.5 seconds
		
	def play(self):		# driver function for beginning AI simulation
		captureTank = 0
		tanksInfo = self._query("mytanks")

		angle = self.getAdjustedAngle(float(tanksInfo[captureTank][8]))

		# assign shooting tolerance (tolerance is a measure of time)
		shootTolerance = self.getRandomShotTolerance()
		shootTime = time.time()

		while 1:
			currTime = time.time()
			#tanksInfo = self._query("mytanks")
			#tankXPos = int(tanksInfo[captureTank][6])
			#tankYPos = int(tanksInfo[captureTank][7])
			tankPos = self._getCurrentPositionOfTank(0)
			tankXPos = int(tankPos[0])
			tankYPos = int(tankPos[1])
			self.calculateAttractiveFieldAtPoint(int(tankXPos),int(tankYPos),self._getAttractiveGoalParam())
			
			# check to see if the tank should shoot
			if(shootTolerance < (currTime - shootTime) and not self._isCoordinateInBase((tankXPos,tankYPos))):
				self.commandAgent("shoot 0")
				shootTime = currTime
				shootTolerance = self.getRandomShotTolerance()

			# check to see if the tank should rotate once pointed the right way crank up the speed!
			tankHeading = self.getAdjustedAngle(float(tanksInfo[captureTank][8]))
			if tankHeading > self.desiredHeading + self.HEADING_TOLERANCE:
				self.commandAgent("angvel " + str(captureTank) + " -0.75")
			elif tankHeading < self.desiredHeading - self.HEADING_TOLERANCE:
				self.commandAgent("angvel " + str(captureTank) + " 0.75")
			else:
				self.commandAgent("angvel " + str(captureTank) + " 0")

				magnitude = (self.fieldX[tankXPos][tankYPos]**2+self.fieldY[tankXPos][tankYPos]**2)**.5
				if(magnitude > 1):
					magnitude = 1
				if(magnitude < -1):
					magnitude = -1
				self.commandAgent("speed " + str(captureTank) + " " + str(magnitude))

