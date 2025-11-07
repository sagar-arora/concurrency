    import threading

    class ReadWriteLock:
        def __init__(self):
            self._read_lock = threading.Lock()
            self._write_lock = threading.Lock()
            self._readers = 0
            self._condition = threading.Condition(self._read_lock)

        def acquire_read(self):
            with self._condition:
                while self._write_lock.locked():
                    self._condition.wait()
                self._readers += 1

        def release_read(self):
            with self._condition:
                self._readers -= 1
                if self._readers == 0:
                    self._condition.notify_all()

        def acquire_write(self):
            self._write_lock.acquire()
            with self._condition:
                while self._readers > 0:
                    self._condition.wait()

        def release_write(self):
            self._write_lock.release()
            with self._condition:
                self._condition.notify_all()
