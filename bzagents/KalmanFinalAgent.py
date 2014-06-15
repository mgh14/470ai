import sys
import math
import time

from KalmanFilter import *
from PFFinalAgent import *
from grid_filter_gl import *

class KalmanFinalAgent(PFFinalAgent):
	
	# Member Constants
	WAIT = .2 #wait time between filter updates
	NOISE = 5 #noise for filter, The lab makes it sound like it should be set to 5
	TANK_NUM = 0
	ANG_VEL = .2

	#used for visualization
	#predictionGrid1 = []
	#predictionGrid2 = []
	
	def __init__(self, ip, port):
		PFFinalAgent.__init__(self, ip, port)
		
		# world details
		self.SHOT_SPEED = float(self.constants['shotspeed'])
		
		self.target1 = (0,0, False)
		self.target2 = (0,0, False)
		self.delta = 0.0
		self.kalmanFilter1 = KalmanFilter(self.NOISE)
		self.kalmanFilter2 = KalmanFilter(self.NOISE)
		
		#visualization init
		#init_window(self.worldHalfSize * 2, self.worldHalfSize * 2)
		#init_window(self.worldHalfSize * 2, self.worldHalfSize * 2)		
		#self.resetPredictionGrid(self.predictionGrid1)
		#self.resetPredictionGrid(self.predictionGrid2)
		
		
	def get_new_target(self, enemy, tankNum, kalmanFilterNum, whichKalman):
		# Insert kalman filter here
		enemy_status = enemy[2]
		enemyPosition = self.getAdjustedPoint([float(enemy[4]),float(enemy[5])])
		myPosition = self.getMyPosition(tankNum)
		
		if enemy_status == 'alive':
			kalmanFilterNum.update((enemyPosition[0], enemyPosition[1]), self.delta)
			x, y = kalmanFilterNum.get_enemy_position()
			delta_t = self.distance(myPosition, (x, y)) / self.SHOT_SPEED
			x, y = kalmanFilterNum.get_target(delta_t)
			#self.drawPredictionGrid(x,y,predictionGridNum)
			val = (x, y, True)
			if(whichKalman == 1):
				self.target1 = val
			elif(whichKalman == 2):
				self.target2 = val
		else:
			#self.resetPredictionGrid(predictionGridNum)
			if(whichKalman == 1):
				x, y, t = self.target1
			elif(whichKalman == 2):
				x, y, t = self.target2
			kalmanFilterNum.reset()

			val = (x, y, False)
			if(whichKalman == 1):
				self.target1 = val
			elif(whichKalman == 2):
				self.target2 = val
			
	def tank_controller(self, counter, threshold, tankNum, target):
		tankPoint = self.getMyPosition(tankNum)
		tank_x = tankPoint[0]
		tank_y = tankPoint[1]
		tank_angle = self.getMyAngle(tankNum)
		
		target_x, target_y, alive = target
		distance = self.distance(target, (tankPoint[0], tankPoint[1]))
		target_angle = self.getAdjustedAngle(math.atan2(target_y - tankPoint[1],target_x - tankPoint[0]))
		relative_angle = abs(target_angle - tank_angle)

		#if(counter % 5 == threshold-145):
		if(False):
			hisPosition = self.getAdjustedPoint([float(target[0]),float(target[1])])
			print "\nhisPos: " + str(hisPosition)
			print "target: " + str(target)
			print "targAng: " + str(target_angle) + "; relAng: " + str(relative_angle) 
		

		#if relative_angle <= math.pi and alive:
		angleTolerance = .01
		if relative_angle <= angleTolerance and alive:
			#print "shoot!"
			self.commandAgent("shoot " + str(tankNum))
		
		speed = relative_angle/math.pi
		if(speed < self.ANG_VEL):
			speed = self.ANG_VEL
		self.setAngularVelocityByPoint(tankNum, speed,[target_x,target_y])

	'''def drawPredictionGrid(self,x,y, predictionGrid):
		if x >= self.worldHalfSize * 2:
			x = self.worldHalfSize * 2 - 1
		if y >= self.worldHalfSize * 2:
			y = self.worldHalfSize * 2 - 1
		if x < 0:
			x = 0
		if y < 0:
			y = 0
		predictionGrid[x][y] = 1 #visualization
		update_grid(predictionGrid)
		draw_grid(predictionGrid)'''
		
	'''def resetPredictionGrid(self,predictionGrid):
		predictionGrid = zeros((self.worldHalfSize * 2, self.worldHalfSize * 2))'''
	
	def play(self):

		prev_time = time.time()

		counter = 0
		threshold = 150
		while True:
		
			now = time.time()
			time_diff = now - prev_time
			prev_time = now
		
		
			self.delta += time_diff
		
			me = self._query("mytanks")[0]
			target = self._query("othertanks")[0]
			if self.delta >= self.WAIT:
			
				self.get_new_target(target)
				self.delta = 0.0
			
			self.tank_controller(counter, threshold)
			counter += 1
			if(counter > threshold):
				counter = 0
