import time
import threading
from threading import RLock  # Import RLock
from queue import PriorityQueue
from dataclasses import dataclass, field

@dataclass(order=True)
class Node:
    """Data structure to hold the task to be executed."""
    ts: float = field(compare=True)
    fn: callable = field(compare=False)


class DeferFn:
    """
    A multi-threaded, reactive utility to defer function execution
    using an EXPLICIT lock and condition variable.
    """
    def __init__(self):
        self.pq = PriorityQueue()
        
        # 1. Create the explicit lock first.
        #    We use an RLock (Reentrant Lock) which is what Condition
        #    creates by default and is generally safer.
        self._lock = RLock()
        
        # 2. Pass the explicit lock to the Condition constructor.
        self._condition = threading.Condition(self._lock)
        
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._running = False

    def _worker_loop(self):
        """The main loop that runs in a separate thread."""
        print("Worker thread started.")
        while self._running:
            
            # 3. Use the explicit lock for synchronization.
            with self._lock:
                if self.pq.empty():
                    # Wait on the condition. This atomically releases
                    # self._lock and waits.
                    self._condition.wait()
                    continue
                
                next_node = self.pq.queue[0]
                sleep_duration = next_node.ts - time.time()

                if sleep_duration > 0:
                    # Wait for timeout OR a notify(). This also
                    # atomically releases/re-acquires self._lock.
                    self._condition.wait(timeout=sleep_duration)
                    continue
                
                # It's time to run, get the node.
                node_to_run = self.pq.get_nowait()
            
            # Execute outside the lock
            try:
                node_to_run.fn()
                self.pq.task_done()
            except Exception as e:
                print(f"Error executing task: {e}")

    def start(self):
        """Starts the background worker thread."""
        if not self._running:
            self._running = True
            self._worker_thread.start()
            print("Scheduler started.")

    def stop(self):
        """Stops the background worker thread gracefully."""
        if self._running:
            print("Stopping scheduler...")
            self._running = False
            
            # 3. Use the explicit lock to safely notify
            with self._lock:
                self._condition.notify_all()
                
            self._worker_thread.join()
            print("Scheduler stopped.")

    def defer(self, fn: callable, delay_seconds: int):
        """Adds a function to the queue and notifies the worker."""
        if not self._running:
            print("Scheduler is not running. Cannot defer task.")
            return
            
        execution_time = time.time() + delay_seconds
        
        # 3. Use the explicit lock to safely add to the queue
        with self._lock:
            self.pq.put(Node(ts=execution_time, fn=fn))
            # Notify the worker while holding the lock.
            self._condition.notify()
        
        print(f"Scheduled task to run in {delay_seconds} second(s).")


if __name__ == "__main__":
    def task(message: str):
        """A simple task to be deferred."""
        print(f"[{time.ctime()}] EXECUTING TASK: {message}")

    scheduler = DeferFn()
    scheduler.start()

    print(f"[{time.ctime()}] Scheduling a task for 10 seconds from now.")
    scheduler.defer(lambda: task("Long wait task (10s)"), 10)

    print(f"[{time.ctime()}] Main thread sleeping for 2 seconds...")
    time.sleep(2)

    print(f"[{time.ctime()}] Scheduling a MORE URGENT task for 1 second from now.")
    scheduler.defer(lambda: task("URGENT task (1s)"), 1)

    time.sleep(12)
    scheduler.stop()
    print("Program finished.")
