def getAdjustedAngle(self,rawAngle):
	rawAngle = float(rawAngle)

	twoPi = 2*math.pi
	if(rawAngle > twoPi):
		return math.fmod(rawAngle,twoPi)

	if(rawAngle >= 0) and (rawAngle < math.pi):
		return rawAngle
	if(rawAngle < 0):
		return twoPi + rawAngle

	return rawAngle

def getAdjustedPoint(point, worldHalfSize):
	return [worldHalfSize + point[0],worldHalfSize + point[1]]
