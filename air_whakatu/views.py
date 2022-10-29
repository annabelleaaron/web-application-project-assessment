from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
from . import connect
import uuid
from . import app

app.secret_key = 'super secret key'

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
@app.route("/arrivals-departures", methods=['GET','POST'])
def arrivalsdepartures():
    # noselect variable for when the user did not select any airport
    noselect = False
    if request.form.get('airport-name') == "" and request.method == 'POST':
        noselect = True
        return render_template('arrivals-departures.html', noselect=noselect)
    if request.form.get('airport-name') != "" and request.method == 'POST':
        # get airport name from the select tag in arrivals-departures.html
        apname = request.form.get('airport-name')
        cur = getCursor()
        # get airport code based off the airport name received from the select tag
        cur.execute("select AirportCode from airline.airport where AirportName=%s",(apname,))
        apcode = cur.fetchone()
        # change tuple to string
        apcode = str(apcode[0])
        # selects flights between 26 Oct 2022, 5PM and 2 Nov 2022, 5PM for both arrivals and departures
        # selects arrival time
        cur.execute("select r.FlightNum, addtime(f.FlightDate,f.ArrTime) as ArrivalTime, ap.AirportName as ArrivingFrom, f.FlightStatus from airline.route as r inner join airline.flight as f on f.FlightNum = r.FlightNum inner join airline.airport as ap on ap.AirportCode = r.DepCode where ap.AirportName != %s and r.ArrCode = %s and addtime(f.FlightDate,f.ArrTime) >= '2022-10-26 17:00' and addtime(f.FlightDate,f.ArrTime) <= '2022-11-2 17:00' order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode,))
        arr_select_result = cur.fetchall()
        arr_column_names = [desc[0] for desc in cur.description]
        # selects departure time
        cur.execute("select r.FlightNum, addtime(f.FlightDate,f.DepTime) as DepartureTime, ap.AirportName as DepartingTo, f.FlightStatus from airline.route as r inner join airline.flight as f on f.FlightNum = r.FlightNum inner join airline.airport as ap on ap.AirportCode = r.ArrCode where ap.AirportName != %s and r.DepCode = %s and addtime(f.FlightDate,f.DepTime) >= '2022-10-26 17:00' and addtime(f.FlightDate,f.DepTime) <= '2022-11-2 17:00' order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode,))
        dep_select_result = cur.fetchall()
        dep_column_names = [desc[0] for desc in cur.description]
        return render_template('arrivals-departures.html', apname=apname, arrresult=arr_select_result, arrcols=arr_column_names, depresult=dep_select_result, depcols=dep_column_names)
    else:
        return render_template('arrivals-departures.html')

# leads to the page for the user to login before booking for any flights
@app.route("/login", methods=['GET', 'POST'])
def login():
    # denied variable for when the email address entered by the user is not found in the database
    denied = False
    # registration variable used when the user has successfully registered a new account
    registration = False
    if "login-submit" in request.form and request.method == 'POST':
        # get email when user logs in
        email = request.form.get('login-email-address')
        cur = getCursor()
        # searches for the email in the database
        cur.execute("select EmailAddress from airline.passenger where EmailAddress=%s",(email,))
        record = cur.fetchone()
        if record:
            # if the email entered is found, creates a session for that user and directs them to booking.html
            session['loggedin'] = True
            session['username'] = record[0]
            return redirect(url_for('booking'))
        else:
            # if the email entered is not found, return them back to login.html
            denied = True
            return render_template('login.html', denied=denied)
    if "register-submit" in request.form and request.method == 'POST':
        # for successful registration, generates a unique id and enters it with the details entered by the user in the registration form into the database
        id = genID()
        first = request.form.get('register-first-name')
        last = request.form.get('register-last-name')
        email = request.form.get('register-email-address')
        phone = request.form.get('register-phone-number')
        passport = request.form.get('register-passport-number')
        dob = request.form.get('register-date-of-birth')
        cur = getCursor()
        cur.execute("insert into airline.passenger(PassengerID, FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier) values (%s,%s,%s,%s,%s,%s,%s,%s);",(str(id), first, last, email, phone, passport, dob, '1',))
        registration = True
        return render_template('login.html', registration=registration)
    else:
        return render_template('login.html')
    
@app.route("/booking")
def booking():
    cur = getCursor()
    # shows the existing bookings of the user on 2022-10-28 17:00 and 7 days after
    cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight as af inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.DepCode inner join airline.airport as aa2 on aa2.AirportCode = ar.ArrCode inner join airline.passengerflight as apf on apf.FlightID = af.FlightID inner join airline.passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and addtime(FlightDate,DepTime) >= '2022-10-28 17:00' and addtime(FlightDate,DepTime) <= '2022-11-04 17:00';",(session['username'],))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('booking.html', loggedEmail=session['username'], dbresult=select_result, dbcols=column_names)

@app.route("/booking/add")
def bookingAdd():
    return render_template('booking-add.html')

@app.route("/booking/cancel", methods=['GET','POST'])
def bookingCancel():
    if "cancel-booking-submit" in request.form and request.method == 'POST':
        # get flight ID and passenger ID from the form
        fid = request.form.get('flight-id')
        pid = request.form.get('passenger-id')
        cur = getCursor()
        # deletes the row based on flight ID and passenger ID
        cur.execute("delete from airline.passengerflight where PassengerID=%s and FlightID=%s;",(str(pid),str(fid),))
        return redirect("/booking")
    else:
        # get flight id from booking.html
        id = request.args.get('flightid')
        cur = getCursor()
        # get flight details
        cur.execute("select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight as af inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.DepCode inner join airline.airport as aa2 on aa2.AirportCode = ar.ArrCode inner join airline.passengerflight as apf on apf.FlightID = af.FlightID inner join airline.passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and apf.FlightID = %s;",(session['username'], str(id),))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template("booking-cancel.html", dbresult=select_result, dbcols=column_names)

@app.route("/booking/passenger", methods=['GET','POST'])
def passengerUpdate():
    # updated variable for when user has successfully updated their details
    updated = False
    if "update-submit" in request.form and request.method == 'POST':
        updated = True
        id = request.form.get('passenger-id')
        first = request.form.get('update-first-name')
        last = request.form.get('update-last-name')
        email = request.form.get('update-email-address')
        phone = request.form.get('update-phone-number')
        passport = request.form.get('update-passport-number')
        dob = request.form.get('update-date-of-birth')
        cur = getCursor()
        cur.execute("update airline.passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,))
        return render_template('booking-passenger.html', updated=updated)
    else:
        cur = getCursor()
        # get passenger ID based on the user who is in session
        cur.execute ("select PassengerID from airline.passenger where EmailAddress=%s;",(session['username'],))
        id = cur.fetchone()
        # change tuple to integer
        id = int(id[0])
        if id == '':
            return redirect("/booking")
        else:
            cur = getCursor()
            # get passenger details based on passenger ID
            cur.execute("select * from airline.passenger where PassengerID=%s",(str(id),))
            select_result = cur.fetchone()
            return render_template('booking-passenger.html',customerdetails = select_result)

@app.route("/logout")
def logout():
    # removes the current user from the session and directs them to login.html
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))