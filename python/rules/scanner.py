# coding=utf-8

class Scanner(object):

	def __init__(self, string):
		self._string = string
		self._scanLocation = 0
		self._charactersToBeSkipped = ()
		self._caseSensitive = False

	@property
	def caseSensitive(self):
		return self._caseSensitive

	@caseSensitive.setter
	def caseSensitive(self, value):
		self._caseSensitive = value

	@property
	def string(self):
		return self._string

	@property
	def charactersToBeSkipped(self):
		return self._charactersToBeSkipped

	def isAtEnd(self):
		return self.scanLocation == len(self.string)
	atEnd = property(isAtEnd)

	@property
	def scanLocation(self):
		return self._scanLocation

	@scanLocation.setter
	def scanLocation(self, location):
		if location > len(self.string):
			location = len(self.string)
		elif location < 0:
			location = 0
		self._scanLocation = location

	def scanCharactersFromSet(self, scanSet):
		return self._scanWithSet(scanSet, False)

	def scanUpToCharactersFromSet(self, scanSet):
		return self._scanWithSet(scanSet, True)

	def _scanWithSet(self, scanSet, stop):
		if self.atEnd:
			return None

		current = self.scanLocation
		result = None

		while current < len(self.string):
			c = self.string[current]

			if (c in scanSet) == stop:
				break

			if not c in self._charactersToBeSkipped:
				if result is None:
					result = ''
				result += c

			current += 1

		if result:
			self.scanLocation = current

		return result

	def _movePastCharactersToBeSkipped(self):
		current = self.scanLocation
		string = self.string
		toSkip = self.charactersToBeSkipped

		while current < len(string):
			if not string[current] in toSkip:
				break
			current += 1

		self.scanLocation = current

	def scanString(self, s):
		self._movePastCharactersToBeSkipped()

		if self.atEnd:
			return None

		currentStr = self.string[self.scanLocation:]
		if (self.caseSensitive and currentStr != s) or (not self.caseSensitive and (currentStr.lower() != s.lower())):
			return None
		else:
			self.scanLocation += s.length
			return s

	def scanUpToString(self, s):
		current = self.scanLocation
		string = self.string
		captured = None

		while current < len(string):
			currentStr = string[current:current + len(s)]
			if currentStr == s or (not self.caseSensitive and currentStr.lower() == s.lower()):
				break

			if not captured:
				captured = ''
			captured += string[current]
			current += 1

		if captured:
			self.scanLocation = current

		if self.charactersToBeSkipped:
			pass
			# trim charactersToBeSkipped from beginning of captured

		return captured

	def scanWithParseFunction(self, func):
		import math

		self._movePastCharactersToBeSkipped()
		string = self.string
		loc = self.scanLocation

		if self.atEnd:
			return 0

		s = string[loc:]
		f = func(s)

		if math.isnan(f):
			return None

		loc += len(str(f))
		i = 0
		while not math.isnan(float(string[loc + i :])):
			i += 1

		self.scanLocation = loc + i

		return f

	def scanFloat(self):
		import __builtin__
		return self.scanWithParseFunction(__builtin__.float)

	def scanInt(self):
		import __builtin__
		return self.scanWithParseFunction(__builtin__.int)