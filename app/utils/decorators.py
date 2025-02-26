from time import time
from typing import Callable

from flask import current_app


def time_it(f: Callable):

    def wrapper(*args, **kargs):
        start = time()
        result = f(*args, **kargs)
        elapsed = time() - start
        current_app.logger.info(f'WEBHOOK executado em {elapsed:.5f}s')
        return result
    
    return wrapper
