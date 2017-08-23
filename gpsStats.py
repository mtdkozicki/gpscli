#!/bin/env python

from argparse import ArgumentParser
from xml.dom import minidom
import csv
import sys

fields = ['distance meters', 'distance miles', 'time seconds', 'time minutes']
pwx_fields_map =  {'distance meters': 'dist',
        'distance miles': 'gps1_dist',
        'time seconds':    'timeoffset',
        'time minutes':    None
}
def log_it(message, level="INFO"):
    if level == "ERROR" or level == 'CRITIVAL':
        sys.stderr.write(message)
    else:
        sys.stdout.write(message)

def parse_pwx_file(filename):
    try: 
        with open(filename, 'r') as f:
            data = f.read()
    except IOError as e:
        log_it("Unable to open {}".format(filename), "ERROR")
        raise e
    return minidom.parseString(data)

if __name__ == "__main__":
    flags = ArgumentParser()
    flags.add_argument('-f', '--filename',
                         help='file that contains gps data')
    flags.add_argument('-t', '--filetype', choices=['pwx'], default='pwx',
                         help='file type, only pwx supported now')
    flags.add_argument('-s', '--savefile',
                         help='file name to save .csv data')

    options = flags.parse_args()
    
    if not options.filename:
        sys.stderr.write("Please provide a file to parse")
        sys.exit(1)
    
    xml_data = parse_pwx_file(options.filename)        
    sampling_data_list = xml_data.getElementsByTagName('sample')
    if options.filetype == 'pwx':
        data_map = pwx_fields_map    
    data_list = []
    for i, sample in enumerate(sampling_data_list):
        data_dict = {}
        for element in fields:
            try:
                value = sampling_data_list[i].getElementsByTagName(data_map[element])[0].firstChild.nodeValue
            except IndexError:
                value = None
            data_dict.update({element: value})
        data_list.append(data_dict)

    if options.savefile:
        with open(options.savefile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for element in data_list:
                writer.writerow(element)
    
    total_dist_meters = data_list[-1]['distance meters']
    total_dist_miles = data_list[-1]['distance miles']
    total_time_secs = data_list[-1]['time seconds']
    total_mins = int(float(total_time_secs)/60)
    secs = int(float(total_time_secs) - (total_mins * 60))

    log_it("Total dist(meters): {}\n".format(total_dist_meters))
    log_it("Total dist(miles): {}\n".format(total_dist_miles))
    log_it("Total time(s): {}\n".format(total_time_secs))
    log_it("Total time(min): {}:{}\n".format(total_mins, secs))
