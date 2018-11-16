import logging
from flask import send_file, request
from api.v1.resource import Resource
from inject_variants import spike
log = logging.getLogger('spiked1000g')

class Spike(Resource):
    def get(self):
        print request.args
        case = request.args.get('case')
        sample_id = request.args.get('sample')
        hash = request.args.get('hash')

        log.info("case: {}".format(case))
        log.info("sample_id: {}".format(sample_id))
        log.info("hash: {}".format(hash))

        if hash:
            assert not case and not sample_id
        if case and sample_id:
            assert not seed

        f = spike(case, sample_id, hash)

        return send_file(f)
