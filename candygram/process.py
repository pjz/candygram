# process.py
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

"""Process classes"""

__revision__ = "$Id: process.py,v 1.16 2004/09/13 20:11:58 hobb0001 Exp $"


import sys
import atexit
import weakref
from contextlib import contextmanager

from candygram.main import ExitError, _checkSignal
from candygram.threadimpl import allocateLock, startThread, getCurrentThread
from candygram.condition import Condition


class Process:

    """A Candygram Process"""

    def __init__(self):
        self.__alive = True
        self._mailbox = []
        self._mailboxCondition = Condition()
        self.__receiverRefs = []
        self.__signal = None
        self.__signalSet = False
        self.__trapExit = False
        self.__signalLock = allocateLock()
        self.__links = {}
        self.__linksLock = allocateLock()

    def _startThread(self, func, args, kwargs, initialLink):
        """Start process running on new thread"""
        if initialLink is not None:
            self._addLink(initialLink)
            initialLink._addLink(self)
        startThread(self.__run, (func, args, kwargs))

    def isAlive(self):
        """Return True if process is still running"""
        _checkSignal()
        return self.__alive

    isProcessAlive = isAlive

    def send(self, message):
        """Send message to process"""
        _checkSignal()
        if not self.isAlive():
            return message
        with self._mailboxCondition:
            self._mailbox.append(message)
            self._mailboxCondition.notify()
        return message

    __or__ = send

    def __repr__(self):
        return "<PID %d>" % id(self)

    def _signal(self, signal):
        """Send signal to process"""
        assert isinstance(signal, ExitError)
        assert signal.proc is not self
        if not self.isAlive():
            return
        with self.__signalLock:
            if self.__trapExit and signal.reason != "kill":
                self.send(("EXIT", signal.proc, signal.reason))
                return
            elif signal.reason == "normal":
                return
            elif self.__signal is None:
                self.__signal = signal
                self.__signalSet = True
        # Wake up process if it is waiting on a receive().
        with self._mailboxCondition:
            self._mailboxCondition.notify()

    def _addLink(self, proc):
        """link a proc with this process"""
        if not proc.__alive:
            self._signal(ExitError("noproc", proc))
            return
        if proc is self:
            return
        with self.__linksLock:
            self.__links[id(proc)] = proc

    def _removeLink(self, proc):
        """remove link to proc from this process"""
        procId = id(proc)
        with self.__linksLock:
            if procId in self.__links:
                del self.__links[procId]

    def _addReceiver(self, receiver):
        """register a new receiver with this process"""
        with self._mailboxCondition:
            # We don't want the __receiverRefs list to prevent garbage collection of
            # the receiver.
            self.__receiverRefs.append(weakref.ref(receiver, self._removeReceiverRef))

    def _removeReceiver(self, receiver):
        """unregister receiver from this process"""
        with self._mailboxCondition:
            for i in range(len(self.__receiverRefs)):
                if self.__receiverRefs[i]() is receiver:
                    del self.__receiverRefs[i]
                    break
                # end if

    def _removeReceiverRef(self, ref):
        """called when no more [strong] references to a registered receiver"""
        with self._mailboxCondition:
            self.__receiverRefs.remove(ref)

    def _getReceivers(self):
        """return list of registered receivers"""

        def deref(ref):
            """dereference a weakref"""
            receiver = ref()
            assert receiver is not None  # _removeReceiver() shouldn't leave any strays
            return receiver

        assert self._mailboxCondition.locked()
        result = [deref(ref) for ref in self.__receiverRefs]
        return result

    def _exit(self, exitError):
        """signal that process has terminated"""
        assert isinstance(exitError, ExitError)
        # Don't propagate a 'kill' signal; change the reason to 'killed' instead.
        if exitError.reason == "kill":
            exitError.reason = "killed"
        self.__alive = False
        with self.__linksLock:
            links = list(self.__links.values())
        for proc in links:
            proc._removeLink(self)
            proc._signal(exitError)
        # end for

    def _processFlag(self, flag, value):
        """set a process flag"""
        if flag == "trap_exit":
            if not isinstance(value, bool):
                raise ExitError("badarg")
            with self.__signalLock:
                result = self.__trapExit
                self.__trapExit = value
            return result
        else:
            raise ExitError("badarg")
        # end if

    def _checkSignal(self):
        """check if a signal has been received"""
        # Since self.__signalSet is just a boolean value, we don't need to worry
        # about acquiring a lock before inspecting its value. This way, we can check
        # if a signal has been set much more quickly.
        if not self.__signalSet:
            return
        with self.__signalLock:
            signal = self.__signal
            self.__signal = None
            self.__signalSet = False
        self._raise(signal)

    def _raise(self, signal):
        """raise an exception for signal"""
        assert isinstance(signal, ExitError)
        reason = signal.reason
        # Check if 'reason' is an ExceptionReason
        if isinstance(reason, ExceptionReason):
            raise reason.excInfo[0](reason.excInfo[1]).with_traceback(reason.excInfo[2])
        raise signal

    def __run(self, func, args, kwargs):
        """main function of thread"""
        currentThread = getCurrentThread()
        with ProcessMap() as pm:
            pm[currentThread] = self
        exitError = ExitError("normal", self)
        try:
            func(*args, **kwargs)
        except ExitError as ex:
            exitError = ex
        except:
            exitError = ExitError(ExceptionReason(), self)
        self._exit(exitError)
        with ProcessMap() as pm:
            del pm[currentThread]


class RootProcess(Process):

    """a process that represents the main thread"""

    def __init__(self):
        Process.__init__(self)
        self.__exceptionRaised = False
        self.__origExcepthook = sys.excepthook
        sys.excepthook = self.__excepthook
        atexit.register(self.__atexit)

    def _startThread(self, func, args, kwargs, initialLink):
        """Start process running on new thread"""
        raise NotImplementedError("RootProcess does not run on a thread")

    def __excepthook(self, type_, value, traceback):
        """invoked when unhandled exception is raised"""
        self.__exceptionRaised = True
        return self.__origExcepthook(type_, value, traceback)

    def __atexit(self):
        """invoked when interpreter is exiting"""
        # If the main thread exited because of an exception, don't raise another one
        if not self.__exceptionRaised:
            _checkSignal()
        self._exit(ExitError("normal", self))


class ExceptionReason:

    """An ExitError reason that specifies that a process raised an exception"""

    def __init__(self):
        self.excInfo = sys.exc_info()

    def __str__(self):
        return "<exception: %s>" % self.excInfo[1]


# These values are singletons that are accessed only via getProcessMap*()
_ProcessMap = None
_ProcessMapLock = None

@contextmanager
def ProcessMap():
    global _ProcessMap, _ProcessMapLock
    if _ProcessMapLock is None:
        _ProcessMapLock = allocateLock()
    with _ProcessMapLock:
        if _ProcessMap is None:
            _ProcessMap = { getCurrentThread(): RootProcess() }
        yield _ProcessMap

