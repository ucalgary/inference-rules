# coding=utf-8

import collections

from .rules import DefaultModel

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
		if key in self._localValues:
			return self._localValues[key]
		return self.inferValueForKey(key)

	def __setitem__(self, key, value):
		self._localValues[key] = value

	def __delitem__(self, key):
		del self._localValues[key]

	def __iter__(self):
		return iter(self._localValues)

	def __len__(self):
		return len(self._localValues)

	def __keytransform__(self, key):
		return key
