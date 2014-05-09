# coding=utf-8

from . import expressions, predicates

DefaultModel = None

class Rule(object):
	
	def __init__(self, specifier, key, value, weight=0):
		if key is None:
			raise ValueError('key cannot be None')

		if specifier == None:
			specifier = predicates.Predicate.predicateWithValue(True)
		if value == None:
			value = expressions.Expression.expressionForConstantValue(None)

		assert isinstance(specifier, predicates.Predicate), 'specifier is not a Predicate: %s' % str(specifier)
		assert isinstance(value, expressions.Expression), 'value is not an Expression: %s' % str(value)

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
		return self.specifier.evaluateWithObject(context) if self.specifier else True

	def fire(self, context):
		if self.value is None:
			return None
		return self.value.expressionValueWithObject(context)

	def priority(self):
		if self._priority is not -1:
			return self._priority

		priority = self.weight
		if isinstance(self.specifier, predicate.CompoundPredicate):
			priority += len(self.specifier.subpredicates)

		self._priority = priority
		return priority

	def __str__(self):
		return '%s %s: %s [%i]' % (
			self.specifier,
			self.key,
			self.value,
			self.weight
		)

	def __repr__(self):
		return '<%s> %s' % (
			self.__class__.__name__,
			self.__str__()
		)


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

	def __str__(self):
		return '%s' % (
			self.rules
		)

