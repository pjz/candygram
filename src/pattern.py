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

__revision__ = '$Id: pattern.py,v 1.4 2004/08/19 23:13:41 hobb0001 Exp $'


import types


# Generate a unique values for 'Any' and 'AnyRemaining' so that they won't ever
# be confused with any other value.
Any = object()
AnyRemaining = object()


def genFilter(pattern):
	"""generate a pattern filter"""
	if isinstance(pattern, tuple) or isinstance(pattern, list):
		result = genSeqFilter(pattern, t)
	elif isinstance(pattern, dict):
		result = genDictFilter(pattern)
	elif isinstance(pattern, type) or type(pattern) is types.ClassType:
		result = genTypeFilter(pattern)
	elif callable(pattern):
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
	if seq and seq[-1] is AnyRemaining:
		anyRemaining = True
		seq = seq[:-1]
	seqLen = len(seq)
	subFilters = [genFilter(pattern) for pattern in seq]
	seqRange = range(seqLen)
	def filt(x):
		"""resulting filter function"""
		if not isinstance(x, seqType):
			return False
		if anyRemaining and len(x) < seqLen:
			return False
		if not anyRemaining and len(x) != seqLen:
			return False
		for i in seqRange:
			if not subFilters[i](x[i]):
				return False
			# end if
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
			# end if
		return True
	return filt
