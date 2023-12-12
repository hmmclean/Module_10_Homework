# Import the dependencies.
import numpy as np
import datetime as dt
from datetime import date, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def home():
    """List available routes"""
    return (
        f"Welcome to the Climate API for Hawaii!<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"To look at temperature minimums, maximums, and averages over different periods of time<br/>"
        f"enter in either a start date or both a start and end date (separated by a /) at the end of the route.<br/>"
        f"Format dates as YYYY-MM-DD.<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        ) 

@app.route("/api/v1.0/precipitation")
def prcp():
    """Query date and precipitation data from last 12 months"""
    # Last 12 months calculation
    one_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query for data
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()
    # Transfer data into a dictionary
    prcp_dict = [{'date': date, 'prcp': prcp} for date, prcp in prcp_data]
    
    # Return in JSON format
    return jsonify(prcp_dict)
    

@app.route("/api/v1.0/stations")
def stations():
    """List of stations"""
    # Query for data
    all_stations = session.query(station.name).all()
    # Convert to list
    stations_list = [{'name': station[0]} for station in all_stations]
    
    # Return in JSON format
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """List of temperatures over the last 12 months"""
    # Last 12 months calculation
    one_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query for data
    temp_data = session.query(measurement.tobs, measurement.date).filter(measurement.date >= one_year).all()
    # Transfer data into a dictionary
    temp_dict = [{'date': date, 'tobs' : tobs} for date, tobs in temp_data]
    
    # Return in JSON format
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def begin(start):
    # Query for data
    start_data = session.query(
        measurement.date, 
        func.min(measurement.tobs).label('min_obs_temp'), 
        func.max(measurement.tobs).label('max_obs_temp'), 
        func.avg(measurement.tobs).label('avg_obs_temp')).filter(measurement.date >= start).group_by(measurement.date).all()
    # Convert results into dictionary
    start_dict = {}
    for row in start_data:
        date, min_obs_temp, max_obs_temp, avg_obs_temp = row
        start_dict[date] = {
            'min_obs_temp': min_obs_temp,
            'max_obs_temp': max_obs_temp,
            'avg_obs_temp': avg_obs_temp
        }

    # Return in JSON format
    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def range(start, end):
    # Query for data
    date_range = session.query(
        measurement.date, 
        func.min(measurement.tobs).label('min_obs_temp'), 
        func.max(measurement.tobs).label('max_obs_temp'), 
        func.avg(measurement.tobs).label('avg_obs_temp')).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()
    # Convert results into a dictionary
    range_dict = {}
    for row in date_range:
        date, min_obs_temp, max_obs_temp, avg_obs_temp = row
        range_dict[date] = {
            'min_obs_temp': min_obs_temp,
            'max_obs_temp': max_obs_temp,
            'avg_obs_temp': avg_obs_temp
        }

    # Return in JSON format
    return jsonify(range_dict)



if __name__ == "__main__":
    app.run()