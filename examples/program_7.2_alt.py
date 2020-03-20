# I hereby disclaim all copyright to the contents of this file,
# program_7.2_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


start_ = None


def start(n):
    global start_
    start_ = p1(n)
    return start_


def p1(n):
    next = None
    for i in range(n):
        if i == 0:
            top = Top1()
        else:
            top = Top(next, i)
        next = spawn(top.top)
    link(next)
    return next


class Top:
    def __init__(self, next, n):
        self.next = next
        self.n = n

    def fun(self, x):
        self.next.send(x)
        print("Process %s received %s" % (self.n, x))

    def top(self):
        link(self.next)
        r = Receiver()
        r.addHandler(Any, self.fun, Message)
        for _ in r:
            pass
        return True


class Top1:
    def stop(self):
        print("Last process now exiting ")
        exit("finished")

    def fun(self, x):
        print("Last process received %s" % x)

    def top(self):
        r = Receiver()
        r.addHandler("stop", self.stop)
        r.addHandler(Any, self.fun, Message)
        for _ in r:
            pass
        return True


def test(mess):
    return start_.send(mess)
