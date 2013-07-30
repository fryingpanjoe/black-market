from logging import getLogger
from json import load

LOG = getLogger(__name__)


class Config(object):
    def __init__(self):
        self.tree = {}

    def load(self, filename, replace=None):
        LOG.info('loading "%s"', filename)
        with open(filename) as config_file:
            new_tree = load(config_file)
            if replace:
                self.tree = new_tree
            else:
                self.tree.update(new_tree)

    def get(self, *keys):
        node = self.tree
        for key in keys:
            node = node[key]
        return node
