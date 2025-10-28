import threading

class BoundedSemaphore:

    def __init__(self, value: int = 1):
        """
        Initializes the semaphore.
        'value' is the initial count, representing how many
        threads can acquire it before blocking.
        """
        # Your implementation here
        # Hint: You need self.lock, self.condition, and self.value
        self.value = value
        self.lock = threading.Lock()
        self.counter = 0
        self.not_available = self.lock.Condition()
        

    def acquire(self):
        """
        Acquires the semaphore.
        
        If the internal counter is greater than 0, decrement it
        and return immediately.
        
        If the counter is 0, block and wait until 'release()'
        is called by another thread.
        """
        with self.lock:
          while self.counter == self.value:
            self.not_available.wait()
            continue
          self.counter += 1

    def release(self):
        """
        Releases the semaphore.
        
        Increments the internal counter and notifies one
        waiting thread (if any).
        """
        with self.lock:
          self.counter -= 1
          self.not_available.notify()
