from DocClassifier import *

class CategoryClassifier(DocClassifier):
	trainingData = NOT_SET

	def __init__(self):
		DocClassifier.__init__(self)
		self._loadFiles()

	def _loadFiles(self):
		for directory in self.data:
			print "loading dir " + directory + "..."
			for doc in self.data[directory]:
				self.loadFile(self.PATH_TO_TRAINING_DATA + directory + "/" + doc)
		
	def loadFile(self,filename):
		wordArray = dict()
		with open(filename) as f:
			for line in f:
				line = str.lower(line.strip())
				if(len(line) <= 0):
					continue

				# only keep alphanumeric characters and spaces
				line2 = re.sub(r'([^\s\w]|_)+', '', line)
				arr = line2.split()	# splits on whitespace by default
				for word in arr:
					if(word != '' and word not in self.stopWords):
						if(word in wordArray):
							wordArray[word] += 1
						else:
							wordArray[word] = 1
		#print str(wordArray)
		return wordArray

	def train(self):
		print str(self.data)
