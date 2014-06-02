import math
from numpy import matrix, identity
from tankUtil import *


class KalmanFilter():

	worldHalfSize = 400
	
	def __init__(self, noise):
		#initial values
		self.reset()
		
		#constant values
		self.E_x = matrix([[.1,  0,  0,  0,  0,  0],
				   [0,  .1,  0,  0,  0,  0],
				   [0,  0,  25,  0,  0,  0],
				   [0,  0,  0,  .1,  0,  0],
				   [0,  0,  0,  0,  .1,  0],
				   [0,  0,  0,  0,  0,  25]])

		self.E_t = self._getEInitialMatrix()
		
		self.H = matrix([[1.0, 0, 0,   0, 0, 0], 
						 [  0, 0, 0, 1.0, 0, 0]])
		
		self.E_z = matrix([[noise**2,	     0], 
						   [	   0, noise**2]])
		
	def _getEInitialMatrix(self):
		return matrix([[15,   0,   0,   0,   0,   0],
				[  0, 5,   0,   0,   0,   0],
				[  0,   0, 5,   0,   0,   0],
				[  0,   0,   0, 15,   0,   0],
				[  0,   0,   0,   0, 5,   0],
				[  0,   0,   0,   0,   0, 5]])
	
	def _getUInitialMatrix(self):
		return matrix([[0],
								 [0],
								 [0],
								 [0],
								 [0],
								 [0]])

	def _getFMatrix(self, Delta_t):
		return matrix([[1, Delta_t, (Delta_t**2)/2, 0,		0,			  0],
					[0,	      1,      Delta_t, 0,		0,			  0],
					[0,	      0,			1, 0,		0,			  0],
					[0,	      0,			0, 1, Delta_t, (Delta_t**2)/2],
					[0,	      0,			0, 0,		1,		Delta_t],
					[0,	      0,			0, 0,		0,			  1]])

	def reset(self):
		self.mu = self._getUInitialMatrix()
		
		self.E_x = self._getEInitialMatrix()

	def update(self, Z_next, Delta_t):
		F = self._getFMatrix(Delta_t)
		
		FEtFtrans_plus_Ex = (F * self.E_t * F.getT()) + self.E_x
		Hportion = self.H * FEtFtrans_plus_Ex * self.H.getT() + self.E_z
		K_next = FEtFtrans_plus_Ex * self.H.getT() * Hportion.getI()
		
		u_next = F * self.mu + K_next * (Z_next - self.H * F * self.mu)
		
		KnextH = K_next * self.H
		dim = int(math.sqrt(KnextH.size))
		E_next = (identity(dim) - KnextH) * FEtFtrans_plus_Ex
		
		self.mu = u_next
		self.E_x = E_next
		
	def get_enemy_position(self):
		m = self.H * self.mu
		position = (m[0,0], m[0,1])
		return position
		
	def get_target(self, Delta_t):
		F = self._getFMatrix(Delta_t)
		
		u_next = F * self.mu
		m = self.H * u_next
		position = (m[0,0], m[0,1])
		return position
		
		
