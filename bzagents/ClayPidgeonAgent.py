from Agent import *

# agent that moves in a straight line across the x axis
class ClayPidgeonAgent(Agent):
	
	def __init__(self,ip,port):
		Agent.__init__(self,ip,port)

		self.tankNum = 0
		self.velocity = .8
		self.angVel = .3
		self.oscillationThreshold = 40	# (in seconds)
		#self.oscillationAngle = (float(3)/2)*math.pi   # y-axis oscillation
		self.oscillationAngle = 0   # x-axis oscillation

	def _alignTankWithAngle(self):
		tank = self._query("mytanks")[self.tankNum]
		relAngle = abs(self.getMyAngle(self.tankNum) - self.oscillationAngle)
		while (relAngle > .001):
			speed = relAngle/math.pi
			if(speed < .15):
				speed = .15
	
			# reassign variables
			self.setAngularVelocity(0,speed,self.oscillationAngle)
			relAngle = abs(self.getMyAngle(0) - self.oscillationAngle)
		
		# stop tank rotation
		self.stop(0)

	def _moveToParallelPlane(self):
		perpAngle = self.getAdjustedAngle(self.oscillationAngle + math.pi/2)
		# rotate to move (perpendicular to plane of oscillation)
		angleDiff = abs(self.getMyAngle(self.tankNum) - perpAngle)
		while(angleDiff > .001):
			speed = angleDiff/math.pi
			if(speed < .15):
				speed = .15

			# reassign variables
			self.setAngularVelocity(0,speed,perpAngle)
			angleDiff = abs(self.getMyAngle(self.tankNum) - perpAngle)

		self.setAngularVelocity(0,0,perpAngle)

		# move up n units
		originalPosition = self.getMyPosition(0)
		position = originalPosition
		distanceFromEnemyPlane = 200
		while(self.distance(originalPosition, position) < distanceFromEnemyPlane):
			self.commandAgent("speed " + str(self.tankNum) + " " + str(self.velocity))
			position = self.getMyPosition(0)

		# stop
		self.stop(0)
					
	
	def play(self):
		self._moveToParallelPlane()
		
		self._alignTankWithAngle()

		velocity = self.velocity
		lastTime = time.time()
		self.commandAgent("speed " + str(self.tankNum) + " " + str(velocity))
		self.commandAgent("shoot " + str(self.tankNum))
		while 1:
			# reverse direction if enough time has passed
			currTime = time.time()
			if(currTime - lastTime > self.oscillationThreshold):
				velocity *= -1
				self.commandAgent("speed " + str(self.tankNum) + " " + str(velocity))
				lastTime = currTime
				self.commandAgent("shoot " + str(self.tankNum))
