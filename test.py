import threading

def worker():
    for i in range(10):
        print(i)

thread = threading.Thread(target = worker)
thread.start()
