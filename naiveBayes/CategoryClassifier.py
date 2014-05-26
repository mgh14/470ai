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
		for directory in self.trainFiles:	# for each class, do the following:
			print "loading dir " + directory + "..."

			classWords = dict()
			for doc in self.trainFiles[directory]:
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

			numDocsInClass = len(self.trainFiles[directory])
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

				# replace special chars chars with spaces
				specialCharLine = re.sub(r'(@|\.|-|\n)+',' ',line)

				# only keep alphanumeric characters and spaces
				strippedLine = re.sub(r'([^\s\w]|_)+', '', specialCharLine)
				arr = strippedLine.split()	# splits on whitespace by default
				for word in arr:
					if(word != '' and word not in self.stopWords):
						if(word in wordArray):
							wordArray[word] += 1
						else:
							wordArray[word] = 1
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

	def classifyTestData(self):
		for className in self.testFiles:
			classDocs = self.testFiles[className]

			docClass = self.classes[className]
			for doc in classDocs:
				filepath = str(self.PATH_TO_TEST_DATA + className + "/" + doc)
				classification = self.classifyDoc(filepath)
				#print "classification: " + filepath

		print "finished classifying data."

	def classifyDoc2(self,filename):
		print "\tclassifying: " + filename
		
	def classifyDoc(self,filename):
		print "classifying: " + filename
		pass
		fileWordArray = self.loadFile(filename)
		#print "filewords: " + str(fileWordArray)
		# calculate probabilities of each class:
		classProbabilities = dict()
		for className in self.classes:
			docClass = self.classes[className]
			
			# start probability calc with p(class)
			classProbabilities[className] = 0
			classProbability = docClass.getDocCount() / self.totalDocs
			classWordCount = docClass.getWordCount()
			for word in fileWordArray:
				try:
					numOccurrences = docClass.words[word]
				except KeyError:
					numOccurrences = 1	# smoothing effect

				#classProbability = (numOccurrences/classWordCount)^^fileWordArray[word] * classProbability
				print "\tVal for " + className + ":" + word + ": " + str(numOccurrences)
				print "\t" + word + " " + str(fileWordArray[word])
				#print "\tprob of word: " + str(probabilityOfWord)
				print "\tprobability: " + str(numOccurrences) + "/" + str(classWordCount) + "=" + str(numOccurrences/classWordCount)
			#classProbabilities[className] = classProbability
			print "p(class | d): " + str(classProbabilities[className])

			sys.exit(0)
		
		# figure out which of the probabilities for each class is the highest
		highestProbability = NOT_SET
		mostLikelyClass = NOT_SET
		for className in classProbabilities:
			classProbability = classProbabilities[className]
			if(classProbability > highestProbability):
				highestProbability = classProbability
				highestClass = className

		return [mostLikelyClass,highestProbability]
