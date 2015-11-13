import redis
from contextlib import contextmanager

REDIS_CLIENT = redis.Redis()


@contextmanager
def task_lock(key="", timeout=15):
    have_lock = False

    lock = REDIS_CLIENT.lock(key, timeout=timeout)
    try:
        have_lock = lock.acquire(blocking=True)
        if have_lock:
            yield
    finally:
        try:
            if have_lock:
                lock.release()
        except:
            pass
