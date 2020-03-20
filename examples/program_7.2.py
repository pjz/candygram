# I hereby disclaim all copyright to the contents of this file,
# program_7.2.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


start_ = None


def start(n):
    global start_
    start_ = spawnLink(p1, n - 1)
    return start_


def p1(n):
    if n == 0:
        return top1()
    return top(spawnLink(p1, n - 1), n)


def top(next, n):
    r = Receiver()

    def fun(x):
        next | x
        print("Process %s received %s" % (n, x))
        return top(next, n)

    r[Any] = fun, Message
    return r()


def top1():
    r = Receiver()

    def stop():
        print("Last process now exiting ")
        exit("finished")

    r["stop"] = stop

    def fun(x):
        print("Last process received %s" % x)
        return top1()

    r[Any] = fun, Message
    return r()


def test(mess):
    return start_ | mess
