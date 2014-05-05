import string
import unittest

from ..scanner import Scanner

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