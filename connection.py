import threading
import time
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Connection():
    id: Optional[int]
    host: str
    port: int

class ConnectionPool():

    def __init__(self, num_connections: int):
        self.n = num_connections
        
        # --- Fixes ---
        # 1. Use 'range(num_connections)', not len()
        # 2. Add IDs for clarity
        self.unused: List[Connection] = [Connection(id=i, host="localhost", port=10000) 
                                         for i in range(num_connections)]
        
        self.lock = threading.Lock()
        
        # 3. Renamed 'self.full' to 'self.available' for clarity.
        #    This condition signals that a connection IS available.
        self.available = threading.Condition(self.lock)
    
    def acquire(self) -> Connection:
        with self.lock:
            # 4. Wait condition is 'while NOT self.unused' (i.e., while empty)
            while not self.unused:
                print(f"Thread {threading.current_thread().name}: No connections. Waiting...")
                self.available.wait()
            
            # 5. Pop and RETURN the connection
            conn = self.unused.pop()
            print(f"Thread {threading.current_thread().name}: Acquired connection {conn.id}")
            return conn

    
    def release(self, conn: Connection):
        with self.lock:
            # 6. Add the connection back to the pool
            print(f"Thread {threading.current_thread().name}: Releasing connection {conn.id}")
            self.unused.append(conn)
            
            # 7. Notify ONE waiting thread that a connection is free.
            self.available.notify()


# --- Example Usage ---
if __name__ == "__main__":
    
    # Create a small pool of 2 connections
    pool = ConnectionPool(2)

    def worker_task(worker_id: int):
        print(f"Worker {worker_id}: Trying to acquire...")
        conn = pool.acquire()
        
        # Simulate doing work
        print(f"Worker {worker_id}: Got connection, working for 1 sec...")
        time.sleep(1)
        
        pool.release(conn)
        print(f"Worker {worker_id}: Released connection. Done.")

    # Start 3 threads. Since the pool size is 2,
    # one thread will be forced to wait.
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_task, args=(i,), name=f"Worker-{i}")
        t.start()
        threads.append(t)
        time.sleep(0.1) # Stagger starts slightly

    for t in threads:
        t.join()

    print("All workers finished.")
    print(f"Final connections in pool: {len(pool.unused)}")
