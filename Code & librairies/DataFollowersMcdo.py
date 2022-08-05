# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:25:03 2022

@author: 932151706
"""

# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
#To add wait time between requests
import time


os.environ['TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAAJm%2BcgEAAAAAobDvrEQCoB9DjFHw9ZPzJk5j%2BDk%3DbaZ9pxwn85ljTFagUOYZvyYpTFj63IVshXq3qqlNgIifwEJAr8'

def auth(): 
    return os.getenv('TOKEN')


def create_headers(bearer_token): 
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, max_results = 10):
    
    #search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from
    search_url="https://api.twitter.com/2/users/"+keyword+"/followers"
    #change params based on the endpoint you are using
    query_params = {   
                    #'start_time': start_date,
                    #'end_time': end_date,
                    'max_results': max_results,
                    #'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    #'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    #'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'pagination_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['pagination_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def append_to_csv(json_response, fileName):

    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        _id = tweet['id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        #if ('geo' in tweet):   
            #geo = tweet['geo']#['place_id']
       # else:
            #geo = " "

        # 4. Tweet ID
        #tweet_id = tweet['id']

        # 5. Language
        #lang = tweet['lang']
        
        #if ('in_reply_to_user_id' in tweet):
            #in_reply_to_user_id = tweet['in_reply_to_user_id']
       # else:
           # in_reply_to_user_id = " "
        
        

        # 6. Tweet metrics
        #retweet_count = tweet['public_metrics']['retweet_count']
        #reply_count = tweet['public_metrics']['reply_count']
        #like_count = tweet['public_metrics']['like_count']
        #quote_count = tweet['public_metrics']['quote_count']
        
        #test
        #conversation_id= tweet['conversation_id']
        
      


        # 7. source
        #source = tweet['source']

        # 8. Tweet text
        #text = tweet['text']
        
        next_token = json_response['meta']['next_token']
        
        # Assemble all data in a list
        res = [created_at,_id,next_token]
        
        
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 
    
# append_to_csv(json_response, "data.csv") 
    

#Inputs for tweets
bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "71026122"
#start_list=["2009-01-01T00:00:00.000Z"]
#end_list=["2012-01-21T00:00:00.000Z"]
#lang='en'
max_results = 1000



#Total number of tweets we collected from the loop
total_tweets = 0

# Create file
csvFile = open("data.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save, in this example, we only want save these columns in our dataset
csvWriter.writerow(['created_at','id'])
csvFile.close()

# Inputs
count = 0 # Counting tweets per time period
max_count = 4600000 # Max tweets per time period
flag = True
next_token = 'FDQLS8TH981H8ZZZ' #NONE

# Check if flag is true
while flag:
    # Check if max_count reached
    if count >= max_count:
        break
    print("-------------------")
    print("Token: ", next_token)
    url = create_url(keyword, max_results)
    json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        # Save the token to use for next call
        next_token = json_response['meta']['next_token']
        print("Next Token: ", next_token)
        if result_count is not None and result_count > 0 and next_token is not None:
            append_to_csv(json_response, "data.csv")
            count += result_count
            total_tweets += result_count
            print("Total # of Tweets added: ", total_tweets)
            print("-------------------")
            time.sleep(5)                
    # If no next token exists
    else:
        if result_count is not None and result_count > 0:
            print("-------------------")
            append_to_csv(json_response, "test.csv")
            count += result_count
            total_tweets += result_count
            print("Total # of Tweets added: ", total_tweets)
            print("-------------------")
            time.sleep(5)
        
        #Since this is the final request, turn flag to false to move to the next time period.
        flag = False
        next_token = None
    time.sleep(60)
print("Total number of results: ", total_tweets)
df = pd.read_csv('data.csv')

print(df) 