from Agent import *

# agent that moves in a straight line across the x axis
class ClayPidgeonAgent(Agent):
	
	def __init__(self,ip,port):
		Agent.__init__(self,ip,port)

		self.tankNum = 0
		self.velocity = 0.75
		self.oscillationThreshold = 40	# (in seconds)
		self.oscillationAngle = math.pi

	def _alignTankWithAngle(self):
		# desired angle along which the tank will move in a straight line
		movementAngle = math.pi

		myTanks = self._query("mytanks")
		tank0 = myTanks[self.tankNum]
		angVel = 0.2
		while (abs(self.getAdjustedAngle(float(tank0[8])) - self.oscillationAngle) > .001):
			self.commandAgent("angvel " + str(self.tankNum) + " " + str(angVel))
			tank0 = self._query("mytanks")[self.tankNum]
		
		# stop tank rotation
		self.commandAgent("angvel " + str(self.tankNum) + " 0")

	def _moveToParallelPlane(self):
		perpAngle = self.getAdjustedAngle(self.oscillationAngle - math.pi/2)

		# rotate to move up
		angleDiff = abs(self.getMyAngle(self.tankNum) - perpAngle)
		while(angleDiff > .005):
			print "diff: " + str(angleDiff) + "; myAng: " + str(self.getMyAngle(self.tankNum))
			self.setAngularVelocity(0,.3,perpAngle)
			angleDiff = abs(self.getMyAngle(self.tankNum) - perpAngle)

		self.setAngularVelocity(0,0,perpAngle)

		# move up n units
		originalPosition = self.getMyPosition(0)
		position = originalPosition
		while(position[1] - originalPosition[1] < 100):
			self.commandAgent("speed " + str(self.tankNum) + " .3")
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
