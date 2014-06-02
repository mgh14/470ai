import math
from numpy import matrix, identity
from tankUtil import *


class KalmanFilter():

	worldHalfSize = 400
	
	def __init__(self, noise):
		#initial values
		self.reset()
		
		#constant values
		self.E_x = matrix([[0.1,   0, 0,   0,   0, 0],
						   [  0, 0.1, 0,   0,   0, 0],
						   [  0,   0, 1,   0,   0, 0],
						   [  0,   0, 0, 0.1,   0, 0],
						   [  0,   0, 0,   0, 0.1, 0],
						   [  0,   0, 0,   0,   0, 1]])
		
		self.H = matrix([[1.0, 0, 0,   0, 0, 0], 
						 [  0, 0, 0, 1.0, 0, 0]])
		
		self.E_z = matrix([[noise**2,	     0], 
						   [	   0, noise**2]])
		
	def _getEInitialMatrix(self):
		return matrix([[100,   0,   0,   0,   0,   0],
								 [  0, 0.1,   0,   0,   0,   0],
								 [  0,   0, 0.1,   0,   0,   0],
								 [  0,   0,   0, 100,   0,   0],
								 [  0,   0,   0,   0, 0.1,   0],
								 [  0,   0,   0,   0,   0, 0.1]])
	
	def _getUInitialMatrix(self):
		return matrix([[0],
								 [0],
								 [0],
								 [0],
								 [0],
								 [0]])

	def _getFMatrix(self, Delta_t):
		return matrix([[1, Delta_t, Delta_t**2/2, 0,		0,			  0],
					[0,	      1,      Delta_t, 0,		0,			  0],
					[0,	      0,			1, 0,		0,			  0],
					[0,	      0,			0, 1, Delta_t, Delta_t**2/2],
					[0,	      0,			0, 0,		1,		Delta_t],
					[0,	      0,			0, 0,		0,			  1]])

	def reset(self):
		self.u_initial = self._getUInitialMatrix()
		
		self.E_initial = self._getEInitialMatrix()

	def update(self, Z_next, Delta_t):
		F = self._getFMatrix(Delta_t)
		
		FEinitFtrans_plus_Ex = (F * self.E_initial * F.getT()) + self.E_x
		Hportion = self.H * FEinitFtrans_plus_Ex * self.H.getT() + self.E_z
		# it looks like minus 1 on learning suite but I think it is -1 exponent so the inverse of Hportion
		K_next = FEinitFtrans_plus_Ex * self.H.getT() * Hportion.getI()
		
		u_next = F * self.u_initial + K_next * (Z_next - self.H * F * self.u_initial)
		
		KnextH = K_next * self.H
		dim = int(math.sqrt(KnextH.size))
		E_next = (identity(dim) - KnextH) * FEinitFtrans_plus_Ex
		
		self.u_initial = u_next
		self.E_initial = E_next
		
	def get_enemy_position(self):
		m = self.H * self.u_initial
		position = getAdjustedPoint([m[0,0], m[0,1]],self.worldHalfSize)
		return position
		
	def get_target(self, Delta_t):
		F = self._getFMatrix(Delta_t)
		
		u_next = F * self.u_initial
		m = self.H * u_next
		position = (m[0,0], m[0,1])
		return position
		
		
