'''HTTP service for receiving API calls from local services.'''

import json
import logging
import tornado
import tornado.web

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
Tornado HTTP API for receiving calls from local services.
'''
class API(tornado.web.RequestHandler):

    def initialize(self, on_recognized):
        '''Initializer.'''
        self.on_recognized = on_recognized
        logger.info('initialized local http service')

    @tornado.gen.coroutine
    def post(self):
        '''Handle POST.'''
        logger.debug('received {}-byte http request via LPR API'.format(len(self.request.body)))
        logger.debug('{}'.format(self.request))
        if self.on_recognized != None:
            self.on_recognized(json.loads(self.request.body))
