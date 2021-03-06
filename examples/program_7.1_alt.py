# I hereby disclaim all copyright to the contents of this file,
# program_7.1_alt.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


my_name = None


def start():
    global my_name
    process = Process()
    my_name = spawn(process.process)
    return my_name


class Process:
    def __init__(self):
        self.stop = False

    def stop_(self, msg):
        _, method = msg
        if method == "return":
            self.stop = True
        else:
            exit("normal")
        # end if

    def process(self):
        r = Receiver()
        r.addHandler(("stop", Any), self.stop_, Message)
        r.addHandler(Any)
        for _ in r:
            if self.stop:
                break
            # end if
        return True
