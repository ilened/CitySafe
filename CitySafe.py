from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import math
import requests
import googlemaps

def get_possible_directions(start, dest):
    """
    Parameters
        start(str): The address of the start location
        dest(str): The address of the destination
    Return
        result(list of tuples t(int,dict)): Possible routes to take to get from start to destination
        where each route is represented as a tuple t where t[0] is route number
        and t[1] is a dictionary representing the directions by step.
    """

    # Google Maps Directions API
    API = "https://maps.googleapis.com/maps/api/directions/json"

    # Note: alternatives parameter must be set to true in order to retreive more than 1 direction route
    param = {'origin': start, 'destination': dest, 'mode': 'walking', 
            'key':'AIzaSyAysRG8_QBS8sjnTSwQ3oVlGUVYuvarOqw', 'alternatives': 'true'}

    # Make an API call
    response = requests.get(API, params = param)

    # Retreive the json response and for each possible route and add the route to results as
    # tuple t(int,dict) where t[0] is route number and t[1] is a dictionary representing the directions by step.
    json_dict = response.json()
    result = []
    for i in range(len(json_dict['routes'])):
        result.append((i, json_dict['routes'][i]['legs'][0]['steps']))

    return result

def prioritize_routes(routes):
    """
    Params
        routes(list of tuples t(int,dict)): Possible routes to take to get from a start to destination
        stored as tuple t(route_num_found (int), route_steps_info (dict) ) in routes
    Return
        safety_list(list of tuples t(dict, int)): List of all possible tuples representing a possible routes and their safety rating
        where t[0] is a route and t[1] is it's safety score. The list is sorted by safest route where the first route in the list
        is the safest.
    """
    safety_list = []
    for number, route in routes:
        safety_list.append((route, safety_check(route)))

    return sorted(safety_list, key=lambda x: x[1])

def diff_in_meters(pointA, pointB):
    """
    Parameters
        pointA(dict): The start point on the map
        pointB(dict): The destination on the map
    Return
        (float): The distance from point A to point B in meters
    """
    d_lat = pointB['lat'] - pointA['lat']
    d_lng = pointB['lng'] - pointA['lng']

    temp = (
         math.sin(d_lat / 2) ** 2
       + math.cos(lat_1)
       * math.cos(lat_2)
       * math.sin(d_lng / 2) ** 2
    )

    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp))) * 1000



def countRisks(latlng, radius):
    """
    Make an API call to IBM's Cloudant Geospactial API to pull crime data reported in the last 90 days
    within a 0.5 mile (800 meters) radius of a location. 

    
    :param latlng: latitude and longitute information
    :param radius: check the crime rate of the area given the radius
    to scale the range of the area
    :return: the number of crimes reported in the area
    """
    
    API = 'https://education.cloudant.com/crimes/_design/geodd/_geo/geoidx'
    param = {'lat': latlng['lat'], 'lon': latlng['lng'], 'radius': radius, 'relation': 'contains', 'format':'geojson'}
    response = requests.get(API, params = param)
    
    return len(response.json()['features'])

def safety_check(route):
    """
    Parameters
        route(dict): A route from start to destination specifying the step by step directions.
    Return
        score(int): A safety score for the route. The lower the score is the safer it is.
    """
    score = 0.0
    prev_step = None

    for step in route:
        if prev_step != None:
            dist = diff_in_meters(prev_step, step)

        prev_step = step
        countRisks(step['end_location'], 800)
        break

    return score

def print_route(route):
    '''
    Parameters
        route(dict): A route from start to destination specifying the step by step directions.

    Prints readable directions from start to destination.
    '''
    for direction in route:
        instruction = direction['html_instructions']
        instruction = instruction.replace('<b>','')
        instruction = instruction.replace('</b>','')
        instruction = instruction.replace('</div>','')
        instruction = instruction.replace('<div style="font-size:0.9em">','. ')
        instruction = instruction.replace('&nbsp;',' ')
        print instruction + ". "

def main():
    '''
    Driver Code
        User prompted for a start and end address.
        Function calls returns route directions for the safest route assessed
    '''
    start = raw_input("Please enter the start address: ")
    dest = raw_input("Please enter the desination address: ")

    routes = get_possible_directions(start, dest)

    print "Your safest route:"
    print_route(prioritize_routes(routes)[0][0])

main()