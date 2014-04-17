from logging import getLogger
from json import load

LOG = getLogger(__name__)


class Config(object):
    def __init__(self):
        self.tree = {}

    def load(self, filename, replace=None):
        LOG.info('loading %s (replace = %s)', filename, bool(replace))
        with open(filename) as config_file:
            if replace:
                self.tree = load(config_file)
            else:
                self.tree.update(load(config_file))

    def get(self, *keys):
        node = self.tree
        for key in keys:
            node = node[key]
        return node
