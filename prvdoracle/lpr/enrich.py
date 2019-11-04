'''Enrichment service for license tag -> vehicle data.'''

import logging
import requests
import tornado
import tornado.gen

import base64
from bs4 import BeautifulSoup
from functools import reduce

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


'''
Enrichment service for license tag -> vehicle data.
'''
class VehicleEnrichment(object):

    LICENSE_PLATE_ENRICHMENT_BASE_URL = 'https://findbyplate.com'

    def __init__(self, country, state, tag):
        '''Initializer.'''
        self.country = country
        self.state = state
        self.tag = tag
        self.vehicle = None

    @tornado.gen.coroutine
    def enrich(self):
        '''Enrich the vehicle details using all available sources.'''
        logger.info('attempting to enrich vehicle details for {} license plate: {}'.format(self.state, self.tag))
        url = '{}/{}/{}/{}'.format(VehicleEnrichment.LICENSE_PLATE_ENRICHMENT_BASE_URL, self.country, self.state, self.tag)
        resp = requests.get(url)
        parser = BeautifulSoup(resp.text, 'html.parser')

        vehicle_details = {
            'build_data': {},
            'images': {
                'stock': None,
                'tag': None,
            },
            'tag': {
                'country': self.country,
                'state': self.state,
                'tag': self.tag,
            },
            'year': None,
            'make': None,
            'model': None,
            'trim': None,
        }        

        # license plate image
        results = parser.select('div.plate-top img')
        if len(results) == 1:
            src = results[0].get('data-src', None)
            if src != None:
                img = requests.get(src)
                vehicle_details['images']['tag'] = base64.b64encode(img.content)
        
        # vehicle stock photo
        main_report = parser.select('#nav-reports')
        if len(main_report) == 1:
            main_report = main_report[0]
            stock_image = main_report.select('div.row > div > img')
            if len(stock_image) == 1:
                src = stock_image[0].get('data-src', None)
                if src != None:
                    img = requests.get(src)
                    vehicle_details['images']['stock'] = base64.b64encode(img.content)

        # build data
        details = main_report.select('div.pointer')
        if len(details) == 1:
            details = details[0]
            for item in details.select('div.cell'):
                key = item.get('data-title', None)
                if key != None and len(item.contents) == 1:
                    k = reduce(lambda s0, s1: s0 + ('_' if s1.isupper() else '') + s1, key).lower() 
                    vehicle_details['build_data'][k]= item.contents[0].strip()

        # ymmt
        vehicle_details['year'] = vehicle_details['build_data']['model_year']
        vehicle_details['make'] = vehicle_details['build_data']['make']
        vehicle_details['model'] = vehicle_details['build_data']['model']
        vehicle_details['trim'] = vehicle_details['build_data']['trim']

        raise tornado.gen.Return(vehicle_details)
