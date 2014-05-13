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

		self._calculatePriority()

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
		return self._priority

	def _calculatePriority(self):
		priority = self._priorityForPredicate(self.specifier)
		if self.weight != 0:
			priority += self.weight * 1000
		self._priority = priority

	def _priorityForPredicate(self, predicate):
		if not predicate:
			return 0
		if isinstance(predicate, predicates.ComparisonPredicate):
			return 2
		if isinstance(predicate, predicates.CompoundPredicate):
			return 1 + sum(self._priorityForPredicate(p) for p in predicate.subpredicates)
		if isinstance(predicate, predicates.ValuePredicate):
			return 1
		return 0

	def canFireInContext(self, context):
		return self.specifier.evaluateWithObject(context) if self.specifier else True

	def fire(self, context):
		if self.value is None:
			return None
		return self.value.expressionValueWithObject(context)

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

	# Rich Comparison Operators

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

		return self.specifier == other.speciifer and \
		       self.key == other.key and \
		       self.value == other.value and \
		       self.weight == other.weight

	def __ne__(self, other):
		return not self.__eq__(other)

	def __gt__(self, other):
		return self.priority > other.priority

	def __ge__(self, other):
		return self.priority >= other.priority

	def __lt__(self, other):
		return self.priority < other.priority

	def __le__(self, other):
		return self.priority <= other.priority
		

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

