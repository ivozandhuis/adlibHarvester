#! /usr/bin/env python3

import lxml.etree as etree
import urllib.request
import argparse
import sys
import datetime

# initiate the parser
parser = argparse.ArgumentParser()  
parser.add_argument("-v", "--version", help="show program version", action="store_true")
parser.add_argument("-t", "--test", help="test: download first 200 records", action="store_true")
parser.add_argument("-d", "--date", help="date of last harvest (default: '1900-01-01')")
parser.add_argument("-ep", "--endpoint", help="Adlib API endpoint")
parser.add_argument("-db", "--database", help="name of database (default 'collect')")
parser.add_argument("-p", "--path", help="path to directory storing the harvest (default: 'output/')")
parser.add_argument("-s", "--search", help="search value (default: 'all')")
parser.add_argument("-xmltype", "--xmltype", help="search value (default: 'grouped')")


# read arguments from the command line
args = parser.parse_args()

if args.version:  
    print("adlibHarvester version 0.96")
    print("Stores xml-file for every priref in selection SEARCH from DATABASE on ENDPOINT in directory PATH, modified after DATE.")

if args.endpoint:  
    endpoint = args.endpoint
else:
    print("No Adlib API endpoint provided. Use -ep")
    sys.exit()

if args.database:  
    database = args.database
else:
    database = "collect"

if args.date:  
    date = datetime.datetime.strptime(args.date, '%Y-%m-%d')
else:
    date = datetime.datetime.strptime('1900-01-01', '%Y-%m-%d')

if args.path:  
    path = args.path
else:
    path = "output/"

if args.search:  
    search = args.search
else:
    search = "all"

if args.xmltype:  
    xmltype = args.xmltype
else:
    xmltype = "grouped"

limit = 100

## initialize variables for loop
page = 0
numberFound = 1000000

# iterate through resultpages
while (numberFound > (page * limit)):
    startfrom = page * limit
    # read page of records
    requestUrl = endpoint + \
                    "?database=" + database + \
                    "&search=" + search + \
                    "&XMLtype=" + xmltype + \
                    "&limit=" + str(limit) + \
                    "&startfrom=" + str(startfrom)

    print(requestUrl)
    result = urllib.request.urlopen(requestUrl)
    adlibXML = result.read()

    # parse adlibXML
    dom = etree.fromstring(adlibXML)

    # get detailed information with priref
    for record in dom.findall('.//record'):
        priref = record.get('priref')
        modification = record.get('modification')
        mod = datetime.datetime.strptime(modification, '%Y-%m-%dT%H:%M:%S')
        if mod > date:
            requestUrl = endpoint + \
               "?database=" + database + \
               "&search=priref=" + priref + \
               "&XMLtype=" + xmltype

            print(requestUrl)
            result = urllib.request.urlopen(requestUrl)
            adlibXML = result.read()

            # parse adlibXML
            dom2 = etree.fromstring(adlibXML)
            adlibXML = etree.tostring(dom2, pretty_print=True)

            # write adlibXML-file
            filename = path + database + "priref" + str(priref) + ".adlib.xml"
            f = open(filename,"wb")
            f.write(adlibXML)
            f.close()

    # make loop end
    ## read numberFound
    hits = dom.find(".//hits")
    numberFound = int(hits.text)
    if args.test:
        numberFound = 200 # maximum for testing

    page = page + 1
    print(str(page * limit) + "-" + str(page * limit + limit) + " of " + str(numberFound))
