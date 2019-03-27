import logging
from flask import send_file, request, abort
from api.v1.resource import Resource
from inject_variants import get_vcf
import time
import os
from functools import wraps
from api.v1.util import limit


class Download(Resource):
    @limit
    def get(self, sample_id=None):
        f = get_vcf(sample_id)
        return send_file(f, attachment_filename=f, as_attachment=True)
