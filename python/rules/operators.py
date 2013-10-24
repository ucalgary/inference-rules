# coding=utf-8

import __builtin__
import re

from . import predicate

class PredicateOperator(object):

	def __init__(self, operatorType, modifier, **options):
		self._operatorType = operatorType
		self._modifier = modifier
		self._options = options

	@property
	def operatorType(self):
		return self._operatorType

	@property
	def modifier(self):
		return self._modifier

	@property
	def options(self):
		return self._options

	def operatorFunction(self):
		return self.__class__._operatorFunctionsByType[self.operatorType]


class ComparisonPredicateOperator(PredicateOperator):

	_operatorFunctionsByType = {
		predicate.ComparisonPredicateType.LessThan           : lambda l, r: l < r,
		predicate.ComparisonPredicateType.LessThanOrEqual    : lambda l, r: l <= r,
		predicate.ComparisonPredicateType.GreaterThan        : lambda l, r: l > r,
		predicate.ComparisonPredicateType.GreaterThanOrEqual : lambda l, r: l >= r,
		predicate.ComparisonPredicateType.EqualTo            : lambda l, r: l == r,
		predicate.ComparisonPredicateType.NotEqualTo         : lambda l, r: l != r,
		predicate.ComparisonPredicateType.Matches            : lambda l, r: re.match(l, r),
		predicate.ComparisonPredicateType.Like               : None, # subset of MATCHES, similar to SQL like
		predicate.ComparisonPredicateType.BeginsWith         : lambda l, r: l.startswith(r),
		predicate.ComparisonPredicateType.EndsWith           : lambda l, r: l.endwith(r),
		predicate.ComparisonPredicateType.In                 : lambda l, r: l in r,
		predicate.ComparisonPredicateType.CustomSelector     : None, # not supported yet
		predicate.ComparisonPredicateType.Contains           : lambda l, r: r in l, # l contains r, l must be a collection
		predicate.ComparisonPredicateType.Between            : lambda l, r: r[0] < l < r[1]
	}

	def performOperationUsingObjects(self, obj1, obj2):
		operatorFunction = self.operatorFunction()

		return operatorFunction(obj1, obj2)


class CompoundPredicateOperator(PredicateOperator):

	_operatorFunctionsByType = {
		predicate.CompoundPredicateType.Not: lambda p: not p[0],
		predicate.CompoundPredicateType.And: getattr(__builtin__, 'all'),
		predicate.CompoundPredicateType.Or:  getattr(__builtin__, 'any')
	}

	def evaluatePredicatesWithObject(self, predicates, obj, substitutions=None):
		# assert self._compoundPredicateType in (CompoundPredicateType.And, CompoundPredicateType.Or), 'compoundPredicateType is not Not, and is neither And or Or'

		operatorFunction = self.operatorFunction()
		evaluatedPredicates = map(lambda p: p.evaluateWithObject(obj), predicates)

		return operatorFunction(evaluatedPredicates)
