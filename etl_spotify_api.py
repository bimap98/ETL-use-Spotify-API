import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3
from sqlalchemy import create_engine
engine = create_engine('sqlite://', echo=False)


DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
USER_ID = "rda973wio2iudy2d1tz3ebm87" # your Spotify username 
TOKEN = "BQAX46nVqTwnQ_RSFG-NTpRahBN8cybZ7_60N37PbmnhDAto1QNbgJQEouUGUdtuH5_lTsqXqzz8bPwX9yEvUCHVZ7Vjr9Bw6dwts-y7syk4vwwUN_Kg21ttC12Ug1B8YA8xhIXab3g-30wMUkutEDk9QRsnGqzq8bjAjvk-" # your Spotify API token

# Generate your token here:  https://developer.spotify.com/console/get-recently-played/
# Note: You need a Spotify account (can be easily created for free)

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False 

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception("At least one of the returned songs does not have a yesterday's timestamp")

    return True

if __name__ == "__main__":

    # Extract part of the ETL process
 
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token=TOKEN)
    }
    
    # Convert time to Unix timestamp in miliseconds      
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    # Download all songs you've listened to "after yesterday", which means in the last 24 hours      
    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers = headers)

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        
    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    print(song_df)

song_df.to_sql('users', con=engine)
engine.execute("SELECT * FROM users").fetchall()

engine = sqlalchemy.create_engine("postgresql://postgres:11111@localhost/uas_de")
con = engine.connect()
print(engine.table_names())

song_df.to_sql(name="uas_ku",con=engine,index=False,if_exists="append")

df = pd.read_sql_table("uas_ku",engine)