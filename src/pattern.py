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

import types



Any = object()
AnyRemaining = object()


def genFilter(pattern):
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
	return lambda x: True

def genValueFilter(value):
	return lambda x: x == value

def genFuncFilter(func):
	return func

def genTypeFilter(t):
	return lambda x: isinstance(x, t)

def genSeqFilter(seq, seq_type):
	# Define these values as constants outside of the filt() function so that
	# the filter will not have to re-calculate the values every time it's called.
	seq_len = len(seq)
	if seq_len > 0 and seq[-1] is AnyRemaining:
		any_remaining = True
		sub_filters = map(genFilter, seq[:-1])
		seq_range = range(seq_len - 1)
	else:
		any_remaining = False
		sub_filters = map(genFilter, seq)
		seq_range = range(seq_len)
	def filt(x):
		if type(x) is not seq_type:
			return False
		if any_remaining and len(x) < seq_len - 1:
			return False
		if not any_remaining and len(x) != seq_len:
			return False
		for i in seq_range:
			if not sub_filters[i](x[i]):
				return False
			pass
		return True
	return filt

def genDictFilter(dict):
	sub_filters = []
	for key, pattern in dict.items():
		sub_filters.append((key, genFilter(pattern)))
	def filt(x):
		for key, sub_filter in sub_filters:
			if key not in x:
				return False
			if not sub_filter(x[key]):
				return False
			pass
		return True
	return filt
