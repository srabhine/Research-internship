'''

Gathering the data pf the day of the vent when the negatiuve eWOM was posted

'''
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


os.environ['TOKEN'] = '#add your tocken'

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
    

#Inputs for tweets
bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "from: the person youy want too extract the data of the negative eWOM"
start_list=["2007-04-30T00:00:00.000Z"]
end_list=["2022-05-28T01:45:38.000Z"]
lang='en'
max_results = 500



#Total number of tweets we collected from the loop
total_tweets = 0

# Create file
csvFile = open("SSTdelta.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save, in this example, we only want save these columns in our dataset
csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','conversation_id','in_reply_to_user_id','tweet'])
csvFile.close()

for i in range(0,len(start_list)):

    # Inputs
    count = 0 # Counting tweets per time period
    max_count = 2000000 # Max tweets per time period
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
                append_to_csv(json_response, "SSTdelta.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(5)                
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
                time.sleep(5)
            
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None
        time.sleep(5)
print("Total number of results: ", total_tweets)
df = pd.read_csv('SST.csv')


"----------------------------------------------------------------------------"

#transform the date in datetime format 
df['created_at'] = pd.to_datetime(df.created_at, format='%Y-%m-%d %H:%M:%S')


#find the user who trigged the negative eWOM with his ID
_id = ""
user = api.get_user(user_id=_id)

'''
#get his screen_name
'''
user.screen_name
'''
#gathering the tweet from the user.screen_name from the creation of the account until the tweets before the Newom
'''
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


os.environ['TOKEN'] = ''

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
    

#Inputs for tweets
bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "from:username"
start_list=["tao"]
end_list=["(t-1)"]
lang='en'
max_results = 500



#Total number of tweets we collected from the loop
total_tweets = 0

# Create file
csvFile = open("SSTdelta.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save, in this example, we only want save these columns in our dataset
csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','conversation_id','in_reply_to_user_id','tweet'])
csvFile.close()

for i in range(0,len(start_list)):

    # Inputs
    count = 0 # Counting tweets per time period
    max_count = 2000000 # Max tweets per time period
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
                append_to_csv(json_response, "SSTdelta.csv")
                count += result_count
                total_tweets += result_count
                print("Total # of Tweets added: ", total_tweets)
                print("-------------------")
                time.sleep(5)                
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
                time.sleep(5)
            
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None
        time.sleep(5)
print("Total number of results: ", total_tweets)
df = pd.read_csv('SSTTweetsNewom.csv')

"--------------------------------------------------------------------------------"

"""

Create a Dataframe only with the RT to gather plater the given RT

"""

dfRT=pd.DataFrame(df)
from tqdm import tqdm
for i in tqdm(range (len(dfRT['tweet']))):
    if (not (dfRT['tweet'][i][0]=='R') or not(dfRT['tweet'][i][1]=='T') or not(dfRT['tweet'][i][2]==' ') or not(dfRT['tweet'][i][3]=="@")):
        dfRT.drop(i, axis=0, inplace=True)
        
dfRT = dfRT.reset_index(drop=True)
dfRT.to_csv('SSTNewomRT.csv')


"------------------------------------------------------------------------------------"


"""
Gathering the given retweets

"""


import tweepy
import time
import pandas as pd
 
# assign the values accordingly
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
 
# set access to user's access key and access secret
auth.set_access_token(access_token, access_token_secret)
 
# calling the api
api = tweepy.API(auth,wait_on_rate_limit=True)

given_RT=[]


#récupération des given RT 
for i in range(len(dfRT)):
    _id=dfRT['id'][i]
    erreur=True
    cpt=0
    while erreur:
        try:
            user = api.get_status(_id)
            if len(user.entities['user_mentions'])!=0:

                source_screen_name=(user.entities['user_mentions'][0]['screen_name'])

                target_screen_name = "@Brand community"

                # getting the friendship details
                friendship = api.get_friendship(source_screen_name = source_screen_name, target_screen_name = target_screen_name)
                #print("Is " + friendship[0].screen_name + " following " + friendship[1].screen_name, end = "? : ")
                if friendship[0].following == True:
                    given_RT.append(source_screen_name)
                    
            erreur=False

       
        except Exception as inst:
            print(inst)
            if cpt>10:
                erreur=False
                cpt=0
            else:
                erreur=True
                cpt+=1
            time.sleep(30)
            
    given_RT = list(set(given_RT))
        
    
    
    
    
dfGivenRT = pd.DataFrame(given_RT, columns=['Username'])
dfGivenRT.to_csv('dfGivenRT.csv')



"----------------------------------------------------------------------------------"


"""

Gathering the receiving Likes & the receiving Retweets

"""

import tweepy
import time
import pandas as pd
 
# assign the values accordingly
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
 
# set access to user's access key and access secret
auth.set_access_token(access_token, access_token_secret)
 
# calling the api
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token='')

    
retweets_list=[]
like_list=[]
user_listlike=[]
user_listRT=[]



for i in range(len(df)):
    #get received retweets
    for user in tweepy.Paginator(client.get_retweeters,id=int(df['id'][i]), max_results=100).flatten(limit=100): 
        retweets_list.append(user.username)
    time.sleep(20)
    #get received likes
    for user in tweepy.Paginator(client.get_liking_users,id=int(df['id'][i]), max_results=100).flatten(limit=100):
        like_list.append(user.username)
    time.sleep(20)

        
    

        

retweets_list = list(set(retweets_list))
like_list=list(set(like_list))
dfRT = pd.DataFrame(retweets_list, columns=['Username'])
dfL= pd.DataFrame(like_list, columns=['Username'])
#df.to_csv('C:/Users/srabh/Desktop/listRTSST.csv')
        
#print(retweets_list)

#capturer les replies
 
# screen name of the account 1
for i in retweets_list:
    
    source_screen_name = i

 
    # screen name of the account 2
    target_screen_name = "@Brandcommunity"

    # getting the friendship details
    friendship = api.get_friendship(source_screen_name = source_screen_name, target_screen_name = target_screen_name)
    #print("Is " + friendship[0].screen_name + " following " + friendship[1].screen_name, end = "? : ")
    if friendship[0].following == True:
        user_listRT.append(i)
        

for i in like_list:
    #print(i)
    
    source_screen_name = i

 
    # screen name of the account 2
    target_screen_name = "@Brandcommunity"

    # getting the friendship details
    friendship = api.get_friendship(source_screen_name = source_screen_name, target_screen_name = target_screen_name)
    #print("Is " + friendship[0].screen_name + " following " + friendship[1].screen_name, end = "? : ")
    if friendship[0].following == True:
        user_listlike.append(i)

dfuserRT=pd.DataFrame(user_listRT,columns=['Username'])        
dfuserlike=pd.DataFrame(user_listlike,columns=['Username'])



"--------------------------------------------------------------------------------------------------"


"""
Gathering the received Quotes

"""


import tweepy
import time
import pandas as pd
 
# assign the values accordingly
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
 
# set access to user's access key and access secret
auth.set_access_token(access_token, access_token_secret)
 
# calling the api
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token='',wait_on_rate_limit=True)
    
quote_list=[]

cpt=0
for i in tqdm(range(len(df))):
    #get received Quotes
    try:
        for tweet in tweepy.Paginator(client.get_quote_tweets,id=int(df['id'][i]),expansions=['author_id'],max_results=100):
            if (tweet.data!= None):
                users= {u["username"]: u for u in tweet.includes['users']}
                quote_list+=users
                #print(tweet.includes['users'][0]['username'])
    except Exception as inst:
        if(cpt<10):
            cpt+=1
            i=(i-1)
        else:
            cpt=0
            print("passage à la suite")
        print(inst)
        time.sleep(10)


        
    

        

quote_list = list(set(quote_list))
#dfRT = pd.DataFrame(retweets_list, columns=['Username'])
#dfL= pd.DataFrame(like_list, columns=['Username'])
#df.to_csv('C:/Users/srabh/Desktop/listRTSST.csv')
        
#print(retweets_list)

#capturer les replies
 
# screen name of the account 1
for i in quote_list:
    
    source_screen_name = i

 
    # screen name of the account 2
    target_screen_name = "@Brandcommunity"
    
    try:

        # getting the friendship details
        friendship = api.get_friendship(source_screen_name = source_screen_name, target_screen_name = target_screen_name)
        #print("Is " + friendship[0].screen_name + " following " + friendship[1].screen_name, end = "? : ")
        if friendship[0].following == True:
            quote_list.append(i)
    except Exception as inst:
        print(inst)

dfQuote=pd.DataFrame(quote_list,columns=['Username'])
dfQuote.to_csv('dfQuote.csv')



"--------------------------------------------------------------------------------------"


'''
Gathering the Given reply
'''

import tweepy
import time
import pandas as pd
 
# assign the values accordingly
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
 
# set access to user's access key and access secret
auth.set_access_token(access_token, access_token_secret)
 
# calling the api
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token='',wait_on_rate_limit=True)

    
users_list=[]

for i in range(len(df)):
    if df['conversation_id'][i]!=df['id'][i]:
        users_list.append(df['in_reply_to_user_id'][i])
        
               

users_list = list(set(users_list))

username=[]

for i in (users_list):
    response=client.get_user(id=i)
    if response.data!= None:
        username.append(response.data['username'])
        
#capturer les replies
users_reply=[]
# screen name of the account 1
for i in username:
    
    source_screen_name = i

 
    # screen name of the account 2
    target_sreen_name = "@Brandcommunity"
    

    # getting the friendship details
    friendship = api.get_friendship(source_screen_name = source_screen_name, target_screen_name = target_screen_name)
    print("Is " + friendship[0].screen_name + " following " + friendship[1].screen_name, end = "? : ")
    if friendship[0].following == False:
        print("No")
    else:
        print("Yes")
        users_reply.append(i)

dfREPLY=pd.DataFrame(users_reply,columns=['Username'])        






