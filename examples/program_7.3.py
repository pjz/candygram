# I hereby disclaim all copyright to the contents of this file,
# program_7.3.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


demo_ = None


def start():
    global demo_
    demo_ = spawn(demo)
    return demo_


def demo():
    processFlag("trap_exit", True)
    return demo1()


def demo1():
    r = Receiver()

    def normalExit(msg):
        _, from_, _ = msg
        print "Demo process received normal exit from %s" % from_
        return demo1()

    r["EXIT", Process, "normal"] = normalExit, Message

    def otherExit(msg):
        _, from_, reason = msg
        print "Demo process received exit signal %s from %s" % (reason, from_)
        return demo1()

    r["EXIT", Process, Any] = otherExit, Message

    def finished():
        print "Demo finished "

    r["finished_demo"] = finished

    def other(msg):
        print "Demo process message %s" % msg
        return demo1()

    r[Any] = other, Message
    return r()


def demonstrate_normal():
    def func():
        link(demo_)

    return spawn(func)


def demonstrate_exit(what):
    def func():
        link(demo_)
        exit(what)

    return spawn(func)


def demonstrate_message(what):
    def func():
        demo_ | what

    return spawn(func)


def demonstrate_error():
    def func():
        link(demo_)
        1 / 0

    return spawn(func)
