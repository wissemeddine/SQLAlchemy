# import dependencies 
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#database engine steup
engine = create_engine("sqlite:///Hawaii.sqlite")
# recall the database to the new model
Base = automap_base()
# recall  tables
Base.prepare(engine, reflect=True)

# Save references into a table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session (link) from Python to the Database
session = Session(engine)

# Flask Setup
app = Flask(__name__)
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return"""<html>
    <h1>List of all available Honolulu, HI API routes</h1>
    <ul>
    <br>
    <li>
    Return a list of precipitations from last year:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    Return a JSON list of stations from the dataset: 
    <br>
    <a href="/api/v1.0/stations">/api/v1.0/stations</a>
    </li>
    <br>
    <li>
    Return a JSON list of Temperature Observations (tobs) for the previous year:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
    <br>Replace &ltstart&gt with a date in Year-Month-Day format.
    <br>
    <a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-07</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
    <br>
    Replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format. 
    <br>
    <br>
    <a href="/api/v1.0/2017-01-01/2017-01-07">/api/v1.0/2017-01-01/2017-01-07</a>
    </li>
    <br>
    </ul>
    </html>
    """
# ///////////////////////////////////////////////////////////////////////////
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    
    
    rain= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > end_date).\
        order_by(Measurement.date).all()
# ///////////////////////////////////////////////////////////////////
# Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for rain_totals in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#///////////////////////////////////////////
@app.route("/api/v1.0/stations")
def stations():
    list_stations= session.query(Station.name, Station.station)
    stations_list = list(np.ravel(list_stations))
    return jsonify(stations_list)
# //////////////////////////////////////////
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures of pervious year"""
# Query for the dates and temperature observations from the last year.
# Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
# Return the json representation of your dictionary.
    rain = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > end_date).\
        order_by(Measurement.date).all()
# //////////////////////////////////////////////
# Create a list of dicts with `date` and `tobs` as the keys and values
    totals_rain = []
    for totals_rain in rain:
        row = {}
        row["date"] = rain[0]
        row["tobs"] = rain[1]
        totals_rain.append(row)

    return jsonify(totals_rain)
@app.route("/api/v1.0/<start>")
def trip1(start):

 # go back one year from start date and go to end of data for Min/Avg/Max temp   
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    yearago = dt.timedelta(days=365)
    start = start_date-yearago
    yearago_data=  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= yearago_data).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)
# ///////////////////////////////////////////////////////
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    yearago = dt.timedelta(days=365)
    start = start_date-yearago
    end = end_date-yearago
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= yearago).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

# ////////////////////////////////////////////////////

if __name__ == "__main__":
    app.run(debug=True)