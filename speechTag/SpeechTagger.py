#from nltk import *
import random

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
		self.POS = []
		self.langModel = {}
		self.HMMtransition = {}
		self.HMMemission = {}
		self.HMMstartProbability = {}

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
			pos = text[posOfSeparator+1:]
			self.POS.append(pos)
			self.words.append(word)
			#print "word: " + word + "; pos: " + pos
		
		numWords = len(self.words)
		for i in xrange(numWords):
			for j in xrange(i+self.gramDegree, min(numWords,i+self.gramDegree)+1):
				if i+self.gramDegree > numWords-1:
					break
				########################
				# Build Language Model #
				########################
				nGram = tuple(self.words[i:j])
				nextWordSeen = self.words[i+self.gramDegree]			
				nextWordCounts = self.langModel.get(nGram, {}) 
				if nextWordCounts.has_key(nextWordSeen):
					nextWordCounts[nextWordSeen] = nextWordCounts[nextWordSeen] + 1
				else:
					nextWordCounts[nextWordSeen] = 1
				self.langModel[nGram] = nextWordCounts
				
				########################
				# Build HMM transition #
				########################
				nGram = tuple(self.POS[i:j])
				nextPOS = self.POS[i+self.gramDegree]
				nextPOScounts = self.HMMtransition.get(nGram, {})
				if nextPOScounts.has_key(nextPOS):
					nextPOScounts[nextPOS] = nextPOScounts[nextPOS] + 1
				else:
					nextPOScounts[nextPOS] = 1
				self.HMMtransition[nGram] = nextPOScounts
				
			##############################################
			# Build HMM emission  and start probability  #
			##############################################
			for j in xrange(i+1, min(numWords, i+1)+1):
				pos = self.POS[i:j][0]
				word = self.words[i:j][0]
				posWordCounts = self.HMMemission.get(pos,{})
				if posWordCounts.has_key(word):
					posWordCounts[word] = posWordCounts[word] + 1
				else:
					posWordCounts[word] = 1
				self.HMMemission[pos] = posWordCounts
				
				#start prob
				if self.HMMstartProbability.has_key(pos):
					self.HMMstartProbability[pos] = self.HMMstartProbability[pos] + 1
				else:
					self.HMMstartProbability[pos] = 1
				
			
				

		#print str(len(self.tokens))
		#print self.HMMtransition[("IN","DT","NNP")]
		#print self.HMMemission['IN']
		#print self.HMMstartProbability
		print self.viterbi(['The','economy'],list(set(self.POS)),self.HMMstartProbability,self.HMMtransition,self.HMMemission)
		
		
	def viterbi(self,obs, states, start_p, trans_p, emit_p):
		V = [{}]
		path = {}
	 
		# Initialize base cases (t == 0)
		for y in states:
			#print y
			#print emit_p[y]
			V[0][y] = start_p[y] * emit_p[y].get(obs[0], 1)
			path[y] = [y]
	 
		# Run Viterbi for t > 0
		for t in range(1, len(obs)):
			V.append({})
			newpath = {}
			
			for y in states:
				(prob, state) = max((V[t-1][y0] * trans_p[(y0,)].get(y,1) * emit_p[y].get(obs[t], 1), y0) for y0 in states)
				V[t][y] = prob
				newpath[y] = path[state] + [y]
	 
			# Don't need to remember the old paths
			path = newpath
		n = 0           # if only one element is observed max is sought in the initialization values
		if len(obs)!=1:
			n = t
		#print_dptable(V)
		(prob, state) = max((V[n][y], y) for y in states)
		return (prob, path[state])

		
		
	def generateText(self, nGramSeed, numWordsToGenerate):
		print
		
		nGram = nGramSeed
		#print original seed words
		for n in xrange(self.gramDegree):
			print nGramSeed[n],

		for i in xrange(numWordsToGenerate):
			#print i
			#print nGram
			nextWord = self.pickRandomWord(self.langModel.get(nGram, self.langModel[random.choice(self.langModel.keys())]))
			#builds the next nGram by shifting left and appending new word
			nGram = nGram[1:] + (nextWord,)

			#print nGram, ' <-new'
			print nextWord,
			
		print
		print
		
	def pickRandomWord(self, nextWordDict):
		total = 0
		probabilitiesList = []
		for key, value in nextWordDict.items():
			total = total + int(value)
			probabilitiesList.append([key,float(value)])
		
		for prob in probabilitiesList:
			prob[1] = float(prob[1]) / float(total)
		
		#print total
		#print probabilitiesList
			
	
		r, s = random.random(), 0
		for num in probabilitiesList:
			s += num[1]
			if s >= r:
				return num[0]

  
#prob_list = [[1, 0.09], [2, 0.9], [3,0.01]]

#for i in xrange(100):
#	print pick_random(prob_list);
		
