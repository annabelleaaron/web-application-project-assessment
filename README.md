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
views.py
```
Route: /
render_template: home.html
```
```
Route: /arrivals-departures
Return SQL data: select FlightNum, addtime(FlightDate,DepTime) as DepartureTime, addtime(FlightDate,ArrTime) as ArrivalTime from airline.flight where addtime(FlightDate,DepTime) >= '2022-10-26 17:00' and addtime(FlightDate,DepTime) <= '2022-11-2 17:00' order by addtime(FlightDate,DepTime);
Pass data variables: dbresult=select_result, dbcols=column_name
render_template: arrivals-departures.html
```
```
Route: /login
render_template: login.html
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
- [x] static
    - [x] logo_blue.jpg
- [x] .gitignore | _virtual environment_
- [x] requirements.txt
- [ ] Extract of database from MySQL

