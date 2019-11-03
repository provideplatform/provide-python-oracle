'''Main entrypoint and runloop for provide LPR oracle instances.'''

import json
import logging
import os

import tornado.gen

from main import bootstrap, ProvideOracle
from lpr.service import LPR
from lpr.enrich import VehicleEnrichment

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
LPR oracle main runloop.
'''
class LPROracle(ProvideOracle):

    DEFAULT_MESSAGE_SUBJECT = 'lpr.recognized'

    def __init__(self):
        '''Initializer.'''
        super(LPROracle, self).__init__() 
        logger.info('provide LPR oracle instance initialized')

    @tornado.gen.coroutine
    def start(self):
        '''Attempt to start the provide-oracle instance using the configured environment.'''
        super(LPROracle, self).start() 
        self.lpr = LPR(self.recognize)
        logger.info('started provide LPR oracle instance')

    @tornado.gen.coroutine
    def shutdown(self):
        '''Attempt to gracefully shutdown provide LPR oracle instance.'''
        super(LPROracle, self).shutdown() 
        self.lpr.unload()

    @tornado.gen.coroutine
    def recognize(self, params):
        '''Handle the successful recognition of a license plate.'''
        logger.info('attempting to publish lpr recognition message')
        candidates = params.get('results', [])
        if len(candidates) > 0:
            vehicle_details = VehicleEnrichment('us', 'KY', candidates[0]['plate']).enrich()
            vehicle_details['lpr'] = candidates
            self.message_bus.publish_message(LPROracle.DEFAULT_MESSAGE_SUBJECT, json.dumps(vehicle_details, indent=2))


if __name__ == '__main__':
    bootstrap(LPROracle())
