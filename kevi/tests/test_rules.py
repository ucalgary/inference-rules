import unittest

from ..expressions import Expression
from ..predicates import Predicate
from ..rules import Rule

class RulePriorityTest(unittest.TestCase):

	def setUp(self):
		self.trueValue = Expression.expressionForConstantValue(True)

	def testComparisonPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('key == True')
		rule = Rule(predicate, 'key', self.trueValue)
		self.assertEqual(rule.priority, 2)

	def testCompoundPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('key == TRUE && key == FALSE')
		rule = Rule(predicate, 'key', self.trueValue)
		self.assertEqual(rule.priority, 5)

	def testNestedCompoundPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('(key == TRUE && key == FALSE) || (key == FALSE)')
		rule = Rule(predicate, 'key', self.trueValue)
		self.assertEqual(rule.priority, 8)

	def testValuePredicatePriority(self):
		predicate = Predicate.predicateWithFormat('TRUEPREDICATE')
		rule = Rule(predicate, 'key', self.trueValue)
		self.assertEqual(rule.priority, 1)

class WeightedRulePriorityTest(unittest.TestCase):

	def setUp(self):
		self.trueValue = Expression.expressionForConstantValue(True)

	def testWeightedComparisonPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('key == True')
		rule = Rule(predicate, 'key', self.trueValue, 1)
		self.assertEqual(rule.priority, 1002)

	def testWeightedCompoundPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('key == TRUE && key == FALSE')
		rule = Rule(predicate, 'key', self.trueValue, 2)
		self.assertEqual(rule.priority, 2005)

	def testWeightedNestedCompoundPredicatePriority(self):
		predicate = Predicate.predicateWithFormat('(key == TRUE && key == FALSE) || (key == FALSE)')
		rule = Rule(predicate, 'key', self.trueValue, 3)
		self.assertEqual(rule.priority, 3008)

	def testWeightedValuePredicatePriority(self):
		predicate = Predicate.predicateWithFormat('TRUEPREDICATE')
		rule = Rule(predicate, 'key', self.trueValue, 4)
		self.assertEqual(rule.priority, 4001)
		