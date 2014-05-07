import string
import unittest

from .. import expressions
from ..scanners import Scanner, ExpressionScanner

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
