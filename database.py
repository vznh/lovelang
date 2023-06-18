# attempt to connect python function to mongodb database and add/access items to the database

'''to clean up the code, i'm planning to turn the adding feature and accessing feature into 2 (or 3?) separate functions.
i want to apply what i tested to our app since right now i'm just testing with a sample database
also pymongo isn't importing for some reason Lol i've uninstalled n reinstalled but im not sure what's wrong'''

import pymongo
from pymongo import MongoClient
client = MongoClient('mongodb+srv://userhack:ZPO4BzbPYQvRFhf7@hackathoncluster.ljjbuhm.mongodb.net/')

db = client['sample_airbnb']
collection = db['listingsAndReviews']

def addToDB(**kwargs): # not sure if this will work, but the function will take the user's input of a key value pair and add it to the database collection
    result = collection.insert_one(kwargs)
    if result.acknowledged:
        print('Data was added successfully to the database')
    else:
        print('Data could not be added to the database')

# here, we will try to add data to the database specified above
# data = {
#     'key1' : 'value1',
#     'key2' : 'value2',
# }
# result = collection.insert_one(data) # adds one key:value pair to the database as one index
# if result.acknowledged:
#     print('Data was added successfully to the database')
# else:
#     print('Data could not be added to the database')


def accessDB(**kwargs): # this function is meant to find the database key value pair that matches the user's input and prints it
    results = collection.find(kwargs)
    if results == -1:
        print('Sorry, the information you provided is not stored in the database')
    else:
        print(results)

'''actually might add another function when the user wants to filter information and list specific things from the database but idk how that'll work'''


# # now, we will try to request data from the mongodb and have it be returned to us
# filter_criteria = { # matches conditions you need to retrieve data
#     'bedrooms' : {'$gt' : 7}, # finds airbnbs that have at least 7 bedrooms
# }
#
# results = collection.find(filter_criteria)
#
# for document in results:
#     listing = document['listing_url']
#     bedrooms = document['bedrooms']
#     print(f'Listing: {listing}, # of bedrooms: {bedrooms}') # lists all the airbnbs that have at least 7 bedrooms with their respective urls

client.close() # closes database connection when you're done