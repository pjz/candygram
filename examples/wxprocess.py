# I hereby disclaim all copyright to the contents of this file,
# wxprocess.py, and place it into the public domain.
#   -- Michael Hobbs

"""A Candygram Process subclass that integrates with wxPython.

It is a little difficult to integrate Candygram with wxPython. The problem
arises when Candygram handler functions need to invoke wxPython methods. Since
it is not safe to invoke wxPython methods from outside the main GUI thread, the
handler functions ought to run from within the GUI thread. Since a wx.App will
run its own event loop, however, there is no good place to run a Candygram
Receiver.receive() loop in the same thread.

One common solution to this type of problem is to periodically poll for either
new Candygram messages or new GUI events. The problem with this approach,
however, is determining what the correct polling interval should be. If set too
long, important messages may not be processed as quickly as they should. If set
too short, we have an unneccessary amount of overhead from polling too
frequently. Usually, there isn't a single good interval, since messages often
come in bursts.

We avoid this problem by overriding the Process.send() method so that it sends
a custom notification event to the wx.App whenever a new message is placed in
the process's mailbox. With this approach, the wx.App knows that it needs to
check for new Candygram messages only when it receives a notification event.

[NB: This same technique can also be used with a process that checks for network
activity by looping on select.select(), a la Twisted. In that scenario, we can
notify the process of a new message by sending an empty UDP packet across a
loopback socket.]

To use this module, invoke spawn() or spawnLink() with the `_processClass=
wxProcess' keyword argument. The spawned function should create an instance of
your own wx.App subclass. The wxProcess class has a `receiver' attribute, which
you can use to define your Candygram handler functions by calling
  candygram.self().receiver.addHandler(...)
within the spawned process. Your subclass's OnInit() method is one good place
to add your handlers.

There is some sample code at the bottom of this file that demonstrates one way
to spawn a wxProcess, using wx.PySimpleApp.

"""


import wx

import candygram as cg


class wxProcess(cg.Process):

    """A wxPython compatible Process class"""

    def __init__(self):
        # Don't bind a custom notification event to wx.App at this point, since
        # a wx.App shouldn't be instantiated yet. We bind to the wx.App, instead,
        # when the first time send() is called.
        cg.Process.__init__(self)
        self.__app = None
        self.__notifyEventType = None
        self.receiver = cg.Receiver()

    def send(self, message):
        """Send message to the process and then send notification event"""
        self.__checkAppBound()
        cg.Process.send(self, message)
        notifyEvent = wx.PyEvent()
        notifyEvent.SetEventType(self.__notifyEventType)
        wx.PostEvent(self.__app, notifyEvent)

    def __checkAppBound(self):
        """Bind custom notification event to wx.App"""
        if self.__app is not None:
            return
        # Save a copy of wx.GetApp() locally so that we don't have to refetch it
        # every time send() is called.
        self.__app = wx.GetApp()
        self.__notifyEventType = wx.NewEventType()
        notifyEventBinder = wx.PyEventBinder(self.__notifyEventType, 0)
        self.__app.Bind(notifyEventBinder, self.__receive)

    def __receive(self, event):
        """Called in response to a notification event"""
        # Since this method is only be invoked when a new message is present, we can
        # set a timeout of 0.
        self.receiver.receive(0)


def sampleSpawn():
    """Start GUI event loop in separate process"""
    # Unique value used to acknowledge that the wx.App has been created:
    ack = object()
    # Unique value used to signal a receive() timeout:
    timeout = object()
    # Spawn a new wxProcess, calling mainLoop():
    proc = cg.spawn(mainLoop, cg.self(), ack, _processClass=wxProcess)
    # We wait for acknowledgement from the spawned process before proceeding,
    # since we should make sure that the wx.App has been instantiated before
    # allowing anyone to send messages to the process.
    r = cg.Receiver()
    r.addHandler(ack)
    # Wait at most 30 seconds.
    result = r.receive(30000, lambda: timeout)
    assert result is not timeout
    return proc


def mainLoop(proc, ack):
    """Create a wx.PySimpleApp and run its MainLoop()"""
    app = wx.PySimpleApp()
    proc.send(ack)
    # We can define our Candygram handler functions here:
    r = cg.self().receiver
    # r.addHandler(...)
    # r.addHandler(...)
    # ... and so on ...
    app.MainLoop()
