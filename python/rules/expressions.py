# coding=utf-8

import __builtin__
import datetime
import math
import random

from . import expression
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
	'add:to:'          : lambda n, m: n + m,
	'from:subtract:'   : lambda n, m: n - m,
	'multiply:by:'     : lambda n, m: n * m,
	'divide:by:'       : lambda n, m: n / m,
	'sqrt:'            : math.sqrt,
	'raise:toPower:'   : math.pow,
	'abs:'             : math.fabs,
	'now'              : lambda _: datetime.datetime.now,
	'ln:'              : math.log10,
	'exp:'             : math.exp,
	'ceiling:'         : math.ceil,
	'random:'          : lambda num: random.randint(0, num),
	'modulus:by:'      : lambda n, m: n % m,
	'chs'              : lambda num: -num,

	'valueForKeyPath:' : lambda object, keyPath: kvc.valueForKeyPath(object, keyPath)
}

class ConstantValueExpression(expression.Expression):

	def __init__(self, value):
		super(ConstantValueExpression, self).__init__(expression.ExpressionType.ConstantValue)

		self._value = value

	@property
	def constantValue(self):
		return self._value

	def expressionValueWithObject(self, object, context=None):
		return self.constantValue

class SelfExpression(expression.Expression):

	def __init__(self):
		super(SelfExpression, self).__init__(expression.ExpressionType.EvaluatedObject)

	def expressionValueWithObject(self, object, context=None):
		return object

class VariableExpression(expression.Expression):

	def __init__(self, variable):
		super(VariableExpression, self).__init__(expression.ExpresionType.Variable)

		self._variable = variable

	@property
	def variable(self):
		return self._variable

	def expressionValueWithObject(self, object, context=None):
		return None # return from the variable bindings dictionary the value for the key variable

class AggregateExpression(expression.Expression):

	def __init__(self, collection):
		super(AggregateExpression, self).__init__(expression.ExpresionType.Aggregate)

		self._collection = collection

	@property
	def collection(self):
		return self._collection

	def expressionValueWithObject(self, object, context=None):
		return self.collection

class SetExpression(expression.Expression):

	_expressionFunctionNamesByType = {
		expression.ExpressionType.UnionSet : 'union',
		expression.ExpressionType.IntersectSet: 'intersection',
		expression.ExpressionType.MinusSet: 'difference'
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

		return expressionFunction(leftValue, rightValue)

class FunctionExpression(expression.Expression):

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
		super(KeyPathExpression, self).__init__(expression.expressionForConstantValue(_BuiltInFunctions), 'valueForKeyPath:', [expression.expressionForEvaluatedObject(), expression.expressionForConstantValue(keyPath)], expression.ExpressionType.KeyPath)

	@property
	def pathExpression(self):
		return self.arguments[0]

	@property
	def keyPath(self):
		return self.pathExpression.constantValue
