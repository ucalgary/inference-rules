import unittest

from .. import pathutils

class PathUtilsPathComponentTest(unittest.TestCase):

	def _testFunctionWithData(self, f, data, exp=False):
		for args, expectedResult in data:
			result = f(*args) if exp else f(args)
			self.assertEqual(result, expectedResult)

	def testPathWithComponents(self):
		data = (
			(['a', 'b', 'c'], 'a/b/c'),
			(['a', 'b', '/'], 'a/b'),
			(['a', 'b', ''], 'a/b'),
			(['/', 'a', 'b'], '/a/b'),
			(['', 'a', 'b'], 'a/b')
		)

		self._testFunctionWithData(pathutils.pathWithComponents, data)

	def testPathComponents(self):
		data = (
			('a/b/c', ['a', 'b', 'c']),
			('a/b/', ['a', 'b', '/']),
			('a/b//', ['a', 'b', '/']),
			('a//b/', ['a', 'b', '/']),
			('/a/b', ['/', 'a', 'b']),
			('//a/b', ['/', 'a', 'b']),
			('a/b', ['a', 'b'])
		)

		self._testFunctionWithData(pathutils.pathComponents, data)

	def testLastPathComponent(self):
		data = (
			('a/b/c', 'c'),
			('a/b/c.txt', 'c.txt'),
			('a/b/', 'b'),
			('a/b//', 'b'),
			('/', '/'),
			('//', '/')
		)

		self._testFunctionWithData(pathutils.lastPathComponent, data)

	def testDeleteLastPathComponent(self):
		data = (
			('a/b/c', 'a/b'),
			('a/b/c.txt', 'a/b'),
			('a/b/', 'a'),
			('a/b//', 'a'),
			('/', '/'),
			('//', '/')
		)

		self._testFunctionWithData(pathutils.deleteLastPathComponent, data)

	def testAppendPathComponent(self):
		data = (
			(('a/b', 'c'), 'a/b/c'),
			(('a/b/', 'c'), 'a/b/c'),
			(('a/b/', '/c'), 'a/b/c'),
			(('a/b', '/c'), 'a/b/c'),
			(('a/b', '//c'), 'a/b/c'),
			(('a/b//', '/c'), 'a/b/c')
			(('a/b//', 'c'), 'a/b/c')
		)

		self._testFunctionWithData(pathutils.appendPathComponent, data, exp=True)
