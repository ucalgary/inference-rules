# coding=utf-8

import string

from . import characters
from .expressions import Expression
from .predicates import ComparisonPredicateModifier, ComparisonPredicateType, ComparisonPredicateOptions
from .predicates import CompoundPredicateType
from .predicates import Predicate, ComparisonPredicate, CompoundPredicate


class Scanner(object):

	def __init__(self, string):
		self._string = string
		self._scanLocation = 0
		self._charactersToBeSkipped = characters.ScannerCharactersToBeSkippedCharacterSet
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

	@charactersToBeSkipped.setter
	def charactersToBeSkipped(self, value):
		self._charactersToBeSkipped = value

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

		f = None
		i = 0

		if self.atEnd:
			return f
			
		while loc + i + 1 <= len(string):
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
		ident = self.scanCharactersFromSet(characters.IdentifierExpressionCharacterSet)
		if not ident:
			raise ValueError('Missing identifier: %s' % self.string[self.scanLocation:])
		return Expression.expressionForKeyPath(ident)

	def parseSimpleExpression(self):
		dbl = self.scanFloat()
		if dbl is not None:
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
				return Expression.expressionForAggregate([])
			a = []
			a.append(self.parseExpression())
			while self.scanString(','):
				e = self.parseExpression()
				a.append(e)
			if not self.scanString('}'):
				raise ValueError('Missing } in aggregate')
			return Expression.expressionForAggregate(a)
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
				self.scanString(q)
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
			if left.keyPath and self.scanString(':'):
				left = Expression.expressionForKeyPath(left.keyPath + ':')
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
				left = Expression.expressionForFunction(left.keyPath, parameters=args)
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


class PredicateScanner(ExpressionScanner):

	def scanPredicateKeyword(self, key):
		loc = self.scanLocation
		self.caseSensitive = False

		if not self.scanString(key):
			return False
		if self.atEnd:
			return True

		# Does the next character still belong to the token?
		c = self.string[self.scanLocation]
		if not (c in string.letters or c in string.digits):
			return True

		# Back up, no match
		self.scanLocation = loc
		return False

	def parsePredicate(self):
		return self.parseConjunction()

	def parseConjunction(self):
		l = self.parseNot()

		predicate_type_container = [-1,]
		def hasKeyword():
			for keyword, predicate_type_i in (
				('AND', CompoundPredicateType.And),
				('&&', CompoundPredicateType.And),
				('OR', CompoundPredicateType.Or),
				('||', CompoundPredicateType.Or),
				('', -1)
			):
				if self.scanPredicateKeyword(keyword):
					predicate_type_container[0] = predicate_type_i
					return True
				if not keyword:
					return False

		while hasKeyword():
			predicate_type = predicate_type_container[0]
			r = self.parseNot()

			if isinstance(r, CompoundPredicate) and r.compoundPredicateType == predicate_type:
				if isinstance(l, CompoundPredicate) and l.compoundPredicateType == predicate_type:
					subpredicates = l.subpredicates + r.subpredicates
				else:
					subpredicates = r.subpredicates + [l]
			elif isinstance(l, CompoundPredicate) and l.compoundPredicateType == predicate_type:
				subpredicates = l.subpredicates + [r]
			else:
				subpredicates = [l, r]

			l = CompoundPredicate(subpredicates, type=predicate_type)

		return l

	def parseNot(self):
		if self.scanString('('):
			r = self.parsePredicate()
			if not self.scanString(')'):
				raise ValueError('Missing ) in compound predicate')
			return r

		if self.scanPredicateKeyword('NOT') or self.scanPredicateKeyword('!'):
			return CompoundPredicate((self.parseNot(),), type=CompoundPredicateType.Not)

		for keyword, value in (
			('TRUEPREDICATE', True),
			('FALSEPREDICATE', False)
		):
			if self.scanPredicateKeyword(keyword):
				return Predicate.predicateWithValue(value)
		
		return self.parseComparison()

	def parseComparison(self):
		for keyword, predicate_modifier, negate in (
			('ANY', ComparisonPredicateModifier.Any, False),
			('ALL', ComparisonPredicateModifier.All, False),
			('NONE', ComparisonPredicateModifier.Any, True),
			('SOME', ComparisonPredicateModifier.All, True),
			('', ComparisonPredicateModifier.Direct, False)
		):
			if not keyword or self.scanPredicateKeyword(keyword):
				break

		left = self.parseExpression()

		for keyword, predicate_type in (
			('<=', ComparisonPredicateType.LessThanOrEqual),
			('=<', ComparisonPredicateType.LessThanOrEqual),
			('>=', ComparisonPredicateType.GreaterThanOrEqual),
			('=>', ComparisonPredicateType.GreaterThanOrEqual),
			('==', ComparisonPredicateType.EqualTo),
			('!=', ComparisonPredicateType.NotEqualTo),
			('<>', ComparisonPredicateType.NotEqualTo),
			('<', ComparisonPredicateType.LessThan),
			('>', ComparisonPredicateType.GreaterThan),
			('=', ComparisonPredicateType.EqualTo),
			('MATCHES', ComparisonPredicateType.Matches),
			('LIKE', ComparisonPredicateType.Like),
			('BEGINSWITH', ComparisonPredicateType.BeginsWith),
			('ENDSWITH', ComparisonPredicateType.EndsWith),
			('IN', ComparisonPredicateType.In),
			('CONTAINS', ComparisonPredicateType.Contains),
			('BETWEEN', ComparisonPredicateType.Between),
			('', 99)
		):
			if not keyword or self.scanPredicateKeyword(keyword):
				break
		
		if predicate_type == 99:
			raise ValueError('Invalid comparison predicate: %s' % self.string[self.scanLocation:])

		for opt_string, options in (
			('[cd]', ComparisonPredicateOptions.CaseInsensitive | ComparisonPredicateOptions.DiacriticInsensitive),
			('[c]', ComparisonPredicateOptions.CaseInsensitive),
			('[d]', ComparisonPredicateOptions.DiacriticInsensitive),
			('', 0)
		):
			if not opt_string or self.scanString(opt_string):
				break

		right = self.parseExpression()

		predicate = ComparisonPredicate(left, right, modifier=predicate_modifier, type=predicate_type, options=options)
		if negate:
			predicate = CompoundPredicate((predicate,), type=CompoundPredicateType.Not)

		return predicate
