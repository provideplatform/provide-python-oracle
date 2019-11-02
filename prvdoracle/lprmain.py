'''Main entrypoint and runloop for provide LPR oracle instances.'''

import logging
import os

import tornado.gen

from main import bootstrap, ProvideOracle
from lpr.service import LPR

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
LPR oracle main runloop.
'''
class LPROracle(ProvideOracle):

    def __init__(self):
        '''Initializer.'''
        super(LPROracle, self).__init__() 
        logger.info('provide LPR oracle instance initialized')

    @tornado.gen.coroutine
    def start(self):
        '''Attempt to start the provide-oracle instance using the configured environment.'''
        super(LPROracle, self).start() 
        self.lpr = LPR()
        logger.info('started provide LPR oracle instance')

    @tornado.gen.coroutine
    def shutdown(self):
        '''Attempt to gracefully shutdown provide LPR oracle instance.'''
        super(LPROracle, self).shutdown() 
        self.lpr.unload()

if __name__ == '__main__':
    bootstrap(LPROracle())
