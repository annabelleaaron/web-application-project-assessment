## Project Summary

* To reinstall the packages used in the environment:
```pip install -r requirements.txt```


* To run the application in the terminal:
```
cd air_whakatu
set FLASK_APP=webapp
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
Read method: GET
Return SQL data: select * from airlines.flight;
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

