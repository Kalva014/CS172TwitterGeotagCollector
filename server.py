import json
import configparser
# import time for its sleep method
from time import sleep

# import the datetime libraries datetime.now() method
from datetime import datetime

# use the Elasticsearch client's helpers class for _bulk API
from elasticsearch import Elasticsearch, helpers

from flask import Flask, request
from flask_cors import CORS

# define a function that will load a text file
def get_data_from_text_file(self):
    # the function will return a list of docs
    return [l.strip() for l in open(str(self), encoding="utf8", errors='ignore')]

# declare a client instance of the Python Elasticsearch library
config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

client = Elasticsearch(
    cloud_id=config['elasticsearch']['cloud_id'],
    basic_auth=(config['elasticsearch']['elastic_user'], config['elasticsearch']['elastic_pw'])
)

app = Flask(__name__)
CORS(app)

# call the function to get the string data containing docs
docs = get_data_from_text_file("Sample Data/sample0.txt")

# print the length of the documents in the string
#print ("String docs length:", len(docs))

# define an empty list for the Elasticsearch docs
doc_list = []

# use Python's enumerate() function to iterate over list of doc strings
for num, doc in enumerate(docs):

    # catch any JSON loads() errors
    try:
        # prevent JSONDecodeError resulting from Python uppercase boolean
        doc = doc.replace("True", "true")
        doc = doc.replace("False", "false")

        # convert the string to a dict object
        dict_doc = json.loads(doc)

        # add a new field to the Elasticsearch doc
        dict_doc["timestamp"] = datetime.now()

        # add a dict key called "_id" if you'd like to specify an ID for the doc
        dict_doc["_id"] = num

        # append the dict object to the list []
        doc_list += [dict_doc]

    except json.decoder.JSONDecodeError as err:
    # print the errors
        print ("ERROR for num:", num, "-- JSONDecodeError:", err, "for doc:", doc)

#print ("Dict docs length:", len(doc_list))

# attempt to index the dictionary entries using the helpers.bulk() method
try:
    print ("\nAttempting to index the list of docs using helpers.bulk()")

    # use the helpers library's Bulk API to index list of Elasticsearch docs
    resp = helpers.bulk(
    client,
    doc_list,
    index = "some_index"
    )

    # print the response returned by Elasticsearch
    print ("helpers.bulk() RESPONSE:", resp)
    print ("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))

except Exception as err:

# print any errors returned w
## Prerequisites while making the helpers.bulk() API call
    print("Elasticsearch helpers.bulk() ERROR:", err)
    quit()

# These are the endpoints
@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

@app.route("/getData", methods=['POST'])
def getData():
    print(request.json) # This is the input
    input = request.json['dataToFetch']
    print(input) 
    
    # get all of docs for the index
    # Result window is too large, from + size must be less than or equal to: [10000]
    query_all = {
        'size' : 10_000,
        'query': {
            "query_string" : {
                "query" : input
            }
        }
    }

    print ("\nSleeping for a few seconds to wait for indexing request to finish.")
    sleep(2)

    # pass the query_all dict to search() method
    resp = client.search(
        index = "some_index",
        body = query_all
    )

    print ("search() response:", json.dumps(resp.body, indent=4))

    # print the number of docs in index
    print ("Length of docs returned by search():", len(resp['hits']['hits']))
    
    return json.dumps(resp.body, indent=4)