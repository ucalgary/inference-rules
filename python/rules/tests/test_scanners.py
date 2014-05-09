import pkg_resources
import string
import unittest

from .. import expressions, predicates
from ..scanners import Scanner, ExpressionScanner, PredicateScanner, ModelScanner

class ScannerTest(unittest.TestCase):

	def setUp(self):
		self.numbers_and_strings = '12345alpha67890bravo12345charlie67890delta'
		self.strings_and_numbers = 'alpha12345bravo67890charlie12345delta67890'

	def testScanString(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanString('12345')
		self.assertEqual(result, '12345')
		self.assertEqual(scanner.scanLocation, 5)

	def testScanUpToString(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanUpToString('bravo')
		self.assertEqual(result, '12345alpha67890')
		self.assertEqual(scanner.scanLocation, 15)
		self.assertFalse(scanner.atEnd)

	def testScanFloat(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanFloat()
		self.assertEqual(result, 12345.0)

	def testScanInt(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanInt()
		self.assertEqual(result, 12345)
		self.assertEqual(scanner.scanLocation, 5)

	def testScanFloat(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanFloat()
		self.assertEqual(result, 12345.0)
		self.assertEqual(scanner.scanLocation, 5)

	def testScanIntFloatAndStringCombo(self):
		scanner = Scanner(self.numbers_and_strings)
		self.assertEqual(scanner.scanInt(), 12345)
		self.assertEqual(scanner.scanLocation, 5)
		self.assertEqual(scanner.scanUpToString('6'), 'alpha')
		self.assertEqual(scanner.scanLocation, 10)
		self.assertEqual(scanner.scanFloat(), 67890.0)
		self.assertEqual(scanner.scanLocation, 15)
		self.assertEqual(scanner.scanUpToString('1'), 'bravo')
		self.assertEqual(scanner.scanLocation, 20)

	def testScanCharactersFromSet(self):
		scanner = Scanner(self.strings_and_numbers)
		result = scanner.scanCharactersFromSet(string.ascii_lowercase)
		self.assertEqual(result, 'alpha')
		self.assertEqual(scanner.scanLocation, 5)

	def testScanUpToCharactersFromSet(self):
		scanner = Scanner(self.numbers_and_strings)
		result = scanner.scanUpToCharactersFromSet(string.ascii_lowercase)
		self.assertEqual(result, '12345')
		self.assertEqual(scanner.scanLocation, 5)


class ExpressionScannerTest(unittest.TestCase):

	def testParseTrueFalseNullConstantValueExpression(self):
		for expressionFormat, expectedValue in (
			('TRUE', True), ('YES', True),
			('FALSE', False), ('NO', False),
			('NULL', None), ('NIL', None),
		):
			scanner = ExpressionScanner(expressionFormat)
			expression = scanner.parseExpression()
			self.assertIsInstance(expression, expressions.ConstantValueExpression)
			self.assertEqual(expression.constantValue, expectedValue)
			self.assertTrue(scanner.atEnd)

	def testParseNumberConstantValueExpression(self):
		scanner = ExpressionScanner('1')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.ConstantValueExpression)
		self.assertEqual(expression.constantValue, 1)
		self.assertTrue(scanner.atEnd)

	def testParseStringConstantValueExpression(self):
		for string in ('"string"', "'string'"):
			scanner = ExpressionScanner(string)
			expression = scanner.parseExpression()
			self.assertIsInstance(expression, expressions.ConstantValueExpression)
			self.assertEqual(expression.constantValue, 'string')
			self.assertTrue(scanner.atEnd)

	def testParseSelfExpression(self):
		scanner = ExpressionScanner('SELF')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.SelfExpression)
		self.assertTrue(scanner.atEnd)

	def testParseVariableExpression(self):
		scanner = ExpressionScanner('$variable')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.VariableExpression)
		self.assertEqual(expression.variable, 'variable')
		self.assertTrue(scanner.atEnd)

	def testParseAggregateExpression(self):
		scanner = ExpressionScanner('{0, 1, 2}')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.AggregateExpression)
		for n in range(0, 3):
			self.assertIsInstance(expression.collection[n], expressions.ConstantValueExpression)
			self.assertEqual(expression.collection[n].constantValue, n)
		self.assertTrue(scanner.atEnd)

	def testParseSetExpression(self):
		for set_type, expression_type in (
			('UNION', expressions.ExpressionType.UnionSet),
			('INTERSECT', expressions.ExpressionType.IntersectSet),
			('MINUS', expressions.ExpressionType.MinusSet)
		):
			expression_format = '{"a", "b"} %s {"b", "c"}' % set_type
			scanner = ExpressionScanner(expression_format)
			expression = scanner.parseExpression()
			self.assertIsInstance(expression, expressions.SetExpression)
			self.assertIsInstance(expression.leftExpression, expressions.AggregateExpression)
			self.assertIsInstance(expression.rightExpression, expressions.AggregateExpression)
			self.assertEqual(expression.expressionType, expressions.ExpressionType.UnionSet)
			self.assertTrue(scanner.atEnd)

	def testParseFunctionExpression(self):
		scanner = ExpressionScanner('sum:(1, 2)')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.FunctionExpression)
		self.assertNotIsInstance(expression, expressions.KeyPathExpression)
		self.assertEqual(expression.function, 'sum:')
		self.assertEqual(expression.arguments[0].constantValue, 1)
		self.assertEqual(expression.arguments[1].constantValue, 2)
		self.assertTrue(scanner.atEnd)

	def testParseKeyPathExpression(self):
		scanner = ExpressionScanner('a.b.c')
		expression = scanner.parseExpression()
		self.assertIsInstance(expression, expressions.KeyPathExpression)
		self.assertEqual(expression.keyPath, 'a.b.c')
		self.assertTrue(scanner.atEnd)


