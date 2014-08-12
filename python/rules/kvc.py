# coding=utf-8

import collections

def valueForKey(obj, key):
	if not key:
		return None

	if isinstance(obj, (list, tuple)):
		return map(lambda o: valueForKey(o, key), obj)
	elif isinstance(obj, collections.Mapping):
		return obj.get(key)
	else:
		value = getattr(obj, key)
		if callable(value):
			value = value()
		return value

def valueForKeyPath(obj, keyPath):
	separatorIndex = keyPath.find('.')

	if separatorIndex is -1:
		return valueForKey(obj, keyPath)

	firstKeyComponent = keyPath[0 : separatorIndex]
	remainingKeyPath = keyPath[separatorIndex + 1 :]
	intermediateValue = valueForKey(obj, firstKeyComponent)

	return valueForKeyPath(intermediateValue, remainingKeyPath)

def setValueForKey(obj, value, key):
	pass

def setValueForKeyPath(obj, value, keyPath):
	pass