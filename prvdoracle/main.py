'''Main entrypoint and runloop for provide oracle instances.'''

import logging
import os
import uuid

import tornado
import tornado.gen
import tornado.process
from tornado.ioloop import IOLoop

from prvd.message_bus import MessageBus

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
Entry point for the provide oracle main runloop.
'''
class ProvideOracle(object):

    def __init__(self):
        '''Initializer.'''
        logger.info('provide oracle instance initialized')

    def configure(self, token, wallet_addr, multipart_chunk_size):
        '''Configure the oracle with the Provide API token and wallet address.'''
        self.token = token
        self.wallet_addr = wallet_addr
        self.multipart_chunk_size = multipart_chunk_size
        logger.info('provide oracle instance configured with wallet address: {}'.format(self.wallet_addr))

    @tornado.gen.coroutine
    def publish_message(self, subject, msg):
        '''Publish a message on a specific subject using the message bus.'''
        try:
            filename = '{}.json'.format(uuid.uuid4())
            logger.info('oracle attempting to publish {}-byte message {} on subject: {}'.format(len(msg), filename, subject))
            self.message_bus.publish_message(subject, msg, filename=filename, wrap_with_directory=True)
        except Exception as e:
            logger.warning('oracle failed to publish {}-byte message via message bus; {}'.format(len(msg), e))

    @tornado.gen.coroutine
    def start(self):
        '''Attempt to start the provide-oracle instance using the configured environment.'''
        self.message_bus = MessageBus(self.token, self.wallet_addr, self.multipart_chunk_size)
        logger.info('provide oracle instance started with message bus application id: {}'.format(self.message_bus.application_id))

    @tornado.gen.coroutine
    def shutdown(self):
        '''Attempt to gracefully shutdown the provide oracle instance.'''
        logger.debug('attempting to gracefully shutdown provide oracle instance')
        # no-op...

def bootstrap(oracle_instance=None):
    '''Bootstrap.'''
    token = os.environ.get('PROVIDE_API_TOKEN', None)
    wallet_addr = os.environ.get('PROVIDE_WALLET_ADDRESS', None)
    multipart_chunk_size = int(os.environ.get('PROVIDE_MULTIPART_CHUNKSIZE', MessageBus.DEFAULT_MULTIPART_CHUNK_SIZE))
    if token == None or wallet_addr == None:
        raise Exception('provide oracle requires PROVIDE_API_TOKEN and PROVIDE_WALLET_ADDRESS set in the environment')

    worker_count = os.getenv('WORKER_COUNT', 1)
    logger.info('provide oracle main entry point entered; attempting to start {} worker(s)...'.format(worker_count))

    # FIXME-- audit how we handle before- and after-the-fork when worker_count > 1...
    #tornado.process.fork_processes(worker_count, worker_max_attempts)

    try:
        instances = []
        for _ in range(worker_count):
            try:
                instance = oracle_instance if oracle_instance != None else ProvideOracle()
                instance.configure(token, wallet_addr, multipart_chunk_size)
                instances.append(instance)

                if tornado.process.task_id() != 0:
                   ioloop = IOLoop.instance()
                   ioloop.add_callback(instance.start)
                   ioloop.start()
                else:
                    logger.warning('provide oracle main entry point process didn\'t start IOLoop')
            except (KeyboardInterrupt):
                logger.debug('provide oracle instance exiting due to keyboard interrupt')
            finally:
                logger.info('provide oracle instance exited')
    finally:
        for inst in instances:
            inst.shutdown() # gracefully shutdown the worker...

if __name__ == '__main__':
    bootstrap()
