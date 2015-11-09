import redis

REDIS_CLIENT = redis.Redis()

def task_lock(function=None, key="", timeout=15):
    """Enforce only one celery task at a time."""

        def _dec(run_func):
            """Decorator."""

            def _caller(*args, **kwargs):
                """Caller."""
                ret_value = None
                have_lock = False

                lock = REDIS_CLIENT.lock(key, timeout=timeout)
                try:
                    print("Waiting to lock node " + key )
                    have_lock = lock.acquire(blocking=True)
                    print("Lock acquired on " + key )
                    
                    if have_lock:
                        ret_value = run_func(*args, **kwargs)

                finally:
                    if have_lock:
                        lock.release()
                        print("Released lock on " + key )

                return ret_value

            return _caller
            
        return _dec(function) if function is not None else _dec


'''
import redis

# Lock will automatically be released (cache item expires)
LOCK_TIMEOUT = 15

def acquire_lock( lock_id ):

    # Loop until the lock can be acquired
    while not cache.add( lock_id, "True", LOCK_TIMEOUT ):
        print("Waiting to lock node " + lock_id )

    print("Lock acquired on " + lock_id )

    return

def release_lock( lock_id ):

    cache.delete( lock_id )
    print("Released lock on " + lock_id )
    return
'''
