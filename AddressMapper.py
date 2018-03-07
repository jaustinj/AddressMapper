import json
import time

import pandas as pd
import requests

# Constants user must configure in config.py
from config import API_KEY, OUTPUT_FILE, ADDRESSES

class GoogleMapper(object):
    '''Takes an address or place name and "google maps" the result
    via the google API. 

    Arguments:
    address [required]:  address or name of place

    Returns:
    GoogleMapper.name:    Same as argument
    GoogleMapper.lat:     Latitude of address
    GoogleMapper.lon:     Longitude of address

    Note, standard google API allows for 2500 free requests
    per day, with a max of 50/sec queries.  Make sure not
    to go over these limits or you may be charged
    '''

    URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    
    def __init__(self, address):
        self.name = address
        self.result = None
        self.geo_attributes = None
        self._main()
        
    def __repr__(self):
        return str(self.geo_attributes)
    
    def _encode_name(self):
        return self.name.replace(',', ''
                       ).replace('&', 'and'
                       ).replace(' ', '+')
    
    class AddressParser(object):
        def __init__(self, address_components):
            self.ac = address_components
            
        def try_dec(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except IndexError:
                    return None
            return wrapper
        
        def filter_list(self, filter_condition, length='long_name'):
            return [a[length] for a in self.ac if filter_condition in a['types']][0]
            
        @try_dec
        def parse_street(self):
            return self.filter_list('street_number')
        
        @try_dec
        def parse_route(self):
            return self.filter_list('route')
        
        @try_dec
        def parse_city(self):
            return self.filter_list('locality')
        
        @try_dec
        def parse_county(self):
            return self.filter_list('administrative_area_level_2')
        
        @try_dec
        def parse_state(self):
            return self.filter_list('administrative_area_level_1')
        
        @try_dec
        def parse_state_abbr(self):
            return self.filter_list('administrative_area_level_1',length='short_name')
        
        @try_dec
        def parse_country(self):
            return self.filter_list('country')
        
        @try_dec
        def parse_country_abbr(self):
            return self.filter_list('country', length='short_name')
        
        @try_dec
        def parse_postal(self):
            return self.filter_list('postal_code')
        
            
    
    def _parse_result(self, result):
        attrs = {}

        r_str = result.decode('utf8')
        r_json = json.loads(r_str)

        lat_lon = r_json['results'][0]['geometry']['location']
        attrs['lat'] = lat_lon['lat']
        attrs['lon'] = lat_lon['lng']

        addr = r_json['results'][0]['address_components']
        A = self.AddressParser(addr)
        
        attrs['street_num'] = A.parse_street()
        attrs['route'] = A.parse_route()
        attrs['city'] = A.parse_city()
        attrs['county'] = A.parse_county()
        attrs['state'] = A.parse_state()
        attrs['state_abbr'] = A.parse_state_abbr()
        attrs['country'] = A.parse_country()
        attrs['country_abbr'] = A.parse_country_abbr()
        attrs['postal'] = A.parse_postal()

        attrs['name'] = self.name
        
        return attrs
    
    def _main(self):
        encoded_name = self._encode_name()
        formatted_url = self.URL.format(address=encoded_name, api_key=API_KEY)
        
        r = requests.get(formatted_url).content
        self.result = r
        self.geo_attributes = self._parse_result(r)


if __name__ == '__main__':
    # grab addresses from config file
    address_list = ADDRESSES

    # Use GoogleMapper Class to parse results from Google API
    geo_list = []
    for ind, name in enumerate(address_list):
        G = GoogleMapper(name)
        geo_list.append(G)
        print('Finished {}/{}'.format(ind+1, len(address_list)))
        time.sleep(0.1) #Google Standard Max = 50/sec

    #convert list of addresses to pandas df
    d = {}
    for key in G.geo_attributes.keys():
        d[key] = [a.geo_attributes[key] for a in geo_list]

    df = pd.DataFrame(d)[['name', 'lat', 'lon', 
                          'street_num', 'route', 'city', 
                          'county', 'state', 'state_abbr',
                          'country', 'country_abbr', 'postal']]

    df.to_csv(OUTPUT_FILE, index=False)

    print('DONE \nFile written to: {}'.format(OUTPUT_FILE))
