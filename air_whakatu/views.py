from flask import Flask, render_template, url_for
from . import app

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/arrivals-departures")
def arrivalsdepartures():
    return render_template("arrivals-departures.html")

@app.route("/login")
def login():
    return render_template("login.html")