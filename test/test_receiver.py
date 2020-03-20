"""Tests that patterns in documentation work as advertised"""


import unittest

import candygram as cg


class TestReceiver(unittest.TestCase):
    def tearDown(self):
        # Remove any spurrious messages from mailbox
        r = cg.Receiver()
        timeout = object()
        r.addHandler(cg.Any)
        while r.receive(0, lambda: timeout) is not timeout:
            pass
        # end while

    def receive(self, receiver):
        receiver.receive()

    def testSingleProc(self):
        r = cg.Receiver()
        r.addHandler(1, cg.self().send, "one")
        proc = cg.spawn(self.receive, r)
        proc.send(1)
        r = cg.Receiver()
        r.addHandler("one", lambda: "success")
        self.assertEqual(r.receive(1000), "success")
        cg.exit(proc, "kill")

    def testMultiProc(self):
        r1 = cg.Receiver()
        r1.addHandler(1, cg.self().send, "one")
        proc1 = cg.spawn(self.receive, r1)
        proc2 = cg.spawn(self.receive, r1)
        proc1.send(1)
        proc2.send(1)
        r = cg.Receiver()
        r.addHandler("one", lambda: "success")
        self.assertEqual(r.receive(1000), "success")
        self.assertEqual(r.receive(1000), "success")
        proc3 = cg.spawn(self.receive, r1)
        proc3.send(1)
        self.assertEqual(r.receive(1000), "success")
        cg.exit(proc1, "kill")
        cg.exit(proc2, "kill")
        cg.exit(proc3, "kill")

    def testReset(self):
        # test that Receiver resets pointer back to front of mailbox after switching
        # to another process
        r1 = cg.Receiver()
        r1.addHandler(1, cg.self().send, "one")
        proc1 = cg.spawn(self.receive, r1)
        proc1.send(2)
        proc1.send(1)
        r = cg.Receiver()
        r.addHandler("one", lambda: "success")
        self.assertEqual(r.receive(1000), "success")
        proc2 = cg.spawn(self.receive, r1)
        proc2.send(1)
        self.assertEqual(r.receive(1000), "success")
        cg.exit(proc1, "kill")
        cg.exit(proc2, "kill")

    def testRemoveHandler(self):
        r = cg.Receiver()
        ref1 = r.addHandler(1)
        ref2 = r.addHandler(2)
        ref3 = r.addHandler(3)
        self.assert_(len(r._Receiver__handlers), 3)
        cg.self().send(2)
        self.assertEqual(r.receive(0, lambda: "to"), None)
        r.removeHandler(ref2)
        self.assert_(len(r._Receiver__handlers), 2)
        cg.self().send(2)
        self.assertEqual(r.receive(0, lambda: "to"), "to")
        self.assertRaises(cg.ExitError, r.removeHandler, ref2)

    def testRemoveHandlers(self):
        r1 = cg.Receiver()
        ref1 = r1.addHandler(1)
        ref2 = r1.addHandler(2)
        ref3 = r1.addHandler(3)
        r2 = cg.Receiver()
        r2.addHandler(4)
        r2.addHandler(5)
        r2.addHandler(6)
        refs = r2.addHandlers(r1)
        self.assert_(len(r2._Receiver__handlers), 6)
        cg.self().send(2)
        self.assertEqual(r2.receive(0, lambda: "to"), None)
        r2.removeHandler(refs[1])
        self.assert_(len(r2._Receiver__handlers), 5)
        cg.self().send(2)
        self.assertEqual(r2.receive(0, lambda: "to"), "to")
        self.assertRaises(cg.ExitError, r2.removeHandler, refs[1])
