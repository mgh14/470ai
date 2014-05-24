from DocClassifier import *
from ClassHolder import *
from DocHolder import *

class CategoryClassifier(DocClassifier):
	classes = NOT_SET
	totalDocs = NOT_SET

	testData = NOT_SET

	def __init__(self):
		DocClassifier.__init__(self)

		self.classes = dict()
		self.totalDocs = 0

		self._train()

	def _train(self):
		print "Training from files:"
		for directory in self.files:	# for each class, do the following:
			print "loading dir " + directory + "..."

			classWords = dict()
			for doc in self.files[directory]:
				fileWordArray = self.loadFile(self.PATH_TO_TRAINING_DATA + directory + "/" + doc)
				for word in fileWordArray:
					#if(word in self.words):
					#	self.words[word] += 1
					#else:
					#	self.words[word] = 1
					numOfThisWord = fileWordArray[word]		
					if(word in classWords):
						classWords[word] += numOfThisWord
					else:
						classWords[word] = numOfThisWord

			numDocsInClass = len(self.files[directory])
			self.classes[directory] = ClassHolder(directory,numDocsInClass,classWords)
			print "\tnumWords in " + directory + ": " + str(self.classes[directory].getWordCount())
			print "\tnumDocs in " + directory + ": " + str(self.classes[directory].getDocCount())

			# add docs in class to total doc count
			self.totalDocs += numDocsInClass

		print "\nFinished training. " + str(self.totalDocs) + " docs evaluated over " + str(len(self.classes)) + " classes."

	def loadFile(self,filename):
		wordArray = dict()
		with open(filename) as f:
			for line in f:
				line = str.lower(line.strip())
				if(len(line) <= 0):
					continue

				# replace '@' and '.' chars with spaces
				domainReplaceLine = re.sub(r'(@|\.|-|\n)+',' ',line)

				# only keep alphanumeric characters and spaces
				strippedLine = re.sub(r'([^\s\w]|_)+', '', domainReplaceLine)
				arr = strippedLine.split()	# splits on whitespace by default
				for word in arr:
					if(word != '' and word not in self.stopWords):
						if(word in wordArray):
							wordArray[word] += 1
						else:
							wordArray[word] = 1
		#print str(wordArray)
		return wordArray

	def classifyDocByBaseline(self,filename):
		maxClass = NOT_SET
		highestDocs = 0
		for newsClass in self.classes:
			classObj = self.classes[newsClass]

			currDocCount = classObj.getDocCount()
			if(currDocCount > highestDocs):
				highestDocs = currDocCount
				maxClass = newsClass

		return maxClass

	def classifyDoc(self,filename):
		fileWordArray = self.loadFile(filename)
		#print "filewords: " + str(fileWordArray)
		# calculate probabilities of each class:
