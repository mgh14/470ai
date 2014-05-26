import sys
import math
import re
import os

NOT_SET = "not_set"
class DocClassifier(object):
	PATH_TO_TRAINING_DATA = "20news-bydate-train/"
	PATH_TO_TEST_DATA = "20news-bydate-test/"

	trainFiles = NOT_SET
	testFiles = NOT_SET
	stopWords = NOT_SET

	def __init__(self):
		self.trainFiles = dict()
		self.testFiles = dict()

		self._initializeFileStructures()
		self._loadStopwords("stopwords.txt")

	def _initializeFileStructures(self):

		trainDirs = os.listdir(self.PATH_TO_TRAINING_DATA)
		for directory in trainDirs:
			# create array of document names for class name (a.k.a. directory)
			self.trainFiles[directory] = []
			trainDirFiles = os.listdir(self.PATH_TO_TRAINING_DATA + "/" + directory)
			for doc in trainDirFiles:
				self.trainFiles[directory].append(doc)

			# (words inserted differently for children classes, thus not included here)

		testDirs = os.listdir(self.PATH_TO_TEST_DATA)
		for directory in testDirs:
			# create array of document names for class name (a.k.a. directory)
			self.testFiles[directory] = []
			testDirFiles = os.listdir(self.PATH_TO_TEST_DATA + "/" + directory)
			for doc in testDirFiles:
				self.testFiles[directory].append(doc)

	def _loadStopwords(self,filename):
		self.stopWords = []
		with open(filename) as f:
			for line in f:
				self.stopWords.append(line.strip())
