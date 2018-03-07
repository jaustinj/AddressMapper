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

    Without an API KEY this script will only pull 1-3 addresses
    Before throwing an error
    '''

    URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    
    def __init__(self, address):
        self.name = address
        self.geo_attributes = None
        self._main()
        
    def __repr__(self):
        return str(self.geo_attributes)
    
    def _encode_name(self):
        return self.name.replace(',', ''
                       ).replace('&', 'and'
                       ).replace(' ', '+')
    
    def _parse_result(self, result):
        attrs = {}

        r_str = result.decode('utf8')
        r_json = json.loads(r_str)

        lat_lon = r_json['results'][0]['geometry']['location']
        attrs['lat'] = lat_lon['lat']
        attrs['lon'] = lat_lon['lng']

        address_components = r_json['results'][0]['address_components']
        attrs['city_long'] = address_components[0]['long_name']
        attrs['city_short'] = address_components[0]['short_name']
        attrs['county_long'] = address_components[1]['long_name']
        attrs['county_short'] = address_components[1]['short_name']
        attrs['state_long'] = address_components[2]['long_name']
        attrs['state_short'] = address_components[2]['short_name']
        attrs['country_long'] = address_components[0]['long_name']
        attrs['country_short'] = city_long = address_components[0]['short_name']

        attrs['name'] = self.name
        
        return attrs
    
    def _main(self):
        encoded_name = self._encode_name()
        formatted_url = self.URL.format(address=encoded_name, api_key=API_KEY)
        
        r = requests.get(formatted_url).content
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
                          'city_short', 'city_long', 'county_short', 
                          'county_long', 'state_short', 'state_long', 
                          'country_short', 'country_long']]

    df.to_csv(OUTPUT_FILE, index=False)

    print('DONE \nFile written to: {}'.format(OUTPUT_FILE))
