"""Tests that all programs in the examples directory work as they should"""


import unittest
import os
import time
import sys
import io

import candygram as cg
import pytest


# note this *must* not be 0.1s b/c that's used by candygram itself, and will cause sync issues
PAUSE = 0.15  # seconds

def wait_for(pred):
    while not pred():
        time.sleep(PAUSE)
    time.sleep(PAUSE)


class TestExamplePrograms(unittest.TestCase):
    def setUp(self):
        # Add the examples directory to sys.path so that we can import them.
        pwd = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(pwd)
        self.exDir = os.path.join(parent, "examples")
        # Redirect stdout to a StringIO buffer.
        self.oldOut = sys.stdout
        sys.stdout = io.StringIO()

    def tearDown(self):
        # Restore stdout
        sys.stdout.close()
        sys.stdout = self.oldOut

    def resetStdout(self):
        sys.stdout.close()
        sys.stdout = io.StringIO()

    def execFile(self, name):
        vdict = {}
        fullname = os.path.join(self.exDir, name)
        exec(compile(open(fullname, "rb").read(), fullname, 'exec'), vdict)
        return vdict

    def testProgram_5_1(self):
        def test(dict):
            proc = dict["start"]()
            proc.send("increment")
            proc.send("increment")
            while proc._mailbox:
                print("pending messages")
                time.sleep(PAUSE)
            assert proc.isAlive()
            cg.exit(proc, "kill")

        test(self.execFile("program_5.1.py"))
        time.sleep(PAUSE)
        test(self.execFile("program_5.1_alt.py"))

    def testProgram_5_2(self):
        def test(dict):
            proc = dict["start"]()
            dict["increment"](proc)
            dict["increment"](proc)
            assert dict["value"](proc) == 2
            dict["stop"](proc)
            time.sleep(PAUSE)
            assert not proc.isAlive()

        test(self.execFile("program_5.2.py"))
        test(self.execFile("program_5.2_alt.py"))

    def testProgram_5_3(self):
        def test(dict):
            proc = cg.spawn(dict["s1"])
            proc.send("msg_a")
            proc.send("msg_x")
            proc.send("msg_b")
            proc.send("msg_c")
            proc.send("msg_y")
            proc.send("msg_h")
            proc.send("msg_i")
            time.sleep(PAUSE)
            assert proc.isAlive()
            assert len(proc._mailbox) == 0
            proc.send("msg_a")
            proc.send("msg_x")
            time.sleep(PAUSE)
            assert len(proc._mailbox) == 2
            cg.exit(proc, "kill")

        test(self.execFile("program_5.3.py"))
        test(self.execFile("program_5.3_alt.py"))

    def testProgram_5_4(self):
        def test(dict):
            r = cg.Receiver()
            r.addHandler("alarm", lambda: "beep")
            start = time.time()
            proc = dict["timeout"](1000, "alarm")
            assert r.receive() == "beep"
            time.sleep(PAUSE)
            assert not proc.isAlive()
            start = time.time()
            proc = dict["timeout"](1000, "alarm")
            time.sleep(0.5)
            dict["cancel"](proc)
            time.sleep(0.1)
            assert not proc.isAlive()
            assert time.time() - start < 1.0

        test(self.execFile("program_5.4.py"))
        test(self.execFile("program_5.4_alt.py"))

    def testProgram_5_5(self):
        def test(dict):
            proc = dict["start"]()
            resp = dict["add_number"]("555-1111", "Company A")
            assert resp == "ack"
            resp = dict["add_number"]("666-2222", "Company B")
            assert resp == "ack"
            resp = dict["analyse"]("555-1111")
            assert resp == "Company A"
            resp = dict["analyse"]("666-2222")
            assert resp == "Company B"
            resp = dict["analyse"]("777-3333")
            assert resp == None
            cg.exit(proc, "kill")

        test(self.execFile("program_5.5.py"))
        test(self.execFile("program_5.5_alt.py"))

    def testProgram_5_6(self):
        def test(dict):
            proc = dict["start"](["a", "b", "c"])
            resp = dict["free"]("a")
            assert resp == "error"
            resp = dict["allocate"]()
            assert resp == ("yes", "a")
            resp = dict["allocate"]()
            assert resp == ("yes", "b")
            resp = dict["allocate"]()
            assert resp == ("yes", "c")
            resp = dict["allocate"]()
            assert resp == "no"
            resp = dict["free"]("b")
            assert resp == "ok"
            resp = dict["allocate"]()
            assert resp == ("yes", "b")
            cg.exit(proc, "kill")

        test(self.execFile("program_5.6.py"))
        test(self.execFile("program_5.6_alt.py"))

    def testProgram_7_1(self):
        def test(dict):
            proc = dict["start"]()
            proc.send("message")
            time.sleep(PAUSE)
            assert proc.isAlive()
            proc.send(("stop", "return"))
            time.sleep(PAUSE)
            assert not proc.isAlive()
            proc = dict["start"]()
            proc.send(("stop", "hello"))
            time.sleep(PAUSE)
            assert not proc.isAlive()

        test(self.execFile("program_7.1.py"))
        test(self.execFile("program_7.1_alt.py"))

    def testProgram_7_2(self):
        def test(dict):
            proc = dict["start"](3)
            dict["test"](123)
            time.sleep(PAUSE)
            assert sys.stdout.getvalue() == \
                "Process 2 received 123\n" \
                "Process 1 received 123\n" \
                "Last process received 123\n"
            self.resetStdout()
            dict["test"]("stop")
            time.sleep(PAUSE)
            assert sys.stdout.getvalue() == \
                "Process 2 received stop\n" \
                "Process 1 received stop\n" \
                "Last process now exiting \n"
            self.resetStdout()
            with pytest.raises(cg.ExitError):
                proc.isAlive()

        test(self.execFile("program_7.2.py"))
        test(self.execFile("program_7.2_alt.py"))

    def testProgram_7_3(self):
        def test(dict):
            proc = dict["start"]()
            normal = dict["demonstrate_normal"]()
            wait_for(lambda: not normal.isAlive())
            assert not normal.isAlive()
            wait_for(sys.stdout.getvalue)
            assert sys.stdout.getvalue() == \
                "Demo process received normal exit from %s\n" % normal
            self.resetStdout()
            hello = dict["demonstrate_exit"]("hello")
            wait_for(lambda: not hello.isAlive())
            assert not hello.isAlive()
            assert sys.stdout.getvalue() == \
                "Demo process received exit signal hello from %s\n" % hello
            self.resetStdout()
            normal = dict["demonstrate_exit"]("normal")
            wait_for(lambda: not normal.isAlive())
            assert not normal.isAlive()
            assert sys.stdout.getvalue() == \
                "Demo process received normal exit from %s\n" % normal
            self.resetStdout()
            error = dict["demonstrate_error"]()
            wait_for(lambda: not error.isAlive())
            assert not error.isAlive()
            assert sys.stdout.getvalue() == \
                "Demo process received exit signal " \
                "<exception: division by zero> from %s\n" % error
            self.resetStdout()
            message = dict["demonstrate_message"]("hello")
            wait_for(lambda: not message.isAlive())
            assert not message.isAlive()
            assert sys.stdout.getvalue() == "Demo process message hello\n"
            self.resetStdout()
            finished = dict["demonstrate_message"]("finished_demo")
            wait_for(lambda: not finished.isAlive())
            assert not finished.isAlive()
            assert sys.stdout.getvalue() == "Demo finished \n"
            assert not proc.isAlive()
            self.resetStdout()

        test(self.execFile("program_7.3.py"))
        test(self.execFile("program_7.3_alt.py"))
