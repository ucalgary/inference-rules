import unittest

from .. import pathutils

class PathUtilsPathComponentTest(unittest.TestCase):

	def _testFunctionWithData(self, f, data, exp=False):
		for args, expectedResult in data:
			result = f(*args) if exp else f(args)
			self.assertEqual(result, expectedResult, '%s != %s (%s)' % (repr(result), repr(expectedResult), args))

	def testPathWithComponents(self):
		data = (
			(['a', 'b', 'c'], 'a/b/c'),
			(['a', 'b', '/'], 'a/b'),
			(['a', 'b', ''], 'a/b'),
			(['/', 'a', 'b'], '/a/b'),
			(['', 'a', 'b'], 'a/b'),
			(['a', '/', 'b'], 'a/b'),
			(['a', '//', 'b'], 'a/b'),
			(['a', 'b/c'], 'a/b/c'),
			(['a', 'b//c'], 'a/b/c'),
			(None, None),
			([], '')
		)

		self._testFunctionWithData(pathutils.pathWithComponents, data)

	def testPathComponents(self):
		data = (
			('a/b/c', ['a', 'b', 'c']),
			('a/b/', ['a', 'b', '/']),
			('a/b/ ', ['a', 'b', ' ']),
			('a/b//', ['a', 'b', '/']),
			('a//b/', ['a', 'b', '/']),
			('/a/b', ['/', 'a', 'b']),
			('//a/b', ['/', 'a', 'b']),
			('a/b', ['a', 'b']),
			('a\\/b', ['a\\', 'b']),
			(None, None),
			('', [])
		)

		self._testFunctionWithData(pathutils.pathComponents, data)

	def testLastPathComponent(self):
		data = (
			('a/b/c', 'c'),
			('a/b/c.txt', 'c.txt'),
			('a/b/', 'b'),
			('a/b//', 'b'),
			('a//b/', 'b'),
			('/a/b', 'b'),
			('//a/b', 'b'),
			('a/b', 'b'),
			('a\\/b', 'b'),
			('/', '/'),
			('//', '/'),
			(None, None),
			('', '')
		)

		self._testFunctionWithData(pathutils.lastPathComponent, data)

	def testDeleteLastPathComponent(self):
		data = (
			('a/b/c', 'a/b'),
			('a/b/c.txt', 'a/b'),
			('a/b/', 'a'),
			('a/b//', 'a'),
			('a//b/', 'a'),
			('/a/b', '/a'),
			('//a/b', '/a'),
			('a/b', 'a'),
			('a\\/b', 'a\\'),
			('/', '/'),
			('//', '/'),
			(None, None),
			('', '')
		)

		self._testFunctionWithData(pathutils.deleteLastPathComponent, data)

	def testAppendPathComponent(self):
		data = (
			(('a/b', 'c'), 'a/b/c'),
			(('a/b/', 'c'), 'a/b/c'),
			(('a/b/', '/c'), 'a/b/c'),
			(('a/b', '/c'), 'a/b/c'),
			(('a/b', '//c'), 'a/b/c'),
			(('a/b//', '/c'), 'a/b/c'),
			(('a/b//', 'c'), 'a/b/c'),
			((None, None), None),
			((None, 'a'), 'a'),
			(('a', None), 'a'),
			(('', ''), ''),
			((None, ''), ''),
			(('', None), '')
		)

		self._testFunctionWithData(pathutils.appendPathComponent, data, exp=True)
