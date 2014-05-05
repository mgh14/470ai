from Agent import *

class DumbAgent(Agent):

	def getRandomShotTolerance(self):
		return (1.5 + random.random())	# between 1.5 and 2.5 seconds

	def getRandomMoveTolerance(self):
		return (3.0 + (random.random() * 5))	# between 3.0 and 8.0 seconds
	
	def play(self):		# driver function for beginning AI simulation
		tanksInfo = self.queryMyTanks()

		angle = self.getAdjustedAngle(float(tanksInfo[0][9]))

		# assign shooting tolerance (tolerance is a measure of time)
		shootTolerance = self.getRandomShotTolerance()
		shootTime = time.time()

		# give initial velocity and assign straight and turning tolerance
		self.commandAgent("speed 0 0.75")
		moveTolerance = self.getRandomMoveTolerance()
		moveTime = time.time()
		while 1:
			currTime = time.time()

			# check to see if the tank should shoot
			if(shootTolerance < (currTime - shootTime)):
				self.commandAgent("shoot 0")
				shootTime = currTime
				shootTolerance = self.getRandomShotTolerance()

			# check to see if the tank should rotate
			if(moveTolerance < (currTime - moveTime)):
				tanksInfo = self.queryMyTanks()
				newAngle = self.getAdjustedAngle(float(tanksInfo[0][9]))
				angleDifference = newAngle - angle
				if(newAngle < angle):
					angleDifference = angle - newAngle
				#print "Angles: " + str(newAngle) + " " + str(angle) + " " + str(angleDifference)
				angularVelocity = float(tanksInfo[0][12])
				#print "AngVel: " + str(angularVelocity) + " " + str(angularVelocity == 0.0)

				if(angularVelocity == 0.0): # start rotating
					self.commandAgent("speed 0 0")
					self.commandAgent("angvel 0 0.25")
				elif(angleDifference > 1.047): # stop rotate and move forward
					self.commandAgent("angvel 0 0")
					self.commandAgent("speed 0 0.75")
					angle = newAngle
					moveTime = currTime
					moveTolerance = self.getRandomMoveTolerance()

