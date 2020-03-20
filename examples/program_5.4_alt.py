# I hereby disclaim all copyright to the contents of this file,
# program_5.4_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


def timeout(time, alarm):
    timer = Timer(self(), time, alarm)
    return spawn(timer.timer)


def cancel(timer):
    return timer.send((self(), "cancel"))


class Timer:
    def __init__(self, pid, time, alarm):
        self.pid = pid
        self.time = time
        self.alarm = alarm

    def timeout(self):
        self.pid.send(self.alarm)

    def timer(self):
        r = Receiver()
        r.addHandler((Process, "cancel"))
        r.after(self.time, self.timeout)
        r.receive()
