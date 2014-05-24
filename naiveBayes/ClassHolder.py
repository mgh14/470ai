NOT_SET = "not_set"

class ClassHolder(object):
	docCount = NOT_SET
	words = NOT_SET
	wordCount = NOT_SET

	def __init__(self,numDocsInClass,wordArray):
		self.docCount = numDocsInClass
		self.words = wordArray

		self.wordCount = 0
		for word in wordArray:
			self.wordCount += wordArray[word]

	def getDocCount(self):
		return self.docCount

	def getWordCount(self):
		return self.wordCount
