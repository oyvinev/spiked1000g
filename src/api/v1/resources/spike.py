import logging
from flask import send_file, request, abort
from api.v1.resource import Resource
from inject_variants import spike
import time
import os
from functools import wraps

log = logging.getLogger('spiked1000g')

class RateLimit(object):
    RATE_INTERVAL = int(os.environ.get('RATE_INTERVAL', 5*60))
    LIMIT = int(os.environ.get('RATE_LIMIT', 10))
    ALLOW = ['172.17.0.1', '127.0.0.1']
    REQUESTS = []

    def _allow(self, addr):
        if addr in RateLimit.ALLOW:
            return True
        else:
            return [a for t,a in RateLimit.REQUESTS].count(addr) <= RateLimit.LIMIT

    def __call__(self, addr):
        t = int(time.time())
        RateLimit.REQUESTS.append((t, addr))
        cutoff = t - RateLimit.RATE_INTERVAL
        try:
            cutoff_index = next(i for i,(t, _) in enumerate(RateLimit.REQUESTS) if t > cutoff)
            RateLimit.REQUESTS = RateLimit.REQUESTS[cutoff_index:]
        except StopIteration:
            RateLimit.REQUESTS = []

        if not self._allow(addr):
            log.info('Rejected request from {}'.format(addr))
            abort(429)
        else:
            log.info("Accepted request from {}".format(addr))



REQUESTS = RateLimit()

def limit(func):
    @wraps(func)
    def inner(*args, **kwargs):
        REQUESTS(request.remote_addr)
        return func(*args, **kwargs)

    return inner

class Spike(Resource):
    @limit
    def get(self):
        case = request.args.get('case')
        sample_id = request.args.get('sample')
        hash = request.args.get('hash')

        if hash:
            assert not case and not sample_id
        if case and sample_id:
            assert not seed

        f, case_id, sample_id, hash = spike(case, sample_id, hash)

        return send_file(f, attachment_filename=sample_id+"_"+case_id+".vcf.gz", as_attachment=True)
