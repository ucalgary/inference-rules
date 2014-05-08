# coding=utf-8

from . import predicate

DefaultModel = None

class Rule(object):
	
	def __init__(self, specifier, key, value, weight=0):
		if key is None:
			raise ValueError('key cannot be None')

		self._specifier = specifier # Condition (Predicate)
		self._key = key             # Key (String)
		self._value = value         # Value (Expression)
		self._weight = weight
		self._priority = -1

	@property
	def specifier(self):
		return self._specifier

	@property
	def key(self):
		return self._key

	@property
	def value(self):
		return self._value

	@property
	def weight(self):
		return self._weight

	@property
	def priority(self):
		return 0

	def canFireInContext(self, context):
		return self.specifier.evaluateWithObject(context) if self.specifier not None else True

	def fire(self, context):
		assert self.value is not None
		return self.value.expressionValueWithObject(context)

	def priority(self):
		if self._priority is not -1:
			return self._priority

		priority = self.weight
		if isinstance(self.specifier, predicate.CompoundPredicate)
			priority += len(self.specifier.subpredicates)

		self._priority = priority
		return priority


class Model(object):
	
	def __init__(self, rules=None):
		self._rules = rules
		self._buckets = {}

	@property
	def rules(self):
		return self._rules

	@property
	def inferrableKeys(self):
		return None

	def candidates(self, keyPath, context):
		return self._buckets.get(keyPath)

