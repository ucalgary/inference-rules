# coding=utf-8

import __builtin__
import datetime
import math
import random

from . import kvc

_BuiltInFunctions = {
	'sum:'             : __builtin__.sum,
	'count:'           : __builtin__.len,
	'min:'             : __builtin__.min,
	'max:'             : __builtin__.max,
	'average:'         : lambda params: sum(params) / len(params),
	'first:'           : lambda params: params[0],
	'last:'            : lambda params: params[-1],
	'fromObject:index:': lambda object, index: object[index],
	'add:to:'          : lambda (n, m): n + m,
	'from:subtract:'   : lambda (n, m): n - m,
	'multiply:by:'     : lambda (n, m): n * m,
	'divide:by:'       : lambda (n, m): n / m,
	'sqrt:'            : lambda (num,): math.sqrt(num),
	'raise:toPower:'   : lambda (n, m): math.pow(n, m),
	'abs:'             : lambda (num,): math.fabs(num),
	'now'              : lambda _: datetime.datetime.now,
	'ln:'              : lambda (num,): math.log10(num),
	'exp:'             : lambda (num,): math.exp(num),
	'ceiling:'         : lambda (num,): math.ceil(num),
	'random:'          : lambda (num,): random.randint(0, num),
	'modulus:by:'      : lambda (n, m): n % m,
	'chs'              : lambda (num,): -num,

	'valueForKeyPath:' : lambda object, keyPath: kvc.valueForKeyPath(object, keyPath)
}

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

	# Creating an Expression for a Value

	@staticmethod
	def expressionForConstantValue(value):
		return ConstantValueExpression(value)

	@staticmethod
	def expressionForEvaluatedObject():
		return SelfExpression()

	@staticmethod
	def expressionForKeyPath(keyPath):
		return KeyPathExpression(keyPath)

	@staticmethod
	def expressionForVariable(variable):
		return VariableExpression(variable)

	# Creating a Collection Expression

	@staticmethod
	def expressionForAggregate(collection):
		return AggregateExpression(collection)

	@staticmethod
	def expressionForUnionSet(leftExpression, rightExpression):
		return SetExpression(ExpressionType.UnionSet, leftExpression, rightExpression)

	@staticmethod
	def expressionForIntersectSet(leftExpression, rightExpression):
		return SetExpression(ExpressionType.IntersectSet, leftExpression, rightExpression)

	@staticmethod
	def expressionForMinusSet(leftExpression, rightExpression):
		return SetExpression(ExpressionType.MinusSet, leftExpression, rightExpression)

	# Creating a Subquery

	@staticmethod
	def expressionForSubquery(expression, variable, predicate):
		raise NotImplementedError

	# Creating an Expression Using Blocks

	@staticmethod
	def expressionForBlock(block, arguments=None):
		raise NotImplementedError

	# Creating an Expression for a Function

	@staticmethod
	def expressionForFunction(functionName, parameters=None):
		if not functionName in _BuiltInFunctions:
			raise ValueError('Function "%s" not found' % functionName)

		operand = Expression.expressionForConstantValue(_BuiltInFunctions)
		return FunctionExpression(operand, functionName, parameters or [], ExpressionType.Function)

	# Creating an Expression

	@staticmethod
	def expressionWithFormat(format, **args):
		from .scanners import ExpressionScanner
		scanner = ExpressionScanner(format)
		return scanner.parseExpression()
		
	# Initializing an Expression

	def __init__(self, type):
		self._type = type

	@property
	def expressionType(self):
		return self._type

	# Getting Information About an Expression

	def _default_expression_info(self):
		return None

	arguments = property(_default_expression_info)
	collection = property(_default_expression_info)
	constantValue = property(_default_expression_info)
	expressionType = property(_default_expression_info)
	function = property(_default_expression_info)
	keyPath = property(_default_expression_info)
	leftExpression = property(_default_expression_info)
	operand = property(_default_expression_info)
	predicate = property(_default_expression_info)
	rightExpression = property(_default_expression_info)
	variable = property(_default_expression_info)

	# Evaluating an Expression

	def expressionValueWithObject(self, object, context=None):
		return None

