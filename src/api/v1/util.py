import os
import logging
import time
from functools import wraps
from flask import request, abort

log = logging.getLogger("spiked1000g")


class RateLimit(object):
    RATE_INTERVAL = int(os.environ.get("RATE_INTERVAL", 5 * 60))
    LIMIT = int(os.environ.get("RATE_LIMIT", 10))
    ALLOW = ["172.17.0.1", "127.0.0.1"]
    REQUESTS = []

    def _allow(self, addr):
        if addr in RateLimit.ALLOW:
            return True
        else:
            return [a for t, a in RateLimit.REQUESTS].count(addr) <= RateLimit.LIMIT

    def __call__(self, addr):
        t = int(time.time())
        RateLimit.REQUESTS.append((t, addr))
        cutoff = t - RateLimit.RATE_INTERVAL
        try:
            cutoff_index = next(
                i for i, (t, _) in enumerate(RateLimit.REQUESTS) if t > cutoff
            )
            RateLimit.REQUESTS = RateLimit.REQUESTS[cutoff_index:]
        except StopIteration:
            RateLimit.REQUESTS = []

        if not self._allow(addr):
            log.info("Rejected request from {}".format(addr))
            abort(429)
        else:
            log.info("Accepted request from {}".format(addr))


REQUESTS = RateLimit()


def limit(func):
    @wraps(func)
    def inner(*args, **kwargs):
        print args
        print kwargs
        REQUESTS(request.remote_addr)
        return func(*args, **kwargs)

    return inner
