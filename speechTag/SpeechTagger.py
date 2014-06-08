#from nltk import *

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
		self.words = []
		self.model = {}

		self.train(self.DATA_FOLDER + self.TRAIN_PATH)

	def train(self,filepath):
		fileStr = ""
		with open(filepath) as f:
			for line in f:
				fileStr += "\n" + line.strip() + "\n"

		self.tokens = fileStr.split()
		for text in self.tokens:
			#print "text: " + text
			posOfSeparator = text.index(self.SEPARATOR_CHAR)
			word = text[0:posOfSeparator]
			POS = text[posOfSeparator+1:]
			self.words.append(word)
			#print "word: " + word + "; pos: " + POS
		
		numWords = len(self.words)
		for i in xrange(numWords):
			for j in xrange(i+self.gramDegree, min(numWords,i+self.gramDegree)+1):
				
				nGram = tuple(self.words[i:j])
				if i+self.gramDegree > numWords-1:
					break
				nextWordSeen = self.words[i+self.gramDegree]
				#print nGram,
				#print nextWordSeen
				
				nextWordCounts = self.model.get(nGram, {}) 
				if nextWordCounts.has_key(nextWordSeen):
					nextWordCounts[nextWordSeen] = nextWordCounts[nextWordSeen] + 1
				else:
					nextWordCounts[nextWordSeen] = 1
				self.model[nGram] = nextWordCounts
		
		#print self.model
		#print str(len(self.tokens))
		
		
	def generateText()	
		
	def pick_random(prob_list):
		r, s = random.random(), 0
		for num in prob_list:
			s += num[1]
			if s >= r:
				return num[0]

  
#prob_list = [[1, 0.09], [2, 0.9], [3,0.01]]

#for i in xrange(100):
#	print pick_random(prob_list);
		
