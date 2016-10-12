# coding=utf-8

import builtins
import datetime
import math
import random

from . import kvc, pathutils

_BuiltInFunctions = {
	'sum:'             : builtins.sum,
	'count:'           : builtins.len,
	'min:'             : builtins.min,
	'max:'             : builtins.max,
	'average:'         : lambda params: sum(params) / len(params),
	'first:'           : lambda params: params[0],
	'last:'            : lambda params: params[-1],
	'fromObject:index:': lambda object, index: object[index],
	'add:to:'          : lambda n_m: n_m[0] + n_m[1],
	'from:subtract:'   : lambda n_m1: n_m1[0] - n_m1[1],
	'multiply:by:'     : lambda n_m2: n_m2[0] * n_m2[1],
	'divide:by:'       : lambda n_m3: n_m3[0] / n_m3[1],
	'sqrt:'            : lambda num4: math.sqrt(num4[0]),
	'raise:toPower:'   : lambda n_m5: math.pow(n_m5[0], n_m5[1]),
	'abs:'             : lambda num6: math.fabs(num6[0]),
	'now'              : lambda _: datetime.datetime.now,
	'ln:'              : lambda num7: math.log10(num7[0]),
	'exp:'             : lambda num8: math.exp(num8[0]),
	'ceiling:'         : lambda num9: math.ceil(num9[0]),
	'random:'          : lambda num10: random.randint(0, num10[0]),
	'modulus:by:'      : lambda n_m11: n_m11[0] % n_m11[1],
	'chs'              : lambda num12: -num12[0],

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
		if functionName == 'FUNCTION':
			if len(parameters) < 2:
				raise ValueError('Insufficient parameters for custom function.')
			operand = parameters[0]
			functionName = parameters[1].expressionValueWithObject(None)
			parameters = parameters[2:]
		else:
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

	def _expressionWithSubstitutionVariables(self, variables):
		raise NotImplementedError('Subclasses of Expression should implement _expressionWithSubstitutionVariables:')
		
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

	def _expressionWithSubstitutionVariables(self, variables):
		return self

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

	def _expressionWithSubstitutionVariables(self, variables):
		return self

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

	def _expressionWithSubstitutionVariables(self, variables):
		result = variables.get(self.variable, None)

		if result != None:
			return ConstantValueExpression(result)
		else:
			return self

	@property
	def variable(self):
		return self._variable

	def expressionValueWithObject(self, object, context=None):
		# Special case: if the variable is _NSPathUtilities,
		# return pathutils. Otherwise, return None because the
		# variable has not been substituted with an actual value.
		if self.variable == '_NSPathUtilities':
			return pathutils

		return None

	# Getting Representations

	def __str__(self):
		return '$%s' % (
			self.variable
		)

	def __repr__(self):
		return '<%s> $%s' % (
			self.__class__.__name__,
			self.__str__()
		)

class AggregateExpression(Expression):

	def __init__(self, collection):
		super(AggregateExpression, self).__init__(ExpressionType.Aggregate)

		self._collection = collection

	def _expressionWithSubstitutionVariables(self, variables):
		collection = [e._expressionWithSubstitutionVariables(variables) for e in self.collection]
		return AggregateExpression(collection)

	@property
	def collection(self):
		return self._collection

	def expressionValueWithObject(self, object, context=None):
		return [e.expressionValueWithObject(object, context=context) for e in self.collection]

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

	def _expressionWithSubstitutionVariables(self, variables):
		leftExpression = self.leftExpression._expressionWithSubstitutionVariables(variables)
		rightExpression = self.rightExpression._expressionWithSubstitutionVariables(variables)
		return SetExpression(self.expressionType, leftExpression, rightExpression)

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

	def _expressionWithSubstitutionVariables(self, variables):
		arguments = [e.expressionValueWithObject(object, context=context) for e in self.arguments]
		return FunctionExpression(self.operand, self.function, self.arguments, self.expressionType)

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
		arguments = [arg.expressionValueWithObject(object, context=context) for arg in self.arguments]

		return target_function(*arguments)

	def _expressionWithSubstitutionVariables(self, variables):
		operand = self.operand._expressionWithSubstitutionVariables(variables)
		arguments = [arg._expressionWithSubstitutionVariables(variables) for arg in self.arguments]

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
