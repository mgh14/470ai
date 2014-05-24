import sys
import math
import re
import os

NOT_SET = "not_set"
class DocClassifier(object):
	PATH_TO_TRAINING_DATA = "20news-bydate-train/"
	PATH_TO_TEST_DATA = "20news-bydate-test/"

	data = NOT_SET
	stopWords = NOT_SET

	def __init__(self):
		self._initializeData()
		self._loadStopwords("stopwords.txt")

	def _initializeData(self):
		self.data = dict()

		dirs = os.listdir(self.PATH_TO_TRAINING_DATA)
		for directory in dirs:
			# create directory class
			self.data[directory] = []

			# insert document names
			files = os.listdir(self.PATH_TO_TRAINING_DATA + "/" + directory)
			for doc in files:
				self.data[directory].append(doc)

			# (words inserted differently for children, thus not included here)

	def _loadStopwords(self,filename):
		self.stopWords = []
		with open(filename) as f:
			for line in f:
				self.stopWords.append(line.strip())
