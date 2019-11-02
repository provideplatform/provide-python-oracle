'''Main entrypoint and runloop for provide oracle instances.'''

import json
import logging
import os
import sys
import time
import uuid

import tornado.ioloop
import tornado.gen
import tornado.process
from tornado.ioloop import IOLoop

from prvd.message_bus import MessageBus

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


"""
Entry point for the provide oracle main runloop.
"""
class ProvideOracle(object):

    def __init__(self, message_bus):
        """Initializer."""
        self.message_bus = message_bus
        logger.info('provide oracle instance initialized with message bus application id: {}'.format(self.message_bus.application_id))

    @tornado.gen.coroutine
    def publish_message(self, subject, msg):
        """Publish a message on a specific subject using the message bus."""
        logger.info('oracle publishing message on subject: {}'.format(subject))
        self.message_bus.publish_message(subject, msg)

    @tornado.gen.coroutine
    def start(self):
        """Attempt to start the provide-oracle instance using the configured environment."""
        logger.info('started provide oracle instance')
        self.publish_message('test.subject', 'hello world')

    @tornado.gen.coroutine
    def shutdown(self):
        """Attempt to gracefully shutdown the provide oracle instance."""
        logger.debug('attempting to gracefully shutdown provide oracle instance')
        # no-op...

def bootstrap(message_bus):
    """Bootstrap."""
    worker_count = os.getenv('WORKER_COUNT', 1)
    logger.info('provide oracle main entry point entered; attempting to start {} worker(s)...'.format(worker_count))

    # FIXME-- audit how we handle before- and after-the-fork when worker_count > 1...
    #tornado.process.fork_processes(worker_count, worker_max_attempts)

    try:
        instances = []
        for _ in range(worker_count):
            try:
                instance = ProvideOracle(message_bus)
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
    # main entrypoint
    # if len(sys.argv) != 2:
    #     raise IOError('Invalid usage; the correct format is: main.py <token> <wallet_addr>')
    token = os.environ.get('PROVIDE_API_TOKEN', None)
    wallet_addr = os.environ.get('PROVIDE_WALLET_ADDRESS', None)
    if token == None or wallet_addr == None:
        raise IOError('provide oracle requires PROVIDE_API_TOKEN and PROVIDE_WALLET_ADDRESS set in the environment')
    message_bus = MessageBus(token, wallet_addr)
    bootstrap(message_bus)
