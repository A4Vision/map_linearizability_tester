import operations


class TimedOperation(object):
    def __init__(self, operation, interval):
        assert isinstance(interval, operations.Interval)
        assert isinstance(operation, operations.MapOperation)
        self.interval = interval
        self.operation = operation


class History(object):
    def __init__(self, core_to_timed_operations):
        assert sorted(core_to_timed_operations.keys()) == list(range(len(core_to_timed_operations)))
        self._sorted_thread_histories = {}
        for core, timed_operations in core_to_timed_operations.items():
            current = self._sorted_thread_histories[core] = sorted(timed_operations, key=lambda to: to.interval.start)
            for op1, op2 in zip(current, current[1:]):
                assert op1.interval.end < op2.interval.start

    def _all_times_sorted(self):
        all_times = set()
        for timed_ops_list in self._sorted_thread_histories.values():
            for timed_op in timed_ops_list:
                all_times.add(timed_op.interval.start)
                all_times.add(timed_op.interval.end)
        return sorted(all_times)

    def __str__(self):
        times = self._all_times_sorted()
        time2index = {t: i for i, t in enumerate(times)}
        LEN = 10
        res = ""
        for i in sorted(self._sorted_thread_histories.keys()):
            prefix = "Core{:3d}: ".format(i)
            ops_strings = [' ' * LEN] * (len(times) * 2)
            for timed_op in self._sorted_thread_histories[i]:
                i1 = time2index[timed_op.interval.start]
                i2 = time2index[timed_op.interval.end]
                middle = (str(timed_op.operation) + ' ' * LEN)[:LEN]
                ops_strings[i1 * 2] = ' ' * (LEN // 2) + '[' + ' ' * ((LEN - 1) // 2)
                ops_strings[i1 * 2 + 1] = middle
                ops_strings[i2 * 2] = ' ' * (LEN // 2) + ']' + ' ' * ((LEN - 1) // 2)
            res += prefix + ''.join(ops_strings) + '\n'
        return res

    def n_cores(self):
        return len(self._sorted_thread_histories)

    def is_linearizable(self):
        map_state = dict()
        indices = [0] * self.n_cores()
        return self._is_linearizable(map_state, indices)

    def _is_linearizable(self, map_state, indices):
        # Wing Gong naive test
        first_operations = []
        for i in range(self.n_cores()):
            ops_list = self._sorted_thread_histories[i]
            index = indices[i]
            if index < len(ops_list):
                first_operations.append(ops_list[index])
            else:
                first_operations.append(None)
        if first_operations == [None] * self.n_cores():
            # History left to linearize is empty.
            return True
        smallest_end_among_first = min(timed_op.interval.end for timed_op in first_operations if timed_op is not None)
        for i, timed_op in enumerate(first_operations):
            if timed_op is None:
                continue
            # Check whether the operation is minimal
            if timed_op.interval.start < smallest_end_among_first:
                indices[i] += 1
                op = timed_op.operation
                actual_retval = op.do(map_state)
                if actual_retval == op.retval and self._is_linearizable(map_state, indices):
                    return True
                op.undo(map_state)
                indices[i] -= 1
        return False


def main():
    h0 = [TimedOperation(operations.Get(12, 3), operations.Interval(1, 4)),
          TimedOperation(operations.Get(12, 4), operations.Interval(5, 7)),
          TimedOperation(operations.Scan(11.2, 20, [(12, 4), (13, 4)]), operations.Interval(8.1, 8.7)),
          TimedOperation(operations.Get(12, 3), operations.Interval(8.8, 10))]

    h1 = [TimedOperation(operations.Put(12, 3), operations.Interval(1, 5.1)),
          TimedOperation(operations.Put(12, 4), operations.Interval(6, 7.2)),
          TimedOperation(operations.Put(10, 4), operations.Interval(7.3, 7.4)),
          TimedOperation(operations.Put(11, 4), operations.Interval(7.5, 7.6)),
          TimedOperation(operations.Put(13, 4), operations.Interval(8, 8.2)),
          TimedOperation(operations.Put(12, 3), operations.Interval(9.5, 12))]
    h = History({0: h0, 1: h1})
    print(h)
    print(h.is_linearizable())


if __name__ == '__main__':
    main()
