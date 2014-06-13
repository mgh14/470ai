#from nltk import *
import random
import math
import time
import sys
class SpeechTagger2Gram(object):
	
	# Member constants
	DATA_FOLDER = "assignment3data/"
	TRAIN_PATH = "allTraining.txt"
	TEST_PATH = "devtest.txt"
	SEPARATOR_CHAR = "_"

	def __init__(self,gramDegree):
		# Member variables
		self.gramDegree = gramDegree
		self.trainingTokens = []
		self.words = []
		self.POS = []
		self.POSdict = {}
		self.langModel = {}
		self.HMMtransition = {}
		self.HMMemission = {}
		self.HMMstartProbability = {}
		self.totalPOScount = {}
		self.transitionTotal = {}
		self.defaultProb = .00001

		self.train(self.DATA_FOLDER + self.TRAIN_PATH)

	def train(self,filepath):
		print "Training on data..."
		startTime = time.time() 

		fileStr = ""
		with open(filepath) as f:
			for line in f:
				fileStr += "\n" + line.strip()

		self.trainingTokens = fileStr.split()
		counter = 0
		for text in self.trainingTokens:
			if self.SEPARATOR_CHAR in text:
				posOfSeparator = text.index(self.SEPARATOR_CHAR)
				word = text[0:posOfSeparator].lower()
				pos = text[posOfSeparator+1:]
			else:
				word = text
				pos = text

			self.POS.append(pos)
			self.POSdict[pos] = pos
			counter += 1
			self.words.append(word)
		
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
				
				#start prob
				if self.HMMstartProbability.has_key(nGram):
					self.HMMstartProbability[nGram] += 1
				else:
					self.HMMstartProbability[nGram] = 1
				
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
		
	def viterbi(self, wordSequence, states, startProbs, transProbs, emitProbs):	
		origTime = time.time()
		V = {0:{}}

		for state1 in states:
			for state2 in states:
				startProb = startProbs.get((state1, state2), self.defaultProb)
				V[0][(state1,state2)] = math.log(startProb) + math.log(emitProbs.get(wordSequence[0], self.defaultProb))

		for k in xrange(1,len(wordSequence)):
			if(k % 100 == 0):
				print "Calculating k=" + str(k) + " (" + str(time.time()-origTime) + " seconds elapsed)..."
			V[k] = {}
			for prevState in states:
				for currState in states:
					# calculate highest probability and associated 
					# argmax (which state provides highest probability)
					(prob, state) = max((V[k-1][(twoPrevState,prevState)] + math.log(transProbs.get((twoPrevState,prevState),{}).get(currState,self.defaultProb)) + math.log(emitProbs[currState].get(wordSequence[k], self.defaultProb)), twoPrevState) for twoPrevState in states)

					V[k][(prevState,currState)] = prob

			# re-assign to most likely key
			(myprob, mykey) = max((V[k-1][key],key) for key in V[k-1].keys())
			V[k-1] = mykey

		# do once more for the last entry in V
		(myprob, mykey) = max((V[k][key],key) for key in V[k].keys())			
		V[k] = mykey

		n = 0
		if len(wordSequence) != 1:
			n = k
		
		path = []
		for n in range(1,len(V)):
			path += [V[n][0]]

		return path

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
		fileWords = []
		counts = {}
		counter = 0
		for text in tokens:
			if self.SEPARATOR_CHAR in text:
				posOfSeparator = text.index(self.SEPARATOR_CHAR)
				word = text[0:posOfSeparator].lower()
				pos = text[posOfSeparator+1:]
			else:
				word = text
				pos = text

			POS.append(pos)
			if pos in counts:
				counts[pos] += 1
			else:
				counts[pos] = 1

			fileWords.append(word)

		return (tokens, fileWords, POS, counts)

  	def classifyTestData(self):
		path = self.DATA_FOLDER + self.TEST_PATH
		print "Parsing test file " + path
		testArrays = self.parseTestFile(path)
		tokens = testArrays[0]
		fileWords = testArrays[1]
		POS = testArrays[2]
		testCounts = testArrays[3]
		
		# tag the words in the sequence
		print str(len(fileWords)) + " words to be classified from " + self.TEST_PATH
		print "Running Viterbi..."
		startTime = time.time()
		tags = self.viterbi(fileWords,self.POSdict,self.HMMstartProbability,self.HMMtransition,self.HMMemission)
		print "Finished classifying in " + str(time.time() - startTime) + " seconds."
		
		# print out statistics
		counter = 0
		counts = {}
		misClassified = {}
		correctClassified = {}
		for a in range(0,len(tags)-1):
			tag = tags[a]
			correctTag = POS[a]
			if(tag != correctTag):
				counter += 1

				if(correctTag in misClassified.keys()):
					if(tag in misClassified[correctTag]):
						misClassified[correctTag][tag] += 1
					else:
						misClassified[correctTag][tag] = 1
				else:
					misClassified[correctTag] = {}
					misClassified[correctTag][tag] = 1
			else:
				if(correctTag in correctClassified.keys()):
					if(tag in correctClassified[correctTag]):
						correctClassified[correctTag][tag] += 1
					else:
						correctClassified[correctTag][tag] = 1
				else:
					correctClassified[correctTag] = {}
					correctClassified[correctTag][tag] = 1
			
			if tag in counts:
				counts[tag] += 1
			else:
				counts[tag] = 1
		
		print "\nIncorrect Classifications:"
		for key in misClassified:
			print key + " classified as: "
			for tag in misClassified[key]:
				print "\t" + tag + ": " + str(misClassified[key][tag])

		print "\nCorrect Classifications:"
		for key in correctClassified:
			print key + " classified as: " 
			for tag in correctClassified[key]:
				print "\t" + tag + ": " + str(correctClassified[key][tag])
		
		print "\nTotal Classifications:"		
		for key in testCounts:
			val = 0
			if key in counts:
				val = counts[key]
			print "Class \'" + key + "\': " + str(val) + " out of " + str(testCounts[key]) + " (" + str(float(val)*100/testCounts[key]) + "%)"

		correct = len(tags) - counter
		print str(correct) + " total words correctly classified out of " + str(len(tags)) + " (" + str(float(correct)*100/len(tags)) + "%)"
