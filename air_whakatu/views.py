from flask import Flask, render_template, url_for
import mysql.connector
from . import connect
import uuid
from . import app

dbconn = None

def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser, \
        password=connect.dbpass, host=connect.dbhost, \
        database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn

def genID():
    return uuid.uuid4().fields[1]

# leads to the home page
@app.route("/")
def home():
    return render_template('home.html')

# leads to the page where the arrivals and departures flights are listed
@app.route("/arrivals-departures")
def arrivalsdepartures():
    cur = getCursor()
    # selects flights between 26 Oct 2022, 5PM and 2 Nov 2022, 5PM
    cur.execute("select FlightNum, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime "
    "from airline.flight "
    "where addtime(FlightDate,DepTime) >= '2022-10-26 17:00' and addtime(FlightDate,DepTime) <= '2022-11-2 17:00' "
    "order by addtime(FlightDate,DepTime);")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    print(f"{column_names}")
    return render_template('arrivals-departures.html', dbresult=select_result, dbcols=column_names)

# leads to the page for the user to login before booking for any flights
@app.route("/login")
def login():
    return render_template('login.html')