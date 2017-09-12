"""
Annotate block graph with voter registration db.

The goal of this module is to take an existing networkx block graph and
annotate it with voter registration data. Using a voter registration database,
containing addresses and precincts, map the address to a spatial (lat/long)
coordinate, find the block that contains that coordinate, and add the record
to the block.
"""
import csv
import random
from collections import defaultdict
import pickle
import os

import requests
from shapely.geometry import Point

def geocode(address_string):
    """Takes an address string and returns a Shapely Point object."""
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json",
                     params={"address": address_string,
                             "key": "AIzaSyDV3WKAIL3ywBs7yMafnZiDi4qV3nAS4tI"})
    output = r.json()['results']

    coords = output[0]['geometry']['location']
    return Point(coords['lng'], coords['lat'])

def find_block(graph, point):
    """Takes a point and returns the vertex of the block that contains that point."""
    # start at a random node (node = name of node, data = associated data)
    node, data = random.choice(graph.nodes(data=True))
    
    while not data['block'].contains(point):
        # among all of the neighbors of node, find the one whose distance is minimal
        node = min(graph.neighbors(node), key=lambda n: graph.node[n]['block'].distance(point))
        data = graph.node[node]

    return node

#pylint: disable=R0914
def build_block_map(graph, address_dir, address_file):
    """Build a map of records to blocks they're in (and vice-versa)."""
    record_to_block = {}
    block_to_record = defaultdict(list)
    with open(os.path.join(address_dir, address_file), 'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        next(tsvin, None) # skip header

        for record in tsvin:
            if len(record) is 0:
                continue

            [state_voter_id, _, _, _, _, _, _, _, _, street_num, street_frac, street_name,
             street_type, unit_type, street_pre_direction, street_post_direction,
             unit_num, city, state, zip_code, _, _, _, _, _, _, _, _, _, _, _, _,
             _, _, _, _, status_code, _] = record
            # (state_voter_id, county_voter_id, title, first_name, middle_name, last_name,
            #     name_suffix, birthdate, gender, street_num, street_frac, street_name,
            #     street_type, unit_type, street_pre_direction, street_post_direction,
            #     unit_num, city, state, zip_code, county_code, precinct_code, precinct_part,
            #     legislative_district, congressional_district, mail_1, mail_2, mail_3, mail_4,
            #     mail_city, mail_zip, mail_state, mail_country, registration_date, absentee_type,
            #     last_voted, status_code, d_flag) = record
            if not (status_code == "A" or status_code == "P"):
                continue
            point = geocode(" ".join([street_num, street_pre_direction, street_frac, street_name,
                                      street_type, street_post_direction, unit_type, unit_num,
                                      city, state, zip_code]))
            print(point)
            block = find_block(graph, point)
            record_to_block[state_voter_id] = block
            block_to_record[block].append(state_voter_id)

    pickle.dump(record_to_block, open(os.path.join(address_dir, "record_to_block.pickle")))
    pickle.dump(block_to_record, open(os.path.join(address_dir, "block_to_record.pickle")))

