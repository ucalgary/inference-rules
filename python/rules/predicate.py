# coding=utf-8

# Quasi-Enums

class ComparisonPredicateModifier(object):

	Direct = 0
	All = 1
	Any = 2


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


class CompoundPredicateType(object):

	Not = 0
	And = 1
	Or = 2


class Predicate(object):
	
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
	
	def __init__(self, leftExpression, rightExpression, type=ComparisonPredicateType.EqualTo, modifier=ComparisonPredicateModifier.Direct, **options):
		from .operators import ComparisonPredicateOperator

		self._leftExpression = leftExpression
		self._rightExpression = rightExpression
		self._operator = ComparisonPredicateOperator(operatorType, modifier, **options)
	
	@property
	def leftExpression(self):
		return self._leftExpression

	@property
	def rightExpression(self):
		return self._rightExpression

	@property
	def modifier(self):
		return self._modifier

	@property
	def operatorType(self):
		return self._operator.operatorType

	# Evaluating

	def evaluateWithObject(self, obj):
		leftValue = self.leftExpression.expressionValueWithObject(obj)
		rightValue = self.rightExpression.expressionValueWithObject(obj)

		return self._operator.performOperationUsingObjects(leftValue, rightValue)

class CompoundPredicate(Predicate):

	def __init__(self, subpredicates, type=CompoundPredicateType.And):
		from .operators import CompoundPredicateOperator

		self._subpredicates = subpredicates
		self._operator = CompoundPredicateOperator(operatorType, 0)

	@property
	def compoundPredicateType(self):
		return self._operator.operatorType

	@property
	def subpredicates(self):
		return self._subpredicates

	# Evaluating

	def evaluateWithObject(self, obj):
		return self._operator.evaluatePredicatesWithObject(self.subpredicates, obj)

# Creation functions

def predicateWithFormat(format, **args):
	pass

def predicateWithValue(value):
	pass

def andPredicateWithSubpredicates(subpredicates):
	return CompoundPredicate(subpredicates, type=CompoundPredicateType.And)

def notPredicateWithSubpredicate(subpredicate):
	return CompoundPredicate((subpredicate,), type=CompoundPredicateType.Not)

def orPredicateWithSubpredicates(subpredicates):
	return CompoundPredicate(subpredicates, type=CompoundPredicateType.Or)

