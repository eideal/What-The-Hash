############
# Extract recent 8 hours of Twitter tweets
############

import psycopg2
import datetime

def connect_to_db():
   """
   Connect to the tweetsdb database
   """

   host   = 'tweetsdb.cqfliozhpzqt.us-west-2.rds.amazonaws.com:5432'
   dbname = 'tweetsdb'

   user = ''
   pswd = ''

   with open('db_credentials', 'r') as f:
       credentials = f.readlines()
       f.close()
   
       user = credentials[0].rstrip()
       pswd = credentials[1].rstrip()

   connection = psycopg2.connect(
       database=dbname,
       user=user,
       password=pswd,
       host=host.split(':')[0],
       port=5432)

   return connection

def get_tweets():
    # Access database and pull the last 8 hours of tweets
    conn = psycopg2.connect("host=52.40.74.90 port=5432 dbname=emoji_db user=postgres password=darkmatter")
    cur = conn.cursor()
    print('Connected to database')
    
    # Get the last 8 hours of tweet data, where the tweets must have a '#' in it 
    start_time=datetime.datetime.now()-datetime.timedelta(hours=8)
    word="%#%"
    cur.execute("""SELECT text FROM tweet_dump 
                WHERE (created_at > %s AND lang = 'en' AND text LIKE %s AND id > 140000000) ORDER BY id DESC;""", [start_time,word])
    results = cur.fetchall() # returns a list
    
    # Close the database connection
    conn.close()
    print 'Done pulling tweets'
  
    conn = connect_to_db()
    cur = conn.cursor()
    print('Connected to my database')
    
    # Drop the tweets table
    cur.execute("""DROP TABLE IF EXISTS tweets;""")
    print('Done dropping the tweets table')
    
    # Recreate the table and fill it
    cur.execute("""CREATE TABLE tweets (tweet text);""")
    print('Created the tweets table')
    
    for i, result in enumerate(results):
        cur.execute("""INSERT INTO tweets VALUES(%s);""", result)
        if (i % 100 == 0): print 'On ', i
    conn.commit()
    conn.close()
    print('Done inserting the tweets into the tweets table')
