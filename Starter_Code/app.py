# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
import numpy as np
import pandas as pd
import datetime as dt 

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql.functions import session_user
from sqlalchemy.sql.selectable import subquery


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement= Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the SQL-Alchemy APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: Start and End date format: YYYY-mm-dd/YYYY-mm-dd"
    )
    

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server request climate app precipitation page...")

    # --- perform a query to retrieve all the date and precipitation values ---
    prcp_data = session.query(measurement.date, measurement.prcp).all()

    # --- close the session ---
    session.close()

    # --- convert the query results to a dictionary using date as the key and prcp as the value ---
    prcp_dict = {} 
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp
    
    # Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server request climate app station data...")
    
    # --- perform a query to retrieve all the station data ---
    results = session.query(station.id, station.station, station.name).all()

    # --- close the session ---
    session.close()

    # --- create a list of dictionaries with station info using for loop---
    list_stations = []

    for stn in results:
        station_dict = {}

        station_dict["id"] = stn[0]
        station_dict["station"] = stn[1]
        station_dict["name"] = stn[2]

        list_stations.append(station_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(list_stations)

@app.route("/api/v1.0/tobs<br")
def tobs():
    # --- perform a query to retrieve all the the dates and temperature observations 
    # of the most-active station for the previous year of data. ---
    recent_active_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active).first()

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=query_date).filter(Measurement.station == most_active).all()

    # --- close the session ---
    session.close()

    # --- create a list of dictionaries with tobs,date info using for loop---
    tobs_data = []
    tobs_date = []
    for temp, date in tobs:
        tobs_data.append(tobs)
        tobs_date.append(date)
        tobs_dict = dict(zip(tobs_date, tobs_data))
            # Return a JSON list of stations from the dataset.
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
# Define function, set "start" date entered by user as parameter for start_date decorator 
def start_date(start):
    session = Session(engine) 

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # Create query for minimum, average, and max tobs where query date is greater than or equal to the date the user submits in URL
    start_date_tobs_results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close() 

    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_date_tobs_values =[]
    for min, avg, max in start_date_tobs_results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["average"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)
    
    return jsonify(start_date_tobs_values)

# Create a route that when given the start date only, returns the minimum, average, and maximum temperature observed for all dates greater than or equal to the start date entered by a user

@app.route("/api/v1.0/<start>/<end>")

# Define function, set start and end dates entered by user as parameters for start_end_date decorator
def Start_end_date(start, end):
    session = Session(engine)

    """Return a list of min, avg and max tobs between start and end dates entered"""
    
    # Create query for minimum, average, and max tobs where query date is greater than or equal to the start date and less than or equal to end date user submits in URL

    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()
  
    # Create a list of min,max,and average temps that will be appended with dictionary values for min, max, and avg tobs queried above
    start_end_tobs_date_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_date_dict = {}
        start_end_tobs_date_dict["min_temp"] = min
        start_end_tobs_date_dict["avg_temp"] = avg
        start_end_tobs_date_dict["max_temp"] = max
        start_end_tobs_date_values.append(start_end_tobs_date_dict) 
    

    return jsonify(start_end_tobs_date_values)
   
if __name__ == '__main__':
    app.run(debug=True) 