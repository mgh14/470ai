from Agent import *

# agent that moves in a straight line across the x axis
class ClayPidgeonAgent(Agent):
	
	def __init__(self,ip,port):
		Agent.__init__(self,ip,port)

		self.TANK_NUM = 0
		self.VELOCITY = .8
		self.ANG_VELOCITY = .3
		self.OSCILLATION_THRESHOLD = 40	# (in seconds)
		#self.OSCILLATION_ANGLE = (float(3)/2)*math.pi   # y-axis oscillation
		self.OSCILLATION_ANGLE = 0   # x-axis oscillation

	def _alignTankWithAngle(self):
		tank = self._query("mytanks")[self.TANK_NUM]
		relAngle = abs(self.getMyAngle(self.TANK_NUM) - self.OSCILLATION_ANGLE)
		while (relAngle > .001):
			speed = relAngle/math.pi
			if(speed < .15):
				speed = .15
	
			# reassign variables
			self.setAngularVelocity(0,speed,self.OSCILLATION_ANGLE)
			relAngle = abs(self.getMyAngle(0) - self.OSCILLATION_ANGLE)
		
		# stop tank rotation
		self.stop(0)

	def _moveToParallelPlane(self):
		perpAngle = self.getAdjustedAngle(self.OSCILLATION_ANGLE + math.pi/2)
		# rotate to move (perpendicular to plane of oscillation)
		angleDiff = abs(self.getMyAngle(self.TANK_NUM) - perpAngle)
		while(angleDiff > .001):
			speed = angleDiff/math.pi
			if(speed < .15):
				speed = .15

			# reassign variables
			self.setAngularVelocity(0,speed,perpAngle)
			angleDiff = abs(self.getMyAngle(self.TANK_NUM) - perpAngle)

		self.setAngularVelocity(0,0,perpAngle)

		# move up n units
		originalPosition = self.getMyPosition(0)
		position = originalPosition
		distanceFromEnemyPlane = 200
		while(self.distance(originalPosition, position) < distanceFromEnemyPlane):
			self.commandAgent("speed " + str(self.TANK_NUM) + " " + str(self.VELOCITY))
			position = self.getMyPosition(0)

		# stop
		self.stop(0)
					
	
	def play(self):
		self._moveToParallelPlane()
		
		self._alignTankWithAngle()

		velocity = self.VELOCITY
		lastTime = time.time()
		self.commandAgent("speed " + str(self.TANK_NUM) + " " + str(velocity))
		self.commandAgent("shoot " + str(self.TANK_NUM))
		while 1:
			# reverse direction if enough time has passed
			currTime = time.time()
			if(currTime - lastTime > self.OSCILLATION_THRESHOLD):
				velocity *= -1
				self.commandAgent("speed " + str(self.TANK_NUM) + " " + str(velocity))
				lastTime = currTime
				self.commandAgent("shoot " + str(self.TANK_NUM))
