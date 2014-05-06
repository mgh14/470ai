import telnetlib
import sys
import time
import random
import math

class Agent:
	# constants	
	SERVER_CONNECT_ACKNOWLEDGED = "bzrobots 1\n"
	NOT_SET = "not_set"

	# member variables
	ipAddr = NOT_SET
	port = NOT_SET
	socket = NOT_SET

	def __init__(self, ip, port):
		self.ipAddr = ip
		self.port = port

		# connect to telnet bzrflag server
		self.socket = telnetlib.Telnet(ip, port)
		response = self.socket.read_until("\n")
		if (response == self.SERVER_CONNECT_ACKNOWLEDGED):
			print "connect to server: successful"
		else:
			print "failed connection!"
			sys.exit(-1)

		# register agent
		self.registerAgent()

	def registerAgent(self):		
		self.socket.write("agent 1\n")
		print "Registration Successful"

	def commandAgent(self, command):
		print "Cmd: " + command
		self.socket.write(command + "\n")
		print "ResponseL1: " + self.socket.read_until("\n").rstrip()
		print "ResponseL2: " + self.socket.read_until("\n")

	def closeSocket(self):
		self.socket.close()

	def _parseList(self,stringList):
		stringList = stringList[6:-5]	# parse off 'begin\n' and 'end\n'
		listOfLines = stringList.split("\n")	# split strings by newline
		
		# split each line by whitespace
		lineArrays = []
		for line in listOfLines:
			lineArrays.append(line.split())

		return lineArrays
	
	def queryMyTanks(self):
		#print "query: mytanks"
		self.socket.write("mytanks\n")
		response = self.socket.read_until("\n").rstrip()
		#print "ResponseL1: " + self.socket.read_until("\n").rstrip()

		# get list of my tanks' info
		myTanks = self.socket.read_until("end\n")
		
		tanksInfo = self._parseList(myTanks)
		
		#print "List:"
		#for tankInfo in tanksInfo:
		#	print str(tankInfo)
		#print "(end list)"

		return tanksInfo
		
	def queryObstacles(self):
		self.socket.write("obstacles\n")
		response = self.socket.read_until("\n")
		obstacles = self.socket.read_until("end\n")
		obstaclesInfo = self._parseList(obstacles)
		return obstaclesInfo
		
	def getObstacles(self):
		obstacles = self.queryObstacles()
		obstacleList = []
		
		for obs in obstacles:
			p1 = (obs[1],obs[2])
			p2 = (obs[3],obs[4])
			p3 = (obs[5],obs[6])
			p4 = (obs[7],obs[8])
			obsTuple = (p1,p2,p3,p4)
			obstacleList.append(obsTuple)
			
		return obstacleList
		
	def queryFlags(self):
		self.socket.write("flags\n")
		response = self.socket.read_until("\n")
		flags = self.socket.read_until("end\n")
		flagsInfo = self._parseList(flags)
		return flagsInfo
		
	def query(self, qString):
		self.socket.write(qString+"\n")
		response = self.socket.read_until("\n")
		response = self.socket.read_until("end\n")
		info = self._parseList(response)
		return info

	def getAdjustedAngle(self,rawAngle):
		if(rawAngle >= 0 and rawAngle < math.pi):
			return rawAngle
		if(rawAngle < 0):
			return 2*math.pi + rawAngle

	def play(self):		# driver function for beginning AI simulation
		print "no implemented play method: tanks will just sit."

