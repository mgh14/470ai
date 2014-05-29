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
		enemy_x = float(enemy[4])
		enemy_y = float(enemy[5])
		me_x = int(me[6])
		me_y = int(me[7])
		
		if enemy_status == 'alive':
			self.kalmanFilter.update((enemy_x, enemy_y), self.delta)
			x, y = self.kalmanFilter.get_enemy_position()
			delta_t = self.shot_speed / self.distance((me_x, me_y), (x, y))
			#print delta_t
			x, y = self.kalmanFilter.get_target(delta_t)
			self.target = (x, y, True)
		else:
			x, y, t = self.target
			self.kalmanFilter.reset()
			self.target = (x, y, False)
			
	def tank_controller(self, tank):
		tank_index = tank[0]
		tank_x = int(tank[6])
		tank_y = int(tank[7])
		tank_angle = self.getAdjustedAngle(float(tank[8]))
		
		target_x, target_y, alive = self.target
		distance = self.distance(self.target, (tank_x, tank_y))
		target_angle = self.getAdjustedAngle(math.atan2(target_y - tank_y,target_x - tank_x))
		relative_angle = self.getAdjustedAngle(target_angle - tank_angle)
		if relative_angle <= .005 and alive:
			self.commandAgent("shoot " + tank_index)
		self.commandAgent("angvel " + str(tank_index) + " " + str(relative_angle))
		
	def distance(self, a , b):
		return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)


	def play(self):

		prev_time = time.time()

	
		while True:
		
			now = time.time()
			time_diff = now - prev_time
			prev_time = now
		
		
			#print time_diff
			self.delta += time_diff
		
			myTanksInfo = self._query("mytanks")
			otherTanksInfo = self._query("othertanks")
			flagsInfo = self._query("flags")
			target = otherTanksInfo[0]
			me = myTanksInfo[0]
			#self.kalmanFilter.update((target.x, target.y), time_diff)
			if self.delta >= self.WAIT:
			
				self.get_new_target(target, me)
				self.delta = 0.0
			
			for tank in myTanksInfo:
				self.tank_controller(tank)
		
