import bisect


class MapOperation(object):
    def __init__(self, retval):
        self.retval = retval

    def do(self, m):
        raise NotImplementedError

    def undo(self, m):
        raise NotImplementedError

    def is_const(self):
        raise NotImplementedError


class Get(MapOperation):
    def __init__(self, key, retval):
        self.key = key
        super(Get, self).__init__(retval)

    def do(self, m):
        return m.get(self.key, None)

    def undo(self, m):
        pass

    def __str__(self):
        return "G({})->{}".format(self.key, self.retval)

    def is_const(self):
        return True


class Put(MapOperation):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self._prev = None
        assert value is not None
        super(Put, self).__init__(None)

    def do(self, m):
        self._prev = m.get(self.key, None)
        m[self.key] = self.value

    def undo(self, m):
        if self._prev is None:
            del m[self.key]
        else:
            m[self.key] = self._prev

    def __str__(self):
        return "P({}, {})".format(self.key, self.value)

    def is_const(self):
        return False


class Scan(MapOperation):
    def __init__(self, key_start, key_end, retval):
        self.key_start = key_start
        self.key_end = key_end
        super(Scan, self).__init__(retval)

    def do(self, m):
        return [(key, value) for key, value in m.items() if self.key_start <= key <= self.key_end]

    def undo(self, m):
        pass

    def __str__(self):
        return "Scan({}, {})->{}".format(self.key_start, self.key_end, len(self.retval))

    def is_const(self):
        return True


class Size(MapOperation):
    def __init__(self, retval):
        super(Size, self).__init__(retval)

    def do(self, m):
        return len(m)

    def undo(self, m):
        pass

    def __str__(self):
        return "Size()->".format(self.retval)

    def is_const(self):
        return True


class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        assert start < end


