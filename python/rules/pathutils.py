# coding=utf-8

import re

pathSeparator = '/'

def pathWithComponents(components):
	if components == None:
		return None
	if len(components) == 0:
		return ''

	# Eliminate runs of pathSeparator and empty components
	components = [re.sub(pathSeparator + r'+', pathSeparator, component) for component in components if component != '']
	# Eliminate components that are only a separator, past the first component
	components[1:] = [component for component in components[1:] if component != pathSeparator]
	# If the first component is just pathSeparator, replace it with an empty string
	if components[0] == pathSeparator:
		components[0] = ''

	return pathSeparator.join(components)

def pathComponents(path):
	if path == None:
		return None
	if len(path) == 0:
		return []

	# Collapse runs of / to a single /
	path = re.sub(r'/+', pathSeparator, path)
	# Split into components by path separator
	pathComponents = path.split(pathSeparator)
	# Replace empty strings at the beginning and end with path separator
	if pathComponents[0] == '':
		pathComponents[0] = pathSeparator
	if pathComponents[-1] == '':
		pathComponents[-1] = pathSeparator

	return pathComponents

def lastPathComponent(path):
	if path == None:
		return None
	if len(path) == 0:
		return ''

	# Collapse runs of / to a single /
	path = re.sub(r'/+', pathSeparator, path)

	# If path is just /, return it
	if path == '/':
		return path

	pathComponent = path
	separatorIndex = path.rfind(pathSeparator)
	lastIndex = len(path) - 1;

	if separatorIndex == lastIndex:
		separatorIndex = path.rfind(pathSeparator, 0, lastIndex - 1)
		if separatorIndex >= 0 and separatorIndex < lastIndex:
			pathComponent = path[separatorIndex + 1:lastIndex]
		else:
			pathComponent = path[0:lastIndex]
	else:
		if separatorIndex >= 0 and separatorIndex < lastIndex:
			pathComponent = path[separatorIndex + 1:]

	return pathComponent

def deleteLastPathComponent(path):
	if path == None:
		return None
	if len(path) == 0:
		return ''

	# Collapse runs of / to a single /
	path = re.sub(r'/+', pathSeparator, path)

	# If path is just /, return it
	if path == '/':
		return path

	separatorIndex = path.rfind(pathSeparator)
	firstSeparatorIndex = 0
	lastIndex = len(path) - 1

	if re.match('^\w', path) != None:
		if path.find(':/') == 1 or path.find(':\\') == 1:
			firstSeparatorIndex = 2
			if separatorIndex == -1:
				separatorIndex = path.rfind('\\')
		else:
			if path.find(':') == 1:
				separatorIndex = firstSeparatorIndex = 1
	if separatorIndex > -1 and separatorIndex == firstSeparatorIndex:
		return path[0:firstSeparatorIndex + 1]
	if separatorIndex == lastIndex:
		separatorIndex = path.rfind(pathSeparator, 0, lastIndex - 1)
	if separatorIndex > -1 and separatorIndex == firstSeparatorIndex:
		return path[0:firstSeparatorIndex + 1]
	if separatorIndex > 0:
		return path[0:separatorIndex]

	return ''

def appendPathComponent(path, component):
	if path == None:
		return component if component != None else ''
	if component == None:
		return path

	pathLength = len(path)
	componentLength = len(component)

	if pathLength == 0:
		return component
	if componentLength == 0:
		return path

	pathEndsWithFileSeparator = path[-1] == pathSeparator
	componentStartsWithFileSeparator = component[0] == pathSeparator

	if pathEndsWithFileSeparator and componentStartsWithFileSeparator:
		return path[0:pathLength - 1] + component
	if pathEndsWithFileSeparator or componentStartsWithFileSeparator:
		return path + component
	return path + pathSeparator + component

def pathExtension(path):
	if path == None:
		return None
	pathLength = len(path)
	if pathLength == 0:
		return ''

	extensionIndex = path.rfind('.')
	if extensionIndex >= 0:
		separatorIndex = path.rfind(pathSeparator)
		lastIndex = pathLength - 1
		substringIndex = pathLength

		if separatorIndex == lastIndex:
			separatorIndex = path.rfind(pathSeparator, 0, lastIndex - 1)
			substringIndex = lastIndex

		if (separatorIndex < 0 or extensionIndex > separatorIndex) and extensionIndex < pathLength - 1:
			return path[extensionIndex + 1:substringIndex]

	return ''

def deletePathExtension(path):
	length = len(path)
	pos = 0

	if re.match('^\/*$', path) != None:
		if length == 0:
			return ''
		else:
			return pathSeparator

	lastSlash = path.rfind(pathSeparator)
	pos = path.find('.', lastSlash)

	return path[0:lastSlash + 1] if pos == -1 else path[0:pos]

def appendPathExtension(path):
	if path == None:
		if extension == None:
			return '.' + extension
		else:
			return None
	if extension == None:
		return path

	pathLength = len(path)

	if path[-1] == '/' and pathLength > 1:
		return path[0:pathLength - 1] + '.' + extension
	else:
		return path + '.' + extension

def standardizePath(path):
	if path == None:
		return None
	if len(path) == 0:
		return ''

	# Collapse runs of / to a single /
	path = re.sub(r'/+', pathSeparator, path)
	pathLength = len(path)

	if path[-1] == '/' and pathLength > 1:
		pathLength -= 1
		path = path[0, pathLength]

	searchStartIndex = 0
	idx = path.find('..', searchStartIndex)

	while idx >= 0:
		if idx == 0:
			raise ValueError('Cannot resolve path starting with ..')
		if path[idx - 1] == pathSeparator:
			idx2 = path.rfind(pathSeparator, 0, idx - 2)
			if idx + 2 >= pathLength:
				path = '' if idx2 < 0 else pathSeparator if idx2 == 0 else path[0:idx2]
			elif path[idx + 2] == pathSeparator:
				path = path[idx + 3:] if idx2 < 0 else path[idx + 2:] if idx2 == 0 else path[0:idx2 + 1] + path[idx + 3:]
			else:
				searchStartIndex = idx + 2
		else:
			searchStartIndex = idx + 2
		idx = path.find('..', searchStartIndex)
		pathLength = len(path)

	return path
