# coding=utf-8

import string

ScannerCharactersToBeSkippedCharacterSet = set(('\t', '\n', '\v', '\f', '\r', ' ', '\0085', '\00a0'))
IdentifierExpressionCharacterSet = set(c for c in '_$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
PropertyKeyCharacterSet = set(c for c in string.ascii_letters + string.digits + '_-')
