import sys
import math
import re
import os

NOT_SET = "not_set"
class DocClassifier(object):
	PATH_TO_TRAINING_DATA = "20news-bydate-train/"
	PATH_TO_TEST_DATA = "20news-bydate-test/"

	files = NOT_SET
	stopWords = NOT_SET

	def __init__(self):
		self.files = dict()

		self._initializeFileStructure()
		self._loadStopwords("stopwords.txt")

	def _initializeFileStructure(self):

		dirs = os.listdir(self.PATH_TO_TRAINING_DATA)
		for directory in dirs:
			# create array of document names for class name (a.k.a. directory)
			self.files[directory] = []
			dirFiles = os.listdir(self.PATH_TO_TRAINING_DATA + "/" + directory)
			for doc in dirFiles:
				self.files[directory].append(doc)

			# (words inserted differently for children classes, thus not included here)

	def _loadStopwords(self,filename):
		self.stopWords = []
		with open(filename) as f:
			for line in f:
				self.stopWords.append(line.strip())
