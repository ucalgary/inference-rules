import unittest

from .. import kvc

class KVCTest(unittest.TestCase):

	def setUp(self):
		self.obj = {
			'title': 'The Hitchhiker\'s Guide to the Galaxy',
			'author': 'Douglas Adams',
			'numbers': [1, 2, 3, 4, 5],
			'places': [
				{
					'name': 'Calgary',
					'pop': 988195
				},
				{
					'name': 'Edmonton',
					'pop': 730375
				},
				{
					'name': 'Vancouver',
					'pop': 578040
				}
			],
			'names': {
				'short': [
					'Ada',
					'Bob',
					'Jim'
				],
				'long': [
					'Jacqueline',
					'Isabella',
					'Nathaniel'
				],
				'total': 6
			}
		}

		import random
		import string

		self.key = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.value = ''.join(random.choice(string.ascii_lowercase) for _ in range(6))
		self.object = {
			self.key: self.value
		}
		
	# Values

	def testValueForKey(self):
		value = kvc.valueForKey(self.obj, 'title')
		self.assertEqual(value, 'The Hitchhiker\'s Guide to the Galaxy')

	def testValueForKeyPath(self):
		value = kvc.valueForKeyPath(self.obj, 'names.total')
		self.assertEqual(value, 6)