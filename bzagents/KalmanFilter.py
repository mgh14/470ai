import math
from numpy import matrix, identity


class KalmanFilter():
	
	def __init__(self, noise):
		#initial values
		self.u_initial = matrix([[0],
					 [0],
					 [0],
					 [0],
					 [0],
					 [0]])
		
		self.E_initial = matrix([[100,   0,   0,   0,   0,   0],
					 [  0, 0.1,   0,   0,   0,   0],
					 [  0,   0, 0.1,   0,   0,   0],
					 [  0,   0,   0, 100,   0,   0],
					 [  0,   0,   0,   0, 0.1,   0],
					 [  0,   0,   0,   0,   0, 0.1]])
		
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
		
	def reset(self):
		self.u_initial = matrix([[0],
					 [0],
					 [0],
					 [0],
					 [0],
					 [0]])
		
		self.E_initial = matrix([[100,   0,   0,   0,   0,   0],
					 [  0, 0.1,   0,   0,   0,   0],
					 [  0,   0, 0.1,   0,   0,   0],
					 [  0,   0,   0, 100,   0,   0],
					 [  0,   0,   0,   0, 0.1,   0],
					 [  0,   0,   0,   0,   0, 0.1]])

	def update(self, Z_next, Delta_t):
		F = matrix([[1, Delta_t, Delta_t**2/2, 0,	0,	      0],
			    [0	      1,      Delta_t, 0,	0,	      0],
			    [0,	      0,	    1, 0,	0,	      0],
			    [0,	      0,	    0, 1, Delta_t, Delta_t**2/2],
			    [0,	      0,	    0, 0,	1,	Delta_t],
			    [0,	      0,	    0, 0, 	0, 	      1]])
		
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
