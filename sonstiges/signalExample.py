import threading
from time import sleep

# Create an Event object
event = threading.Event()

# Worker thread function
def worker_thread():
    while True:
        print("Worker thread waiting for signal...")
        event.wait()  # Wait for the event to be set
        print("Worker thread received signal and continuing...")

# Create and start the worker thread
thread = threading.Thread(target=worker_thread)
thread.start()

# Main thread
print("Main thread doing some work...")
# Signal the worker thread to continue

for i in range(10):
    event.set()
    event.clear()
    event.clear()
    sleep(1)

# Wait for the worker thread to finish
thread.join()
print("Main thread exiting.")
