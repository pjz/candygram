# I hereby disclaim all copyright to the contents of this file,
# wxcandygram.py, and place it into the public domain.
#   -- Michael Hobbs

"""A wx.App subclass that can process Candygram messages.

It is a little difficult to integrate Candygram with wxPython. The problem
arises when Candygram handler functions need to invoke wxPython methods. Since
it is not safe to invoke wxPython methods from outside the main GUI thread, the
handler functions ought to run from within the GUI thread. Since a wx.App will
run its own event loop, waiting for GUI events, there is no good place to run
a Candygram Receiver.receive() loop.

One common solution to this type of problem is to periodically poll for either
new Candygram messages or new GUI events. The problem with this approach,
however, is determining what the correct polling interval should be. If set too
long, important messages may not be processed as quickly as they should. If set
too short, we have an unneccessary amount of overhead from polling too
frequently. Usually, there isn't a single good interval, since messages often
come in bursts.

We avoid these problems by overriding the Process.send() method so that it sends
a custom notification event to the wx.App whenever a new message is placed in
the process's mailbox. With this approach, the wx.App knows that it needs to
check for new Candygram messages only when it receives a notification event.

This technique can also be used with a process that checks for network activity
by looping on select.select(). In that scenario, we can notify the process of
a new message by sending a byte across a loopback socket.

To use this module, first define your own wx.App class, deriving from
wxCandygramApp. The app's OnInit() function should invoke wxCandygramApp.OnInit
and add handlers to the `receiver' attribute, as well as create a top window.
To start the GUI thread, call either the spawn() or spawnLink() functions
defined in this module. These functions take the wxCandygramApp subclass as a
parameter, as well as any constructor arguments. The spawned process will invoke
the class's constructor and run its MainLoop(). The spawn() and spawnLink()
functions return the wxCandygramApp instance that is created in the spawned
process. You may call the app's send() method to send messages to the process.

"""


import wx

import candygram as cg


# Define a unique value to be returned if a receive() times out.
TIMEOUT_RESULT = object()

def returnTimeout():
	return TIMEOUT_RESULT


class wxCandygramApp(wx.App):

	"""A Candygram compatible wx.App class."""

	def OnInit(self):
		self.process = cg.self()
		self.receiver = cg.Receiver()
		# Define a custom notification event and bind it to self.receive().
		self.notifyEventType = wx.NewEventType()
		notifyEventBinder = wx.PyEventBinder(self.notifyEventType, 0)
		self.Bind(notifyEventBinder, self.receive)

	def send(self, message):
		"""Send message to the process and then send notification event"""
		self.process.send(message)
		notifyEvent = wx.PyEvent()
		notifyEvent.SetEventType(self.notifyEventType)
		wx.PostEvent(self, notifyEvent)

	__or__ = send  # Alias for send()

	def receive(self, event):
		"""Called in response to a notification event"""
		# Since this method should only be invoked when a new message is present,
		# we set a timeout of 0 and assert that we don't timeout.
		assert self.receiver.receive(0, returnTimeout) is not TIMEOUT_RESULT


def spawn(appClass, *appArgs, **appKWArgs):
	"""Create the GUI thread by invoking the given wx.App class's constructor in
	a new Candygram process."""
	return doSpawn(cg.spawn, appClass, appArgs, appKWArgs)


def spawnLink(appClass, *appArgs, **appKWArgs):
	"""Create the GUI thread by invoking the given wx.App class's constructor in
	a new Candygram process."""
	return doSpawn(cg.spawnLink, appClass, appArgs, appKWArgs)


def doSpawn(spawnFunc, appClass, appArgs, appKWArgs):
	"""Perform spawn() or spawnLink() function"""
	assert issubclass(appClass, wxCandygramApp), \
			'The given class is not a subclass of wxCandygramApp'
	# Unique value used to acknowledge that app has been created.
	ack = object()
	proc = spawnFunc(procFunc, cg.self(), ack, appClass, appArgs, appKWArgs)
	# Wait 30 seconds for acknowledgement from spawned app.
	r = cg.Receiver()
	r.addHandler((ack, wxCandygramApp), lambda msg: msg[1], cg.Message)
	r.after(30000, returnTimeout)
	app = r.receive()
	assert app is not TIMEOUT_RESULT
	return app


def procFunc(proc, ack, appClass, appArgs, appKWArgs):
	"""Constructs a wx.App and runs its MainLoop()"""
	app = appClass(*appArgs, **appKWArgs)
	proc.send((ack, app))
	app.MainLoop()
