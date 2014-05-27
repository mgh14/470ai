from DocClassifier import *
from ClassHolder import *

class BernoulliClassifier(DocClassifier):
	allWords = NOT_SET
	classes = NOT_SET
	totalDocs = NOT_SET

	testData = NOT_SET

	def __init__(self):
		DocClassifier.__init__(self)

		self.allWords = dict()
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
					if(word in classWords):
						classWords[word] += 1
					else:
						classWords[word] = 1

			numDocsInClass = len(self.trainFiles[directory])
			self.classes[directory] = ClassHolder(directory,numDocsInClass,classWords)
			print "\tnumWords in " + directory + ": " + str(self.classes[directory].getWordCount())
			print "\tnumDocs in " + directory + ": " + str(self.classes[directory].getDocCount())

			# add docs in class to total doc count
			self.totalDocs += numDocsInClass

		print "\nFinished training. " + str(self.totalDocs) + " docs evaluated over " + str(len(self.classes)) + " classes.\n"

	def loadFile(self,filename):
		wordArray = dict()
		with open(filename) as f:
			for line in f:
				line = str.lower(line.strip())
				if(len(line) <= 0):
					continue

				# replace special chars with spaces
				specialCharLine = re.sub(r'(@|\.|-|\n)+',' ',line)

				# only keep alphanumeric characters and spaces
				strippedLine = re.sub(r'([^\s\w]|_)+', '', specialCharLine)
				arr = strippedLine.split()	# splits on whitespace by default
				for word in arr:

					# add unique words to the document
					if(word != '' and word not in self.stopWords and word not in wordArray):
						wordArray[word] = 1
						if(word not in self.allWords):
							self.allWords[word] = 1
		return wordArray

	def classifyTrainingData(self):
		print "Classifying training data..."

		counter = 0
		classificationNums = self._getClassesDictionary()
		for className in self.trainFiles:
			print "\tClassifying " + className + "..."
			classDocs = self.trainFiles[className]

			docClass = self.classes[className]
			classClassificationNums = self._getClassesDictionary()

			classDocCounter = 0
			myCounter = 0
			for doc in classDocs:
				myCounter += 1
				filepath = str(self.PATH_TO_TRAINING_DATA + className + "/" + doc)
				classification = self.classifyDoc(filepath)
				print "classify: " + str(myCounter)

				# update class classification numbers
				classClassificationNums[classification[0]] += 1

				# update overall classification numbers
				classificationNums[classification[0]] += 1

				classDocCounter += 1
				if(className == classification[0]):
					counter += 1

			print "\t\tClass results (out of " + str(classDocCounter) + "):"
			for classNameAgain in classClassificationNums:
				print "\t\t\t" + classNameAgain + ": " + str(classClassificationNums[classNameAgain]) + " out of " + str(classDocCounter)

		print "\nfinished classifying training data. " + str(counter) + " correctly classified instances out of " + str(self.totalTrainFiles) + " (" + str(float(counter)/self.totalTrainFiles) +" accuracy)\n"
		

		print "Results:"
		total = 0
		for className in classificationNums:
			print className + ": " + str(classificationNums[className])
			total += classificationNums[className]

		print "\ntotal classifications: " + str(total) + "\n"

	def classifyTestData(self):
		print "Classifying test data..."

		counter = 0
		classificationNums = self._getClassesDictionary()
		for className in self.testFiles:
			print "\tClassifying " + className + "..."
			classDocs = self.testFiles[className]

			docClass = self.classes[className]
			classClassificationNums = self._getClassesDictionary()

			classDocCounter = 0
			for doc in classDocs:
				filepath = str(self.PATH_TO_TEST_DATA + className + "/" + doc)
				classification = self.classifyDoc(filepath)

				# update class classification numbers
				classClassificationNums[classification[0]] += 1

				# update overall classification numbers
				classificationNums[classification[0]] += 1

				classDocCounter += 1
				if(className == classification[0]):
					counter += 1

			print "\t\tClass results (out of " + str(classDocCounter) + "):"
			for classNameAgain in classClassificationNums:
				print "\t\t\t" + classNameAgain + ": " + str(classClassificationNums[classNameAgain]) + " out of " + str(classDocCounter)

		print "\nfinished classifying training data. " + str(counter) + " correctly classified instances out of " + str(self.totalTestFiles) + " (" + str(float(counter)/self.totalTestFiles) +" accuracy)\n"
		

		print "Results:"
		total = 0
		for className in classificationNums:
			print className + ": " + str(classificationNums[className])
			total += classificationNums[className]

		print "\ntotal classifications: " + str(total) + "\n"		

	def classifyDoc(self,filename):
		fileWordArray = self.loadFile(filename)

		# calculate probabilities of each class:
		classProbabilities = dict()
		for className in self.classes:
			docClass = self.classes[className]
			docWords = docClass.words
			
			# start probability calc with p(class)
			classProbability = math.log(float(docClass.getDocCount()) / self.totalDocs)
			classWordCount = docClass.getWordCount()
			classDocCount = docClass.getDocCount()
			probOutsideClass = math.log(float(1) / classDocCount)
			for word in self.allWords:
				probVar = 0
				wordInDocWords = (word in docWords)
				wordInFileWordArray = (word in fileWordArray)
				if(wordInDocWords and not wordInFileWordArray):
					try:
						probFalseButInClass = math.log(1 - float(docWords[word])/classDocCount)
					except ValueError:
						probFalseButInClass = 1e-100
					probVar = probFalseButInClass
				elif(wordInDocWords and wordInFileWordArray):
					probTrueInClass = math.log(float(docWords[word])/classDocCount)		 
					probVar = probTrueInClass
				else:
					probVar = 0
				#elif(not wordInDocWords and not wordInFileWordArray):
				#	probFalseAndNotInClass = probOutsideClass
				#	probVar = 0#probFalseAndNotInClass
				#elif(not wordInDocWords and wordInFileWordArray):
				#	probFalseAndInClass = probOutsideClass
				#	probVar = 0#probFalseAndInClass
				#else:
				#	raise Exception("This shouldn't happen")

				classProbability += probVar

			classProbabilities[className] = classProbability
		print("exit classes")
		# figure out which of the probabilities for each class is the highest and return that prediction
		highestProbability = -1000000
		mostLikelyClass = NOT_SET
		for className in classProbabilities:
			classProbability = classProbabilities[className]
			if(classProbability > highestProbability):
				highestProbability = classProbability
				mostLikelyClass = className

		return [mostLikelyClass,highestProbability]
