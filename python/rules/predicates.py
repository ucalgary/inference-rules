# coding=utf-8

# Quasi-Enums

class ComparisonPredicateModifier(object):

	Direct = 0
	All = 1
	Any = 2

	_str = {
		Direct: '',
		All: 'ALL',
		Any: 'ANY'
	}


class ComparisonPredicateType(object):

	LessThan = 0
	LessThanOrEqual = 1
	GreaterThan = 2
	GreaterThanOrEqual = 3
	EqualTo = 4
	NotEqualTo = 5
	Matches = 6
	Like = 7
	BeginsWith = 8
	EndsWith = 9
	In = 10
	CustomSelector = 11
	Contains = 12
	Between = 13

	_str = {
		LessThan: '<',
		LessThanOrEqual: '<=',
		GreaterThan: '>',
		GreaterThanOrEqual: '>=',
		EqualTo: '==',
		NotEqualTo: '!=',
		Matches: 'MATCHES',
		Like: 'LIKE',
		BeginsWith: 'BEGINSWITH',
		EndsWith: 'ENDSWITH',
		In: 'IN',
		CustomSelector: 'SEL',
		Contains: 'CONTAINS',
		Between: 'BETWEEN'
	}


class ComparisonPredicateOptions(object):

	CaseInsensitive = 1
	DiacriticInsensitive = 2
	Normalized = 4


class CompoundPredicateType(object):

	Not = 0
	And = 1
	Or = 2

	_str = {
		Not: 'NOT',
		And: 'AND',
		Or: 'OR'
	}


class Predicate(object):
	
	# Creating a Predicate

	@staticmethod
	def predicateWithFormat(format, **args):
		from .scanners import PredicateScanner
		scanner = PredicateScanner(format)
		return scanner.parsePredicate()

	@staticmethod
	def predicateWithValue(value):
		return TruePredicate if value else FalsePredicate

	@staticmethod
	def andPredicateWithSubpredicates(subpredicates):
		return CompoundPredicate(subpredicates, type=CompoundPredicateType.And)

	@staticmethod
	def notPredicateWithSubpredicate(subpredicate):
		return CompoundPredicate((subpredicate,), type=CompoundPredicateType.Not)

	@staticmethod
	def orPredicateWithSubpredicates(subpredicates):
		return CompoundPredicate(subpredicates, type=CompoundPredicateType.Or)

	# Initializing a Predicate

	def __init__(self):
		pass

	# Evaluating a Predicate

	def evaluateWithObject(self, obj):
		return False

	def evaluateWithObjectAndSubstitutionValues(self, obj, **substitutions):
		return False
	
	# Getting Representations

	# def __str__(self):
	# 	pass

	# def __repr__(self):
	# 	pass


class ComparisonPredicate(Predicate):
	
	def __init__(self, leftExpression, rightExpression, modifier=ComparisonPredicateModifier.Direct, type=ComparisonPredicateType.EqualTo, options=0):
		from .operators import ComparisonPredicateOperator

		self._leftExpression = leftExpression
		self._rightExpression = rightExpression
		self._operator = ComparisonPredicateOperator(type, modifier, options)
	
	@property
	def leftExpression(self):
		return self._leftExpression

	@property
	def rightExpression(self):
		return self._rightExpression

	@property
	def modifier(self):
		return self._operator.modifier

	@property
	def operatorType(self):
		return self._operator.operatorType

	@property
	def options(self):
		return self._operator.options

	# Evaluating

	def evaluateWithObject(self, obj):
		leftValue = self.leftExpression.expressionValueWithObject(obj)
		rightValue = self.rightExpression.expressionValueWithObject(obj)

		return self._operator.performOperationUsingObjects(leftValue, rightValue)

	# Getting Representations

	def __str__(self):
		return ('%s %s %s %s' % (
			ComparisonPredicateModifier._str.get(self.modifier, 'UNKNOWN'),
			self.leftExpression,
			ComparisonPredicateType._str.get(self.operatorType, 'UNKNOWN'),
			self.rightExpression
		)).lstrip()

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class CompoundPredicate(Predicate):

	def __init__(self, subpredicates, type=CompoundPredicateType.And):
		from .operators import CompoundPredicateOperator

		self._subpredicates = subpredicates
		self._operator = CompoundPredicateOperator(type, 0, 0)

	@property
	def compoundPredicateType(self):
		return self._operator.operatorType

	@property
	def subpredicates(self):
		return self._subpredicates

	# Evaluating

	def evaluateWithObject(self, obj):
		return self._operator.evaluatePredicatesWithObject(self.subpredicates, obj)

	# Getting Representations

	def __str__(self):
		return '%s' % (
			self.subpredicates
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class ValuePredicate(Predicate):

	def __init__(self, value):
		self._value = value

	@property
	def value(self):
		return self._value

	# Evaluating

	def evaluateWithObject(self, obj):
		return self.value

	# Getting Representations

	def __str__(self):
		return 'TRUE' if self.value else 'FALSE'

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

TruePredicate = ValuePredicate(True)
FalsePredicate = ValuePredicate(False)

