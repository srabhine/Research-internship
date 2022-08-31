'''

Gathering the followers of the brand community 

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
keyword = "ID of the brand community"
#start_list=["2009-01-01T00:00:00.000Z"]
#end_list=["2012-01-21T00:00:00.000Z"]
#lang='en'
max_results = 1000



#Total number of tweets we collected from the loop
total_tweets = 0

# Create file
csvFile = open("Brandcommunityfollowers.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile)

#Create headers for the data you want to save, in this example, we only want save these columns in our dataset
csvWriter.writerow(['created_at','id'])
csvFile.close()

# Inputs
count = 0 # Counting tweets per time period
max_count = 100000 # Max tweets per time period
flag = True
next_token = None

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
            append_to_csv(json_response, "Uberfollowers.csv")
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
df = pd.read_csv('Brandcommunityfollowers.csv')


"-----------------------------------------------------------------------------"

'''
Gathering the tweets of the first 14 days since the creatio of the account of every followers
'''


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

"---------------------------------------------------------------------------------------------"




colnames=['created_at', 'ID', 'Token']
df = pd.read_csv('Brandcommunityfollowers.csv',sep=',',names=colnames,low_memory=False)
print(df)
df.drop([0], axis=0, inplace=True)
#df.drop([2001], axis=0, inplace=True)
#df.drop([808964], axis=0, inplace=True)
#df.drop([1179936], axis=0, inplace=True)
#df.drop([3587829], axis=0, inplace=True)
#df.drop([3738829], axis=0, inplace=True)
#df=df.reset_index(drop=True)
df['created_at']=pd.to_datetime(df['created_at'])
df['ID']=pd.to_numeric(df['ID'])
df['Token']=df['Token'].astype(str)
#df.info()

#df['created_at'] = pd.to_datetime(df.created_at, format='%Y-%m-%d %H:%M:%S') 


#groupedlist=[]
csvFile = open("Tweets14dBrandcommmunity.csv", "a", newline="", encoding='utf-8')
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
                                    append_to_csv(json_response, "Tweets14dBrandcommmunity.csv")
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
                    
                    
                    
"------------------------------------------------------------------------------------------"

'''

Removing all the RT on the dataframe to keep only the tweets

'''

import pandas as pd
from tqdm import tqdm
df=pd.read_csv('Tweets14dBrandcommmunity.csv')

for i in tqdm(range(len(df))):
    try:
        if len(df['tweet'][i])<=3:
            df.drop(i,axis=0,inplace=True)
        elif (df['tweet'][i][0]=='R') or (df['tweet'][i][1]=='T') or (df['tweet'][i][2]==' ') or (df['tweet'][i][3]=="@"):
            df.drop(i, axis=0, inplace=True)
    except Exception as inst:
        print(inst)
        df.drop(i,axis=0, inplace=True)
        
        
df = df.reset_index(drop=True)
df.to_csv('Tweets14dBrandcommunity2.csv')



#do the same for the user I that triggered the negative eWOM (download his first 2 weeks tweets)


"-------------------------------------------------------------------------------------------------------------------------"


"""

Second part implement the LSM algorithm

"""


#Create a dictionnaru of 9 different categories ( (1)auxiliary verbs , (2)articles, (3)common adversb, (4)personal pronouns, (5)impersonal pronous,(6)prepositions,(7)negations,(8)conjuctions,(9)quantifiers)


fwords = dict(
    auxiliary_verbs=['am',
                    'had',
                    'could',
                     'is',
                    'did',
                    'does',
                    'are',
                    'shall',
                    'do',
                    'was',
                    'will',
                    'need',
                    'were',
                    'should',
                    'ought to',
                    'being',
                    'would',
                    'dare',
                    'been',
                    'may',
                    'going to',
                    'be',
                    'might',
                    "be able to",
                    "has",
                    "must",
                    "have to",
                    "have",
                    "can",
                    "had better"],
    articles=['a',
              'an',
              'the'],
    
    common_adverbs=
        ['accidentally',
         'afterwards',
         'almost',
         'always',
         'angrily',
         'annually',
         'anxiously',
         'awkwardly',
         'badly',
         'blindly',
         'boastfully',
         'boldly',
         'bravely',
         'briefly',
         'brightly',
         'crossly',
         'cruelly',
         'daily',
         'defiantly',
         'deliberately',
         'doubtfully',
         'easily',
         'elegantly',
         'enormously',
         'enthusiastically',
         'equally',
         'even',
         'eventually',
         'exactly',
         'faithfully',
         'gladly',
         'gracefully',
         'greedily',
         'happily',
         'hastily',
         'honestly',
         'hourly',
         'hungrily',
         'innocently',
         'inquisitively',
         'irritably',
         'joyously',
         'justly',
         'kindly',
         'lazily',
         'nearly',
         'neatly',
         'nervously',
         'never',
         'noisily',
         'not',
         'obediently',
         'obnoxiously',
         'often',
         'only',
         'painfully',
         'perfectly',
         'politely',
         'poorly',
         'powerfully',
         'reluctantly',
         'repeatedly',
         'rightfully',
         'roughly',
         'rudely',
         'sadly',
         'safely',
         'seldom',
        'selfishly',
        'seriously',
        'shakily',
        'sharply',
        'shrilly',
        'shyly',
        'silently',
        'sternly',
        'successfully',
        'suddenly',
        'suspiciously',
        'swiftly',
        'tenderly',
        'tensely',
        'thoughtfully',
        'tightly',
        'tomorrow',
        'too',
        'truthfully',
        'unexpectedly',
        'very',
        'victoriously'],
    
    personal_pronouns=["i",
                       "you",
                       "he",
                       "she",
                       "it",
                       "we",
                       "they",
                       "them",
                       "us", 
                       "him", 
                       "her", 
                       "his", 
                       "hers", 
                       "its", 
                       "theirs", 
                       "our", 
                       "your"],
    
    impersonal_pronouns=["one",
                        "they",
                        "it",
                        "you"],
    
    prepositions=['about',
                  'above',
                  'across',
                  'after',
                  'ago',
                  'at',
                  'below',
                  'by',
                  'down',
                  'during',
                  'for',
                  'from',
                  'in',
                  'into',
                  'off',
                  'on',
                  'over',
                  'past',
                  'since',
                  'through',
                  'to',
                  'under',
                  'until',
                  'up',
                  'with'],
    
    negations=['doesn’t',
               'isn’t',
               'wasn’t',
               'shouldn’t',
               'wouldn’t',
               'couldn’t',
               'won’t',
               'can’t',
               'don’t',
               'hardly',
               'scarcely',
               'barely',
               'no',
               'not',
               'none',
               'no one',
               'nobody',
               'nothing',
               'neither',
               'nowhere',
               'never'],
    conjunctions=['after',
                  'after all',
                  'although',
                  'and',
                  'as', 
                  'as if',
                  "as long as",
                  "as much as",
                  "as soon as",
                  "as though",
                  "barely when",
                  "because","Before",
                  "but",
                  "by the time",
                  "bonsequently",
                  "bum",
                  "either or",
                  "even",
                  "even if",
                  "even though",
                  "ever since",
                  "every time",
                  "finally",
                  "for",
                  "furthermore",
                  "hardly when",
                  "hence",
                  "how",
                  "however",
                  "if",
                  'if … then',
                  'if only',
                  'if then',
                  'if when',
                  'in addition',
                  'in order that',
                  'inasmuch',
                  'incidentally',
                  'just as',
                  'lest',
                  'likewise',
                  'meanwhile',
                  'nor',
                  'now',
                  'now since',
                  'now that',
                  'now when',
                  'once',
                  'only if',
                  'or',
                  'or else',
                  'otherwise',
                  'provided',
                  'provided that',
                  'rather than',
                  'scarcely when',
                  'since'],
    
    quantifiers=['much',
                 'a bit',
                 'little',
                 'great deal of',
                 'large quantity of',
                 'a little',
                 'very little',
                 'a large amount of',
                 'a majority of',
                 'a great number of',
                 'several',
                 'many',
                 'a large number of',
                 'a number of',
                 'few',
                 'a few',
                 'very few',
                 'all',
                 'enough',
                 'none',
                 'no',
                 'some',
                 'more',
                 'most',
                 'lots of',
                 'less',
                 'least',
                 'any',
                 'not any',
                 'plenty of']
)
 


'''

