# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 09:48:00 2022

@author: 932151706
"""
import pandas as pd 
import datetime
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

def create_url(keyword, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
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
        author_id = tweet['author_id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']#['place_id']
        else:
            geo = " "

        # 4. Tweet ID
        tweet_id = tweet['id']

        # 5. Language
        lang = tweet['lang']
        
        if ('in_reply_to_user_id' in tweet):
            in_reply_to_user_id = tweet['in_reply_to_user_id']
        else:
            in_reply_to_user_id = " "
        
        

        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']
        
        #test
        conversation_id= tweet['conversation_id']
        
      


        # 7. source
        #source = tweet['source']

        # 8. Tweet text
        text = tweet['text']
        
        # Assemble all data in a list
        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count,conversation_id,in_reply_to_user_id,text]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 
    
# append_to_csv(json_response, "data.csv") 

"---------------------------------------------------------------------------------------------"




colnames=['created_at', 'ID', 'Token']
df = pd.read_csv('data.csv',sep=',',names=colnames,low_memory=False)
df.drop([0], axis=0, inplace=True)
df.drop([2001], axis=0, inplace=True)
df.drop([808964], axis=0, inplace=True)
df.drop([1179936], axis=0, inplace=True)
df.drop([3587829], axis=0, inplace=True)
df.drop([3738829], axis=0, inplace=True)
df=df.reset_index(drop=True)
df['created_at']=pd.to_datetime(df['created_at'])
df['ID']=pd.to_numeric(df['ID'])
df['Token']=df['Token'].astype(str)
#df.info()

#df['created_at'] = pd.to_datetime(df.created_at, format='%Y-%m-%d %H:%M:%S') 


#groupedlist=[]
csvFile = open("Tweets14dMcdo.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save, in this example, we only want save these columns in our dataset
csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','conversation_id','in_reply_to_user_id','tweet'])
csvFile.close()

df['created_at']=pd.to_datetime(df['created_at'], format='%Y-%m-%d %H:%M:%S')
#print(df["created_at"])
groupeddf=df.groupby([df["created_at"].dt.year,
                           df["created_at"].dt.month,
                           df["created_at"].dt.day])

for name,group in groupeddf:
    
    #strdate=str(name[0])+"-"+str(name[1])+"-"+str(name[2])
    #print(startdate)
    start_date = datetime.datetime(name[0],name[1], name[2])
    #print(start_date)
    end_date = start_date + datetime.timedelta(days=14)
    
    #print(end_date)
    keyword =""
    for i in group["ID"]:
               
        if len(keyword) + 5 + len(str(i)) < 1024:
            keyword += "from:"+str(i) + " OR "
        else:
            erreur = True
            cpt=0
            while erreur:
                try:
                    # Supprime OR
                    keyword = keyword[0:len(keyword)-4]
                    # Send requete
                    #Inputs for tweets
                    bearer_token = auth()
                    headers = create_headers(bearer_token)
        
                    lang='en'
                    max_results = 500
                    
        
                        
                    start_list= [start_date.isoformat("T")+"Z"]
                    end_list=[end_date.isoformat("T")+"Z"]
        
                    #Total number of tweets
                    #Total number of tweets we collected from the loop
                    total_tweets = 0
                    
                    # Create file
                    
                    
                    for i in range(0,len(start_list)):
                    
                        # Inputs
                        count = 0 # Counting tweets per time period
                        max_count = 200000000000000000 # Max tweets per time period
                        flag = True
                        next_token = None
                        
                        # Check if flag is true
                        while flag:
                            # Check if max_count reached
                            if count >= max_count:
                                break
                            print("-------------------")
                            print("Token: ", next_token)
                            url = create_url(keyword, start_list[i],end_list[i], max_results)
                            json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
                            result_count = json_response['meta']['result_count']
                    
                            if 'next_token' in json_response['meta']:
                                # Save the token to use for next call
                                next_token = json_response['meta']['next_token']
                                print("Next Token: ", next_token)
                                if result_count is not None and result_count > 0 and next_token is not None:
                                    print("Start Date: ", start_list[i])
                                    append_to_csv(json_response, "Tweets14dMcdo.csv")
                                    count += result_count
                                    total_tweets += result_count
                                    print("Total # of Tweets added: ", total_tweets)
                                    print("-------------------")
                                    time.sleep(1)                
                            # If no next token exists
                            else:
                                if result_count is not None and result_count > 0:
                                    print("-------------------")
                                    print("Start Date: ", start_list[i])
                                    append_to_csv(json_response, "test.csv")
                                    count += result_count
                                    total_tweets += result_count
                                    print("Total # of Tweets added: ", total_tweets)
                                    print("-------------------")
                                    time.sleep(1)
                                
                                #Since this is the final request, turn flag to false to move to the next time period.
                                flag = False
                                next_token = None
                            time.sleep(2.1)
                    print("Total number of results: ", total_tweets)
                    # Reinitialise 
                    keyword = ""
                    erreur = False
                
                except Exception as inst:
                    print(inst)
                    if cpt <=10:
                        erreur = True
                        print("Erreur. 30 sec d'attente")
                        cpt+=1
                    else:
                        erreur = False
                        print("Requete annulée")
                        cpt=0
                    time.sleep(30)