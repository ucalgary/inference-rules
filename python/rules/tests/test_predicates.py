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
		falsePredicate = Predicate.predicateWithValue(False)

		trueAndTruePredicate = Predicate.andPredicateWithSubpredicates([truePredicate, truePredicate])
		trueAndFalsePredicate = Predicate.andPredicateWithSubpredicates([truePredicate, falsePredicate])
		falseAndTruePredicate = Predicate.andPredicateWithSubpredicates([falsePredicate, truePredicate])
		falseAndFalsePredicate = Predicate.andPredicateWithSubpredicates([falsePredicate, falsePredicate])

		self.assertTrue(trueAndTruePredicate.evaluateWithObject(self.object))
		self.assertFalse(trueAndFalsePredicate.evaluateWithObject(self.object))
		self.assertFalse(falseAndTruePredicate.evaluateWithObject(self.object))
		self.assertFalse(falseAndFalsePredicate.evaluateWithObject(self.object))

	def testOrPredicate(self):
		truePredicate = Predicate.predicateWithValue(True)
		falsePredicate = Predicate.predicateWithValue(False)

		trueOrTruePredicate = Predicate.orPredicateWithSubpredicates([truePredicate, truePredicate])
		trueOrFalsePredicate = Predicate.orPredicateWithSubpredicates([truePredicate, falsePredicate])
		falseOrTruePredicate = Predicate.orPredicateWithSubpredicates([falsePredicate, truePredicate])
		falseOrFalsePredicate = Predicate.orPredicateWithSubpredicates([falsePredicate, falsePredicate])

		self.assertTrue(trueOrTruePredicate.evaluateWithObject(self.object))
		self.assertTrue(trueOrFalsePredicate.evaluateWithObject(self.object))
		self.assertTrue(falseOrTruePredicate.evaluateWithObject(self.object))
		self.assertFalse(falseOrFalsePredicate.evaluateWithObject(self.object))
