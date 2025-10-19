import time
import threading
import queue # Import the queue module for queue.Empty
from queue import PriorityQueue
from dataclasses import dataclass, field

@dataclass(order=True)
class Node:
    ts: float = field(compare=True)
    fn: callable = field(compare=False)

class DeferFn:
    """
    A scheduler that uses a simple 'polling' loop
    to check for tasks.
    """
    def __init__(self):
        # The PriorityQueue is thread-safe
        self.pq = PriorityQueue()
        self._running = False
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)

    def _worker_loop(self):
        """The main loop that runs in a separate thread."""
        print("Worker thread started (Polling Mode).")
        while self._running:
            node = None
            try:
                # Try to get a node without blocking
                node = self.pq.get_nowait()
            except queue.Empty:
                # Queue is empty, sleep for 1ms and try again
                time.sleep(0.001)
                continue

            # We got a node. Check its time.
            current_time = time.time()
            if current_time >= node.ts:
                # It's time to run the task
                try:
                    node.fn()
                    self.pq.task_done()
                except Exception as e:
                    print(f"Error executing task: {e}")
            else:
                # Not time yet, PUT IT BACK in the queue
                self.pq.put(node)
                # Sleep for 1ms to avoid spinning
                time.sleep(0.001) 
    
    def start(self):
        if not self._running:
            self._running = True
            self._worker_thread.start()
            print("Scheduler started.")

    def stop(self):
        if self._running:
            self._running = False
            self._worker_thread.join()
            print("Scheduler stopped.")

    def defer(self, fn: callable, delay_seconds: int):
        if not self._running:
            print("Scheduler is not running.")
            return
            
        execution_time = time.time() + delay_seconds
        self.pq.put(Node(ts=execution_time, fn=fn))
        print(f"Scheduled task in {delay_seconds} second(s).")
