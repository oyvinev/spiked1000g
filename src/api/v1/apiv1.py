import resources


class ApiV1(object):
    def __init__(self, app, api):
        self.app = app
        self.api = api

    def _add_resource(self, resource, *paths):
        self.api.add_resource(resource, *paths, strict_slashes=False)

    def setup_api(self):
        self._add_resource(resources.spike.Spike, "/")