class PredicateScannerTest(unittest.TestCase):

	def testParseValuePredicate(self):
		for format, value in (
			('TRUEPREDICATE', True),
			('FALSEPREDICATE', False)
		):
			scanner = PredicateScanner(format)
			predicate = scanner.parsePredicate()
			self.assertIsInstance(predicate, predicates.ValuePredicate)
			self.assertEqual(predicate.value, value)
			self.assertTrue(scanner.atEnd)

	def testParseConjunctionCompoundPredicate(self):
		format = 'TRUEPREDICATE %s FALSEPREDICATE'
		for conjunction, predicate_type in (
			('AND', predicates.CompoundPredicateType.And),
			('&&', predicates.CompoundPredicateType.And),
			('OR', predicates.CompoundPredicateType.Or),
			('||', predicates.CompoundPredicateType.Or)
		):
			scanner = PredicateScanner(format % conjunction)
			predicate = scanner.parsePredicate()
			self.assertIsInstance(predicate, predicates.CompoundPredicate)
			self.assertEqual(predicate.compoundPredicateType, predicate_type)
			self.assertTrue(scanner.atEnd)

	def testParseNotCompoundPredicate(self):
		format = '%s (TRUEPREDICATE)'
		for keyword in ('NOT', '!'):
			scanner = PredicateScanner(format % keyword)
			predicate = scanner.parsePredicate()
			self.assertIsInstance(predicate, predicates.CompoundPredicate)
			self.assertEqual(predicate.compoundPredicateType, predicates.CompoundPredicateType.Not)
			self.assertTrue(scanner.atEnd)

	def testParseAggregateComparisonPredicate(self):
		format = '%s children.age < 18'
		for keyword, modifier, negate in (
			('ANY', predicates.ComparisonPredicateModifier.Any, False),
			('ALL', predicates.ComparisonPredicateModifier.All, False),
			('NONE', predicates.ComparisonPredicateModifier.Any, True),
			('SOME', predicates.ComparisonPredicateModifier.All, True),
		):
			scanner = PredicateScanner(format % keyword)
			predicate = scanner.parsePredicate()
			if negate:
				self.assertIsInstance(predicate, predicates.CompoundPredicate)
				self.assertEqual(predicate.compoundPredicateType, predicates.CompoundPredicateType.Not)
				predicate = predicate.subpredicates[0]
			self.assertIsInstance(predicate, predicates.ComparisonPredicate)
			self.assertEqual(predicate.modifier, modifier)
			self.assertTrue(scanner.atEnd)

	def testParseBasicComparisonPredicate(self):
		format = 'value %s 1'
		for keyword, predicate_type in (
			('<=', predicates.ComparisonPredicateType.LessThanOrEqual),
			('=<', predicates.ComparisonPredicateType.LessThanOrEqual),
			('>=', predicates.ComparisonPredicateType.GreaterThanOrEqual),
			('=>', predicates.ComparisonPredicateType.GreaterThanOrEqual),
			('==', predicates.ComparisonPredicateType.EqualTo),
			('!=', predicates.ComparisonPredicateType.NotEqualTo),
			('<>', predicates.ComparisonPredicateType.NotEqualTo),
			('<', predicates.ComparisonPredicateType.LessThan),
			('>', predicates.ComparisonPredicateType.GreaterThan),
			('=', predicates.ComparisonPredicateType.EqualTo),
			('MATCHES', predicates.ComparisonPredicateType.Matches),
			('LIKE', predicates.ComparisonPredicateType.Like),
			('BEGINSWITH', predicates.ComparisonPredicateType.BeginsWith),
			('ENDSWITH', predicates.ComparisonPredicateType.EndsWith),
			('IN', predicates.ComparisonPredicateType.In),
			('CONTAINS', predicates.ComparisonPredicateType.Contains),
			('BETWEEN', predicates.ComparisonPredicateType.Between)
		):
			scanner = PredicateScanner(format % keyword)
			predicate = scanner.parsePredicate()
			self.assertIsInstance(predicate, predicates.ComparisonPredicate)
			self.assertEqual(predicate.modifier, predicates.ComparisonPredicateModifier.Direct)
			self.assertEqual(predicate.operatorType, predicate_type)
			self.assertTrue(scanner.atEnd)

	def testParseComparisonPredicateOptions(self):
		format = 'value ==%s 1'
		for keyword, options in (
			('[cd]', predicates.ComparisonPredicateOptions.CaseInsensitive | predicates.ComparisonPredicateOptions.DiacriticInsensitive),
			('[c]', predicates.ComparisonPredicateOptions.CaseInsensitive),
			('[d]', predicates.ComparisonPredicateOptions.DiacriticInsensitive)
		):
			scanner = PredicateScanner(format % keyword)
			predicate = scanner.parsePredicate()
			self.assertIsInstance(predicate, predicates.ComparisonPredicate)
			self.assertEqual(predicate.options, options)
			self.assertTrue(scanner.atEnd)


