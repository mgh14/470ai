"""BZRFlag: BZFlag with Robots!

"""
import logging
import os

import config
#from main import run

LOG_FILENAME = os.path.abspath(os.path.join(
    os.path.split(__file__)[0], '..', 'debug.log'))


def run():
    config.init()
    from game import Game
    level = logging.WARNING
    if config.config['debug']:
        level = logging.DEBUG
    fname = config.config.get('debug_out', None)
    logging.basicConfig(level=level, filename=fname)
    g = Game()
    g.loop()
