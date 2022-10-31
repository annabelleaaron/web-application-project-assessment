## Project Summary


* To reinstall the packages used in the environment:
```pip install -r requirements.txt```


___


### Routes and Functions
* User will first view home.html
```
route: /
render_template: home.html
links to: arrivals-departures.html and login.html
```
* When the user clicks the 'Arrivals & Departures' link in home.html, arrivals-departures.html will show up where user can select their desired airport and click the select button to display the arrivals and departures for that selected airport
```
route: /arrivals-departures
render_template: arrivals-departures.html
```
```
route: /arrivals-departures
method: POST
sql: "select r.FlightNum, addtime(f.FlightDate,f.ArrTime) as ArrivalTime, ap.AirportName as ArrivingFrom, f.FlightStatus from  route as r inner join  flight as f on f.FlightNum = r.FlightNum inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName != %s and r.ArrCode = %s and addtime(f.FlightDate,f.ArrTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.ArrTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow)
sql: "select r.FlightNum, addtime(f.FlightDate,f.DepTime) as DepartureTime, ap.AirportName as DepartingTo, f.FlightStatus from  route as r inner join  flight as f on f.FlightNum = r.FlightNum inner join  airport as ap on ap.AirportCode = r.ArrCode where ap.AirportName != %s and r.DepCode = %s and addtime(f.FlightDate,f.DepTime) >= date_sub(%s, interval 2 day) and addtime(f.FlightDate,f.DepTime) <= date_add(%s, interval 5 day) order by addtime(f.FlightDate,f.ArrTime);",(apname, apcode, timeNow, timeNow,)
variables: apname, arrresult, arrcols, depresult, depcols
render_template: arrivals-departures.html
```
* When the user clicks the 'Book a flight' link in home.html, login.html will show up where user can login an existing account or register a new account
```
route: /login
render_template: login.html
```
```
route: /login
method: POST
sql: "select EmailAddress from  passenger where EmailAddress=%s",(email,)
variables: denied
render_template: login.html (if email is not registered) | booking.html (if email is registered)
```
```
route: /login
method: POST
sql: "insert into  passenger(PassengerID, FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier) values (%s,%s,%s,%s,%s,%s,%s,%s);",(str(id), first, last, email2, phone, passport, dob, '1',)
variables: registration
render_template: login.html
```
* When the user successfully logs in and starts a session, the user will be lead to booking.html where their existing bookings are shown
```
route: /booking
method: GET
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join  passengerflight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and addtime(FlightDate,DepTime) >= %s;",(session['username'], timeNow,)
variables: loggedEmail, dbresult=select_result, dbcols=column_name
render_template: booking.html
```
* When the user in session clicks the 'Logout' link in booking.html, the session is ended and directs the user to login.html
```
route: /logout
render_template: login.html
```
* Clicking the 'Change details' link in booking.html, the user will be lead to booking-passenger.html where they can update their details
```
route: /booking/passenger
method: GET
sql: "select PassengerID from  passenger where EmailAddress=%s;",(session['username'],)
sql: "select * from  passenger where PassengerID=%s",(str(id),)
variables: customerdetails
render-template: booking-passenger.html
```
```
route: /booking/passenger
method: POST
sql: "update  passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,)
variables: updated
render_template: booking-passenger.html
```
* When the user clicks 'Book a flight' link in booking.html, leads them to booking-add.html where they can select the departure airport and select the date. Clicking the select button will list the available flights from the selected day up to 7 days after the selected date
```
route: /booking/add
render_template: booking-add.html
```
```
route: /booking/add
method: POST
sql: "select r.DepCode from  route as r inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName = %s;",(apname,)
sql: "select FlightID from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum where ar.DepCode = %s and af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(depcode, depdate, depdate,)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from  flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from  passengerflight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where ar.DepCode = %s;",(x, depcode,)
variables: apname, dbresult, dbcols
render_template: booking-add.html
```
* Selecting a flight number in booking-add.html will lead user to booking-add-confirm.html, where they can confirm their booking - their flight details will be inserted into passengerflight and they will be redirected to booking.html, or cancel and be redirected to booking.html
```
route: /booking/add/confirm
method: GET
sql: "select af.FlightID, af.FlightNum, af.FlightDate, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where af.FlightID = %s;",(str(id),)
variables: dbresult, dbcols
render_template: booking-add-confirm.html
```
```
route: /booking/add/confirm
method: POST
sql: "select PassengerID from  passenger where EmailAddress = %s;",(session['username'],)
sql: "insert ignore into  passengerflight(FlightID, PassengerID) values (%s,%s);",(str(fid),str(pid),)
```
* When the user in session selects one of the flight number in booking.html, leads them to booking-cancel.html where they can cancel the booking for that particular flight number. After cancelling the booking, the user will be redirected to booking.html
```
route: /booking/cancel
method: GET
sql: "select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join  passengerflight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.EmailAddress = %s and apf.FlightID = %s;",(session['username'], str(id),)
variables: dbresult, dbcols
render_template: /booking/cancel?flightid={{result[0]}}
```
```
route: /booking/cancel
method: POST
sql: "delete from  passengerflight where PassengerID=%s and FlightID=%s;",(str(pid),str(fid),)
render_template: booking.html
```
* A list of staff names are displayed where they can click their name to login
```
route: /admin
method: GET
sql: "select StaffID, IsManager, CONCAT(FirstName,' ',LastName) as Name from staff;"
variables: dbresult, dbcols
render_template: admin-home.html
```
* When the staff logs in, there are two links in admin-login.html. 'Passenger List' links to admin-passenger-list.html, showing the list of passengers while 'Flights List' links to admin-flights-list.html, showing the list of flights
```
route: /admin/login
render_template: admin-login.html
```
* Clicking into 'Passenger List' displays all registered passengers. The staff can search passengers by their last name
```
route: /admin/passenger
method: GET
sql: "select PassengerID, CONCAT(FirstName,' ',LastName) as Name, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth from passenger;"
variables: dbresult, dbcols
render_template: admin-passenger-list.html
```
```
route: /admin/passenger
method: POST
sql: "select * from passenger where LastName = %s;",(lastName,)
variables: dbresult, dbcols
render_template: admin-passenger-list.html
```
* Clicking a passenger's name will lead the staff to the selected passenger's details regarding their information and existing bookings. In this template, the staff can edit the passenger's information. Otherwise, the staff can click a flight number from the passenger's existing bookings to cancel it, or click the 'Add Booking' button to add a flight booking for the passenger
```
route: /admin/passenger/details
method: GET
sql: "select * from  passenger where PassengerID=%s",(session['adminpassenger'],)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,)
variables: customerdetails, dbresult, dbcols
render_template: admin-passenger-details.html
```
```
route: /admin/passenger/details
method: POST
sql: "update  passenger set FirstName=%s, LastName=%s, EmailAddress=%s, PhoneNumber=%s, PassportNumber=%s, DateOfBirth=%s where PassengerID=%s;",(first, last, email, phone, passport, dob, id,)
sql: "select * from  passenger where PassengerID=%s",(session['adminpassenger'],)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,)
variables: updated, customerdetails, dbresult, dbcols
render_template: admin-passenger-details.html
```
* Clicking on any flight number from the passenger's existing bookings in admin-passenger-details.html will display the selected flight and a 'Confirm cancellation' button
```
route: /admin/passenger/booking/cancel
method: GET
sql: "select af.FlightID, ap.PassengerID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and apf.FlightID = %s;",(session['adminpassenger'], str(id),)
variables: dbresult, dbcols
render_template: admin-passenger-booking-cancel.html
```
```
route: /admin/passenger/booking/cancel
method: POST
sql: "delete from   passengerFlight where PassengerID=%s and FlightID=%s;",(session['adminpassenger'],str(fid),)
sql: "select * from  passenger where PassengerID=%s;",(session['adminpassenger'],)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,)
variables: customerdetails, dbresult, dbcols
render_template: admin-passenger-details.html
```
* Clicking on the 'Add Booking' button in admin-passenger-details.html will display a dropdown box to choose the departure airport and a date selector box. 
```
route: /admin/passenger/booking
render_template: admin-passenger-booking.html
```
```
route: /admin/passenger/booking
method: POST
sql: "select r.DepCode from  route as r inner join  airport as ap on ap.AirportCode = r.DepCode where ap.AirportName = %s;",(apname,)
sql: "select FlightID from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum where ar.DepCode = %s and af.FlightDate >= %s and af.FlightDate <= date_add(%s, interval 7 day);",(depcode, depdate, depdate,)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime, ac.Seating-NumberOfBookedSits.NumberOfPassengers as NumberOfAvailableSeats from  flight as af inner join (select pf.FlightID, count(pf.PassengerID) as NumberOfPassengers from   passengerFlight as pf where pf.FlightID = %s) as NumberOfBookedSits on af.FlightID = NumberOfBookedSits.FlightID inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where ar.DepCode = %s;",(x, depcode,)
variables: apname, dbresult, dbcols
render_template: admin-passenger-booking.html
```
* Selecting a flight number from the list of flights displayed in admin-passenger-booking.html after inputting the departure airport and date will send the staff to admin-passenger-booking-confirm.html where they can confirm the booking for the passenger
```
route: /admin/passenger/booking/confirm
method: GET
sql: "select af.FlightID, af.FlightNum, af.FlightDate, (select aa.AirportName where aa.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  aircraft as ac on ac.RegMark = af.Aircraft inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.ArrCode where af.FlightID = %s;",(str(id),)
variables: dbresult, dbcols
render_template: admin-passenger-booking-confirm.html
```
```
route: /admin/passenger/booking/confirm
method: POST
sql: "insert ignore into   passengerFlight(FlightID, PassengerID) values (%s,%s);",(str(fid),session['adminpassenger'],)
sql: "select * from  passenger where PassengerID=%s;",(session['adminpassenger'],)
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom,addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from  flight as af inner join  route as ar on ar.FlightNum = af.FlightNum inner join  airport as aa on aa.AirportCode = ar.DepCode inner join  airport as aa2 on aa2.AirportCode = ar.ArrCode inner join   passengerFlight as apf on apf.FlightID = af.FlightID inner join  passenger as ap on ap.PassengerID = apf.PassengerID where ap.PassengerID = %s and addtime(FlightDate,DepTime) >= %s;",(session['adminpassenger'], timeNow,)
variables: customerdetails, dbresult, dbcols
render_template: admin-passenger-details.html
```
* Clicking the 'Flights List' link in admin-login.html will direct the staff to admin-flights-list.html where a list of flights is displayed according to the timeNow variable. The list displays flights from the start of timeNow to 7 days after. There is also a dropdown box and data selection box where the staff can choose the departure airport and date of departure. Clicking the 'Select' button will display the list of flights according to the criteria chosen from both boxes. An 'Add Flights' button can only be viewed by a staff who is a manager where they can add flights for following week.
```
route: /admin/flights
method: GET
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from flight as af inner join route as ar on af.FlightNum = ar.FlightNum inner join airport as aa on aa.AirportCode = ar.DepCode inner join airport as aa2 on aa2.AirportCode = ar.ArrCode where addtime(FlightDate,DepTime) >= %s and addtime(FlightDate,DepTime) <= date_add(%s, interval 7 day) order by FlightDate;",(timeNow, timeNow,)
variables: manager, dbresult, dbcols
render_template: admin-flights-list.html
```
```
route: /admin/flights
method: POST
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from flight as af inner join route as ar on af.FlightNum = ar.FlightNum inner join airport as aa on aa.AirportCode = ar.DepCode inner join airport as aa2 on aa2.AirportCode = ar.ArrCode where aa.AirportName = %s and FlightDate >= %s and FlightDate <= date_add(%s, interval 7 day) order by FlightDate;",(apname, depdate, depdate,)
variables: manager, dbresult, dbcols
render_template: admin-flights-list.html
```
```
route: /admin/flights
method: POST
sql: "INSERT INTO flight(FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft) SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day), DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft FROM flight WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);"
sql: "select af.FlightID, af.FlightNum, (select aa.AirportName where aa.AirportCode = ar.DepCode) as DepartingFrom, addtime(FlightDate,DepTime) as DepartureTime, (select aa2.AirportName where aa2.AirportCode = ar.ArrCode) as DepartingTo, addtime(FlightDate,ArrTime) as ArrivalTime from flight as af inner join route as ar on af.FlightNum = ar.FlightNum inner join airport as aa on aa.AirportCode = ar.DepCode inner join airport as aa2 on aa2.AirportCode = ar.ArrCode where addtime(FlightDate,DepTime) >= %s and addtime(FlightDate,DepTime) <= date_add(%s, interval 7 day) order by FlightDate;",(timeNow, timeNow,)
variables: updated, manager, dbresult, dbcols
render_template: admin-flights-list.html
```

___


### Files
- [x] air_whakatu
    - [x] app.py
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
    - [x] admin-home.html
    - [x] admin-login.html
    - [x] admin-passenger-list.html
    - [x] admin-passenger-details.html
    - [x] admin-passenger-booking-cancel.html
    - [x] admin-passenger-booking.html
    - [x] admin-passenger-booking-confirm.html
    - [x] admin-flights-list.html
    - [ ] admin-flights-manifest.html
- [x] static
    - [x] logo_blue.jpg
- [x] .gitignore | _virtual environment_
- [x] requirements.txt
- [x] Extract of database from MySQL | PythonAnywhere

