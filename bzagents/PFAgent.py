from Agent import *

class PFAgent(Agent):
	# constants
	CLOSE_TO_ENEMY = 30 	# within a radius of 30 pixels of the enemy
	SEMI_CLOSE_TO_ENEMY = 2*CLOSE_TO_ENEMY

	# member variables
	fieldX = []
	fieldY = []

	def __init__(self, ip, port):
		Agent.__init__(self, ip, port)
		self._initializePF()

	def _initializePF(self):
		for x in range((-1*self.worldHalfSize),self.worldHalfSize):
			colX = []
			colY = []
			for y in range((-1*self.worldHalfSize),self.worldHalfSize):
				colX.append(0)
				colY.append(0)
			self.fieldX.append(colX)
			self.fieldY.append(colY)

	### aggregated field methods
	def calculatePF(self):
		otherTanks = self._query("othertanks")
		goals = self._getEnemyFlagPositions()
		flagPosition = self._getMyFlagPosition()
		for x in range((-1*self.worldHalfSize),self.worldHalfSize):
			for y in range((-1*self.worldHalfSize),self.worldHalfSize):
				self.calculateAttractiveFieldAtPoint(x,y,goals)

				for tank in otherTanks:
					self.calculateRepulsiveFieldAtPoint(x,y,tank)

				if(not self._isMyFlagCaptured()):
					self.calculateTangentialFieldAtPoint(x,y)

	### attractive field methods
	def calculateAttractivePF(self):
		#if(self.hasEnemyFlag):
		#	 calculate base position
		#	return

		goals = self._getEnemyFlagPositions()
		for x in range((-1*self.worldHalfSize),self.worldHalfSize):
			for y in range((-1*self.worldHalfSize),self.worldHalfSize):
				self.calculateAttractiveFieldAtPoint(x,y,goals)
	
	def calculateAttractiveFieldAtPoint(self, x, y, goals):
		fieldStrength = 1
		
		innerRadius = 80
		outerRadius = 2*innerRadius
	
		deltaX = 0
		deltaY = 0
		distance = 10000
		goalX = self.NOT_SET
		goalY = self.NOT_SET
	
		for goal in goals:
			gX = goal[0]
			gY = goal[1]
			currDistance = math.sqrt((gX - x)**2 + (gY - y)**2)
			if distance > currDistance:
				goalX = gX
				goalY = gY
				distance = currDistance
				theta = math.atan2((goalY-y),(goalX-x))
	
		const = fieldStrength * (distance-innerRadius)
		if innerRadius <= distance and distance <= innerRadius+outerRadius:
			deltaX = const * math.cos(theta)
			deltaY = const * math.sin(theta)
		elif distance > outerRadius:
			deltaX = const * math.cos(theta)
			deltaY = const * math.sin(theta)
	
		# assign deltas to delta x, delta y fields		
		self.fieldX[x][y] += deltaX
		self.fieldY[x][y] += deltaY

	### repulsive field methods
	def calculateRepulsivePF(self):
		otherTanks = self._query("othertanks")

		fieldStrength = .50
		
		# check distance from point to each enemy tank
		for tank in otherTanks:
			for x in range((-1*self.worldHalfSize),self.worldHalfSize):
				for y in range((-1*self.worldHalfSize),self.worldHalfSize):
					self.calculateRepulsiveFieldAtPoint(x,y,tank)

	def calculateRepulsiveFieldAtPoint(self, x, y, tank):
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

		self.fieldX[x][y] += deltaX
		self.fieldY[x][y] += deltaY

	def getDistanceToEnemyTank(self,x,y,tankInfo):
		tankXPos = int(float(tankInfo[4]))
		tankYPos = int(float(tankInfo[5]))

		distance = math.sqrt((tankXPos-x)**2 + (tankYPos - y)**2)

		#print distance
		return distance

	def getAngleToEnemyTank(self,x,y,tankInfo):
		tankXPos = int(float(tankInfo[4]))
		tankYPos = int(float(tankInfo[5]))

		#print "angleCalc: " + str(x) + ", " + str(y) + "; " + str(tankXPos) + ","+str(tankYPos)
		if(tankYPos == y):
			#print "returning 0"
			return 0

		angle = math.atan2((tankYPos-y),(tankXPos-x))

		return (angle);	    
	
	### tangential field methods
	def calculateTangentialFieldAtPoint(x,y):
		# write method here -- reference the other two '*AtPoint' methods above
		return
