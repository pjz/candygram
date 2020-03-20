"""Tests that all examples in documentation work as advertised"""


import unittest
import StringIO

from candygram import *


class TestDocExample(unittest.TestCase):
    def setUp(self):
        self.out = StringIO.StringIO()

    def tearDown(self):
        self.out.close()

    def test1(self):
        import time

        def proc_func():
            r = Receiver()
            r["land shark"] = lambda m: "Go Away " + m, Message
            r["candygram"] = lambda m: "Hello " + m, Message
            for message in r:
                print >>self.out, message

        proc = spawn(proc_func)
        proc | "land shark"
        proc | "candygram"
        # Give the proc a chance to print its messages before termination:
        time.sleep(1)
        exit(proc, "kill")
        # Assert print statements worked as advertised
        self.assertEqual(
            self.out.getvalue(), "Go Away land shark\n" "Hello candygram\n"
        )

    def test2(self):
        import candygram as cg
        import time

        def proc_func():
            r = cg.Receiver()
            r.addHandler("land shark", shut_door, cg.Message)
            r.addHandler("candygram", open_door, cg.Message)
            for message in r:
                print >>self.out, message

        def shut_door(name):
            return "Go Away " + name

        def open_door(name):
            return "Hello " + name

        proc = cg.spawn(proc_func)
        proc.send("land shark")
        proc.send("candygram")
        # Give the proc a chance to print its messages before termination:
        time.sleep(1)
        cg.exit(proc, "kill")
        # Assert print statements worked as advertised
        self.assertEqual(
            self.out.getvalue(), "Go Away land shark\n" "Hello candygram\n"
        )

    def test3(self):
        import time

        def proc_func(name):
            r = Receiver()
            r["msg", Process, str] = print_string, name, Message
            r["msg", Process, str, Any] = print_any, name, Message
            r[Any]  # Ignore any other messages
            for result in r:
                pass

        def print_string(name, message):
            msg, process, string = message
            # 'msg' and 'process' are unused
            print >>self.out, "%s received: %s" % (name, string)

        def print_any(name, message):
            msg, process, prefix, value = message
            # 'msg' and 'process' are unused
            print >>self.out, "%s received: %s %s" % (name, prefix, value)

        a = spawn(proc_func, "A")
        b = spawn(proc_func, "B")
        a | ("msg", b, "Girl Scout cookies")
        a | "plumber?"
        a | ("msg", b, "The meaning of life is:", 42)
        # Give the proc a chance to print its messages before termination:
        time.sleep(1)
        exit(a, "kill")
        exit(b, "kill")
        # Assert print statements worked as advertised
        self.assertEqual(
            self.out.getvalue(),
            "A received: Girl Scout cookies\n"
            "A received: The meaning of life is: 42\n",
        )
