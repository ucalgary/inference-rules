# coding=utf-8

import string

ScannerCharactersToBeSkippedCharacterSet = {'\t', '\n', '\v', '\f', '\r', ' ', u'\0085', u'\00a0'}
IdentifierExpressionCharacterSet = set(c for c in '_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
PropertyKeyCharacterSet = set(c for c in string.ascii_letters + string.digits + '_-')