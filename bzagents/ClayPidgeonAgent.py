from Agent import *

# agent that moves in a straight line across the x axis
class ClayPidgeonAgent(Agent):
	
	def __init__(self,ip,port):
		Agent.__init__(self,ip,port)

		self.tankNum = 0
		self.velocity = 0.75
		self.oscillationThreshold = 40	# (in seconds)

	def _alignTankWithAngle(self):
		# desired angle along which the tank will move in a straight line
		movementAngle = math.pi

		myTanks = self._query("mytanks")
		tank0 = myTanks[self.tankNum]
		angVel = 0.2
		while (self.getAdjustedAngle(float(tank0[8])) - math.pi > .005):
			self.commandAgent("angvel " + str(self.tankNum) + " " + str(angVel))
			tank0 = self._query("mytanks")[self.tankNum]
		
		# stop tank rotation
		self.commandAgent("angvel " + str(self.tankNum) + " 0")

	def play(self):
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
