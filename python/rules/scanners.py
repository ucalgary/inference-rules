# coding=utf-8

from .expressions import Expression


class Scanner(object):

	def __init__(self, string):
		self._string = string
		self._scanLocation = 0
		self._charactersToBeSkipped = ()
		self._caseSensitive = False

	# Getting a Scanner's String

	@property
	def string(self):
		return self._string

	# Configuring a Scanner

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

	@property
	def caseSensitive(self):
		return self._caseSensitive

	@caseSensitive.setter
	def caseSensitive(self, value):
		self._caseSensitive = value

	@property
	def charactersToBeSkipped(self):
		return self._charactersToBeSkipped

	# Scanning a String	

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
		if not self.charactersToBeSkipped:
			return

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

		currentStr = self.string[self.scanLocation:self.scanLocation + len(s)]
		if (self.caseSensitive and currentStr != s) or (not self.caseSensitive and (currentStr.lower() != s.lower())):
			return None
		else:
			self.scanLocation += len(s)
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
		self._movePastCharactersToBeSkipped()
		string = self.string
		loc = self.scanLocation

		f = func(0)
		i = 0

		if self.atEnd:
			return f
			
		while not self.atEnd:
			try:
				f = func(string[loc:loc + i + 1])
			except ValueError:
				break
			i += 1

		self.scanLocation = loc + i

		return f

	def scanFloat(self):
		import __builtin__
		return self.scanWithParseFunction(__builtin__.float)

	def scanInt(self):
		import __builtin__
		return self.scanWithParseFunction(__builtin__.int)

	def isAtEnd(self):
		return self.scanLocation == len(self.string)
	atEnd = property(isAtEnd)


class ExpressionScanner(Scanner):

	def parseExpression(self):
		return self.parseBinaryExpression()

	def parseIdentifierExpression(self):
		pass

	def parseSimpleExpression(self):
		pass

	def parseFunctionalExpression(self):
		left = self.parseSimpleExpression()

		while True:
			if self.scanString('('):
				

	def parsePowerExpression(self):
		left = self.parseFunctionalExpression()

		while True:
			right = None

			if self.scanString('**'):
				right = self.parseFunctionalExpression()
				left = Expression.expressionForFunction('raise:toPower:', parameters=[left, right])
			else:
				return left

	def parseMultiplicationExpression(self):
		left = self.parsePowerExpression()

		while True:
			right = None

			if self.scanString('*'):
				right = self.parsePowerExpression()
				left = Expression.expressionForFunction('multiply:by:', parameters=[left, right])
			elif self.scanString('/'):
				right = self.parsePowerExpression()
				left = Expression.expressionForFunction('divide:by:', parameters=[left, right])
			else:
				return left

	def parseAdditionExpression(self):
		left = self.parseMultiplicationExpression()

		while True:
			right = None

			if self.scanString('+'):
				right = self.parseMultiplicationExpression()
				left = Expression.expressionForFunction('add:to:', parameters=[left, right])
			elif self.scanString('-'):
				right = self.parseMultiplicationExpression()
				left = Expression.expressionForFunction('from:subtract:', parameters=[left, right])
			else:
				return left

	def parseBinaryExpression(self):
		left = self.parseAdditionExpression()

		while True:
			right = None

			if self.scanString(':='):
				right = self.parseAdditionExpression()
			else:
				return left


class PredicateScanner(Scanner):

	def parsePredicate(self):
		return self.parseAnd()

	def parseAnd(self):
		pass

	def parseNot(self):
		pass

	def parseOr(self):
		pass

	def parseComparison(self):
		pass
