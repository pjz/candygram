# __init__.py
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

from candygram import *
from process import Process
from receiver import Receiver, Message
from pattern import Any, AnyRemaining

# TODO: verify that we should use __all__ (Isn't it for listing sub-packages?)
__all__ = ['Any', 'AnyRemaining', 'Message', 'self', 'self_', 'spawn',
		'spawnLink', 'link', 'unlink', 'exit', 'processes', 'send', 'processFlag',
		'Process', 'Receiver', 'ExitError']

import thread_impl
thread_impl.setImplementation(thread_impl.DEFAULT)
