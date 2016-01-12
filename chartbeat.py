import urllib, json, sys
from urllib2 import Request, urlopen, URLError
from time import sleep
from StringIO import StringIO
from csv import DictReader

# read the api-key from a text file
def getAPIkey():

    try:
        f = open('chartbeat_api_key.txt')
        key = json.load(f)['api-key']
        return key
    except Exception, e:
        print "Error loading API key from local file called 'chartbeat_api_key.txt'"
        print "\tThere should be a local file in this directory called chartbeat_api_key.txt "
        print "\tWhich has contents like this:"
        print """

        {
        "api-key": "123bda456c7f890e001"
        }

        """

        sys.exit("System error: " + str(e) );

# read in list of sites
def getSites():
    
    f = open('sites.txt')
    sites = json.load(f)
    return sites
        
def createQuery(metrics_set, site, params):
    
    if not params['start']: return "error"
    if not params['end']: return "error"
    if not params['metrics']: return "error"
    
    params['apikey'] = getAPIkey()
    params['host'] = site
    
    endpoint = "http://chartbeat.com/query/v2/submit/"
    
    requestUrl = endpoint + metrics_set + "/?" + urllib.urlencode(params)
    
    req = Request(requestUrl)
    try: 
        response = urlopen(req)
    except URLError as e:
        print e.reason
    query = json.loads(response.read())
    
    query_params = {
        "host": params['host'],
        "apikey": params['apikey'],
        "query_id": query["query_id"]
    }
    
    return query_params

def fetchQuery(query_params):
    
    query_endpoint = "http://chartbeat.com/query/v2/fetch/"
        
    queryUrl = query_endpoint + "?" + urllib.urlencode(query_params)
    
    q = Request(queryUrl)
    
    completed = False
    while not completed:
        try:
            response = urlopen(q)
            completed = True
            result = response.read()
        except URLError as e:
            if e.reason == "Internal Server Error":
                sleep(5)
                pass
            else:
                print e.reason
    
    return result

def processResults(results,metric,dim="none"):
    if dim == "none":
        return DictReader(StringIO(fetchQuery(results))).next()[metric]
    elif len(dim.split(',')) == 2:
        dim1, dim2 = dim.split(',')
        return dict((row[dim1] + row[dim2], row[metric]) for row in DictReader(StringIO(fetchQuery(results))))
    else:
        return dict((row[dim], row[metric]) for row in DictReader(StringIO(fetchQuery(results))))