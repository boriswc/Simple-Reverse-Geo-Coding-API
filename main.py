import os
import csv
import json
import requests
import itertools
import geopy.distance
from io import StringIO
from flask import Flask, request, abort

GOOGLE_MAP_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
api_key = os.environ.get('API_KEY')

api = Flask(__name__)


# Receives a POST type API Request with a CSV file and returns the addresses and distances of all the geo-locations
@api.route("/calculateDistances", methods=["POST"])
def calculate_distances():
    csv_file = request.files['file']
    # Verifying that the file is correct and the API Key is set up
    check_exceptions(csv_file)
    # Read the file in-memory to avoid saving to disk and save it in a list of dictionaries
    csv_file_stream = StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
    coordinates = [coordinate for coordinate in csv.DictReader(csv_file_stream)]
    # Checking if the column names are correct
    if not all(column in coordinate.keys() for column in ['Point', 'Latitude', 'Longitude']
               for coordinate in coordinates):
        abort(400, 'Wrong column names in file, please verify that they are Point, Latitude, and Longitude')
    # Formatting the coordinates list of dictionaries to a format that will allow us to use combinations
    coordinates_dictionary = dict(zip([coordinate['Point'] for coordinate in coordinates],
                                      [{'Latitude': coordinate['Latitude'], 'Longitude': coordinate['Longitude']}
                                       for coordinate in coordinates]))

    # Using Google's map api to get the address of the coordinates
    ret_address = get_address_from_gapi(coordinates_dictionary)
    # Calculating the distances between all combinations of locations received
    distances = calculate_distances_between_all_combinations(coordinates, coordinates_dictionary)
    # Formatting the response of the API call
    returned_dict = {
        'points': [{'name': name, 'address': address} for name, address in ret_address.items()],
        'links': [{'name': distance['name'], 'distance': distance['distance']} for distance in distances]
    }
    # Replace return with return json.dumps(returned_dict, indent=4) for a response that is easier to look at
    return returned_dict


# Receives the list of dictionaries and dictionary to calculate the distance between all the different locations
def calculate_distances_between_all_combinations(coordinates, coordinates_dictionary):
    distances = []
    for combination in itertools.combinations([coordinate['Point'] for coordinate in coordinates], 2):
        origin, destination = combination
        distances.append({
            'name': "".join(combination),
            'distance': str(geopy.distance.distance((coordinates_dictionary[origin]['Latitude'],
                                                     coordinates_dictionary[origin]['Longitude']),
                                                    (coordinates_dictionary[destination]['Latitude'],
                                                     coordinates_dictionary[destination]['Longitude'])).meters)
        })

    return distances


# Receives the dictionary containing all the points and their coordinates and returns the addresses via the google api
def get_address_from_gapi(coordinates_dictionary):
    ret_address = {}
    for name, location in coordinates_dictionary.items():
        response = requests.get(GOOGLE_MAP_API_URL,
                                params={'latlng': f"{location['Latitude']},{location['Longitude']}",
                                        'result_type': 'street_address',
                                        'key': {api_key}})
        if not response.ok:
            abort(500, f'Google API returned status {response.status_code}')
        parsed_json = json.loads(response.content)
        ret_address[name] = parsed_json['results'][0]['formatted_address']

    return ret_address


# Receives a file and checks if the extension is a csv file
def check_exceptions(file):
    if not api_key:
        abort(400, "Missing API KEY, please configure the API_KEY environment variable")
    file_name = file.filename
    if not file:
        abort(400, "Missing file from request")
    elif file_name == '':
        abort(400, "Empty file name from request")
    elif os.path.splitext(file_name)[-1] != ".csv":
        abort(400, "Wrong file extension")


if __name__ == '__main__':
    api.run(debug=False)
