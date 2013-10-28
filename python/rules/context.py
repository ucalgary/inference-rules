# coding=utf-8

from .model import DefaultModel

class Context(object):

	def __init__(self, model=None, parentContext=None):
		self._model = parentContext.model if parentContext is not None else model if model is not None else DefaultModel
		self._parentContext = parentContet

	@property
	def model(self):
		return self._model

	def inferValueForKey(self, key):
		self.model.fireRuleForKeyPathInContext(key, self)

	def inferAllPossibleValuesForKey(self, key):
		self.model.fireAllRulesForKeyPathInContext(key, self)

