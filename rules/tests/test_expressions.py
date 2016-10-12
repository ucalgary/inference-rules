import unittest

from ..expressions import Expression

class ExpressionsBasicCreationAndEvaluationTest(unittest.TestCase):

	def setUp(self):
		import random
		import string

		self.key = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.value = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.object = {
			self.key: self.value
		}
		
	# Values

	def testConstantValue(self):
		expression = Expression.expressionForConstantValue(self.value)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, self.value, 'ConstantValue expression returned an evaluated value that differs from the constant value.')
		
	def testEvaluatedObject(self):
		expression = Expression.expressionForEvaluatedObject()
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, self.object, 'EvaluatedObject expression returned an evaluated value that differs from the evaluated object.')

	def testKeyPath(self):
		expression = Expression.expressionForKeyPath(self.key)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, self.value, 'KeyPath expression returned an evaluated value that is not the value of the keyPath in the evaluated object.')

	def testVariable(self):
		expression = Expression.expressionForKeyPath(self.key)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		# NotImplementedYet

	# Collections

	def testAggregate(self):
		expression1 = Expression.expressionForConstantValue(1)
		expression2 = Expression.expressionForConstantValue(2)
		collection = [expression1, expression2]
		expression = Expression.expressionForAggregate(collection)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue[0], 1, 'Aggregate expression returned an evaluated value whose first member is not the evaluated value of the first expression.')
		self.assertEqual(evaluatedValue[1], 2, 'Aggregate expression returned an evaluated value whose second member is not the evaluated value of the second expression.')

	def testUnionSet(self):
		leftSet = set(range(1, 6))
		rightSet = set(range(1, 6, 2))
		leftExpression = Expression.expressionForConstantValue(leftSet)
		rightExpression = Expression.expressionForConstantValue(rightSet)
		expression = Expression.expressionForUnionSet(leftExpression, rightExpression)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, leftSet.union(rightSet), 'UnionSet expression evaluated to %s. Expected %s.' % (evaluatedValue, leftSet.union(rightSet)))

	def testIntersectSet(self):
		leftSet = set(range(1, 6))
		rightSet = set(range(1, 6, 2))
		leftExpression = Expression.expressionForConstantValue(leftSet)
		rightExpression = Expression.expressionForConstantValue(rightSet)
		expression = Expression.expressionForIntersectSet(leftExpression, rightExpression)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, leftSet.intersection(rightSet), 'IntersectSet expression evaluated to %s. Expected %s.' % (evaluatedValue, leftSet.intersection(rightSet)))

	def testMinusSet(self):
		leftSet = set(range(1, 6))
		rightSet = set(range(1, 6, 2))
		leftExpression = Expression.expressionForConstantValue(leftSet)
		rightExpression = Expression.expressionForConstantValue(rightSet)
		expression = Expression.expressionForMinusSet(leftExpression, rightExpression)
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, leftSet.difference(rightSet), 'MinusSet expression evaluated to %s. Expected %s.' % (evaluatedValue, leftSet.difference(rightSet)))		

	# Subquery - Not Implemented Yet



	# Block - Not Implemented Yet

	# Function

	def testFunction(self):
		numbers = range(1,4)
		numbersExpression = Expression.expressionForConstantValue(numbers)
		expression = Expression.expressionForFunction('sum:', parameters=[numbersExpression])
		evaluatedValue = expression.expressionValueWithObject(self.object)
		self.assertEqual(evaluatedValue, sum(numbers), 'Function expression for sum evaluated to %i. Expected %i.' % (evaluatedValue, sum(numbers)))

	# Format - Not Implemented Yet
