'''LPR service leveraging OpenLPR bindings.'''

import logging
import tornado
import tornado.web

from api import API
from openalpr import Alpr

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
License plate recognition service.
'''
class LPR(object):

    DEFAULT_API_PORT = 9000
    DEFAULT_LPR_MAX_RESULTS = 3
    DEFAULT_OPENALPR_CONFIG_PATH = '/usr/share/openalpr/config/openalpr.defaults.conf'
    DEFAULT_OPENALPR_RUNTIME_DATA_PATH = '/usr/share/openalpr/runtime_data'

    def __init__(self,
                 on_recognized,
                 country='us',
                 openalpr_config_path=DEFAULT_OPENALPR_CONFIG_PATH,
                 openalpr_runtime_data_path=DEFAULT_OPENALPR_RUNTIME_DATA_PATH):
        '''Initializer.'''
        self.on_recognized = on_recognized
        self.alpr = None
        self.country = country
        self.alpr_config_path = openalpr_config_path
        self.alpr_runtime_data_path = openalpr_runtime_data_path
        self.bootstrap_api()
        self.bootstrap_alpr()
        logger.info('initialized automatic LPR service')

    @tornado.gen.coroutine
    def bootstrap_api(self):
        '''Bootstrap a local http endpoint for receiving metadata from local video services.'''
        app = tornado.web.Application([
            (r'/', API, dict(on_recognized=self.on_recognized)),
        ])
        app.listen(LPR.DEFAULT_API_PORT)

    @tornado.gen.coroutine
    def bootstrap_alpr(self):
        '''Bootstrap the openalpr bindings.'''
        try:
            self.alpr = Alpr(self.country, self.alpr_config_path, self.alpr_runtime_data_path)
            if not self.alpr.is_loaded():
                logger.warning('failed to bootstrap openalpr')
            self.alpr.set_top_n(LPR.DEFAULT_LPR_MAX_RESULTS)
            self.alpr.set_detect_region(True)
            # alpr.set_default_region('')
        except Exception as e:
            logger.warning('failed to bootstrap openalpr; {}'.format(e))

    @tornado.gen.coroutine
    def unload(self):
        if self.alpr != None:
            self.alpr.unload()

    @tornado.gen.coroutine
    def process_frame(self, frame):
        '''Process a single arbitrary frame and extract license plates.'''
        logger.info('attempting to extract license plate features from {}-byte frame'.format(len(frame)))
        i = 0
        results = self.alpr.recognize_array(frame)
        for plate in results['results']:
            i += 1
            self.on_recognized(plate['candidates'][0])
            # for candidate in plate['candidates']:
            #     # prefix = '-'
            #     # if candidate['matches_template']:
            #     #     prefix = "*"
            #     logger.debug('recognized candidate plate #{}: {}; confidence: {}'.format(i, candidate['plate'], candidate['confidence']))
            #     if self.on_recognized != None:
