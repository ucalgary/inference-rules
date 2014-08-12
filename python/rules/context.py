# coding=utf-8

import collections

from .model import DefaultModel

class Context(collections.MutableMapping):

	def __init__(self, model=None, parentContext=None):
		self._model = parentContext.model if parentContext is not None else model if model is not None else DefaultModel
		self._parentContext = parentContext
		self._localValues = dict()

	@property
	def model(self):
		return self._model

	def inferValueForKey(self, key):
		self.model.fireRuleForKeyPathInContext(key, self)

	def inferAllPossibleValuesForKey(self, key):
		self.model.fireAllRulesForKeyPathInContext(key, self)

	def __getitem__(self, key):
		pass

	def __setitem__(self, key, value):
		pass

	def __delitem__(self, key):
		pass

	def __iter__(self):
		pass

	def __len__(self):
		pass

	def __keytransform__(self, key):
		pass
