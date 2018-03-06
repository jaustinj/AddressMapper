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
        self._main()
        
    def __repr__(self):
        return str(self.__dict__)
    
    def _encode_name(self):
        return self.name.replace(',', ''
                       ).replace('&', 'and'
                       ).replace(' ', '+')
    
    def _parse_result(self, result):
        r_str = result.decode('utf8')
        r_json = json.loads(r_str)
        lat_lon = r_json['results'][0]['geometry']['location']
        lat = lat_lon['lat']
        lon = lat_lon['lng']
        
        return lat, lon
    
    def _main(self):
        encoded_name = self._encode_name()
        formatted_url = self.URL.format(address=encoded_name, api_key=API_KEY)
        
        r = requests.get(formatted_url).content
        self.lat, self.lon = self._parse_result(r)


if __name__ == '__main__':
	# convert str of addresses into list
	address_list = ADDRESSES.split('\n')
	# In case extra spaces introduced in config file
	address_list = [a for a in address_list if a != '']

	# Use GoogleMapper Class to parse results from Google API
	geo_list = []
	for ind, name in enumerate(address_list):
	    G = GoogleMapper(name)
	    geo_list.append(G)
	    print('Finished {}/{}'.format(ind+1, len(address_list)))
	    time.sleep(0.1) #Google Standard Max = 50/sec

	#convert list of addresses to pandas df
	d = {'name': [a.name for a in geo_list],
	     'lat': [a.lat for a in geo_list],
	     'lon': [a.lon for a in geo_list]
	    }
	df = pd.DataFrame(d)[['name', 'lat', 'lon']]
	df.to_csv(OUTPUT_FILE, index=False)

	print('DONE \nFile written to: {}'.format(OUTPUT_FILE))
