import time
import threading

class TokenBucket:

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        
        # Start with a full bucket
        self.current_tokens = self.capacity
        # Use float time, not int
        self.last_refill = time.time()
        
        # Fix typo: threading.Lock()
        self.lock = threading.Lock()
        
        # This condition is just used to 'wait'
        self.condition = threading.Condition(self.lock)

    def _refill(self):
        now = time.time()
        time_passed = now - self.last_refill
        
        if time_passed > 0:
            new_tokens = time_passed * self.refill_rate
            self.current_tokens = min(self.current_tokens + new_tokens, self.capacity)
            self.last_refill = now

    def consume(self):
        with self.lock:
            # Always refill first to get the most up-to-date token count
            self._refill()
            
            while self.current_tokens < 1:
                tokens_needed = 1.0 - self.current_tokens
                time_to_wait = tokens_needed / self.refill_rate
      
                self.condition.wait(timeout=time_to_wait)
                
                # When we wake up, we MUST re-run the refill logic
                # to add the tokens we just waited for.
                self._refill()

            # We have at least 1 token, so consume it
            self.current_tokens -= 1


# --- Example Usage ---
if __name__ == "__main__":
    
    # Bucket with capacity 5, refills 1 token/sec
    bucket = TokenBucket(capacity=5, refill_rate=1)

    def worker():
        print(f"[{time.time():.2f}] {threading.current_thread().name}: Requesting token...")
        bucket.consume()
        print(f"[{time.time():.2f}] {threading.current_thread().name}: Got token!")

    threads = []
    # Start 7 threads. 
    # The first 5 should get a token instantly.
    # The 6th should wait ~1 second.
    # The 7th should wait ~2 seconds.
    for i in range(7):
        t = threading.Thread(target=worker, name=f"Worker-{i}")
        t.start()
        threads.append(t)
        time.sleep(0.1) # Stagger starts slightly

    for t in threads:
        t.join()
    
    print("All threads finished.")
