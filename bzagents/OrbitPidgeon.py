from ClayPidgeonAgent import *

class OrbitPidgeon(ClayPidgeonAgent):

	def __init__(self,host,ip):
		ClayPidgeonAgent.__init__(self,host,ip)

		self.VELOCITY = 1
		self.ANG_VELOCITY = -.2

	def _alignTankWithAngle(self, angle):
		relAngle = abs(self.getMyAngle(self.TANK_NUM) - angle)
		while (relAngle > .001):
			speed = relAngle/math.pi
			if(speed < .15):
				speed = .15
	
			# reassign variables
			self.setAngularVelocity(0,speed,angle)
			relAngle = abs(self.getMyAngle(0) - angle)
		
		# stop tank rotation
		self.stop(0)

	def _moveTankToHalfwayPoint(self):
		# move up n units
		originalPosition = self.getMyPosition(0)
		position = originalPosition
		distanceFromEnemyBase = 140	# bases 300 pixels part
		while(self.distance(originalPosition, position) < distanceFromEnemyBase):
			self.commandAgent("speed " + str(self.TANK_NUM) + " " + str(self.VELOCITY))
			position = self.getMyPosition(0)

		# stop
		self.stop(0)


	def play(self):
		angle = 0
		self._alignTankWithAngle(angle)
		self._moveTankToHalfwayPoint()
		self._alignTankWithAngle(angle + math.pi/2)
		
		# orbit
		self.commandAgent("angvel " + str(self.TANK_NUM) + " " + str(self.ANG_VELOCITY))
		self.commandAgent("speed " + str(self.TANK_NUM) + " " + str(self.VELOCITY))
		
