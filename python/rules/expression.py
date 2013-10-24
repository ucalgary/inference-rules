# coding=utf-8

# Quasi-Enums

class ExpressionType(object):

	ConstantValue = 0
	EvaluatedObject = 1
	Variable = 2
	KeyPath = 3
	Function = 4
	UnionSet = 5
	IntersectSet = 6
	MinusSet = 7
	Subquery = 13
	Aggregate = 14
	AnyKey = 15         # Not supported. Represents any key for a Spotlight query.
	Block = 19          # Not supported. Uses a Bbock for evaluating objects.

class Expression(object):

	def __init__(self, type):
		self._type = type

	@property
	def expressionType(self):
		return self._type

	# Evaluating an Expression

	def expressionValueWithObject(self, object, context=None):
		return None

# Creating an Expression for a Value

def expressionForConstantValue(value):
	from .expressions import ConstantValueExpression
	return ConstantValueExpression(value)

def expressionForEvaluatedObject():
	from .expressions import SelfExpression
	return SelfExpression()

def expressionForKeyPath(keyPath):
	from .expressions import KeyPathExpression
	return KeyPathExpression(keyPath)

def expressionForVariable(variable):
	from .expressions import VariableExpression
	return VariableExpression(variable)

# Creating a Collection Expression

def expressionForAggregate(collection):
	from .expressions import AggregateExpression
	return AggregateExpression(collection)

def expressionForUnionSet(left, right):
	from .expressions import SetExpression
	return SetExpression(ExpressionType.UnionSet, leftSet, rightSet)

def expressionForIntersectSet(left, right):
	from .expressions import SetExpression
	return SetExpression(ExpressionType.IntersectSet, leftSet, rightSet)

def expressionForMinusSet(left, right):
	from .expressions import SetExpression
	return SetExpression(ExpressionType.MinusSet, leftSet, rightSet)

# Creating a Subquery

def expressionForSubquery(expression, variable, predicate):
	raise NotImplementedError

# Creating an Expression Using Blocks

def expressionForBlock(block, arguments=None):
	raise NotImplementedError

# Creating an Expression for a Function

def expressionForFunction(functionName, parameters=None):
	from .expressions import _BuiltInFunctions, FunctionExpression
	if not functionName in _BuiltInFunctions:
		raise

	operand = expressionForConstantValue(_BuiltInFunctions)
	return FunctionExpression(operand, functionName, parameters or [], ExpressionType.Function)

# Creating an Expression

def expressionWithFormat(format, **args):
	pass