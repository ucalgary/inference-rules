import unittest

from ..expressions import Expression
from ..predicates import Predicate, ComparisonPredicate

class PredicatesBasicCreationAndEvaluationTest(unittest.TestCase):

	def setUp(self):
		import random
		import string

		self.key = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.value = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.object = {
			self.key: self.value
		}

	def testPredicateWithValue(self):
		predicate = Predicate.predicateWithValue(True)
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)

	def testComparisonPredicate(self):
		leftExpression = Expression.expressionForKeyPath(self.key)
		rightExpression = Expression.expressionForConstantValue(self.value)
		predicate = ComparisonPredicate(leftExpression, rightExpression)
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)

	def testAndPredicate(self):
		leftExpression = Expression.expressionForKeyPath(self.key)
		rightExpression = Expression.expressionForConstantValue(self.value)
		comparisonPredicate = ComparisonPredicate(leftExpression, rightExpression)
		predicate = Predicate.andPredicateWithSubpredicates([comparisonPredicate, comparisonPredicate])
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)

	def testOrPredicate(self):
		leftExpression = Expression.expressionForKeyPath(self.key)
		correctRightExpression = Expression.expressionForConstantValue(self.value)
		incorrectRightExpression = Expression.expressionForConstantValue(None)
		correctPredicate = ComparisonPredicate(leftExpression, correctRightExpression)
		incorrectPredicate = ComparisonPredicate(leftExpression, incorrectRightExpression)
		predicate = Predicate.orPredicateWithSubpredicates([correctPredicate, incorrectPredicate])
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)