class ModelScannerTest(unittest.TestCase):

	def _testModelData(self, data_name):
		data = pkg_resources.resource_string('rules.tests.data', data_name)
		scanner = ModelScanner(data)
		model = scanner.parseModel()

		return scanner, model

	def test0001SimpleModel(self):
		# Expecting 1 rule
		# TRUEPREDICATE { key1: '1' }
		scanner, model = self._testModelData('0001-simple-model.irl')
		self.assertEqual(len(model.rules), 1)
		
		rule = model.rules[0]
		self.assertIsInstance(rule.specifier, predicates.ValuePredicate)
		self.assertTrue(rule.specifier.value)

		self.assertEqual(rule.key, 'key1')
		self.assertEqual(rule.value.constantValue, '1')

	def test0002TwoSpecifiers(self):
		# Expecting 2 rules
		# TRUEPREDICATE { key1: '1' }
		# FALSEPREDICATE { key1: '1' }
		scanner, model = self._testModelData('0002-two-specifiers.irl')
		self.assertEqual(len(model.rules), 2)

		rule = model.rules[0]
		self.assertIsInstance(rule.specifier, predicates.ValuePredicate)
		self.assertTrue(rule.specifier.value)
		self.assertEqual(rule.key, 'key1')
		self.assertEqual(rule.value.constantValue, '1')

		rule = model.rules[1]
		self.assertIsInstance(rule.specifier, predicates.ValuePredicate)
		self.assertFalse(rule.specifier.value)

		self.assertEqual(rule.key, 'key1')
		self.assertEqual(rule.value.constantValue, '1')

	def test0003SubRuleset(self):
		# Expecting 2 rules
		# TRUEPREDICATE { key1: '1' }
		# TRUEPREDICATE AND FALSEPREDICATE { key2: '2' }
		scanner, model = self._testModelData('0003-sub-ruleset.irl')
		self.assertEqual(len(model.rules), 2)

		rule = model.rules[0]
		self.assertIsInstance(rule.specifier, predicates.ValuePredicate)
		self.assertTrue(rule.specifier.value)
		self.assertEqual(rule.key, 'key1')
		self.assertEqual(rule.value.constantValue, '1')

		rule = model.rules[1]
		self.assertIsInstance(rule.specifier, predicates.CompoundPredicate)
		self.assertEqual(rule.specifier.compoundPredicateType, predicates.CompoundPredicateType.And)
		self.assertEqual(len(rule.specifier.subpredicates), 2)

		predicate = rule.specifier.subpredicates[0]
		self.assertIsInstance(predicate, predicates.ValuePredicate)
		self.assertTrue(predicate.value)

		predicate = rule.specifier.subpredicates[1]
		self.assertIsInstance(predicate, predicates.ValuePredicate)
		self.assertFalse(predicate.value)

		self.assertEqual(rule.key, 'key2')
		self.assertEqual(rule.value.constantValue, '2')		
