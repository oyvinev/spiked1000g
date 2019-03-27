import logging
from flask import send_file, request, abort
from api.v1.resource import Resource
from inject_variants import spike
import time
import os
from functools import wraps
from api.v1.util import limit


class Spike(Resource):
    @limit
    def get(self):
        case = request.args.get("case")
        sample_id = request.args.get("sample")
        hash = request.args.get("hash")

        if hash:
            assert not case and not sample_id
        if case and sample_id:
            assert not hash

        f, case_id, sample_id, hash = spike(case, sample_id, hash)

        return send_file(
            f,
            attachment_filename=sample_id + "_" + case_id + ".vcf.gz",
            as_attachment=True,
        )
