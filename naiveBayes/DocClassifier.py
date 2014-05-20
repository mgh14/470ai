import sys
import math
import re

class DocClassifier(object):
	NOT_SET = "not_set"

	#lines = NOT_SET
	stopWords = NOT_SET

	def __init__(self):
		self._loadStopwords("stopwords.txt")

	def _loadStopwords(self,filename):
		self.stopWords = []
		with open(filename) as f:
			for line in f:
				self.stopWords.append(line.strip())

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
		return wordArray
