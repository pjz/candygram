# pattern.py
#
# Copyright (c) 2004 Michael Hobbs
#
# This file is part of Candygram.
#
# Candygram is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# Candygram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Candygram; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Pattern filter generator"""

__revision__ = '$Id: pattern.py,v 1.3 2004/08/18 22:10:24 hobb0001 Exp $'

import types



Any = object()
AnyRemaining = object()


def genFilter(pattern):
	"""generate a pattern filter"""
	t = type(pattern)
	if t is types.TupleType or t is types.ListType:
		result = genSeqFilter(pattern, t)
	elif t is types.DictType:
		result = genDictFilter(pattern)
	elif t is types.TypeType or t is types.ClassType:
		result = genTypeFilter(pattern)
	elif t is types.FunctionType or t is types.MethodType or \
			t is types.BuiltinFunctionType:
		result = genFuncFilter(pattern)
	elif pattern is Any:
		result = genAnyFilter(pattern)
	else:
		result = genValueFilter(pattern)
	return result

def genAnyFilter(unused):
	"""gen filter for Any"""
	return lambda x: True

def genValueFilter(value):
	"""gen filter for a specific value"""
	return lambda x: x == value

def genFuncFilter(func):
	"""gen filter for a function"""
	return func

def genTypeFilter(t):
	"""gen filter for a type check"""
	return lambda x: isinstance(x, t)

def genSeqFilter(seq, seqType):
	"""gen filter for a sequence pattern"""
	# Define these values as constants outside of the filt() function so that
	# the filter will not have to re-calculate the values every time it's called.
	anyRemaining = False
	if len(seq) > 0 and seq[-1] is AnyRemaining:
		anyRemaining = True
		seq = seq[:-1]
	seqLen = len(seq)
	subFilters = [genFilter(pattern) for pattern in seq]
	seqRange = range(seqLen)
	def filt(x):
		"""resulting filter function"""
		if type(x) is not seqType:
			return False
		if anyRemaining and len(x) < seqLen:
			return False
		if not anyRemaining and len(x) != seqLen:
			return False
		for i in seqRange:
			if not subFilters[i](x[i]):
				return False
			pass
		return True
	return filt

def genDictFilter(dict_):
	"""gen filter for a dictionary pattern"""
	subFilters = []
	for key, pattern in dict_.items():
		subFilters.append((key, genFilter(pattern)))
	def filt(x):
		"""resulting filter function"""
		for key, subFilter in subFilters:
			if key not in x:
				return False
			if not subFilter(x[key]):
				return False
			pass
		return True
	return filt
