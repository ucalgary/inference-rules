# coding=utf-8

import builtins
import re

from . import predicates

class PredicateOperator(object):

	def __init__(self, operatorType, modifier, options):
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
		predicates.ComparisonPredicateType.LessThan           : lambda l, r: l < r,
		predicates.ComparisonPredicateType.LessThanOrEqual    : lambda l, r: l <= r,
		predicates.ComparisonPredicateType.GreaterThan        : lambda l, r: l > r,
		predicates.ComparisonPredicateType.GreaterThanOrEqual : lambda l, r: l >= r,
		predicates.ComparisonPredicateType.EqualTo            : lambda l, r: l == r,
		predicates.ComparisonPredicateType.NotEqualTo         : lambda l, r: l != r,
		predicates.ComparisonPredicateType.Matches            : lambda l, r: re.match(r, l) != None,
		predicates.ComparisonPredicateType.Like               : None, # subset of MATCHES, similar to SQL like
		predicates.ComparisonPredicateType.BeginsWith         : lambda l, r: l.startswith(r) if l else False,
		predicates.ComparisonPredicateType.EndsWith           : lambda l, r: l.endwith(r) if l else False,
		predicates.ComparisonPredicateType.In                 : lambda l, r: l in r if r else False,
		predicates.ComparisonPredicateType.CustomSelector     : None, # not supported yet
		predicates.ComparisonPredicateType.Contains           : lambda l, r: r in l if l else False, # l contains r, l must be a collection
		predicates.ComparisonPredicateType.Between            : lambda l, r: r[0] < l < r[1]
	}

	def performOperationUsingObjects(self, obj1, obj2):
		operatorFunction = self.operatorFunction()

		return operatorFunction(obj1, obj2)


class CompoundPredicateOperator(PredicateOperator):

	_operatorFunctionsByType = {
		predicates.CompoundPredicateType.Not: lambda p: not p[0],
		predicates.CompoundPredicateType.And: getattr(builtins, 'all'),
		predicates.CompoundPredicateType.Or:  getattr(builtins, 'any')
	}

	def evaluatePredicatesWithObject(self, predicates, obj, substitutions=None):
		# assert self._compoundPredicateType in (CompoundPredicateType.And, CompoundPredicateType.Or), 'compoundPredicateType is not Not, and is neither And or Or'

		operatorFunction = self.operatorFunction()

		return operatorFunction(p.evaluateWithObject(obj) for p in predicates)
