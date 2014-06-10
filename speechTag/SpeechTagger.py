#from nltk import *
import random
import math
import time

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
		self.POSdict = {}
		self.langModel = {}
		self.HMMtransition = {}
		self.HMMemission = {}
		self.HMMstartProbability = {}
		self.totalPOScount = {}
		self.transitionTotal = {}

		self.train(self.DATA_FOLDER + self.TRAIN_PATH)

	def train(self,filepath):
		print "Training on data..."
		startTime = time.time() 

		fileStr = ""
		with open(filepath) as f:
			for line in f:
				fileStr += "\n" + line.strip() + "\n"

		self.tokens = fileStr.split()
		counter = 0
		for text in self.tokens:
			#print "text: " + text
			posOfSeparator = text.index(self.SEPARATOR_CHAR)
			word = text[0:posOfSeparator].lower()
			pos = text[posOfSeparator+1:]
			self.POS.append(pos)
			self.POSdict[pos] = pos
			counter += 1
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
				if not nextPOScounts.has_key('total'):
					nextPOScounts['total'] = 0
				if nextPOScounts.has_key(nextPOS):
					nextPOScounts[nextPOS] += 1
					nextPOScounts['total'] += 1
				else:
					nextPOScounts['total'] += 1
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
		
		for key in self.HMMstartProbability:
			self.HMMstartProbability[key] /= float(len(self.POS))
		
		for key in self.HMMtransition:
			for posKey in self.HMMtransition[key]:
				if posKey == 'total':
					self.transitionTotal[key] = self.HMMtransition[key]['total']
					continue
				self.HMMtransition[key][posKey] /= float(self.HMMtransition[key]['total'])

			del self.HMMtransition[key]['total']
			
		for key in self.HMMemission:
			total = 0
			for word in self.HMMemission[key]:
				total += self.HMMemission[key][word]
			self.totalPOScount[key] = total
			
		for key in self.HMMemission:
			for word in self.HMMemission[key]:
				self.HMMemission[key][word] /= float(self.totalPOScount[key])

		print "Training finished in " + str(time.time() - startTime) + " seconds"
		
	def viterbi(self, obs, states, start_p, trans_p, emit_p):
		origTime = time.time()
		V = {0: {}}
		path = {}
	 
		# Initialize base cases (t == 0)
		for y in states:
			#V[0][y] = start_p[y] * emit_p[y].get(obs[0], 0.1/self.totalPOScount[y])
			smoothingConst = float(.1) / self.totalPOScount[y]
			V[0][y] = math.log(start_p[y]) + math.log(emit_p[y].get(obs[0], smoothingConst))
			path[y] = [y]
	 
		# Run Viterbi for t > 0
		for t in range(1, len(obs)):
			if(t % 10000 == 0):
				print "Calculating t=" + str(t) + " (" + str(time.time()-origTime) + " seconds elapsed)..."
			V[t] = {}
			newpath = {}
			
			for y in states:				
				transitionConst = float(.1) / self.transitionTotal[(y,)]
				emitConst = float(.1) / self.totalPOScount[y]

				(prob, state) = max((V[t-1][y0] + math.log(trans_p[(y0,)].get(y,transitionConst)) + math.log(emit_p[y].get(obs[t], emitConst)), y0) for y0 in states)

				V[t][y] = prob
				newpath[y] = path[state] + [y]
	 
			# Don't need to remember the old paths
			path = newpath

		n = 0           # if only one element is observed max is sought in the initialization values
		if len(obs)!=1:
			n = t

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

	def parseTestFile(self, filepath):
		fileStr = ""
		with open(filepath) as f:
			for line in f:
				fileStr += "\n" + line.strip() + "\n"

		tokens = fileStr.split()
		POS = []
		words = []
		counts = {}
		for text in self.tokens:
			#print "text: " + text
			posOfSeparator = text.index(self.SEPARATOR_CHAR)
			word = text[0:posOfSeparator].lower()
			pos = text[posOfSeparator+1:]
			POS.append(pos)
			if pos in counts:
				counts[pos] += 1
			else:
				counts[pos] = 1

			words.append(word)
			#print "word: " + word + "; pos: " + pos		

		return (tokens, words, POS, counts)

  	def classifyTestData(self):
		testArrays = self.parseTestFile(self.DATA_FOLDER + self.TRAIN_PATH)
		#for a in range(0,len(testArrays[0])-1):
		#	print "here: " + str(testArrays[0][a]) + "; " + str(testArrays[1][a]) + "; " + str(testArrays[2][a])
		
		print "Running Viterbi..."
		startTime = time.time()
		(prob, tags) = self.viterbi(testArrays[1],self.POSdict,self.HMMstartProbability,self.HMMtransition,self.HMMemission)
		print "Finished classifying in " + str(time.time() - startTime) + " seconds."
		
		counter = 0
		counts = {}
		testCounts = testArrays[3]
		for a in range(0,len(tags)-1):
			if(tags[a] != testArrays[2][a]):
				counter += 1
			else:
				if tags[a] in counts:
					counts[tags[a]] += 1
				else:
					counts[tags[a]] = 1
				
		for key in testCounts:
			val = 0
			if key in counts:
				val = counts[key]
			print "Class \'" + key + "\': " + str(val) + " out of " + str(testCounts[key]) + " (" + str(float(val)*100/testCounts[key]) + "%)"

		correct = len(tags) - counter
		print str(correct) + " total words correctly classified out of " + str(len(tags)) + " (" + str(float(correct)*100/len(tags)) + "%)"