FWC function for the user that triggred the Newom

'''


#FWC function 
import pandas as pd
import numpy as np

df=pd.read_csv('D:/Users/932151706/.spyder-py3/Tweets14DBrandcommunity.csv')

#case 0 nombres de mots dans le dic 
#case 1 nombres totals de mots dans les tweets 

tableautot=[0,0] 

tableaucategories=np.zeros(9)

for i in range(len(df['tweet'])):
    
    split = df['tweet'][i].split()


    tableau=[0,0,0,0,0,0,0,0,0]

    for i in range(len(split)):
        cptcategories=0
        for j in (fwords.items()):

            if split[i].lower() in j[1]:

                #print(split[i])
                tableau[cptcategories]+=1

            cptcategories+=1
    tableautot[0]+=sum(tableau)
    tableautot[1]+=len(split)
    
    tableaucategories+=np.array(tableau)
    
#print(tableautot)

if tableautot[1]==0:
    FWC=0
    somme1=0
else:
    FWC= tableautot[0]/tableautot[1]
    somme1= tableaucategories/tableautot[1]
    #print(tableaucategories)
print(FWC)
print(somme1)


'''

FWC function for the BrandCommunity

'''

#FWC function 
import pandas as pd
import numpy as np

df2=pd.read_csv("D:/Users/932151706/.spyder-py3/Tweets14dBrandcommunity.csv",low_memory=False)

#case 0 nombres de mots dans le dic 
#case 1 nombres totals de mots dans les tweets 

tableautot=[0,0] 

tableaucategories=np.zeros(9)

for i in range(len(df2['tweet'])):
    
    if type(df2['tweet'][i])== str:
        
    
        split = df2['tweet'][i].split()


        tableau=[0,0,0,0,0,0,0,0,0]

        for i in range(len(split)):
            cptcategories=0
            for j in (fwords.items()):

                if split[i].lower() in j[1]:

                    #print(split[i])
                    tableau[cptcategories]+=1

                cptcategories+=1
        tableautot[0]+=sum(tableau)
        tableautot[1]+=len(split)

        tableaucategories+=np.array(tableau)

    #print(tableautot)

FWC2= tableautot[0]/tableautot[1]
somme2= tableaucategories/tableautot[1]
#print(tableaucategories)
print(FWC2)
print(somme2)


'''
LSM formula
'''

#LSM
LSM= 1-(abs(FWC-FWC2/abs(FWC+FWC2+0.0001)))
print(LSM)









