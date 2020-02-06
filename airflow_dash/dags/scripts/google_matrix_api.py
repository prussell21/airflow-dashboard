import requests
import json
import datetime as dt
import pandas as pd
import psycopg2
import config

def insertData(config):

    '''
    Makes API call to the google matrix api
    and inserts into database
    origin: point of origin
    dest: destination point
    key: google api key
    '''
    conn = psycopg2.connect(user = config.user,
                        password = config.password,
                        host = config.host,
                        port = "5432",
                        database = config.database)

    origin=config.origin
    dest=config.destination
    traffic_model='pessimistic'
    departure_time='now'
    key=config.api_key

    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='
    r = requests.get(url+origin+'&destinations='+dest+'&traffic_model='+traffic_model+'&departure_time='+departure_time+'&key='+key)
    print (r.json())

    #Parse Json response to obtain time data
    time_to = list(r.json()['rows'][0]['elements'][0]['duration_in_traffic'].values())[0]

    sql = 'INSERT INTO time_to_destination2 VALUES(%s, %s)'
    c = conn.cursor()
    c.execute(sql, (dt.datetime.now(),time_to))
    conn.commit()

if __name__ == '__main__':
    insertData(config)
