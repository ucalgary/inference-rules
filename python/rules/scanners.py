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
		self.scanString('#')
		ident = self.scanCharactersFromSet(self.parseIdentifierExpression._identifier)
		if not ident:
			raise ValueError('Missing identifier: %s' % self.string[self.scanLocation:])
		return Expression.expressionForKeyPath(ident)
	parseIdentifierExpression._identifier = '_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

	def parseSimpleExpression(self):
		dbl = self.scanFloat()
		if dbl:
			return Expression.expressionForConstantValue(dbl)
		if self.scanString('-'):
			return Expression.expressionForFunction('_chs', parameters=[self.parseExpression()])
		if self.scanString('('):
			arg = self.parseExpression()
			if not self.scanString(')'):
				raise ValueError('Missing ) in expression')
			return arg
		if self.scanString('{'):
			if self.scanString('}'):
				return Expression.expressionForConstantValue([])
			a = []
			a.append(self.parseExpression())
			while self.scanString(','):
				a.append(self.parseExpression())
			if not self.scanString('}'):
				raise ValueError('Missing } in aggregate')
			return Expression.expressionForConstantValue(a)
		if self.scanString('NULL') or self.scanString('NIL'):
			return Expression.expressionForConstantValue(None)
		if self.scanString('TRUE') or self.scanString('YES'):
			return Expression.expressionForConstantValue(True)
		if self.scanString('FALSE') or self.scanString('NO'):
			return Expression.expressionForConstantValue(False)
		if self.scanString('SELF'):
			return Expression.expressionForEvaluatedObject()
		if self.scanString('$'):
			var = self.parseIdentifierExpression()
			if not var.keyPath:
				raise ValueError('Invalid variable identifier: %s' % var)
			return Expression.expressionForVariable(var.keyPath)

		location = self.scanLocation
		if self.scanString('%'):
			if not self.atEnd:
				c = self.string[location]
				if c == '%':
					location = self.scanLocation
				elif c == 'K':
					self.scanLocation += 1
					return Expression.expressionForKeyPath(self.nextArg())
				elif c in '@cCdDioOuUxXeEfgG':
					self.scanLocation += 1
					return Expression.expressionForConstantValue(self.nextArg())
				elif c == 'h':
					self.scanString('h')
					if not self.atEnd:
						c = self.string[self.scanLocation]
						if c in 'iu':
							self.scanLocation += 1
							return Expression.expressionForConstantValue(self.nextArg())
				elif c == 'q':
					self.scanString('q')
					if not self.atEnd:
						c = self.string[self.scanLocation]
						if c in 'iuxX':
							self.scanLocation += 1
							return Expression.expressionForConstantValue(self.nextArg())
			self.scanLocation = location

		for q, q_name in (('"', 'double quoted'), ("'", 'single quoted')):
			if self.scanString(q):
				skip = self.charactersToBeSkipped
				self.charactersToBeSkipped = None
				scanned = self.scanUpToString(q)
				if not scanned:
					self.charactersToBeSkipped = skip
					raise ValueError('Invalid %s literal at %i' % (q_name, location))
				self.charactersToBeSkipped = skip
				self.scanString('"')
				return Expression.expressionForConstantValue(scanned)
		if self.scanString('@'):
			e = self.parseIdentifierExpression()
			if not e.keyPath:
				raise ValueError('Invalid keypath identifier: %s' % e)
			return Expression.expressionForKeyPath('@%s' % e.keyPath)

		return self.parseIdentifierExpression()

	def parseFunctionalExpression(self):
		left = self.parseSimpleExpression()

		while True:
			if self.scanString('('):
				# function expression
				if not left.keyPath:
					raise ValueError('Invalid function identifier: %s' % left)
				if not self.scanString(')'):
					args = []
					args.append(self.parseExpression())
					while self.scanString(','):
						args.append(self.parseExpression())
					if not self.scanString(')'):
						raise ValueError('Missing ) in function arguments')
			elif self.scanString('['):
				# index expression
				if self.scanPredicateKeyword('FIRST'):
					left = Expression.expressionForFunction('_first', parameters=[self.parseExpression()])
				elif self.scanPredicateKeyword('LAST'):
					left = Expression.expressionForFunction('_last', parameters=[self.parseExpression()])
				elif self.scanPredicateKeyword('SIZE'):
					left = Expression.expressionForFunction('count', parameters=[self.parseExpression()])
				else:
					left = Expression.expressionForFunction('_index', parameters=[left, self.parseExpression()])
				if not self.scanString(']'):
					raise ValueError('Missing ] in index argument')
			elif self.scanString('.'):
				# keypath expression
				if not left.keyPath:
					raise ValueError('Invalid left keypath: %s' % left)
				right = self.parseExpression()
				if not right.keyPath:
					raise ValueError('Invalid right keypath: %s' % left)
				left = Expression.expressionForKeyPath('%s.%s' % (left.keyPath, right.keyPath))
			else:
				return left

	def parsePowerExpression(self):
		left = self.parseFunctionalExpression()

		while True:
			if self.scanString('**'):
				right = self.parseFunctionalExpression()
				left = Expression.expressionForFunction('raise:toPower:', parameters=[left, right])
			else:
				return left

	def parseMultiplicationExpression(self):
		left = self.parsePowerExpression()

		while True:
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
