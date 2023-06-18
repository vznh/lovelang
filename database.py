# attempt to connect python function to mongodb database and add/access items to the database

from pymongo import MongoClient
client = MongoClient('mongodb+srv://userhack:ZPO4BzbPYQvRFhf7@hackathoncluster.ljjbuhm.mongodb.net/')

db = client['sample_airbnb']
collection = db['listingsAndReviews']

# # here, we will try to add data to the database specified above
# data = {
#     'key1' : 'value1',
#     'key2' : 'value2',
# }
# result = collection.insert_one(data) # adds one key:value pair to the database as one index
# if result.acknowledged:
#     print('Data was added successfully to the database')
# else:
#     print('Data could not be added to the database')

# now, we will try to request data from the mongodb and have it be returned to us
filter_criteria = { # matches conditions you need to retrieve data
    'bedrooms' : {'$gt' : 2}, # finds airbnbs that have at least 2 bedrooms
}

results = collection.find(filter_criteria)

for document in results:
    listing = document['listing_url']
    bedrooms = document['bedrooms']
    print(f'Listing: {listing}, # of bedrooms: {bedrooms}')



client.close() # closes database connection when you're done