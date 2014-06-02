import sys
import math
import time

from KalmanFilter import *
from PFAgent import *
from grid_filter_gl import *

class KalmanAgent(PFAgent):
	
	# Member Constants
	WAIT = .2 #wait time between filter updates
	NOISE = 5 #noise for filter, The lab makes it sound like it should be set to 5
	TANK_NUM = 0
	ANG_VEL = .2
	
	def __init__(self, ip, port):
		Agent.__init__(self, ip, port)
		self._initializePF()
		
		# world details
		self.shot_speed = float(self.constants['shotspeed'])
		
		self.target = (0,0, False)
		self.delta = 0.0
		self.kalmanFilter = KalmanFilter(self.NOISE)
		
		
	def get_new_target(self, enemy, me):
		# Insert kalman filter here
		enemy_status = enemy[2]
		enemyPosition = self.getAdjustedPoint([float(enemy[4]),float(enemy[5])])
		myPosition = self.getAdjustedPoint([int(me[6]),int(me[7])])
		
		if enemy_status == 'alive':
			self.kalmanFilter.update(enemyPosition, self.delta)
			x, y = self.kalmanFilter.get_enemy_position()
			delta_t = self.distance(myPosition, (x, y)) / self.shot_speed
			#print delta_t
			x, y = self.kalmanFilter.get_target(delta_t)
			self.target = (x, y, True)
		else:
			x, y, t = self.target
			self.kalmanFilter.reset()
			self.target = (x, y, False)
			
	def tank_controller(self, tank, counter,threshold):
		tankPoint = self.getAdjustedPoint([int(tank[6]),int(tank[7])])
		tank_x = tankPoint[0]
		tank_y = tankPoint[1]
		tank_angle = self.getAdjustedAngle(float(tank[8]))
		
		target_x, target_y, alive = self.target
		distance = self.distance(self.target, (tank_x, tank_y))
		target_angle = self.getAdjustedAngle(math.atan2(target_y - tank_y,target_x - tank_x))
		relative_angle = abs(target_angle - tank_angle)

		if(counter > threshold):
			otherTank = self._query("othertanks")[0]
			hisPosition = self.getAdjustedPoint([float(otherTank[4]),float(otherTank[5])])
			print "\nhisPos: " + str(hisPosition)
			print "target: " + str(self.target)
			print "targAng: " + str(target_angle) + "; relAng: " + str(relative_angle) 
		


		if relative_angle <= .001 and alive:
			print "shoot!"
			self.commandAgent("shoot " + str(self.TANK_NUM))
		
		self.setAngularVelocityByPoint(self.TANK_NUM, relative_angle,[target_x,target_y])

	def play(self):

		prev_time = time.time()
		otherTankNum = 0
	
		counter = 0
		threshold = 150
		while True:
		
			now = time.time()
			time_diff = now - prev_time
			prev_ti1me = now
		
		
			#print time_diff
			self.delta += time_diff
		
			myTanksInfo = self._query("mytanks")
			otherTanksInfo = self._query("othertanks")

			target = otherTanksInfo[otherTankNum]
			me = myTanksInfo[self.TANK_NUM]

			if self.delta >= self.WAIT:
			
				self.get_new_target(target, me)
				self.delta = 0.0

			self.tank_controller(me,counter,threshold)
			if(counter > threshold):
				counter = 0
			counter += 1
