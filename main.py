# Localization for Bear Project
# Author: Jacob Oakman with help from Ezra Alberts
# Data was pulled from
# https://arctos.database.museum/
# https://ucmpdb.berkeley.edu/
# https://paleobiodb.org/#/
# https://geo.fcc.gov/api/census/#!/area/get_area

import json
import requests

# Open files
ursus_file = open('ursus_id.json')
ucmp_file = open('ucmp.json')
mvz_file = open('bears_mvz.json')

# Read Files into json objects
ursus_data = json.load(ursus_file)
ucmp_data = json.load(ucmp_file)
mvz_data = json.load(mvz_file)

print("Loaded files successfully :)")

for bear in ursus_data:
    # Add fields with default values
    bear['State'] = ""
    bear['Lat'] = ""
    bear['Long'] = ""
    bear['County'] = ""

    # Handle Specimens in the MVZ
    if bear['Museum'] == "MVZ":
        # Search for the bear number in the guid of the mvz data
        for mvz_element in mvz_data['Records']:
            if "/guid/MVZ:Mamm:"+bear['Number'] in mvz_element['guid']:
                # Pull data from the relevant element
                bear['State'] = mvz_element['state_prov']
                bear['Lat'] = mvz_element['dec_lat']
                bear['Long'] = mvz_element['dec_long']

                # Use Lat and Long to lookup the county using the FCC API
                if bear['Lat'] and bear['Long']:
                    # Send call to the FCC API
                    print("https://geo.fcc.gov/api/census/area?lat="+str(bear['Lat'])+"&lon="+str(bear['Long'])+"&censusYear=2020&format=json")
                    county_data = requests.get("https://geo.fcc.gov/api/census/area?lat="+str(bear['Lat'])+"&lon="+str(bear['Long'])+"&censusYear=2020&format=json").json()
                    
                    # Parse Returned data
                    if len(county_data['results']) == 1:
                        bear['County'] = county_data['results'][0]['county_name']
                    else:
                        if len(county_data['results']) == 0:
                            # No records for county were returned
                            print("No County Found")
                        else:
                            # Multiple records for county were returned, check if all the same county name
                            safe = True
                            for result in county_data['results']:
                                if result['county_name'] != county_data['results'][0]['county_name']:
                                    safe = False
                                    break
                            
                            if safe:
                                # All county records returned contain the same county name
                                bear['County'] = county_data['results'][0]['county_name']
                            else:
                                # County records returned multiple different values
                               print("Multiple options found for county")
                               print(county_data)
                break
    # Handle Specimens in the UCMP
    else:
        # Search for the bear number in the spec_id field of the ucmp data
        for ucmp_element in ucmp_data:
            if bear['Number'] == ucmp_element['spec_id']:
                bear['State'] = ucmp_element['state_prov_std']
                bear['County'] = ucmp_element['county_std']
                print(ucmp_element['spec_id'])
                print(ucmp_element['loc_name'])
                break

    
    print(bear)

# Export results to json file
with open("results.json", "w") as outfile:
    json.dump(ursus_data, outfile)