## Project Summary

* To reinstall the packages used in the environment:
```pip install -r requirements.txt```


* To run the application in the terminal:
```
cd air_whakatu
set FLASK_APP=webapp (Windows) OR export set FLASK_APP=webapp (Linux and macOS)
python -m flask run
```
___


### Routes and Functions
* User will first view home.html
```
route: /
render_template: home.html
links to: arrivals-departures.html and login.html
```
* When the user clicks the 'Arrivals & Departures' link in home.html, arrivals-departures.html will show up where user can select their desired airport and click the select button to showcase the arrivals and departures for that selected airport
```
route: /arrivals-departures
method: POST
sql: "select r.FlightNum, addtime(f.FlightDate,f.ArrTime) as ArrivalTime, ap.AirportName as ArrivingFrom, f.FlightStatus from airline.route as r inner join airline.flight as f on f.FlightNum = r.FlightNum inner join airline.airport as ap on ap.AirportCode = r.DepCode where ap.AirportName != %s and r.ArrCode = %s and addtime(f.FlightDate,f.ArrTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.ArrTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow)
sql: "select r.FlightNum, addtime(f.FlightDate,f.DepTime) as DepartureTime, ap.AirportName as DepartingTo, f.FlightStatus from airline.route as r inner join airline.flight as f on f.FlightNum = r.FlightNum inner join airline.airport as ap on ap.AirportCode = r.ArrCode where ap.AirportName != %s and r.DepCode = %s and addtime(f.FlightDate,f.DepTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.DepTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow,)
variables: apname, arrresult, arrcols, depresult, depcols
render_template: arrivals-departures.html
```
* When the user clicks the 'Book a flight' link in home.html, login.html will show up where user can login an existing account or register a new account
```
route: /login
method: POST
sql: "select EmailAddress from airline.passenger where EmailAddress=%s",(email,)
variables: denied
render_template: login.html (if email is not registered) | booking.html (if email is registered)
```
```
route: /login
method: POST
sql: "insert into airline.passenger(PassengerID, FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier) values (%s,%s,%s,%s,%s,%s,%s,%s);",(str(id), first, last, email2, phone, passport, dob, '1',)
variables: registration
render_template: login.html
```
* When the user successfully logs in and starts a session, the user will be lead to booking.html where their existing bookings are shown
```
route: /booking
method: GET
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight as af inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.DepCode inner join airline.airport as aa2 on aa2.AirportCode = ar.ArrCode inner join airline.passengerflight as apf on apf.FlightID = af.FlightID inner join airline.passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and addtime(FlightDate,DepTime) >= %s;",(session['username'], timeNow,)
variables: loggedEmail, dbresult=select_result, dbcols=column_name
render_template: booking.html
```
* When the user in session clicks the 'Logout' link in booking.html, ends the session the directs the user to login.html
```
route: /logout
render_template: login.html
```
* Clicking the 'Change details' link in booking.html, the user will be lead to booking-passenger.html where they can update their details
```
route: /booking/passenger
method: GET
sql: "select PassengerID from airline.passenger where EmailAddress=%s;",(session['username'],)
sql: "select * from airline.passenger where PassengerID=%s",(str(id),)
variables: customerdetails
render-template: booking-passenger.html
```
```
route: /booking/passenger
method: POST
sql: "update airline.passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,)
variables: updated
render_template: booking-passenger.html
```
* When the user clicks 'Book a flight' link in booking.html, leads them to booking-add.html where they can select the departure airport and select the date. Clicking select will list the available flights from the selected day up to 7 days after the selected date
```
route: /booking/add
render_template: booking-add.html
```
```
route: /booking/add
method: POST
sql: "select r.DepCode from airline.route as r inner join airline.airport as ap on ap.AirportCode = r.DepCode where ap.AirportName = %s;",(apname,)
sql: "select FlightID from airline.flight as af inner join airline.route as ar on ar.FlightNum = af.FlightNum where ar.DepCode = %s and af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(depcode, depdate, depdate,)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from airline.flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from airline.passengerflight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join airline.aircraft as ac on ac.RegMark = af.Aircraft inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.ArrCode where ar.DepCode = %s;",(x, depcode,)
variables: apname, dbresult, dbcols
render_template: booking-add.html
```
* Selecting a flight number in booking-add.html will lead user to booking-add-confirm.html, where they can confirm their booking - their flight details will be inserted into passengerflight and they will be redirected to booking.html, or cancel and be redirected to booking.html
```
route: /booking/add/confirm
method: GET
sql: "select af.FlightID, af.FlightNum, af.FlightDate, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight as af inner join airline.aircraft as ac on ac.RegMark = af.Aircraft inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.ArrCode where af.FlightID = %s;",(str(id),)
variables: dbresult, dbcols
render_template: booking-add-confirm.html
```
```
route: /booking/add/confirm
method: POST
sql: "select PassengerID from airline.passenger where EmailAddress = %s;",(session['username'],)
sql: "insert ignore into airline.passengerflight(FlightID, PassengerID) values (%s,%s);",(str(fid),str(pid),)
```
* When the user in session selects one of the flight number in booking.html, leads them to booking-cancel.html where they can cancel the booking for that particular flight number. After cancelling the booking, the user will be redirected to booking.html
```
route: /booking/cancel
method: GET
sql: "select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight as af inner join airline.route as ar on ar.FlightNum = af.FlightNum inner join airline.airport as aa on aa.AirportCode = ar.DepCode inner join airline.airport as aa2 on aa2.AirportCode = ar.ArrCode inner join airline.passengerflight as apf on apf.FlightID = af.FlightID inner join airline.passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and apf.FlightID = %s;",(session['username'], str(id),)
variables: dbresult, dbcols
render_template: /booking/cancel?flightid={{result[0]}}
```
```
route: /booking/cancel
method: POST
sql: "delete from airline.passengerflight where PassengerID=%s and FlightID=%s;",(str(pid),str(fid),)
render_template: booking.html
```

___


### Files
- [x] air_whakatu
    - [x] views.py
    - [x] __init__.py
    - [x] webapp.py
    - [x] connect.py
- [x] templates
    - [x] layout.html
    - [x] home.html
    - [x] arrivals-departures.html
    - [x] login.html
    - [x] booking.html
    - [x] booking-passenger.html
    - [x] booking-cancel.html
    - [x] booking-add.html
    - [x] booking-add-confirm.html
- [x] static
    - [x] logo_blue.jpg
- [x] .gitignore | _virtual environment_
- [x] requirements.txt
- [ ] Extract of database from MySQL

