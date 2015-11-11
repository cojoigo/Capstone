import redis
from contextlib import contextmanager

REDIS_CLIENT = redis.Redis()

@contextmanager
def task_lock( key="", timeout=15 ):
    have_lock = False

    lock = REDIS_CLIENT.lock( key, timeout = timeout )
    try:
        #print("Waiting to lock node " + key )
        have_lock = lock.acquire( blocking=True )
        #print("Lock acquired on " + key )

        if have_lock:
            yield

    finally:
        try:
            if have_lock:
                lock.release()
                #print("Released lock on " + key )
        except:
            pass
