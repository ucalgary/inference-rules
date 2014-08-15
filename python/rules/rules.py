# coding=utf-8

import bisect
import itertools
import urllib2

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

	def _ruleWithSubstitutionVariables(self, variables):
		if variables == None:
			return self

		specifier = self.specifier.predicateWithSubstitutionVariables(variables)
		return Rule(specifier, self.key, self.value, weight=self.weight)

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
	
	def __init__(self, rules=None, variables=None):
		self._rules = rules
		self._variables = variables
		self._buckets = {}
		self._bucketsAreValid = False
		self._sortRulesIntoBuckets()

	# Creating Models

	@staticmethod
	def modelFromFile(path):
		with open(path, 'r') as f:
			return Model._modelFromFileObj(f)

	@staticmethod
	def modelFromURL(url):
		f = urllib2.urlopen(url)
		return Model._modelFromFileObj(f)

	@staticmethod
	def _modelFromFileObj(f):
		from .scanners import ModelScanner
		
		data = f.read()
		scanner = ModelScanner(data)
		return scanner.parseModel()

	@property
	def rules(self):
		return self._rules

	def _invalidateCaches(self):
		self._buckets = {}
		self._bucketsAreValid = False

	def _sortRulesIntoBuckets(self):
		self._invalidateCaches()

		# If a variables dictionary is specified, go through all the rule
		# predicates substituting for variables
		if self._variables != None:
			rules = [rule._ruleWithSubstitutionVariables(self._variables) for rule in self.rules]
		else:
			rules = self.rules

		# Group the rules by key, sorted by priority
		for key, group in itertools.groupby(rules, key=lambda x: x.key):
			if not key in self._buckets:
				bucket = []
				self._buckets[key] = bucket
			else:
				bucket = self._buckets[key]

			for rule in group:
				bisect.insort_left(bucket, rule)

		# Reverse the order of the buckets, so most specific specifiers are first
		[bucket.reverse() for bucket in self._buckets.values()]

		self._bucketsAreValid = True

	@property
	def inferrableKeys(self):
		return self._buckets.keys()

	def candidates(self, keyPath, context):
		return self._buckets.get(keyPath)

	def fireRuleForKeyPathInContext(self, keyPath, context):
		candidates = self.candidates(keyPath, context)
		if not candidates:
			return null

		for rule in candidates:
			if rule.canFireInContext(context):
				return rule.fire(context)

		return None

	def fireAllRulesForKeyPathInContext(self, keyPath, context):
		candidates = self.candidates(keyPath, context)
		if not candidates:
			return null

		candidates = filter(lambda rule: rule.canFireInContext(context), candidates)
		
		return map(lambda rule: rule.fire(context), candidates)

	def __str__(self):
		return '%s' % (
			self.rules
		)
