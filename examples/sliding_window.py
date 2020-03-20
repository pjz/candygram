# I hereby disclaim all copyright to the contents of this file,
# sliding_window.py, and place it into the public domain.
#   -- Michael Hobbs

"""A process that limits the number of unacknowledged messages that are queued
in another process's mailbox.

Some processes receive messages in bursts and thus may want to buffer up some
messages while it performs its tasks. By default, a process will buffer an
unlimited number of messages in its mailbox, so this is not a problem in
general. However, if a process can quickly become inundated with a massive
number of messages, it will want to keep the number of outstanding messages to
a fixed amount. In order to accomplish this, any sender process would have to
wait for an acknowledgement before sending its next message. The problem comes
in when the receiver becomes busy performing long tasks and cannot send an
acknowledgement right away. As a result, the sender may not be able to fill up
the receiver's mailbox with pending messages as quickly as it otherwise could.

To resolve this problem, this process runs independently of the receiver and
maintains a "sliding window" of messages that are forwarded to the receiver.
That is, this process will make sure that there are never more than N
unacknowledged messages in the receiver's mailbox, where N is the size of the
sliding window and is specified by the receiver.

This process is actually capable of forwarding messages to any number of
receivers.

To send a message to the receiver, send a tuple of the form (self, rcvr, msg) to
the SlidingWindow process, where 'self' is the sending process, 'rcvr' is the 
receiver process, and 'msg' is the message to send. When the message has been
delivered to the receiver process, the SlidingWindow will send a tuple of the
form ('ack', rcvr) to the sending process, where 'rcvr' is the receiver process.

To act as a proper receiver process, a process needs to send a tuple of the form
('ack', self) to the SlidingWindow process whenever it receives a message, where
'self' is the receiver process. This allows the SlidingWindow process to keep
track of how many messages are in its mailbox.

A receiver process can specify the size of its window by sending a tuple of the
form ('set_size', self, size) to the SlidingWindow process, where 'self' is the
receiver process and 'size' is the desired size of the sliding window.

"""


from candygram import *


class SlidingWindow:

    """The sliding window class.

	Standard usage is swProc = SlidingWindow().spawn()
	The process never terminates naturally. In order to stop it, call
	exit(swProc, 'kill')
	"""

    def __init__(self):
        # Contains (currentSize, maxSize) tuples for windows of each known receiver
        # process.
        self.__sizes = {}
        # Contains [sender] list for sender processes waiting for an acknowledgement
        # from a receiver process.
        self.__waiters = {}
        # Set to True after the process has been spawned.
        self.__running = False

    def spawn(self):
        assert not self.__running, "This SlidingWindow has already been spawned"
        self.__running = True
        return spawn(self.__run)

    def spawnLink(self):
        assert not self.__running, "This SlidingWindow has already been spawned"
        self.__running = True
        return spawnLink(self.__run)

    def __run(self):
        processFlag("trap_exit", True)
        r = Receiver()
        r["set_size", Process, int] = self.__setMaxSize, Message
        r["get_size", Process, Process] = self.__getSize, Message
        r["EXIT", Process, Any] = self.__exit, Message
        r["ack", Process] = self.__ack, Message
        r[Process, Process, Any] = self.__send, Message
        r[Any]  # ignore spurrious messages
        for _ in r:
            pass
        # end for

    def __setMaxSize(self, message):
        _, receiver, maxSize = message
        # Reset the maxSize value in receiver's size tuple.
        recvId = id(receiver)
        size = self.__sizes.get(recvId, (0, 0))[0]
        self.__sizes[recvId] = (size, maxSize)
        # We want to know when the receiver exits, so that we can clear its entry
        # from self.__sizes when it goes away.
        link(receiver)

    def __getSize(self, message):
        _, receiver, proc = message
        # Retrieve the maxSize value from receiver's size tuple.
        recvId = id(receiver)
        size = self.__sizes.get(recvId, (0, 0))[0]
        proc | (self_(), "size", size)

    def __exit(self, message):
        _, receiver, _ = message
        # A process has terminated, delete all references to it from our dicts.
        recvId = id(receiver)
        assert recvId in self.__sizes
        del self.__sizes[recvId]
        if recvId in self.__waiters:
            del self.__waiters[recvId]
        # end if

    def __ack(self, message):
        receiver = message[1]
        # Lookup current window size of receiver.
        recvId = id(receiver)
        assert recvId in self.__sizes
        size, maxSize = self.__sizes[recvId]
        # If there are any senders are waiting for acknowledgement from this
        # receiver, then the receiver's window should be full. (Otherwise the
        # acknowledgement would have already been sent to the sender.)
        if recvId in self.__waiters:
            # Sanity check to make sure that the window is full:
            assert size == maxSize
            waiters = self.__waiters[recvId]
            sender, message = waiters.pop(0)
            if not waiters:
                # clean up empty dictionary entries
                del self.__waiters[recvId]
            receiver | message
            sender | ("ack", receiver)
        else:
            # Sanity check to make sure that the process isn't acknowledging when its
            # window is empty:
            assert size > 0
            self.__sizes[recvId] = (size - 1, maxSize)
        # end if

    def __send(self, message):
        sender, dest, message = message
        destId = id(dest)
        # Define a new window with a default maxSize of 1 if we haven't already
        # encoutered this receiver process.
        if destId not in self.__sizes:
            self.__setMaxSize((None, dest, 1))
        size, maxSize = self.__sizes[destId]
        # If the receiver's window is full, add current sender to the queue of
        # senders that are waiting for an acknowledgement from the receiver. If the
        # receiver's window is not full, send an acknowledgement back to the sender
        # right away.
        if size == maxSize:
            self.__waiters.setdefault(destId, []).append((sender, message))
        else:
            # Sanity check to make sure size hasn't somehow exceeded maxSize:
            assert size < maxSize
            dest | message
            sender | ("ack", dest)
            self.__sizes[destId] = (size + 1, maxSize)
        # end if
