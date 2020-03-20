"""Tests that patterns in documentation work as advertised"""


import unittest

import candygram as cg


class TestFunctions(unittest.TestCase):
    def testSpawnMyProcess(self):
        proc = cg.spawn(echo, cg.self(), _processClass=MyProcess)
        assert isinstance(proc, MyProcess)
        proc.send("test")
        r = cg.Receiver()
        r.addHandler(cg.Any, lambda m: m, cg.Message)
        assert r.receive() == ("MyProcess", "test")
        cg.exit(proc, "kill")

    def testSpawnLinkMyProcess(self):
        proc = cg.spawnLink(echo, cg.self(), _processClass=MyProcess)
        assert isinstance(proc, MyProcess)
        proc.send("test")
        r = cg.Receiver()
        r.addHandler(cg.Any, lambda m: m, cg.Message)
        assert r.receive() == ("MyProcess", "test")
        cg.exit(proc, "kill")


class MyProcess(cg.Process):
    def send(self, message):
        return cg.Process.send(self, ("MyProcess", message))


def echo(proc):
    r = cg.Receiver()
    r.addHandler(cg.Any, proc.send, cg.Message)
    r.receive()
