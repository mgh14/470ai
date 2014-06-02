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
	ANG_VEL = .3
	#used for visualization
	predictionGrid = []
	
	def __init__(self, ip, port):
		Agent.__init__(self, ip, port)
		self._initializePF()
		
		# world details
		self.shot_speed = float(self.constants['shotspeed'])
		
		self.target = (0,0, False)
		self.delta = 0.0
		self.kalmanFilter = KalmanFilter(self.NOISE)
		
		#visualization init
		init_window(self.worldHalfSize * 2, self.worldHalfSize * 2)
		self.resetPredictionGrid()
		
		
	def get_new_target(self, enemy, me):
		# Insert kalman filter here
		enemy_status = enemy[2]
		enemyPosition = self.getAdjustedPoint([float(enemy[4]),float(enemy[5])])
		enemy_x = enemyPosition[0]
		enemy_y = enemyPosition[1]
		myPosition = self.getAdjustedPoint([int(me[6]),int(me[7])])
		me_x = myPosition[0]
		me_y = myPosition[1]
		
		if enemy_status == 'alive':
			self.kalmanFilter.update((enemy_x, enemy_y), self.delta)
			x, y = self.kalmanFilter.get_enemy_position()
			delta_t = self.shot_speed / self.distance((me_x, me_y), (x, y))
			#print delta_t
			x, y = self.kalmanFilter.get_target(delta_t)
			self.drawPredictionGrid(x,y)
			self.target = (x, y, True)
		else:
			self.resetPredictionGrid()
			x, y, t = self.target
			self.kalmanFilter.reset()
			self.target = (x, y, False)
			
	def tank_controller(self, tank):
		tankPoint = self.getAdjustedPoint([int(tank[6]),int(tank[7])])
		tank_x = tankPoint[0]
		tank_y = tankPoint[1]
		tank_angle = self.getAdjustedAngle(float(tank[8]))
		
		target_x, target_y, alive = self.target
		distance = self.distance(self.target, (tank_x, tank_y))
		target_angle = self.getAdjustedAngle(math.atan2(target_y - tank_y,target_x - tank_x))
		relative_angle = abs(self.getAdjustedAngle(target_angle - tank_angle))
		if relative_angle <= .005 and alive:
			self.commandAgent("shoot " + str(self.TANK_NUM))
		#self.commandAgent("angvel " + str(self.TANK_NUM) + " " + str(relative_angle))
		self.setAngularVelocityByPoint(self.TANK_NUM, self.ANG_VEL,[target_x,target_y])

	def drawPredictionGrid(self,x,y):
		self.predictionGrid[x][y] = 1 #visualization
		update_grid(self.predictionGrid)
		draw_grid()
		
	def resetPredictionGrid(self):
		self.predictionGrid = zeros((self.worldHalfSize * 2, self.worldHalfSize * 2))
	
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
			#flagsInfo = self._query("flags")
			target = otherTanksInfo[0]
			me = myTanksInfo[self.TANK_NUM]
			#self.kalmanFilter.update((target.x, target.y), time_diff)
			if self.delta >= self.WAIT:
			
				self.get_new_target(target, me)
				self.delta = 0.0
			
			for tank in myTanksInfo:
				self.tank_controller(tank)
		
