import telnetlib
import sys
import time
import random
import math
import GnuplotUtil

class Agent(object):
	# constants	
	SERVER_DELIMITER = "\n"
	LIST_START = "start" + SERVER_DELIMITER
	LIST_END = "end" + SERVER_DELIMITER
	SERVER_CONNECT_ACKNOWLEDGED = "bzrobots 1" + SERVER_DELIMITER
	NOT_SET = "not_set"

	# member variables
	ipAddr = NOT_SET
	port = NOT_SET
	socket = NOT_SET
	constants = dict()
	iHaveEnemyFlag = False
	worldHalfSize = NOT_SET
	myBaseCoords = NOT_SET
	myFlagStand = NOT_SET

	def __init__(self, ip, port):
		self.ipAddr = ip
		self.port = port

		# connect to telnet bzrflag server
		self.socket = telnetlib.Telnet(ip, port)
		response = self.socket.read_until(self.SERVER_DELIMITER)
		if (response == self.SERVER_CONNECT_ACKNOWLEDGED):
			print "connect to server: successful"
		else:
			print "failed connection!"
			sys.exit(-1)

		# register and prepare agent
		self.registerAgent()
		self.loadConstants()
		self.setMyBase()
		self.setMyFlagStand()

	def registerAgent(self):		
		self.socket.write("agent 1" + self.SERVER_DELIMITER)
		print "Registration Successful"

	def loadConstants(self):
		constList = self._query("constants")
		for item in constList:
			self.constants[item[0]] = item[1]

		self.worldHalfSize = int(self.constants["worldsize"]) / 2

	def setMyBase(self):
		bases = self._query("bases")

		for base in bases:
			if(base[0] == self.constants["team"]):
				self.myBaseCoords = [(int(float(base[1])),int(float(base[2]))),
							(int(float(base[3])),int(float(base[4]))),
							(int(float(base[5])),int(float(base[6]))),
							(int(float(base[7])),int(float(base[8])))]

				return

		print "Error: no base assigned!"
		
	def setMyFlagStand(self):
		flags = self._query("flags")
		
		for flag in flags:
			if(flag[0] == self.constants["team"]):
				self.myFlagStand = [int(float(flag[2])),int(float(flag[3]))]

	def commandAgent(self, command):
		print "Cmd: " + command
		self.socket.write(command + self.SERVER_DELIMITER)
		print "ResponseL1: " + self.socket.read_until(self.SERVER_DELIMITER).rstrip()
		print "ResponseL2: " + self.socket.read_until(self.SERVER_DELIMITER)

	def closeSocket(self):
		self.socket.close()

	# for game queries
	def _query(self, queryCommand):
		#print "query: " + query
		self.socket.write(queryCommand + self.SERVER_DELIMITER)
		response = self.socket.read_until(self.SERVER_DELIMITER).rstrip();
		#print "ResponseL1: " + response

		stringList = self.socket.read_until(self.LIST_END)

		stringList = stringList[len(self.LIST_START):-1*(len(self.LIST_END) + 1)]  # parse off 'begin\n' and 'end\n'
		listOfLines = stringList.split(self.SERVER_DELIMITER)  # split strings by newline
		
		# split each line by whitespace
		lineArrays = []
		for line in listOfLines:
			array = line.split()
			array.pop(0)
			lineArrays.append(array)

		return lineArrays

	def _getRawResponse(self, queryCommand):
		#print "query: " + query
		self.socket.write(queryCommand + self.SERVER_DELIMITER)
		response = self.socket.read_until(self.SERVER_DELIMITER).rstrip();
		#print "ResponseL1: " + response

		stringList = self.socket.read_until(self.LIST_END)
		return stringList

	def printList(self,listToPrint):
		print "List:"
		for current in listToPrint:
			print str(current)
		print "(end list)"

	def _isCoordinateInBase(self, coords):
		# top-right corner check
		trCorner = (coords[0] < self.myBaseCoords[0][0] and 						coords[1] < self.myBaseCoords[0][1])

		# bottom-right corner check
		brCorner = (coords[0] < self.myBaseCoords[1][0] and 						coords[1] > self.myBaseCoords[1][1])

		# bottom-left corner check
		blCorner = (coords[0] > self.myBaseCoords[2][0] and 						coords[1] > self.myBaseCoords[2][1])

		# top-left corner check
		tlCorner = (coords[0] > self.myBaseCoords[3][0] and 						coords[1] < self.myBaseCoords[3][1])

		return (trCorner and brCorner and blCorner and tlCorner)

	def _isMyFlagInMyBase(self):
		flags = self._query("flags")

		for flag in flags:
			if(flag[0] == self.constants["team"]):
				return self._isCoordinateInBase(self._getMyFlagPosition())
		return -1

	def _isMyFlagCaptured(self):
		flags = self._query("flags")

		for flag in flags:
			if(flag[0] == self.constants["team"]):
				return (not (flag[1] == self.constants["team"]))

		return -1

	def _getMyFlagPosition(self):
		flags = self._query("flags")

		for flag in flags:
			if(flag[0] == self.constants["team"]):
				return [int(float(flag[2])),int(float(flag[3]))]

		return [-10000,-10000]	# represents an error (should be found above)

	def _getEnemyFlagPositions(self):
		flags = self._query("flags")
		
		positions = []
		for flag in flags:
			if(flag[0] == self.constants["team"]):
				continue

			positions.append((int(float(flag[2])),int(float(flag[3]))))

		return positions

	def _iHaveEnemyFlag(self):
		flags = self._query("flags")

		for flag in flags:
			if(flag[0] == self.constants["team"]):	# don't count my own flag
				continue

			if(flag[1] == self.constants["team"]):
				return True

		return False

	def getAdjustedAngle(self,rawAngle):
		twoPi = 2*math.pi
		if(rawAngle > twoPi):
			rawAngle = math.fmod(rawAngle,twoPi)

		if(rawAngle >= 0) and (rawAngle < math.pi):
			return rawAngle
		if(rawAngle < 0):
			return twoPi + rawAngle

		return rawAngle

	def _translateComponentCoord(self,cCoord):
		if(cCoord > 0):
			cCoord += self.worldHalfSize
		else:
			cCoord = self.worldHalfSize + cCoord

		return cCoord

	def getAdjustedPoint(self,point):
		return [self._translateComponentCoord(point[0]), self._translateComponentCoord(point[1])]
			

	def play(self):		# driver function for beginning AI simulation
		print "no implemented play method: tanks will just sit."

