# receiver.py
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

"""Receiver class"""

__revision__ = "$Id: receiver.py,v 1.13 2005/02/14 20:56:35 hobb0001 Exp $"


import time

from candygram.main import _checkSignal, self_, ExitError
from candygram.pattern import genFilter
from candygram.threadimpl import allocateLock


# Generate a unique value for 'Message' so that it won't ever be confused with
# any other value.
Message = object()


class Receiver:

    """Retrieves messages from process's mailbox"""

    def __init__(self):
        _checkSignal()
        # Lock for __handlers, __lastMessage,  and __timeout* attributes.
        self.__lock = allocateLock()
        self.__nextHandlerId = 0
        self.__handlers = []
        self.__lastMessage = 0
        self.__currentProcess = None
        self.__mailbox = None
        self.__mailboxCondition = None
        self.__timeout = None
        self.__timeoutHandler = None
        self.__timeoutArgs = None
        self.__timeoutKWArgs = None

    def addHandler(self, pattern, handler=None, *args, **kwargs):
        """add pattern handler to receiver"""
        _checkSignal()
        if handler is not None and not callable(handler):
            raise ExitError("badarg")
        filter_ = genFilter(pattern)
        with self.__lock:
            handlerId = self.__nextHandlerId
            self.__nextHandlerId += 1
            self.__handlers.append((handlerId, filter_, handler, args, kwargs))
            # Clear all skipped messages, since the new handler might be able to handle
            # them.
            self.__lastMessage = 0
        return handlerId

    def after(self, timeout, handler=None, *args, **kwargs):
        """add timeout handler to receiver"""
        _checkSignal()
        self.__setAfter(timeout, handler, args, kwargs)

    def __setitem__(self, key, value):
        if isinstance(value, tuple):
            self.addHandler(key, value[0], *value[1:])
        else:
            self.addHandler(key, value)
        # end if

    def __getitem__(self, key):
        self.addHandler(key)
        return None

    def addHandlers(self, receiver):
        """copy handlers from receiver to self"""
        _checkSignal()
        if not isinstance(receiver, Receiver):
            raise ExitError("badarg")
        with receiver.__lock:
            handlers = receiver.__handlers[:]
        result = []
        with self.__lock:
            for id_, filter_, handler, args, kwargs in handlers:
                handlerId = self.__nextHandlerId
                self.__nextHandlerId += 1
                self.__handlers.append((handlerId, filter_, handler, args, kwargs))
                result.append(handlerId)
            # Clear all skipped messages, since the new handlers might be able to handle
            # them.
            self.__lastMessage = 0
        return result

    def removeHandler(self, handlerReference):
        """remove handler from receiver"""
        with self.__lock:
            for i in range(len(self.__handlers)):
                if self.__handlers[i][0] == handlerReference:
                    del self.__handlers[i]
                    return
        raise ExitError("badarg")

    def receive(self, timeout=None, handler=None, *args, **kwargs):
        """retrieve one message from mailbox"""
        _checkSignal()
        self.__checkCurrentProcess()
        if timeout is not None:
            self.__setAfter(timeout, handler, args, kwargs)
        expire = None
        with self.__lock:
            if self.__timeout is not None:
                expire = time.time() + self.__timeout
        handlerInfo = None
        with self.__mailboxCondition:
            # self.__wait() may raise an exception if this process has received a signal
            while handlerInfo is None:
                handlerInfo = self.__scanMailbox()
                # If none of the filters picked up a message from the mailbox, wait
                # until a new message is sent and then try again.
                if handlerInfo is None:
                    handlerInfo = self.__wait(expire)
                # end if
        if timeout is not None:
            self.__removeAfter()
        message, handler, args, kwargs = handlerInfo
        if handler is None:
            return None
        args = _replaceMessageArgs(args, message)
        kwargs = _replaceMessageKWArgs(kwargs, message)
        return handler(*args, **kwargs)

    __call__ = receive
    __next__ = receive

    def __iter__(self):
        return self

    def __setAfter(self, timeout, handler, args, kwargs):
        """set timeout handler"""
        if not isinstance(timeout, int):
            raise ExitError("badarg")
        if handler is not None and not callable(handler):
            raise ExitError("badarg")
        with self.__lock:
            assert (
                self.__timeout is None
            ), "A timeout has already been set for this Receiver"
            # Timeout is specified in milliseconds
            self.__timeout = float(timeout) / 1000
            self.__timeoutHandler = handler
            self.__timeoutArgs = args
            self.__timeoutKWArgs = kwargs

    def __removeAfter(self):
        """remove timeout handler"""
        with self.__lock:
            assert self.__timeout is not None
            self.__timeout = None
            self.__timeoutHandler = None
            self.__timeoutArgs = None
            self.__timeoutKWArgs = None

    def __scanMailbox(self):
        """see if any message in mailbox matches a registered pattern"""
        assert self.__mailboxCondition.locked()
        # Prevent anyone from adding a new handler while we're scanning the mailbox:
        with self.__lock:
            for i in range(self.__lastMessage, len(self.__mailbox)):
                message = self.__mailbox[i]
                for id_, filter_, handler, args, kwargs in self.__handlers:
                    if filter_(message):
                        self.__deleteMessage(i)
                        return message, handler, args, kwargs
                    # end if
                self.__lastMessage = i + 1
            return None

    def __deleteMessage(self, i):
        """remove i'th message from mailbox, notifying any other receivers"""
        assert self.__mailboxCondition.locked()
        receivers = self.__currentProcess._getReceivers()
        del self.__mailbox[i]
        for receiver in receivers:
            if receiver is not self:
                # Acquire lock to prevent a remote process from calling addHandler and
                # resetting __lastMessage:
                with receiver.__lock:
                    if receiver.__lastMessage > i:
                        receiver.__lastMessage -= 1

    def __wait(self, expire):
        """wait expire milliseconds for a new message"""
        waitTime = None
        if expire is not None:
            waitTime = max(0, expire - time.time())
        if not self.__mailboxCondition.wait(waitTime):
            with self.__lock:
                return (
                    None,
                    self.__timeoutHandler,
                    self.__timeoutArgs,
                    self.__timeoutKWArgs,
                )
        # We may have been woken up by a signal
        _checkSignal()
        return None

    def __checkCurrentProcess(self):
        """check that self.__currentProcess is still current process"""
        currentProcess = self_()
        if self.__currentProcess is currentProcess:
            return
        if self.__currentProcess is not None:
            self.__currentProcess._removeReceiver(self)
        self.__currentProcess = currentProcess
        self.__mailbox = currentProcess._mailbox
        self.__mailboxCondition = currentProcess._mailboxCondition
        with self.__lock:
            self.__lastMessage = 0
        currentProcess._addReceiver(self)


def _replaceMessageArgs(args, message):
    """replace any instance of Message with message"""

    def change(arg):
        """convert arg to message if arg is Message"""
        if arg is Message:
            return message
        return arg

    return [change(arg) for arg in args]


def _replaceMessageKWArgs(kwargs, message):
    """replace any instance of Message with message"""
    result = {}
    for key, value in kwargs.items():
        if value is Message:
            result[key] = message
        else:
            result[key] = value
        # end if
    return result
