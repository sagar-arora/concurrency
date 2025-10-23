import queue
import threading
from typing import Any, Tuple
from dataclasses import dataclass # Need to import this

@dataclass
class CallableFn():
    fn: callable
    args: Tuple

class ThreadPool:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.workers = []
        self.queue: queue.Queue = queue.Queue() # Don't need type hint here
        
        for _ in range(num_workers):
            # Make threads daemons so they don't block program exit
            thread = threading.Thread(target=self._worker_loop, daemon=True)
            thread.start()
            self.workers.append(thread)

    def _worker_loop(self):
        while True:
            # Block and wait for a task
            task = self.queue.get()
            
            if task is None:
                # Got the "stop" signal, so exit the loop
                self.queue.task_done()
                break
            
            try:
                task.fn(*task.args)
            except Exception as e:
                # Good practice to catch errors in the worker
                print(f"Error in worker thread: {e}")
            finally:
                # Mark the task as complete
                self.queue.task_done()

    def submit(self, fn: callable, *args):
        # --- The "Bundle" Fix ---
        # Pass 'args' as a single tuple
        self.queue.put(CallableFn(fn, args))

    def shutdown(self):
        # --- The "Sentinel" Implementation ---
        # Put one "None" pill for each worker
        for _ in self.workers:
            self.queue.put(None)
        
        # --- The "Join" ---
        # Wait for all worker threads to finish
        for worker in self.workers:
            worker.join()
        
        print("Thread pool shut down.")

# --- Example for Part 1 ---
def say_hello(name, delay):
    time.sleep(delay)
    print(f"Hello, {name}!")

pool = ThreadPool(num_workers=2)

pool.submit(say_hello, "Alice", 0.5)
pool.submit(say_hello, "Bob", 0.2)
pool.submit(say_hello, "Charlie", 0.1)

pool.shutdown()