class ConstantValueExpression(Expression):

	def __init__(self, value):
		super(ConstantValueExpression, self).__init__(ExpressionType.ConstantValue)

		self._value = value

	@property
	def constantValue(self):
		return self._value

	def expressionValueWithObject(self, object, context=None):
		return self.constantValue

	# Getting Representations

	def __str__(self):
		return '%s' % (
			repr(self.constantValue)
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class SelfExpression(Expression):

	def __init__(self):
		super(SelfExpression, self).__init__(ExpressionType.EvaluatedObject)

	def expressionValueWithObject(self, object, context=None):
		return object

	# Getting Representations

	def __str__(self):
		return 'SELF'

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class VariableExpression(Expression):

	def __init__(self, variable):
		super(VariableExpression, self).__init__(ExpressionType.Variable)

		self._variable = variable

	@property
	def variable(self):
		return self._variable

	def expressionValueWithObject(self, object, context=None):
		return None # return from the variable bindings dictionary the value for the key variable

	# Getting Representations

	def __str__(self):
		return '%s' % (
			self.variable
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class AggregateExpression(Expression):

	def __init__(self, collection):
		super(AggregateExpression, self).__init__(ExpressionType.Aggregate)

		self._collection = collection

	@property
	def collection(self):
		return self._collection

	def expressionValueWithObject(self, object, context=None):
		return map(lambda e: e.expressionValueWithObject(object, context=context), self.collection)

	# Getting Representations

	def __str__(self):
		return '%s' % (
			self.collection
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class SetExpression(Expression):

	_expressionFunctionNamesByType = {
		ExpressionType.UnionSet : 'union',
		ExpressionType.IntersectSet: 'intersection',
		ExpressionType.MinusSet: 'difference'
	}

	def __init__(self, type, leftExpression, rightExpression):
		super(SetExpression, self).__init__(type)

		self._leftExpression = leftExpression
		self._rightExpression = rightExpression

	@property
	def leftExpression(self):
		return self._leftExpression

	@property
	def rightExpression(self):
		return self._rightExpression

	def expressionFunctionName(self):
		return self.__class__._expressionFunctionNamesByType[self._type]

	def expressionValueWithObject(self, object, context=None):
		leftValue = self.leftExpression.expressionValueWithObject(object, context=context)
		if not isinstance(leftValue, set):
			return None
		rightValue = self.rightExpression.expressionValueWithObject(object, context=context)

		expressionFunctionName = self.expressionFunctionName()
		expressionFunction = getattr(leftValue, expressionFunctionName)

		return expressionFunction(rightValue)

	# Getting Representations

	def __str__(self):
		return '%s %s %s' % (
			self.leftExpression,
			self.expressionFunctionName,
			self.rightExpression
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)

class FunctionExpression(Expression):

	def __init__(self, operand, selector, parameters, type):
		super(FunctionExpression, self).__init__(type)

		self._selector = selector
		self._operand = operand
		self._arguments = parameters
		self._argc = len(parameters) if parameters is not None else 0

	@property
	def function(self):
		return self._selector

	@property
	def arguments(self):
		return self._arguments

	@property
	def operand(self):
		return self._operand

	def expressionValueWithObject(self, object, context=None):
		target = self.operand.expressionValueWithObject(object, context=context)
		target_function = target[self.function] if isinstance(target, dict) else getattr(target, self.function)
		arguments = map(lambda arg: arg.expressionValueWithObject(object, context=context), self.arguments)

		return target_function(*arguments)

	def _expressionWithSubstitutionVariables(self, variables):
		operand = self.operand._expressionWithSubstitutionVariables(variables)
		arguments = map(lambda arg: arg._expressionWithSubstitutionVariables(variables), self.arguments)

		return expressionForFunction(operand, self.function, arguments)

class KeyPathExpression(FunctionExpression):

	def __init__(self, keyPath):
		super(KeyPathExpression, self).__init__(Expression.expressionForConstantValue(_BuiltInFunctions), 'valueForKeyPath:', [Expression.expressionForEvaluatedObject(), Expression.expressionForConstantValue(keyPath)], ExpressionType.KeyPath)

	@property
	def pathExpression(self):
		return self.arguments[1]

	@property
	def keyPath(self):
		return self.pathExpression.constantValue

	# Getting Representations

	def __str__(self):
		return '%s' % (
			self.keyPath
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)
