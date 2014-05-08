# coding=utf-8

from . import predicate

DefaultModel = None

class Rule(object):
	
	def __init__(self, lhs, rhs, weight=0):
		if rhs is None:
			raise ValueError('rhs cannot be None')

		self._lhs = lhs 	# Condition (Predicate)
		self._rhs = rhs 	# Action (Expression)
		self._weight = weight
		self._priority = -1

	@property
	def lhs(self):
		return self._lhs

	@property
	def rhs(self):
		return self._rhs

	@property
	def weight(self):
		return self._weight

	@property
	def priority(self):
		return 0

	def canFireInContext(self, context):
		return self.lhs.evaluateWithObject(context) if self.lhs not None else True

	def fire(self, context):
		assert rhs is not None
		return self.rhs.expressionValueWithObject(context)

	def priority(self):
		if self._priority is not -1:
			return self._priority

		priority = self.weight
		if isinstance(self.lhs, predicate.CompoundPredicate)
			priority += len(self.lhs.subpredicates)

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

