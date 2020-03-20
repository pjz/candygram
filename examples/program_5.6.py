# I hereby disclaim all copyright to the contents of this file,
# program_5.6.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


resource_alloc = None


def start(resources):
    global resource_alloc
    pid = spawn(server, resources, [])
    resource_alloc = pid
    return pid


# The interface functions.
def allocate():
    return request("alloc")


def free(resource):
    return request(("free", resource))


def request(req):
    resource_alloc | (self(), req)
    r = Receiver()
    r[resource_alloc, Any] = lambda msg: msg[1], Message
    return r()


# The server.
def server(free, allocated):
    r = Receiver()
    r[Process, "alloc"] = allocate_, free, allocated, Message
    r[Process, ("free", Any)] = free_, free, allocated, Message
    return r()


def allocate_(free, allocated, msg):
    from_, _ = msg
    if free:
        r, free = free[0], free[1:]
        from_ | (resource_alloc, ("yes", r))
        allocated.insert(0, (r, from_))
        return server(free, allocated)
    from_ | (resource_alloc, "no")
    return server([], allocated)


def free_(free, allocated, msg):
    from_, (_, r) = msg
    if (r, from_) in allocated:
        from_ | (resource_alloc, "ok")
        free.insert(0, r)
        allocated.remove((r, from_))
        return server(free, allocated)
    else:
        from_ | (resource_alloc, "error")
        return server(free, allocated)
    # end if
