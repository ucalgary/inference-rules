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

	def testValuePredicate(self):
		truePredicate = Predicate.predicateWithValue(True)
		falsePredicate = Predicate.predicateWithValue(False)
		self.assertTrue(truePredicate.evaluateWithObject(self.object))
		self.assertFalse(falsePredicate.evaluateWithObject(self.object))

	def testComparisonPredicate(self):
		leftExpression = Expression.expressionForKeyPath(self.key)
		rightExpression = Expression.expressionForConstantValue(self.value)
		predicate = ComparisonPredicate(leftExpression, rightExpression)
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)

	def testAndPredicate(self):
		truePredicate = Predicate.predicateWithValue(True)
		predicate = Predicate.andPredicateWithSubpredicates([truePredicate, truePredicate])
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)

	def testOrPredicate(self):
		truePredicate = Predicate.predicateWithValue(True)
		falsePredicate = Predicate.predicateWithValue(False)
		predicate = Predicate.orPredicateWithSubpredicates([truePredicate, falsePredicate])
		evaluatedValue = predicate.evaluateWithObject(self.object)
		self.assertTrue(evaluatedValue)
