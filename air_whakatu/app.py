from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
import connect
import uuid
from datetime import datetime

dbconn = None

app = Flask(__name__)

global timeNow
timeNow = '2022-10-28 17:00'
app.secret_key = 'super secret key'

def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser, \
        password=connect.dbpass, host=connect.dbhost, \
        database=connect.dbname, autocommit=True)
        dbconn = connection.cursor(buffered=True)
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
        cur.execute("select AirportCode from airport where AirportName=%s",(apname,))
        apcode = cur.fetchone()
        # change tuple to string
        apcode = str(apcode[0])
        # selects flights based on 2 days before timeNow and 5 days after
        # selects arrival time
        cur.execute("select r.FlightNum, addtime(f.FlightDate,f.ArrTime) as ArrivalTime, ap.AirportName as ArrivingFrom, f.FlightStatus from  route as r inner join  flight as f on f.FlightNum = r.FlightNum inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName != %s and r.ArrCode = %s and addtime(f.FlightDate,f.ArrTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.ArrTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow))
        arr_select_result = cur.fetchall()
        arr_column_names = [desc[0] for desc in cur.description]
        # selects departure time
        cur.execute("select r.FlightNum, addtime(f.FlightDate,f.DepTime) as DepartureTime, ap.AirportName as DepartingTo, f.FlightStatus from  route as r inner join  flight as f on f.FlightNum = r.FlightNum inner join  airport as ap on ap.AirportCode = r.ArrCode where ap.AirportName != %s and r.DepCode = %s and addtime(f.FlightDate,f.DepTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.DepTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow,))
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
        cur.execute("select EmailAddress from  passenger where EmailAddress=%s",(email,))
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
        cur.execute("insert into  passenger(PassengerID, FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier) values (%s,%s,%s,%s,%s,%s,%s,%s);",(str(id), first, last, email, phone, passport, dob, '1',))
        registration = True
        return render_template('login.html', registration=registration)
    else:
        return render_template('login.html')

#leads to the page where user successfully logged in and is in session
@app.route("/booking")
def booking():
    cur = getCursor()
    # shows the existing bookings of the user based on timeNow
    cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and addtime(FlightDate,DepTime) >= %s;",(session['username'], timeNow,))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('booking.html', loggedEmail=session['username'], dbresult=select_result, dbcols=column_names)

# leads to the page where the user can choose which flight to book
@app.route("/booking/add", methods=('GET', 'POST'))
def bookingAdd():
    if "select-flight-submit" in request.form and request.method == 'POST':
        # get departure airport name from the select tag in booking-add.html
        apname = request.form.get('departure-airport-name')
        cur = getCursor()
        # get departure code based on the departure airport name
        cur.execute("select r.DepCode from  route as r inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName = %s;",(apname,))
        depcode = cur.fetchone()
        # change tuple to string
        depcode = str(depcode[0])
        # get date from the select tag in booking-add.html
        depdate = request.form.get('date-departure')
        # get flight ID of flights departing from the departure code and in 7 days of the selected date
        cur.execute("select FlightID from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum where ar.DepCode = %s and af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(depcode, depdate, depdate,))
        listOfFlightID = cur.fetchall()
        # change tuple of integers to list of strings
        listOfFlightIDs = []
        for x in listOfFlightID:
            x = str(x[0])
            listOfFlightIDs.append(x)
        # create an empty list to capture all flights
        listOfFlights = []
        # loop through listOfFlightID while appending the fetch into the empty list
        for x in listOfFlightIDs:
            cur = getCursor()
            cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from  flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from   passengerFlight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where ar.DepCode = %s;",(x, depcode,))
            # fetch the row
            flightRow = cur.fetchone()
            # append the row into the empty list
            listOfFlights.append(flightRow)
        select_result = listOfFlights
        column_names = [desc[0] for desc in cur.description]
        return render_template('booking-add.html', apname=apname, dbresult=select_result, dbcols=column_names)
    else:
        return render_template('booking-add.html')

# leads to the page where the user can confirm if they want to book the flight that they chose
@app.route("/booking/add/confirm", methods=['GET','POST'])
def bookingConfirm():
    if "confirm-booking-submit" in request.form and request.method == 'POST':
        # get flight ID from the form in booking-add.html
        fid = request.form.get('flight-id')
        cur = getCursor()
        # get passenger ID from the user in session
        cur.execute("select PassengerID from  passenger where EmailAddress = %s;",(session['username'],))
        pid = cur.fetchone()
        pid = int(pid[0])
        # add passenger into flight, using insert ignore to avoid error
        cur.execute("insert ignore into   passengerFlight(FlightID, PassengerID) values (%s,%s);",(str(fid),str(pid),))
        return redirect("/booking")
    else:
        # get the flight id from booking-add.html
        id = request.args.get('flightid')
        cur = getCursor()
        # get flight details
        cur.execute("select af.FlightID, af.FlightNum, af.FlightDate, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where af.FlightID = %s;",(str(id),))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template("booking-add-confirm.html", dbresult=select_result, dbcols=column_names)

# leads to the page where the user can cancel one of their existing bookings that they chose in booking.html
@app.route("/booking/cancel", methods=['GET','POST'])
def bookingCancel():
    if "cancel-booking-submit" in request.form and request.method == 'POST':
        # get flight ID and passenger ID from the form in booking-cancel.html
        fid = request.form.get('flight-id')
        pid = request.form.get('passenger-id')
        cur = getCursor()
        # deletes the row based on flight ID and passenger ID
        cur.execute("delete from   passengerFlight where PassengerID=%s and FlightID=%s;",(str(pid),str(fid),))
        return redirect("/booking")
    else:
        # get flight id from booking.html
        id = request.args.get('flightid')
        cur = getCursor()
        # get flight details
        cur.execute("select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and apf.FlightID = %s;",(session['username'], str(id),))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template("booking-cancel.html", dbresult=select_result, dbcols=column_names)

# leads to the page where the user can edit their details
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
        cur.execute("update  passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,))
        return render_template('booking-passenger.html', updated=updated)
    else:
        cur = getCursor()
        # get passenger ID based on the user who is in session
        cur.execute ("select PassengerID from  passenger where EmailAddress=%s;",(session['username'],))
        id = cur.fetchone()
        # change tuple to integer
        id = int(id[0])
        if id == '':
            return redirect("/booking")
        else:
            cur = getCursor()
            # get passenger details based on passenger ID
            cur.execute("select * from  passenger where PassengerID=%s",(str(id),))
            select_result = cur.fetchone()
            return render_template('booking-passenger.html',customerdetails = select_result)

# ends the session
@app.route("/logout")
def logout():
    # removes the current user from the session and directs them to login.html
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# admin home page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    cur = getCursor()
    cur.execute("select StaffID, IsManager, CONCAT(FirstName,' ',LastName) as Name from staff;")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template("admin-home.html", dbresult=select_result, dbcols=column_names)

# admin logged in
@app.route('/admin/login')
def adminLogin():
    adminId = request.args.get('adminid')
    cur = getCursor()
    cur.execute("select IsManager from staff where StaffID = %s;",(adminId,))
    isManager = cur.fetchone()
    isManager = str(isManager[0])
    cur.execute("select CONCAT(FirstName,' ',LastName) as Name from staff where StaffID = %s;",(adminId,))
    adminName = cur.fetchone()
    adminName = str(adminName[0])
    session['adminloggedin'] = True
    session['adminuserid'] = adminId
    session['adminmanager'] = isManager
    session['adminname'] = adminName
    return render_template('admin-login.html')

# admin able to view list of passengers
@app.route('/admin/passenger', methods=['GET','POST'])
def adminPassengerList():
    if "search-last-name-submit" in request.form and request.method == 'POST':
        lastName = request.form.get('passenger-last-name')
        cur = getCursor()
        cur.execute("select * from passenger where LastName = %s;",(lastName,))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-list.html', dbresult=select_result, dbcols=column_names)
    else:
        cur = getCursor()
        cur.execute("select PassengerID, CONCAT(FirstName,' ',LastName) as Name, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth from passenger;")
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-list.html', dbresult=select_result, dbcols=column_names)

@app.route('/admin/passenger/details', methods=['GET','POST'])
def adminPassengerDetails():
    # updated variable for when user has successfully updated their details
    updated = False
    if "admin-update-submit" in request.form and request.method == 'POST':
        updated = True
        id = request.form.get('passenger-id')
        first = request.form.get('update-first-name')
        last = request.form.get('update-last-name')
        email = request.form.get('update-email-address')
        phone = request.form.get('update-phone-number')
        passport = request.form.get('update-passport-number')
        dob = request.form.get('update-date-of-birth')
        cur = getCursor()
        cur.execute("update  passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,))
        # get passenger details based on passenger ID
        cur.execute("select * from  passenger where PassengerID=%s",(session['adminpassenger'],))
        select_passengerid = cur.fetchone()
        # shows the existing bookings of the user based on timeNow
        cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-details.html', updated=updated, customerdetails=select_passengerid, dbresult=select_result, dbcols=column_names)
    else:
        pid = request.args.get("passengerid")
        session['adminpassenger'] = pid
        cur = getCursor()
        # get passenger details based on passenger ID
        cur.execute("select * from  passenger where PassengerID=%s",(session['adminpassenger'],))
        select_passengerid = cur.fetchone()
        # shows the existing bookings of the user based on timeNow
        cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-details.html', customerdetails=select_passengerid, dbresult=select_result, dbcols=column_names)

@app.route('/admin/passenger/booking/cancel', methods=['GET','POST'])
def adminPassengerBookingCancel():
    if "admin-cancel-booking-submit" in request.form and request.method == 'POST':
        # get flight ID from the form in admin-passenger-booking-cancel.html
        fid = request.form.get('flight-id')
        cur = getCursor()
        # deletes the row based on flight ID and passenger ID
        cur.execute("delete from   passengerFlight where PassengerID=%s and FlightID=%s;",(session['adminpassenger'],str(fid),))
        # get the passenger details
        cur.execute("select * from  passenger where PassengerID=%s;",(session['adminpassenger'],))
        select_passengerid = cur.fetchone()
        # shows the existing bookings of the user based on timeNow
        cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-details.html', customerdetails=select_passengerid, dbresult=select_result, dbcols=column_names)
    else:
        # get flight id from admin-passenger-details.html
        id = request.args.get('flightid')
        cur = getCursor()
        # get flight details
        cur.execute("select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and apf.FlightID = %s;",(session['adminpassenger'], str(id),))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-booking-cancel.html', dbresult=select_result, dbcols=column_names)

@app.route('/admin/passenger/booking', methods=['GET','POST'])
def adminPassengerBooking():
    if "admin-select-flight-submit" in request.form and request.method == 'POST':
        # get departure airport name from the select tag in admin-passenger-booking.html
        apname = request.form.get('departure-airport-name')
        cur = getCursor()
        # get departure code based on the departure airport name
        cur.execute("select r.DepCode from  route as r inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName = %s;",(apname,))
        depcode = cur.fetchone()
        # change tuple to string
        depcode = str(depcode[0])
        # get date from the select tag in admin-passenger-booking.html
        depdate = request.form.get('date-departure')
        # get flight ID of flights departing from the departure code and in 7 days of the selected date
        cur.execute("select FlightID from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum where ar.DepCode = %s and af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(depcode, depdate, depdate,))
        listOfFlightID = cur.fetchall()
        # change tuple of integers to list of strings
        listOfFlightIDs = []
        for x in listOfFlightID:
            x = str(x[0])
            listOfFlightIDs.append(x)
        # create an empty list to capture all flights
        listOfFlights = []
        # loop through listOfFlightID while appending the fetch into the empty list
        for x in listOfFlightIDs:
            cur = getCursor()
            cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from  flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from   passengerFlight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where ar.DepCode = %s;",(x, depcode,))
            # fetch the row
            flightRow = cur.fetchone()
            # append the row into the empty list
            listOfFlights.append(flightRow)
        select_result = listOfFlights
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-booking.html', apname=apname, dbresult=select_result, dbcols=column_names)
    else:
        return render_template('admin-passenger-booking.html')

@app.route('/admin/passenger/booking/confirm', methods=['GET','POST'])
def adminPassengerBookingConfirm():
    if "admin-confirm-booking-submit" in request.form and request.method == 'POST':
        # get flight ID from the form in admin-passenger-booking.html
        fid = request.form.get('flight-id')
        cur = getCursor()
        # add passenger into flight, using insert ignore to avoid error
        cur.execute("insert ignore into   passengerFlight(FlightID, PassengerID) values (%s,%s);",(str(fid),session['adminpassenger'],))
        # get the passenger details
        cur.execute("select * from  passenger where PassengerID=%s;",(session['adminpassenger'],))
        select_passengerid = cur.fetchone()
        # shows the existing bookings of the user based on timeNow
        cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-details.html', customerdetails=select_passengerid, dbresult=select_result, dbcols=column_names)
    else:
        # get the flight id from admin-passenger-booking.html
        id = request.args.get('flightid')
        cur = getCursor()
        # get flight details
        cur.execute("select af.FlightID, af.FlightNum, af.FlightDate, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where af.FlightID = %s;",(str(id),))
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        return render_template('admin-passenger-booking-confirm.html', dbresult=select_result, dbcols=column_names)

@app.route('/admin/flights', methods = ['GET','POST'])
def adminFlightsList():
    allflights = True
    allflights = False
    cur = getCursor()
    cur.execute("select FlightID from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum where af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(timeNow, timeNow,))
    listOfFlightID = cur.fetchall()
    listOfFlightIDs = []
    for x in listOfFlightID:
        x = str(x[0])
        listOfFlightIDs.append(x)
    listOfFlights = []
    for x in listOfFlightIDs:
        cur = getCursor()
        cur.execute("select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from  flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from   passengerFlight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode;",(x,))
        # fetch the row
        flightRow = cur.fetchone()
        # append the row into the empty list
        listOfFlights.append(flightRow)
    select_result = listOfFlights
    column_names = [desc[0] for desc in cur.description]
    return render_template('admin-passenger-booking.html', allflights=allflights, dbresult=select_result, dbcols=column_names)
    return render_template('admin-flights-list.html')

@app.route('/admin/flights/manifest')
def adminFlightsManifest():
    return render_template('admin-flights-manifest.html')