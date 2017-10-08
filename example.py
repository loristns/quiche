import time
from quiche import Quiche

cache = Quiche('example_cache', lifetime=60)

@cache.cached
def long_runtime_function():
    time.sleep(10)
    return 'Execution ended'

if __name__ == '__main__':
    print(long_runtime_function())