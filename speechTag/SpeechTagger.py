from nltk import *

class SpeechTagger(object):
	
	# Member constants
	DATA_FOLDER = "assignment3data/"
	TRAIN_PATH = "allTraining.txt"
	TEST_PATH = "devTest.txt"
	SEPARATOR_CHAR = "_"

	def __init__(self,gramDegree):
		# Member variables
		self.gramDegree = gramDegree
		self.tokens = []

		self.train(self.DATA_FOLDER + self.TRAIN_PATH)

	def train(self,filepath):
		fileStr = ""
		with open(filepath) as f:
			for line in f:
				fileStr += "\n" + line.strip() + "\n"

		self.tokens = fileStr.split()
		previousWords = []
		for text in self.tokens:
			#print "text: " + text
			posOfSeparator = text.index(self.SEPARATOR_CHAR)
			word = text[0:posOfSeparator]
			POS = text[posOfSeparator+1:]
			#print "word: " + word + "; pos: " + POS
		print str(len(self.tokens))
