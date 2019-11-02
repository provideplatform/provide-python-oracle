'''LPR service leveraging OpenLPR bindings.'''

import logging
import tornado

from openalpr import Alpr

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
License plate recognition service.
'''
class LPR(object):

    DEFAULT_LPR_MAX_RESULTS = 3

    def __init__(self, country='us', openalpr_config_path='./open-alpr.conf', openalpr_runtime_data_path='./openalpr-tmp'):
        '''Initializer.'''
        self.alpr = None
        self.country = country
        self.alpr_config_path = openalpr_config_path
        self.alpr_runtime_data_path = openalpr_runtime_data_path
        self.bootstrap_alpr()
        logger.info('initialized automatic LPR service')

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
        except:
            logger.warning('failed to bootstrap openalpr')

    @tornado.gen.coroutine
    def unload(self):
        if self.alpr != None:
            self.alpr.unload()

    @tornado.gen.coroutine
    def process_frame(self, frame):
        '''Process a single arbitrary frame and extract license plates.'''
        logger.info('attempting to extract license plate features from {}-byte frame'.format(len(frame)))
        logger.warning('process_frame() not implemented')
        i = 0
        results = self.alpr.recognize_array(frame)
        for plate in results['results']:
            i += 1
            for candidate in plate['candidates']:
                # prefix = '-'
                # if candidate['matches_template']:
                #     prefix = "*"
                logger.debug('recognized candidate plate #{}: {}; confidence: {}'.format(i, candidate['plate'], candidate['confidence']))
